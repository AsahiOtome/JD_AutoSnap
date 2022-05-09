import json
import random
import time
import requests
from config import global_config
import os
import pickle
import faker


def check_path(path):
    """检查路径是否存在, 如果文件对象已存在则返回True, 否则新建文件夹"""
    if os.path.exists(path):
        return True
    else:
        os.makedirs(path, exist_ok=True)


def parse_json(string: str) -> dict:
    """
    将获取到的字符串转译为json串
    :param string: 获取到的jsonQuery字符串
    :return:
    """
    begin = string.find('{')
    end = len(string) - string[::-1].find('}')
    return json.loads(string[begin:end])


"""
json.loads()对字符串的读取必须严格按照单引号'包裹双引号"的形式。eg. '{"name": "Demo"}'
"""


def get_random_users() -> str:
    """
    生成随机的用户代理
    :return:
    """
    user_agents = list(json.loads(global_config.get('connect_config', 'user_agents').replace('\n', '')).values())
    return random.choice(user_agents)


def wait_some_time():
    """睡眠0.1s至0.3s"""
    time.sleep(random.randint(100, 300) / 100)


def create_user_agent():
    f = faker.Factory().create()
    ua = f.user_agent()
    return ua


def response_status(resp):
    """检查resp的返回是否为200正常"""
    if resp.status_code != requests.codes.OK:
        print('Status: %u, Url: %s' % (resp.status_code, resp.url))
        return False
    return True


def open_image(image_file):
    if os.name == "nt":
        os.system('start ' + image_file)  # for Windows
    else:
        if os.uname()[0] == "Linux":
            if "deepin" in os.uname()[2]:
                os.system("deepin-image-viewer " + image_file)  # for deepin
            else:
                os.system("eog " + image_file)  # for Linux
        else:
            os.system("open " + image_file)  # for Mac


def save_image(resp, image_file):
    with open(image_file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)

