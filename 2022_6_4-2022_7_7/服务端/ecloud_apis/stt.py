"""
Speech to Text(实时语音转写) API

Author: Wu_Eden
Created: 2022/6/6 14:07
Last Modified: 2022/6/6 19:58
Change Log: 
    1.实现了基本功能 —— Wu_Eden
    2.支持回调函数 —— Wu_Eden
"""

import uuid
try:
    from core import ECloudRequest
except:
    from ecloud_apis.core import ECloudRequest
import json
import base64
import threading
import time


class ECloudSTT():
    def __init__(self):
        self.count = 1  # 计数器
        self.sendUrl = '/api/lingxiyun/cloud/ist/send_request/v1'
        self.queryUrl = '/api/lingxiyun/cloud/ist/query_result/v1'
        self.streamId = self.generate_streamId()  # streamId
        self.running = False  # 正在运行
        self.thread = threading.Thread(
            target=self.result_query)  # result query线程
        self.callback_func = None  # 回调函数

    def set_callback(self, func):
        """设置回调函数"""
        self.callback_func = func

    def generate_streamId(self):
        """生成streamId"""
        return str(uuid.uuid1())

    def renew(self):
        """重新生成streamId"""
        print("renewing streamId")
        self.streamId = self.generate_streamId()  # streamId
        self.count = 1

    def generate_body(self, base64_str):
        """生成请求body"""
        data = {
            "data": base64_str,
            "endFlag": 0
        }
        if self.count == 1:
            data["sessionParam"] = {
                "sid": str(uuid.uuid4()),
                "aue": "raw",
                "eos": "1000",
                "bos": "1000",
                "dwa": "wpgs",
                "rate": "8000",
                "hotword": "",
            }
        return json.dumps(data)

    def generate_headers(self):
        """生成请求头"""
        headers = {
            'Content-Type': 'application/json',
            'streamId': self.streamId,
            'number': str(self.count),
            'language': 'cn'
        }
        return headers

    def send(self, base64_str):
        if not self.running:
            print("STT is not running")
            return
        response = ECloudRequest('POST',
                                 servlet_path=self.sendUrl,
                                 data=self.generate_body(base64_str),
                                 headers=self.generate_headers())
        self.count += 1  # 计数器加1
        # print(response)
        if response["state"] == "FORBIDDEN" and response["errorCode"] == "ERROR_STREAM_ID_DUPLICATE":
            self.renew()

    def parse_result(self, response):
        """解析返回结果"""
        for result in response["body"]["frame_results"]:
            if result["errCode"] != 0:
                if result["errCode"] == 31019 or result["errStr"] == "session already stop":
                    """已经触发断句，会话结束"""
                    self.renew()
                    break
            ans_str = json.loads(result["ansStr"])
            st = ans_str["cn"]["st"]
            type = st["type"]
            for sentence in st["rt"]:
                ws = sentence["ws"]
                if ws is None:
                    break
                t = [word["cw"] for word in ws]
                text = "".join([word[0]['w'] for word in t])
                #print(text, type)
                if self.callback_func is not None:
                    self.callback_func(text, type)
                if type == 0:
                    self.renew()

    def result_query(self):
        print("query thread start")
        while self.running:
            time.sleep(.5)
            response = ECloudRequest('GET',
                                     servlet_path=self.queryUrl,
                                     data={},
                                     headers={'streamId': self.streamId})
            # print(response)
            self.parse_result(response)

        print("query thread stop")

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        data = {
            "data": "",
            "endFlag": 1
        }
        ECloudRequest('POST',
                      servlet_path=self.sendUrl,
                      data=json.dumps(data),
                      headers=self.generate_headers())


if __name__ == '__main__':
    #####################################################################
    # DEBUG ONLY
    #####################################################################
    def callback(text, type):
        print(text, type)

    def MIC(indata, frames, time, status):
        # print(indata, frames)
        # print(max(indata))
        # array to base64 str
        base64_data = base64.b64encode(indata)
        base64_str = base64_data.decode('utf-8')
        # print(base64_str)
        t.send(base64_str)

    import sounddevice as sd
    import time
    stream = sd.InputStream(channels=1,
                            samplerate=8000,
                            blocksize=1024*5,
                            dtype='int16',
                            callback=MIC)
    with stream:
        t = ECloudSTT()
        t.set_callback(callback)
        t.start()
        print("开始语音转写，60s后自动退出！")
        time.sleep(60)
        t.stop()
