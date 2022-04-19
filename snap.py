import json
import time

from config import global_config
import random
from logger import logger
from lxml import etree
from lxml.html import tostring
import re
from util import wait_some_time, SpiderSession

"""
获取商品的抢购链接
点击"抢购"按钮后，会有两次302跳转，最后到达订单结算页面
这里返回第一次跳转后的页面url，作为商品的抢购链接
:return: 商品的抢购链接
"""


class JDSnap(object):
    def __init__(self):
        self.session = SpiderSession()  # 此时为对SpiderSession对象的调用
        self.session.load_cookies_from_local()

        # 初始化信息
        self.sku_id = global_config.get('config', 'sku_id')
        self.snap_num = eval(global_config.get('settings', 'buy_amount'))

        self.cart_url = dict()
        self.snap_params = dict()

        self.session = self.session.get_session()  # 即为SpiderSession.session
        self.user_agent = self.session.user_agent
        self.nick_name = None

    def get_sku_title(self):
        """
        访问商品网站, 获取商品名称
        使用参数: sku_id, header
        """
        url = 'https://item.jd.com/{}.html'.format(self.sku_id)
        header = {
            'host': 'item.jd.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        while True:
            resp = self.session.get(url, headers=header)
            if re.findall(r'returnUrl=', resp.text):
                logger.info("页面跳转，正在重定位……")
                wait_some_time()
                continue
            x_data = etree.HTML(resp.text)
            title = x_data.xpath('/html/head/title/text()')
            logger.info("商品名称：{}".format(title))
            break

    def add_to_cart(self):
        """
        将商品添加到购物车
        使用参数: header, sku_id, pcount
        :return:
        """
        url = 'https://cart.jd.com/gate.action'
        payload = {
            'ptype': self.snap_num,
            'pid': self.sku_id,
            'pcount': '1',
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://item.jd.com/',
        }
        logger.info("正在将商品放入购物车……")
        resp = self.session.get(url=url, headers=headers, params=payload)
        self.cart_url = resp.url

    def cart_check(self):
        """
        对购物车进行一次查询
        """
        url = 'https://cart.jd.com/cart.action'
        param = {
            'r': random.random()
        }
        header = {
            'host': 'cart.jd.com',
            'User-Agent': self.user_agent,
            'Referer': self.cart_url
        }
        logger.info("正在从购物车选取商品……")
        self.session.get(url=url, headers=header, params=param)

    def get_order_info(self):
        """
        获取订单参数
        :return:
        """
        url = 'https://trade.jd.com/shopping/order/getOrderInfo.action'
        header = {
            'host': 'trade.jd.com',
            'Referer': 'https://cart.jd.com/',
            'User-Agent': self.user_agent
        }
        logger.info("获取订单所需信息中……")
        resp = self.session.get(url=url, headers=header)  # 得到生成订单的html完整信息

        x_data_order = etree.HTML(resp.text)  # 建树查询
        ship_info = x_data_order.xpath(
            '//div[@id="container"]//div[@id="shipAndSkuInfo"]/div[@id="payShipAndSkuInfo"]/script')[0]

        """获取shipAndSkuInfo元素"""
        ship_info = tostring(ship_info).decode('utf-8')
        ship_text = re.findall(r'var successRusult=(.*);\n</script>\n', ship_info)[0]
        ship_json = json.loads(ship_text)
        vendor_remark = ship_json.get('freightInsureView').get('venderInsuranceList')[0].get('venderId')
        if vendor_remark <= 0:
            self.snap_params.update({"vendor": "[]"})
        else:
            self.snap_params.update({"vendor": "[{\"venderId\":\"" + str(vendor_remark) + "\",\"remark\":\"\"}]"})

        """获取sopNotPutInvoice元素"""
        sop_info = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="sopNotPutInvoice"]/@value')[0]
        self.snap_params.update({"sop": sop_info})

        """获取TrackID参数"""
        track_id_info = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="TrackID"]/@value')
        self.snap_params.update({"trackID": track_id_info})

        """获取presaleStockSign元素"""
        presale = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="presaleStockSign"]/@value')[0]
        if presale:
            self.snap_params.update({"presale": "1"})
        else:
            self.snap_params.update({"presale": "0"})

        """获取ignorePriceChange参数"""
        ignore_info = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="ignorePriceChange"]/@value')[0]
        self.snap_params.update({"ignore": ignore_info})


def order_submit(self):
    """
    生成订单
    :param self:
    :return:
    """
    url = 'https://trade.jd.com/shopping/order/submitOrder.action'
    data = {
        "overseaPurchaseCookies": "",
        "vendorRemarks": self.vendor,
        "submitOrderParam.sopNotPutInvoice": self.sop,
        "submitOrderParam.trackID": self.trackID,
        "presaleStockSign": self.presale,
        "submitOrderParam.ignorePriceChange": self.ignore,
        "submitOrderParam.btSupport": "0",
        "submitOrderParam.jxj": "1"
    }
    param = {
        'presaleStockSign': 1
    }
    header = {
        'Host': 'trade.jd.com',
        'Origin': 'https://trade.jd.com',
        'Referer': 'https://trade.jd.com/shopping/order/getOrderInfo.action',
        'User-Agent': self.user_agent
    }
    logger.info("尝试提交订单……")
    resp = self.session.get(url, params=param, headers=header, data=data)
    resp_json = resp.json()
    if resp_json.get('success'):
        self.orderId = resp_json.get('orderId')
        return True
    else:
        return False


def order_success(self):
    """提交订单"""
    url = "https://success.jd.com/success/success.action"
    header = {
        "Host": "success.jd.com",
        "Referer": "https://trade.jd.com/",
        "Upgrade-Insecure-Requests": '1'
    }
    param = {
        "orderId": self.orderId,
        "rid": random.random()
    }
    self.session.get(url, headers=header, params=param)
