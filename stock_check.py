import json
import time

from config import global_config
from Seckill import Seckiller
import random
from logger import logger
from lxml import etree
from lxml.html import tostring
import re
from util import wait_some_time

"""获取商品的抢购链接
点击"抢购"按钮后，会有两次302跳转，最后到达订单结算页面
这里返回第一次跳转后的页面url，作为商品的抢购链接
:return: 商品的抢购链接
"""


# 访问商品网站
def get_sku_title(self):
    """获取商品名称"""
    url = 'https://item.jd.com/{}.html'.format(global_config.getRaw('config', 'sku_id'))
    header = {
        'host': 'item.jd.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': self.user_agent
    }
    while True:
        resp = self.session.get(url, headers=header)
        if re.findall(r'returnUrl=', resp.text):
            logger.info("页面跳转，正在重定位……")
            time.sleep(1)
            continue
        x_data = etree.HTML(resp.text)
        title = x_data.xpath('/html/head/title/text()')
        logger.info("商品名称：{}".format(title))
        break


# 添加购物车
def add_to_cart(self):
    url = 'https://cart.jd.com/gate.action'
    payload = {
        'ptype': self.seckill_num,
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


# 查询购物车
def cart_check(self):
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


# 获取订单参数
def get_order_info(self):
    url = 'https://trade.jd.com/shopping/order/getOrderInfo.action'
    header = {
        'host': 'trade.jd.com',
        'Referer': 'https://cart.jd.com/',
        'User-Agent': self.user_agent
    }
    logger.info("获取订单所需信息中……")
    resp = self.session.get(url=url, headers=header)    # 得到生成订单的html完整信息
    x_data_order = etree.HTML(resp.text)  # 建树查询
    ship_info = x_data_order.xpath(
        '//div[@id="container"]//div[@id="shipAndSkuInfo"]/div[@id="payShipAndSkuInfo"]/script')[0]
    # 获取shipAndSkuInfo元素
    ship_info = tostring(ship_info).decode('utf-8')
    ship_text = re.findall(r'var successRusult=(.*);\n</script>\n', ship_info)[0]
    ship_json = json.loads(ship_text)
    vendor_remark = ship_json.get('freightInsureView').get('venderInsuranceList')[0].get('venderId')
    if vendor_remark <= 0:
        self.vendor = "[]"
    else:
        self.vendor = "[{\"venderId\":\"" + str(vendor_remark) + "\",\"remark\":\"\"}]"
    self.sop = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="sopNotPutInvoice"]/@value')[0]
    # 获取sopNotPutInvoice元素
    self.trackID = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="TrackID"]/@value')
    # 获取TrackID参数
    presale = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="presaleStockSign"]/@value')[0]
    # 获取presaleStockSign元素
    if presale:
        self.presale = "1"
    else:
        self.presale = "0"
    self.ignore = x_data_order.xpath('/html/body[@id="mainframe"]/input[@id="ignorePriceChange"]/@value')[0]
    # 获取ignorePriceChange参数


# 生成订单
def order_submit(self):
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


# 提交订单
def order_success(self):
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


if __name__ == "__main__":
    jd_seckill = Seckiller()
    jd_seckill.login_by_qrcode()
    get_sku_title(jd_seckill)
    jd_seckill.timers.start()
    for i in range(3):
        try:
            add_to_cart(jd_seckill)
            while True:
                cart_check(jd_seckill)
                get_order_info(jd_seckill)
                if order_submit(jd_seckill):
                    logger.info("订单生成成功！订单ID为：{}，请前去支付……".format(jd_seckill.orderId))
                    break
                else:
                    logger.info("订单生成失败……")
            break
        except Exception as e:
            logger.info('抢购发生异常，稍后继续执行！', e)
        wait_some_time()

