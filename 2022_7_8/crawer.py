import json
import re
import time
import requests
from alive_progress import alive_it
import curd


class Crawer(object):
    def __init__(self):
        self.timeout = 5 # 超时时间
        self.points_url = 'http://geobiodiversity.com/api/assets/map/points/modern/Phanerozoic.json'
        self.formations_url = 'http://geobiodiversity.com/api/search/map/searchFormationByIds'
        self.section_url = 'http://geobiodiversity.com/api/search/map/section'
        self.units_url = 'http://geobiodiversity.com/api/search/map/units'
        self.fetch_fine_location = True #是否获取详细地址（耗时较多）
        self.fetch_formation_threshold = 100  # 每次从接口获取多少个formation
        self.fetch_units_page_size = 10  # 每次从接口获取多少个unit
        self.points = None  # 网页上绘制的所有点
        self.formation_ids = None  # 所有出现在points中的formation id

        curd.flush()  # 初始化数据库（清空）

    def fetch_points(self):
        """获取网页http://geobiodiversity.com/上绘制的所有点"""
        print('正在获取点数据...')
        try:
            self.points = requests.get(
                self.points_url, timeout=self.timeout).json()  # [:10]#debug only
            print('获取点数据成功！')
        except Exception as e:
            print('获取点数据失败：', e)

    def save_points(self):
        """点数据入库，同时生成映射关系"""
        assert self.points # 必须先获取点数据

        print('\nStep 1: 正在将点数据写入数据库...')
        progress_bar_wrapper = alive_it(self.points, dual_line=True) # 创建进度条
        for point in progress_bar_wrapper:
            name = point["name"]
            p = re.compile(r"[(](.*?)[)]", re.S) # 正则匹配括号内的内容
            section_id = int(re.findall(p, name)[0])
            progress_bar_wrapper.text = f'-> 正在将点 {name} 插入sections表'
            curd.insert_point(
                id=section_id,
                name=" ".join(name.split(" ")[2:]),
                collection_count=int(point["collection_count"]),
                # formation_ids=point["formation_ids"],
                formaton_count=point["count"],
                main_formation_id=point["formation_id"],
                fossil_count=int(point["fossilCount"]),
                longitude=float(point["value"][0]),
                latitude=float(point["value"][1])
            )

            for formation_id in point["formation_ids"].split(","):# 生成映射关系
                progress_bar_wrapper.text = f'-> 正在将映射 {section_id} to {formation_id} 插入sections表'
                curd.insert_section_formation_mapping(
                    section_id=section_id, formation_id=int(formation_id))

    def fetch_formations(self, id_list: list[int]):
        """"利用分页接口批量获取formation数据(一页获取所有)"""
        ids = list(map(str, id_list)) # 将id转换为字符串
        length = len(ids) # 总长度
        payload = {'ids': json.dumps(ids), 'page': 1, "pageSize": length} # 分页接口参数
        # print(payload)
        formations = requests.get(self.formations_url,
                                  params=payload,
                                  timeout=self.timeout
                                  ).json()
        # print(formations)
        assert int(formations['total']) == int(formations['pageSize']) #确保接口返回没问题
        results = formations['result'] # 获取结果
        assert len(results) == length # 再次确认返回全了请求的数据
        # print(results)
        for result in results: #遍历结果
            result["geology_location"] = None
            result["geology_locality"] = None
            if not self.fetch_fine_location: #如果不需要获取详细地址
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
        """formation数据入库"""
        assert self.points

        print('\nStep 2: 正在解析所有formation...')
        self.formation_ids = []
        for point in self.points: # 遍历所有点
            for formation_id in point["formation_ids"].split(","): # 遍历所有formation_id
                if formation_id not in self.formation_ids: # 去重
                    self.formation_ids.append(int(formation_id))
        self.formation_ids.sort() # 排序
        print(f'共有 {len(self.formation_ids)} 个formation')

        progress_bar_wrapper = alive_it(self.formation_ids, dual_line=True) # 创建进度条
        t = []
        for index, formation_id in enumerate(progress_bar_wrapper):
            progress_bar_wrapper.text = f'正在入队id: {formation_id} 等{self.fetch_formation_threshold}个formation'
            if len(t) >= self.fetch_formation_threshold or index == len(self.formation_ids)-1: # 如果队列满了或者是最后一个
                result = self.fetch_formations(t)
                t.clear() # 清空队列
                for formation in result:
                    name = formation['section_name']
                    progress_bar_wrapper.text = f'-> 正在将点 {name} 插入formations表'
                    curd.insert_formation(
                        id=formation['formation_id'],
                        # ref_id=formation['ref_id'],
                        section_id=formation['section_basic_id'],
                        # geology_id=formation['geology_id'],
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
        """通过分页接口获取units"""
        page = 1 # 初始页
        units = [] # 初始化空列表
        time.sleep(1) # 每次请求间隔1秒
        while True:
            payload = {'formation_id': formation_id,
                       'page': page,
                       "pageSize": self.fetch_units_page_size}
            result = requests.get(
                self.units_url, params=payload, timeout=self.timeout).json()
            units.extend(result['result'])
            if len(units) == result["total"]: # 全了则跳出循环
                break
            page += 1 # 页数自增
            time.sleep(1) # 每次请求间隔1秒
        return units

    def save_units(self):
        """unit数据入库"""
        assert self.formation_ids  # 必须先解析完formation

        print('\nStep 3: 正在解析所有unit...')
        print("由于并发限制，请耐心等待")
        progress_bar_wrapper = alive_it(self.formation_ids, dual_line=True) # 创建进度条
        for formation_id in progress_bar_wrapper:
            units = self.fetch_units(formation_id)
            for unit in units: # 遍历所有unit
                id = unit['unit_id']
                progress_bar_wrapper.text = f'-> 正在将 unit id: {id} 插入units表'
                curd.insert_unit(
                    id=id,
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
