import logging.handlers


# 创建日志对象
logger = logging.getLogger()


def setLogger():
    logger.setLevel(logging.INFO)  # 设置日志默认级别为INFO级
    # 设置日志格式
    formatter = logging.Formatter(fmt='[%(asctime)s] %(module)s.%(funcName)s %(levelname)s: %(message)s',
                                  datefmt='%Y-%m-%d %T')

    """
    StreamHandler 控制台输出日志
    FileHandler 日志输出到文件
    TimedRotatingFileHandler 按时间日志分割
    RotatingFileHandler 回滚式输出到文件
    """
    sh = logging.StreamHandler()    # 添加StreamHandler输出规则
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # fh = logging.FileHandler('./Database\\StocksCheck.log', encoding='utf-8')
    # fh.setLevel(logging.INFO)
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)

    # 添加回滚文件保存规则
    rh = logging.handlers.RotatingFileHandler(
        './Logs\\JD_AutoSnap.log', maxBytes=30, backupCount=5, encoding='utf-8')
    rh.setLevel(logging.INFO)
    rh.setFormatter(formatter)
    logger.addHandler(rh)


setLogger()

