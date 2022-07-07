import base64
import json
try:
    from core import ECloudRequest
except:
    from ecloud_apis.core import ECloudRequest


def generate_body(text):
    """
    构建body参数
    :return:dict
    """
    data = {
        "items": [
            {"textId": "0", "text": text}
        ]
    }
    return json.dumps(data)


def generate_headers():
    headers = {
        'Content-Type': 'application/json',
    }
    return headers


baseUrl = '/api/nlp/v1/keywords'


def parse(response):
    if response["state"] == "ERROR":
        raise Exception(response["errorMessage"])
    elif response["state"] == "OK":
        return [i["name"] for i in response["body"]["items"][0]["keywords"]]


def ECloudNLP_Keywords(text=''):

    response = ECloudRequest('POST', servlet_path=baseUrl,
                             data=generate_body(text),
                             headers=generate_headers())
    print(response)
    return parse(response)


if __name__ == '__main__':
    T = ECloudNLP_Keywords("夜黑风高夜，进行了测试，最后发现效果还不错")
    print(T)