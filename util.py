import json
import random
import time
import requests
from config import global_config
import os
from subprocess import Popen
import faker
import shutil
import re


def check_path(path, delete=False, exist_ok=True):
    """
    检查 文件夹/文件 是否存在
    :param path: 对象路径
    :param delete: 如果对象已存在, 是否删除
    :param exist_ok: 如果文件夹内有文件存在, 是否删除, True为继续删除, False为报错
    """
    if re.findall(r'\.[\d\w]+$', path):
        """以是否以.数字/英文结尾来判断是否为文件路径"""
        if os.path.exists(path) and delete:
            os.remove(path)
        return True
    else:
        """对象非文件时按文件夹处理"""
        if not os.path.exists(path):
            """不存在时新建文件夹"""
            os.makedirs(path)
        elif delete and exist_ok:
            shutil.rmtree(path)
        elif delete and not exist_ok:
            try:
                os.rmdir(path)
            except OSError:
                raise Exception("目标文件夹下存在文件, 无法删除!")
        return True


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
    从config中生成随机的用户代理
    :return:
    """
    user_agents = list(json.loads(global_config.get('connect_config', 'user_agents').replace('\n', '')).values())
    return random.choice(user_agents)


def wait_some_time():
    """睡眠0.1s至0.3s"""
    time.sleep(random.randint(100, 300) / 100)


def create_user_agent():
    """使用faker包生成随机user-agent"""
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
    """根据系统类型调用打开图像指令"""
    if os.name == "nt":
        Popen('start ' + image_file, shell=True)  # for Windows
    else:
        if os.uname()[0] == "Linux":
            if "deepin" in os.uname()[2]:
                os.system("deepin-image-viewer " + image_file)  # for deepin
            else:
                os.system("eog " + image_file)  # for Linux
        else:
            os.system("open " + image_file)  # for Mac


def save_image(resp, image_file):
    """
    保存目标图像到本地
    :param resp: 下载对象的response
    :param image_file: 保存路径
    """
    with open(image_file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)


class SlightException(Exception):
    """自定义报错组件, 用于区分是否需要跳出程序的错误"""
    def __init__(self, message):
        super().__init__(message)
