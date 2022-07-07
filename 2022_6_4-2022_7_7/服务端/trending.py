"""
简易热搜模块

Author: Wu_Eden
Created: 2022/7/1 16:32
Last Modified: 2022/7/1 16:48
"""
from datetime import datetime, timedelta

threshold = timedelta(hours=3)  # 时间阈值


class news(object):
    def __init__(self):
        self.last_search_time = datetime.now()
        self.search_count = 1

    def is_expired(self):
        return self.last_search_time + threshold < datetime.now()

    def count_up(self):
        self.last_search_time = datetime.now()
        self.search_count += 1

    def get_count(self):
        return self.search_count

    def get_last_search_time(self):
        return self.last_search_time


class Trending(object):
    def __init__(self):
        self.data = {}

    def maintain(self):
        """维护排行榜"""
        for title in list(self.data.keys()):
            if self.data[title].is_expired():
                del self.data[title]

    def add(self, title):
        """添加对于新闻的计数"""
        if title not in self.data:
            self.data[title] = news()
        else:
            self.data[title].count_up()
        self.maintain()

    def get(self, limit=5):
        self.maintain()  # 维护
        # 按时间先后
        result = sorted(self.data.items(),
                        key=lambda x: x[1].get_last_search_time(), reverse=True)
        # 按搜索次数
        result = sorted(result, key=lambda x: x[1].get_count(), reverse=True)
        return [i[0] for i in result][:limit]  # 返回前limit个


if __name__ == "__main__":
    ##############################################
    # DEBUG ONLY
    ##############################################
    trending = Trending()
    trending.add("a")
    trending.add("b")
    trending.add("c")
    trending.add("d")
    trending.add("e")
    trending.add("f")
    import time
    time.sleep(1)
    trending.add("a")
    time.sleep(1)
    trending.add("b")
    trending.add("b")
    print(trending.get())
