import os
import threading
import time
from pyparsing import And
import requests
from bs4 import BeautifulSoup
from database import DBSession
import schemas
import curd
from toolutils import to_json_str
from retrying import retry
from faker import Faker

fake = Faker()


def get_headers():
    headers = {
        'User-Agent': fake.user_agent(),
    }
    return headers

"""
        for page in soup.select(".page"):  # 获取所有.page标签
            for i in page:
                if i.name == "p":  # 如果是p标签
                    # 如果是标题，则type为title，否则为paragraph
                    type = "title" if i.strong and i.strong.text == i.text else "paragraph"
                    last_index = index-1  # 算出上一个序号
                    last_is_img = False
                    if len(content) > 0:  # 如果不是第一个，则获取上一个是否是图片
                        # 上一个是图片
                        last_is_img = content[last_index]["type"] == "img"
                    if last_is_img and len(i.text) < 50:  # 如果上一个是图片,且是短文本，则合并
                        # 加上caption
                        content[last_index]["type"] += "_with_caption"
                        content[last_index]["caption"] = i.text  # 加上caption
                    else:
                        if i.text:  # 如果有文本
                            # 添加到content
                            content.append({"type": type, "text": i.text})
                            index += 1  # 序号加1
                if i.name == "div" and i.get("class") == ["photo"]:  # 如果是图片
                    url = i.select("img")[0].get("data-src")  # 获取图片url
                    # print(url)
                    # 添加到content
                    content.append({"type": "img", "url": "http:"+url})
                    index += 1  # 序号加1
                    
"""
# @retry(wait_fixed=1000*10)
def fetch(news_list):
    for news_index, news in enumerate(news_list):
        db = DBSession()  # get db session
        print("PROCESSING NEWS INDEX:", news_index, news["title"])
        # if url is empty, skip this news
        if "url" not in news or not news["url"]:
            print("url empty, skip")
            continue
        if curd.get_news_by_title(db, news["title"]):  # check if news exists
            print("news exists, skip")
            continue
        
        html_str = requests.get(
            news["url"], headers=get_headers()).text  # get html str
        soup = BeautifulSoup(html_str, 'lxml')  # 解析html
        # print(soup.prettify())
        t = soup.select("html")[0]  # 获取html标签
        tags = t.get('data-keys')  # 获取标签
        category = t.get("data-category")  # 获取分类
        if t.get("data-rec-category"):
            category = t['data-rec-category']
        summary = news["digest"]    # 获取摘要
        t = soup.select("meta")  # 获取所有meta标签
        for i in t:
            if i.get("name") == "description":  # 获取描述
                summary = i.get("content")
            if i.get("name") == "keywords":  # 获取关键字
                tags = i.get("content")
        if not category:
            print("category empty, skip")
            continue
        for i in ["/",","," ","\\"]:
            category = category.split(i)[0]
        category_whitelist=["推荐", "最新", "科技", "数码", "财经", "娱乐", "教育", "体育", "军事", "历史","社会"]
        if category not in category_whitelist:
            print("category not in whitelist, skip",category)
            continue
        """
        print(tags)
        print(category)
        print(summary)
        print("!!!!")
        """
        content = []
        index = 0  # 记录序号
        for i in soup.select(".article-body")[0]: # 获取所有.article-body标签
            if i.name == "p":  # 如果是p标签
                # 如果是标题，则type为title，否则为paragraph
                type = "title" if i.strong and i.strong.text == i.text else "paragraph"
                last_index = index-1  # 算出上一个序号
                last_is_img = False
                if len(content) > 0:  # 如果不是第一个，则获取上一个是否是图片
                    # 上一个是图片
                    last_is_img = content[last_index]["type"] == "img"
                if last_is_img and len(i.text) < 50:  # 如果上一个是图片,且是短文本，则合并
                    # 加上caption
                    content[last_index]["type"] += "_with_caption"
                    content[last_index]["caption"] = i.text  # 加上caption
                else:
                    if i.text:  # 如果有文本
                        # 添加到content
                        content.append({"type": type, "text": i.text})
                        index += 1  # 序号加1
            if i.name == "figure" and i.get("class") == ["m-photo"]:  # 如果是图片
                url = i.select("img")[0].get("data-src")  # 获取图片url
                # print(url)
                # 添加到content
                content.append({"type": "img", "url": url})
                index += 1  # 序号加1

                  
        if not content:
            print("content empty, skip")
            continue
        print(content)
        #os.exit(0)  

        try:
            curd.insert_news(db, schemas.Article(
                title=news["title"],
                category=category,
                tags=tags,
                source=news["source"],
                background_img=news["imgsrc"],
                summary=summary,
                content=to_json_str(content),
                created_at=news["ptime"],
                owner_id=1,
            ))
        except Exception as e:
            print(e)
            continue
        finally:
            db.close()
    print("DONE")


def main():
    BASE_URL = "http://c.m.163.com/nc/article"
    column_dict = [
        {"prefix": "headline", "tid": "T1348647853363", "name": "头条"},
        {"prefix": "list", "tid": "T1348648517839", "name": "娱乐"},
        {"prefix": "list", "tid": "T1348649079062", "name": "体育"},
        {"prefix": "list", "tid": "T1348648756099", "name": "财经"},
        {"prefix": "list", "tid": "T1348649580692", "name": "科技"},
        {"prefix": "list", "tid": "T1348649776727", "name": "数码"},
        #{"prefix": "list", "tid": "T1348648037603", "name": "社会"},
        #{"prefix": "list", "tid": "T1368497029546", "name": "历史"},
        {"prefix": "list", "tid": "T1348648141035", "name": "军事"},
        {"prefix": "list", "tid": "T1348654225495", "name": "教育"},
    ]
    for column in column_dict:
        url_temp = f"{BASE_URL}/{column['prefix']}/{column['tid']}"#组装url
        STEP = 100
        for i in range(5):
            url = f"{url_temp}/{i*STEP}-{STEP}.html"
            print("FETCHING:", url)
            news_list = requests.get(url, headers=get_headers()).json()[
                column['tid']]
            # print(news_list)
            fetch(news_list)

def run():
    while True:
        main()
        time.sleep(60*30)#每隔30分钟执行一次

threading.Thread(target=run, args=()).start()

