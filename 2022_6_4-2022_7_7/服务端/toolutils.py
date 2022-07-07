import json
import random
import string


def to_json_str(t) -> str:
    """将对象转换为json字符串"""
    return json.dumps(t, ensure_ascii=False)

def random_str(length=32) -> str:
    """生成随机串"""
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


if __name__ == "__main__":
    print(random_str())
