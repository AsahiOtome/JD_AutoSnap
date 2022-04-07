import logging.handlers
from util import check_path


# 创建日志对象
logger = logging.getLogger()


def set_logger():
    """用于为logger实例化对象添加handlers与设置格式"""
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

    check_path('./Logs/')       # 检查logs存储目录是否存在
    rh = logging.handlers.RotatingFileHandler(
        './Logs\\JD_AutoSnap.log', maxBytes=30, backupCount=5, encoding='utf-8')
    # 最大字节数为30b, 回滚文件数为5
    rh.setLevel(logging.INFO)
    rh.setFormatter(formatter)
    logger.addHandler(rh)


set_logger()

