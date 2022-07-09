import asyncio
import json
import os
import shutil
from faker import Faker
from alive_progress import alive_bar
import requests
import websockets as ws
fake = Faker()

LOGIN_URL = "https://www.webofknowledge.com/"
SAVE_TO_FILE_URL = "https://www.webofscience.com/api/wosnx/indic/export/saveToFile"
SEARCH_RESULT_WS_URL = "wss://www.webofscience.com/api/wosnxcorews"

session = requests.session()
sid = None
# sedimentology 的qid(不清楚是怎么生成的，担心有时效限制，还不确定)
qid = "797f56b1-54e3-4554-a8ba-bfb24b858c72-4287cf45"
# qid = "dcf37284-5aee-442f-9065-c213d7ec8125-428a4601"  # network的qid(DEBUG)
step = 1000  # 每次下载的步长
progress_bar = None  # 进度条

path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
dir_path = os.path.dirname(path)  # 所在目录路径
cache_path = os.path.join(dir_path, 'cache')  # 缓存目录路径


def flush_cache():
    """清空缓存目录"""
    shutil.rmtree(cache_path)
    os.mkdir(cache_path)


def get_headers():
    """生成headers"""
    headers = {
        'User-Agent': fake.user_agent(),  # requests的UA被屏蔽了，试了好久
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Host': 'www.webofscience.com',
        'Origin': 'https://www.webofscience.com',
        'Referer': 'https://www.webofscience.com',
    }
    if sid:  # 如果登录了，则添加sid到headers
        headers["X-1P-WOS-SID"] = sid

    return headers


def login():
    print("正在登录...")
    session.get(LOGIN_URL, allow_redirects=True)  # 让服务端鉴权
    cookies = session.cookies.get_dict()  # 获取cookies
    if "SID" in cookies:  # 鉴权成功
        global sid
        sid = cookies["SID"].replace("\"", "")
        print("登录成功,sid为:", sid)
        print("客户名为:", cookies["CUSTOMER"])
        print("Group名为:", cookies["E_GROUP_NAME"])
    else:  # 鉴权失败
        print("认证失败! 请检查是否在校园vpn环境下运行")
        print("cookies for debug: ", cookies)


def get_count():
    """获取搜索到的论文总数"""
    async def do():
        # 居然是websocket接口
        async with ws.connect(f"{SEARCH_RESULT_WS_URL}?SID={sid}") as websocket:
            payload = {
                "commandId": "runQueryGetRecordsStream",
                "params": {
                    "qid": qid,
                    "retrieve": {},
                    "product": "ALLDB",
                    "searchMode": "general"
                },
                "id": 1
            }
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            data = json.loads(response)
            print(data)
            if data["key"] == "searchInfo":
                result = data["payload"]
                print(result)
                return result["RecordsAvailable"]
                """
                # 结果示例

                # RecordsAvailable: 100000
                # RecordsFound: 467624
                # RecordsSearched: 51933969

                # 尝试发现RecordsAvailable是准的,RecordsFound是不准的
                # 可能是因为最大数量需要学校买，否则会限制
                """
            else:
                print("服务器返回非法！")
                return

    assert sid, "请先登录"
    return asyncio.get_event_loop().run_until_complete(do())


def fetch_data(start, end):
    """下载xls文件"""
    payload = {
        "action": "saveToExcel",
        "bm-telemetry": "",
        "colName": "ALLDB",
        "displayTimesCited": "true",
        "displayCitedRefs": "true",
        "displayUsageInfo": "true",

        # 把所有字段都选上了,比如 摘要、会议信息、PubMed ID 这些默认没选的
        "fieldList": [
            "AUTHORS",
            "TITLE",
            "SOURCE",
            "CITTIMES",
            "ACCESSION_NUM",
            "ABSTRACT",
            "AUTHORSIDENTIFIERS",
            "ISSN_ISBN",
            "PMID",
            "CONFERENCE_INFO_SPONSORS",
            "USAGEIND"
        ],

        "fileOpt": "xls",
        "isRefQuery": "false",
        "locale": "zh_CN",
        "markFrom": str(start),
        "markTo": str(end),
        "parentQid": qid,
        "product": "UA",
        "sortBy": "relevance",
        "view": "summary",
    }

    assert sid, "请先登录"

    filename = f"{start}-{end}.xls"  # 文件名
    progress_bar.text = f"-> 正在下载: {filename}"
    r = session.post(SAVE_TO_FILE_URL, json=payload, headers=get_headers())
    if r.status_code == 200:  # 200状态码表示下载成功
        # print("下载成功！")
        pass
    else:
        raise RuntimeError("下载失败！")

    file_path = os.path.join(cache_path, filename)

    with open(file_path, "wb") as f:
        f.write(r.content)
        f.close()


def xls_merge():
    """ TODO: 将xls文件合并成一个 """
    pass


def run():
    flush_cache()
    login()
    if not sid:
        return

    count = get_count()  # 可能是因为服务端有bug，测试发现能获取总数再多一个
    print(f"共找到 {count} 条记录")

    start, end = 1, step
    global progress_bar
    with alive_bar(count, manual=True, dual_line=True, title='总进度') as bar:  # 创建一个进度条
        progress_bar = bar
        while start <= count:
            if end > count:
                end = count
            fetch_data(start, end)
            bar(end/count)  # 更新进度条
            start += step
            end += step

    xls_merge()
    print("DONE!")


if __name__ == "__main__":
    run()
