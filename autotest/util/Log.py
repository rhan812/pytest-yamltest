#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time
import os
import autotest.util.globaval as gl


class Log:
    def __init__(self, logger=None, logpath=None):
        """
        指定保存日志的文件路径，日志级别，以及调用文件
        将日志存入到指定文件中
        """
        # 创建一个 logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个 handler 写日志
        self.log_time = time.strftime("%Y_%m_%d_")
        if logpath:
            self.log_path = logpath
        else:
            self.log_path = gl.get_value("runconf").get("log")

        if not os.path.exists(self.log_path):  # 创建日志目录
            os.makedirs(self.log_path)
        self.log_name = self.log_path+self.log_time+"run.log"
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')
        fh.setLevel(logging.INFO)
        if not self.logger.handlers:
            # 创建一个 handler 输出控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # 定义文件输出格式
            formatter = logging.Formatter('[%(asctime)s] %(filename)s->%(funcName)s '
                                          'line:%(lineno)d [%(levelname)s]%(message)s')
            fh.setFormatter(formatter)

            ch.setFormatter(formatter)
            # 给 logger 添加handler

            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

            fh.close()
            ch.close()

    def getlog(self):
        return self.logger

