"""
Optical Character Recognition(光符文字识别) API

Author: Wu_Eden
Created: 2022/6/6 11:31
Last Modified: 2022/6/6 11:58
Change Log: 
    1.创建了本文件 —— Wu_Eden
    2.实现了基本功能 —— Wu_Eden
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


baseUrl = '/api/ocr/v1/general'


def parse(response):
    result = ''
    for row in response.get('items', []):
        result += row.get('itemstring', '')
    return result


def ECloudOCR(file_path=None, base64_str=''):
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
    ECloudOCR(r"C:\Users\zzxjl\Pictures\deblur.jpg")
