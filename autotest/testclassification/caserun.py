#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import json
from string import Template

import uiautomator2 as u2
from selenium import webdriver
from autotest.util import globaval as gl


# 执行前置stup, teardown
def fixtur_executor(steps, is_setup=True):
    run_type = gl.get_value("runconf").get("runtype")
    # gl.get_value("log").info("--------- 执行 {} 端项目--------- ".format(run_type))
    if is_setup:
        gl.get_value("log").info("==========开始执行setup=============")
        start_time = time.time()
        if run_type == "app":
            # 连接设备
            try:
                u = u2.connect(addr=gl.get_value("device"))
                driver = u.session(gl.get_value("runconf").get("devices").get("apkname"))
                gl.set_value("driver", driver)
                start_done = time.time()
            except Exception as e:
                gl.get_value("log").error("初始化链接失败启动失败, 失败原因：".format(str(e)))
                driver.close()
            # 解锁屏幕 并启动 uiautomator服务
            conn_time = time.time()
            # d.healthcheck()
        elif run_type.lower() == "web":
            if gl.get_value("browser").lower() == "chrome":
                conn_time = time.time()
                try:
                    driver = webdriver.Chrome(gl.get_value("runconf").get("webdriver").get("chrome"))
                    gl.set_value("driver", driver)
                    start_done = time.time()
                except Exception as e:
                    gl.get_value("log").error("初始化启动失败, 失败原因：{}".format(str(e)))
                    driver.quit()
        gl.get_value("log").info("记录启动过程中耗时, 链接设备耗时：{} , 启动耗时： {}".format(str(conn_time-start_time),
                                                                          str(start_done-conn_time)))
        # 接收前置步骤
        if steps:
            gl.get_value("log").info("========== 开始执行setup中的用例 =============")
            case_run(steps.get("steps"), run_type)
            gl.get_value("log").info("========== setup中的用例执行结束 =============")
        gl.get_value("log").info("========== setup执行结束 =============")

    else:
        gl.get_value("log").info("========== 开始执行teardown =============")

        if run_type == "app":
            gl.get_value("driver").close()
        else:
            gl.get_value("driver").quit()
        gl.get_value("log").info("========== teardown执行结束 =============")


# 运行case
def case_run(casesteps, run_type):
    from autotest.testclassification.testclassification import TestClassFactory
    driver = gl.get_value("driver")
    test_type = run_type.lower()
    gl.get_value("log").info("==========================开始执行用例==========================")
    objpage = gl.get_value("objpage")
    run_ = TestClassFactory.product(test_type, driver)
    gl.get_value("log").info("加载页面对象数据:{}".format(json.dumps(objpage, ensure_ascii=False, indent=4)))
    gl.get_value("log").info("加载用例数据:{}".format(json.dumps(casesteps, ensure_ascii=False, indent=4)))
    for case_ in casesteps:
        # print("开始执行用例: ", case_)
        page_name = list(case_.keys())[0]
        if page_name not in objpage:
            gl.get_value("log").error("页面对象未定义:{}".format(page_name))
            assert False
        else:
            # 获取用例对应的 执行步骤
            case_step = objpage.get(page_name)
            # print("获取步骤:", case_step)
            #  重组页面步骤 组装成 exec 可执行的 string （valid= true, false == keyword 是否定义 ）
            if case_.get(page_name):
                case_params = dict(case_.get(page_name).get("data", {}),
                                   **case_.get(page_name).get("assert", {}))
                gl.get_value("log").info("参数与断言组合值:{}".format(json.dumps(case_params, ensure_ascii=False, indent=4)))
            else:
                case_params = {}
            # 连接相关信息
            # case_params["conn_info"] = {"conn_obj": var.connect_obj}

            for step in case_step:
                step = Template(step).safe_substitute(case_params)
                gl.get_value("log").info("重新处理后的步骤:{}".format(step))
                run_.run_setup_ui(step)
    gl.get_value("log").info("==========================用例执行结束==========================")
