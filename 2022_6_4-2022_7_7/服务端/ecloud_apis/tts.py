"""
Text to Speech(语音转文字) API

Author: Wu_Eden
Created: 2022/6/6 13:41
Last Modified: 2022/6/6 21:01
Change Log: 
    1.创建了本文件 —— Wu_Eden
    2.实现了基本功能 —— Wu_Eden
    3.wav缓存到本地，不再重复提交请求 —— Wu_Eden
    4.异常抛出 —— Wu_Eden
"""

import uuid
import json
import base64
import wave
try:
    from core import ECloudRequest
except:
    from ecloud_apis.core import ECloudRequest
import hashlib
import os


def generate_body(text, voice_name="xiaofeng", speed=0, volume=0):
    """
    构建参数
    :return:
    """
    data = {
        "text": text,
        "sessionParam": {
            "sid": str(uuid.uuid4()),
            "audio_coding": "raw",
            "native_voice_name": voice_name,
            "speed": speed,
            "volume": volume
        }
    }
    return json.dumps(data)


def generate_headers():
    headers = {
        'Content-Type': 'application/json',
    }
    return headers


def generate_file_path(text):
    filename = hashlib.md5(text.encode('utf-8')).hexdigest()
    path = f"./ecloud_apis/tts_cache/{filename}.wav"
    return path


def response_to_wav(response, path):
    """
    返回wav文件
    :param response:
    :return:
    """
    if response['state'] == 'OK':
        data = response['body']['data']
        data = data.replace("\n", "")
        if data:
            audio = base64.b64decode(data)
            with wave.open(path, 'wb') as wave_file:
                wave_file.setframerate(16000)
                wave_file.setsampwidth(2)
                wave_file.setnchannels(1)
                wave_file.writeframes(audio)
            return path
        raise Exception("No data received")
    else:
        raise Exception("ecloud remote server error")


baseUrl = '/api/lingxiyun/cloud/tts/v1'


def ECloudTTS(text):
    path = generate_file_path(text)
    if os.path.exists(path):
        print("tts命中缓存，不再进行请求！", text)
        return path
    else:
        response = ECloudRequest('POST', servlet_path=baseUrl,
                                 data=generate_body(text),
                                 headers=generate_headers())
        return response_to_wav(response, path)


if __name__ == '__main__':
    print(ECloudTTS("NUISTer"))
