import hashlib
import os
import requests
import json


class QQLogin():
    def __init__(self, access_token):
        self.app_id = "102007045"
        self.app_key = "KaeU6VigPt88tOeh"
        self.access_token = access_token

    def get_avatar(self, url):
        """ 下载头像 """
        r = requests.get(url)
        # calc md5 from url string
        md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
        path = f'./avatar/{md5}.jpg' # 保存到avatar文件夹
        if not os.path.exists(path): # 如果不存在就下载
            with open(path, 'wb') as f:
                f.write(r.content) # 写入文件系统
        return f'{md5}.jpg'

    def fetch(self):
        """ 获取用户信息 """
        res = requests.get(
            f"https://graph.qq.com/oauth2.0/me?unionid=1&access_token={self.access_token}")
        result = json.loads(res.text[10:-3]) # 去掉前10个字符和最后3个字符(这个接口返回不是纯json)
        print(result)
        openid = result["openid"]
        unionid = result["unionid"]
        info = requests.get(
            f"https://graph.qq.com/user/get_simple_userinfo?access_token={self.access_token}&openid={openid}&oauth_consumer_key={self.app_id}&format=json ")
        result = json.loads(info.text)
        print(result)
        avatarurl = result["figureurl_qq_2"]
        nickname = result["nickname"]
        avatar_path = self.get_avatar(avatarurl)
        print(unionid, avatarurl, nickname, avatar_path)
        return {"unionid": unionid, "avatar_url": avatarurl, "nickname": nickname,"avatar_path":avatar_path}


if __name__ == "__main__":
    qq_login = QQLogin("AC3B16294E87FDAA508A06DA2CC6BF30")
    qq_login.fetch()
