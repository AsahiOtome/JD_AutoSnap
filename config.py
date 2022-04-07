import configparser
import os

"""
conf.ini:
[setting]
url = https://%(host)s/%(id)s.html
host = www.jd.com
id = 10869467

ConfigParser.get() 能够进行%(value)s格式数据的自动填充, 但如果没有对应的key = value对, 将会报错
    print:  https://www.jd.com/10869467.html
RawConfigParser.get() 则不会进行自动的配对, 会把原本的数据内容读入
"""


class GlobalConfig(object):
    def __init__(self, config_file='config.ini'):
        self._path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError('未能在\'{}\'目录下找到配置文件！请检查！'.format(os.getcwd()))
        self._conf = configparser.ConfigParser()
        self._conf.read(self._path, encoding='utf-8-sig')

    def get(self, section: str, option: str) -> str:
        """指定section与option, 返回对应值"""
        return self._conf.get(section, option)

    def set(self, section: str, option: str, value):
        """更改对应值"""
        self._conf.set(section, option, value)

    def delete(self, section: str, option: str):
        """删除目标option"""
        self._conf.remove_option(section, option)

    def save(self):
        """将更改后的信息写回文件中"""
        with open(self._path, "wt", encoding="utf-8-sig") as f:
            self._conf.write(f)

    def get_items(self) -> dict:
        """
        以遍历的形式返回所有config信息
        :return:字典
        """
        items = {}
        for section in self._conf.values():
            items[section.name] = {}
            for key, value in section.items():
                items[section.name][key] = value
        return items


global_config = GlobalConfig()
