import datetime
import json
import re
import time
import requests
from alive_progress import alive_it
import curd


class Crawer(object):
    def __init__(self):
        self.timeout = 5
        self.points_url = 'http://geobiodiversity.com/api/assets/map/points/modern/Phanerozoic.json'
        self.formations_url = 'http://geobiodiversity.com/api/search/map/searchFormationByIds'
        self.section_url = 'http://geobiodiversity.com/api/search/map/section'
        self.units_url = 'http://geobiodiversity.com/api/search/map/units'
        self.fetch_fine_location = False
        self.fetch_formation_threshold = 100  # 每次从接口获取多少个formation
        self.fetch_units_page_size = 10  # 每次从接口获取多少个unit
        self.points = None  # 网页上绘制的所有点
        self.formation_ids = None  # 所有出现在points中的formation id
        self.units = None

        curd.flush()  # 初始化数据库（清空）

    def fetch_points(self):
        print('正在获取点数据...')
        try:
            self.points = requests.get(
                self.points_url, timeout=self.timeout).json()#[:10]#debug only
            print('获取点数据成功！')
        except Exception as e:
            print('获取点数据失败：', e)

    def save_points(self):
        assert self.points

        print('\nStep 1: 正在将点数据写入数据库...')
        progress_bar_wrapper = alive_it(self.points, dual_line=True)
        for point in progress_bar_wrapper:
            name = point["name"]
            p = re.compile(r"[(](.*?)[)]", re.S)
            section_id = int(re.findall(p, name)[0])
            progress_bar_wrapper.text = f'-> 正在将点 {name} 插入points表'
            curd.insert_point(
                id=section_id,
                name=" ".join(name.split(" ")[2:]),
                collection_count=int(point["collection_count"]),
                #formation_ids=point["formation_ids"],
                formaton_count=point["count"],
                main_formation_id=point["formation_id"],
                fossil_count=int(point["fossilCount"]),
                longitude=float(point["value"][0]),
                latitude=float(point["value"][1])
            )
            for formation_id in point["formation_ids"].split(","):
                curd.insert_section_formation_mapping(
                    section_id=section_id, formation_id=int(formation_id))

    def fetch_formations(self, id_list: list[int]):
        ids = list(map(str, id_list))
        length = len(ids)
        payload = {'ids': json.dumps(ids), 'page': 1, "pageSize": length}
        # print(payload)
        formations = requests.get(self.formations_url,
                                  params=payload,
                                  timeout=self.timeout
                                  ).json()
        # print(formations)
        assert int(formations['total']) == int(formations['pageSize'])
        results = formations['result']
        assert len(results) == length
        # print(results)
        for result in results:
            result["geology_location"] = None
            result["geology_locality"] = None
            if not self.fetch_fine_location:
                continue

            formation_id = result['formation_id']
            print(
                f"正在获取完整地址 url:{self.section_url}?formation_id={formation_id}")
            section = requests.get(f"{self.section_url}?formation_id={formation_id}",
                                   timeout=self.timeout
                                   ).json()["result"][0]
            result["geology_location"] = section["geology_location"]
            result["geology_locality"] = section["geology_locality"]
            """
            这个接口只能一次返回一个,大量请求会导致cc防护
            所有必须慢慢请求
            主要是补全 geology_location 和 geology_locality 两个字段
            geology_locality 就是具体地址 eg: Xilong Jiangxi China
            观察发现 geology_location 就是地址更简短一点,一般可以用section_name代替 eg: Xilong
            个人认为可以跳过
            """
            time.sleep(1)  # 每次请求间隔1秒

        return results

    def save_formations(self):
        assert self.points

        print('\nStep 2: 正在解析所有formation...')
        self.formation_ids = []
        for point in self.points:
            for formation_id in point["formation_ids"].split(","):
                if formation_id not in self.formation_ids:
                    self.formation_ids.append(int(formation_id))
        self.formation_ids.sort()
        print(f'共有 {len(self.formation_ids)} 个formation')

        progress_bar_wrapper = alive_it(self.formation_ids, dual_line=True)
        t = []
        for index, formation_id in enumerate(progress_bar_wrapper):
            progress_bar_wrapper.text = f'正在入队id: {formation_id} 等{self.fetch_formation_threshold}个formation'
            if len(t) >= self.fetch_formation_threshold or index == len(self.formation_ids)-1:
                result = self.fetch_formations(t)
                t.clear()
                for formation in result:
                    name = formation['section_name']
                    progress_bar_wrapper.text = f'-> 正在将点 {name} 插入formations表'
                    curd.insert_formation(
                        id=formation['formation_id'],
                        # ref_id=formation['ref_id'],
                        section_id=formation['section_basic_id'],
                        #geology_id=formation['geology_id'],
                        geology_location=formation['geology_location'],
                        geology_locality=formation['geology_locality'],
                        group=formation['formation_group'],
                        member=formation['formation_member'],
                        no=formation['formation_no'],
                        name=formation['formation_name'],
                        bed=formation['formation_bed'],
                        overlying=formation['formation_overlying'],
                        underline=formation['formation_underline'],
                        color=formation['formation_color'],
                        lithology=formation['formation_lithology'],
                        longitude=float(formation['geo_longitude_decimal']),
                        latitude=float(formation['geo_latitude_decimal']),
                        thick_sign=formation['formation_thick_sign'],
                        thick=float(formation['formation_thick']),
                        thick_unit=formation['formation_thick_unit'],
                        conta_base=formation['formation_conta_base'],
                        paleoenvironment=formation['formation_paleoenvironment'],
                        accessibility=formation['accessibility'],
                        release_date=formation['release_date'],
                        early_interval=formation['early_interval'],
                        intage_max=formation['intage_max'],
                        epoch_max=formation['epoch_max'],
                        emlperiod_max=formation['emlperiod_max'],
                        period_max=formation['period_max'],
                        early_age=float(formation['early_age']),
                        late_age=float(formation['late_age']),
                        age_color=formation['age_color'],
                        erathem_max=formation['erathem_max'],
                        section_name=formation['section_name'],
                    )
            else:
                t.append(formation_id)

    def fetch_units(self, formation_id):
        page = 1
        units = []
        time.sleep(1)
        while True:
            payload = {'formation_id': formation_id,
                       'page': page,
                       "pageSize": self.fetch_units_page_size}
            result = requests.get(
                self.units_url, params=payload, timeout=self.timeout).json()
            units.extend(result['result'])
            if len(units) == result["total"]:
                break
            page += 1
            time.sleep(1)
        return units

    def save_units(self):
        assert self.formation_ids  # 必须先解析完formation

        print('\nStep 3: 正在解析所有unit...')
        print("由于并发限制，请耐心等待")
        progress_bar_wrapper = alive_it(self.formation_ids, dual_line=True)
        for formation_id in progress_bar_wrapper:
            progress_bar_wrapper.text = f'-> 正在处理 formation id: {formation_id} 的units'
            units = self.fetch_units(formation_id)
            for unit in units:
                curd.insert_unit(
                    id=unit['unit_id'],
                    no=unit['unit_no'],
                    formation_id=unit['formation_id'],
                    #ref_id = unit['ref_id'],
                    section_id=unit['section_basic_id'],
                    sum=float(unit['unit_sum']),
                    thick_sign=unit['unit_thickness_sign'],
                    thick=float(unit['unit_thickness']),
                    thick_unit=unit['unit_thickness_unit'],
                    con_base=unit['unit_con_base'],
                    lithology1a=unit['unit_lithology1a'],
                    main_lithogya=unit['unit_main_lithogya'],
                    release_date=unit['release_date'],
                    early_interval=unit['early_interval'],
                    early_age=float(unit['early_age']),
                    late_age=float(unit['late_age'])
                )

    def run(self):
        self.fetch_points()
        self.save_points()
        self.save_formations()
        self.save_units()
        print('\nDone! 操作全部完成!')


if __name__ == '__main__':
    t = Crawer()
    t.run()
