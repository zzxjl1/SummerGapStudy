"""
Object detection(目标检测) API

Author: Wu_Eden
Created: 2022/6/6 20:04
Last Modified: 2022/6/6 20:07
Change Log: 
    1.简单复用其它模块代码 —— Wu_Eden
"""

import base64
import json
try:
    from core import ECloudRequest
except:
    from ecloud_apis.core import ECloudRequest


def generate_body(base64_str):
    """
    构建body参数
    :return:dict
    """
    data = {
        "image": base64_str,
    }
    return json.dumps(data)


def generate_headers():
    headers = {
        'Content-Type': 'application/json',
    }
    return headers


baseUrl = '/api/generalimgrecog/v1/generalImageDetect'


def parse(response):
    if response["state"] == "ERROR":
        raise Exception(response["errorMessage"])
    elif response["state"] == "OK":
        return response["body"][0]["classes"][:-1].split(",")


def ECloudOBJ(file_path=None, base64_str=''):
    if file_path:
        with open(file_path, mode='rb') as f:
            base64_str = str(base64.b64encode(f.read()), encoding='utf8')
    response = ECloudRequest('POST', servlet_path=baseUrl,
                             data=generate_body(
                                 base64_str),
                             headers=generate_headers())
    # print(response)
    return parse(response)


if __name__ == '__main__':
    ECloudOBJ(r"C:\Users\zzxjl\Pictures\deblur.jpg")
