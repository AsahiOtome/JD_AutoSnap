# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
area参数自助生成
运行脚本，根据提示逐级选择区域即可
"""
import random
import json
import time

import requests

provinces = [
    {'name': '北京', 'id': 1}, {'name': '上海', 'id': 2}, {'name': '天津', 'id': 3},
    {'name': '重庆', 'id': 4}, {'name': '河北', 'id': 5}, {'name': '山西', 'id': 6},
    {'name': '河南', 'id': 7}, {'name': '辽宁', 'id': 8}, {'name': '吉林', 'id': 9},
    {'name': '黑龙江', 'id': 10}, {'name': '内蒙古', 'id': 11}, {'name': '江苏', 'id': 12},
    {'name': '山东', 'id': 13}, {'name': '安徽', 'id': 14}, {'name': '浙江', 'id': 15},
    {'name': '福建', 'id': 16}, {'name': '湖北', 'id': 17}, {'name': '湖南', 'id': 18},
    {'name': '广东', 'id': 19}, {'name': '广西', 'id': 20}, {'name': '江西', 'id': 21},
    {'name': '四川', 'id': 22}, {'name': '海南', 'id': 23}, {'name': '贵州', 'id': 24},
    {'name': '云南', 'id': 25}, {'name': '西藏', 'id': 26}, {'name': '陕西', 'id': 27},
    {'name': '甘肃', 'id': 28}, {'name': '青海', 'id': 29}, {'name': '宁夏', 'id': 30},
    {'name': '新疆', 'id': 31}, {'name': '台湾', 'id': 32}, {'name': '港澳', 'id': 52993},
    {'name': '钓鱼岛', 'id': 84}
]


def parse_json(string):
    begin = string.find('{') - 1
    end = string[::-1].find('}') - 1
    return json.loads(string[begin:len(string)-end])


def get_area_by_id(_id):
    """
    2022-02-24最新的JD区域代码获取网址
    _id: 上级地区代码号, 为最下一级时返回空
    """
    base_uri = 'https://fts.jd.com/area/get'
    payload = {
        'fid': _id,
        'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
        '_': str(int(time.time() * 1000))
    }
    resp = requests.get(url=base_uri, params=payload)
    return parse_json(resp.text)


def print_area(area_list):
    for area_item in area_list:
        print(area_item)
        print('【{}】 {}'.format(area_item['id'], area_item['name']))
    print('-------------------------------------------------')


def select_area(area_list):
    while True:
        user_input = input('请继续输入编号：').strip()
        selected_area = [area for area in area_list if str(area['id']) == user_input or area['name'] == user_input]
        if not selected_area:
            print('编号错误，请重新输入')
            continue
        print('已选择：{}'.format(selected_area[0]['name']))
        return selected_area[0]


def main():
    print_area(provinces)
    province = select_area(provinces)

    cities = get_area_by_id(province['id'])
    print_area(cities)
    city = select_area(cities)

    districts = get_area_by_id(city['id'])
    print_area(districts)
    district = select_area(districts)

    streets = get_area_by_id(district['id'])
    if not streets:
        print(
            '您选择的区域为：{}-{}-{}，id：{}_{}_{}'.format(
                province['name'], city['name'], district['name'],
                province['id'], city['id'], district['id']
            )
        )
        return

    print_area(streets)
    street = select_area(streets)
    print(
        '您选择的区域为：{}-{}-{}-{}，id：{}_{}_{}_{}'.format(
            province['name'], city['name'], district['name'], street['name'],
            province['id'], city['id'], district['id'], street['id']
        )
    )


if __name__ == '__main__':
    main()
