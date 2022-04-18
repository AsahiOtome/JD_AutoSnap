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
