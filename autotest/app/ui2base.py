#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import re
import pytest
import allure
import os

from autotest.util.Log import Log
import autotest.util.globaval as gl

from bs4 import BeautifulSoup
import json

log = Log().getlog()


class Ui2Base:
    def __init__(self, d):
        self.d = d
        self.timeout = 10
        self.imgfile = gl.get_value("runconf").get("imgpath")
        self.watchers_ = "ALERT"
        self.element_type = {"class": "className",
                             "resource-id": "resourceId",
                             "text": "text",
                             "xpath": "xpath",
                             "content-desc": "description"}

    def app_start(self, apkname):
        self.d.app_start(apkname)

    def click(self, selector, click_="click"):
        log.info("执行点击: {} 事件, 选择器：{}".format(click_, selector))
        # 判断页面是否加载完成
        self.wait_for_ready_state_done()
        # 根据输入的值 转为 响应的定位类型
        element_by_ = self.selector_convert_type(selector)
        log.info("判断是点击方式为：{}".format(click_))
        try:
            if click_ == "click":
                if self.element_type.get(element_by_) == "xpath":
                    self.d.xpath(selector).click()
                else:
                    eval("self.d({}='{}').click()".format(self.element_type.get(element_by_), selector))
            elif click_ == "double":
                if self.element_type.get(element_by_) == "xpath":
                    x, y = self.d.xpath(selector).get_last_match().center()
                    self.d.double_click(x, y)
                else:
                    eval("self.d({}='{}').double_click()".format(self.element_type.get(element_by_),
                                                                 selector))
            elif click_ == "long":
                if self.element_type.get(element_by_) == "xpath":
                    log.info("调用xpath获取中心点")
                    aaa = self.d.xpath(selector).get_last_match()
                    log.info("获取最后get_last_match")
                    log.info(aaa)
                    log.info("获取中心")
                    log.info(aaa.center())
                    log.info("2222222222222222")
                    x, y = self.d.xpath(selector).get_last_match().center()
                    log.info((x, y))
                    # log.info("xpath获取中心点击值为：{}{}".format(str(x), str(y)))
                    self.d.long_click(x, y)
                else:
                    eval("self.d({}='{}').long_click()".format(self.element_type.get(element_by_),
                                                               selector))
        except Exception as e:
            log.error("执行点击出现异常, 原因：{}".format(e))
            raise e

    def watcher_click(self, value):
        # 注册观察者
        if isinstance(value, str):
            if value.startswith("/"):
                el = self.d.xpath(value, self.get_page_source())
                if el.exists:
                    return self.d.click(*el.wait().center())
            elif value.startswith("[") and value.endswith("]"):
                value = eval(value)
            else:
                value = [value]
        elif isinstance(value, list):
            value = value
        self.wait_for_ready_state_done()
        elements = self.d.xpath(
            '//*[re:match(name(), "\.(TextView|Button|ImageView)$")]',
            self.get_page_source()).all()
        if len(value) == 1:
            for el in elements:
                log.info("{}====={}".format(el.text,el.attrib))
                if el.text == value[0]:
                    self.d.click(*el.center())
                elif el.attrib["content-desc"] == value[0]:
                    self.d.click(*el.center())

        elif len(value)>1:
            wen_str = ""
            for va in value:
                for el in elements:
                    if el.text == va:
                        wen_str +=".when(text='{}')".format(va)
                    elif el.attrib["content-desc"] == va:
                        wen_str += ".when(description='{}')".format(va)
            eval("self.d.watcher('{}'){}{}".format(self.watchers_, wen_str, ".click()"))

        self.d.watcher(self.watchers_).remove()

    def one_click(self, selector):
        self.click(selector, "click")

    def double_click(self, selector):
        self.click(selector, "double")

    def long_click(self, selector):
        self.click(selector, "long")

    def clear_text(self, selector):
        # 判断页面是否加载完成
        self.wait_for_ready_state_done()
        # 根据输入的值 转为 响应的定位类型
        element_by_ = self.selector_convert_type(selector)
        try:
            if self.element_type.get(element_by_) == "xpath":
                self.d.xpath(selector).clear_text()
            else:
                log.info("转换为目标执行字符:{}".format("self.d({}='{}').clear_text()".
                                               format(self.element_type.get(element_by_), selector)))
                eval("self.d({}='{}').clear_text()".format(self.element_type.get(element_by_),
                                                           selector))
        except Exception as e:
            log.error("执行清空文本框异常, 原因：{}".format(e))
            raise e

    def send_keys(self, selector, new_value):
        # 判断页面是否加载完成
        self.wait_for_ready_state_done()
        # 根据输入的值 转为 响应的定位类型
        element_by_ = self.selector_convert_type(selector)
        # 先清空输入框clear

        if self.element_type.get(element_by_) == "xpath":
            # xpath_convert_text
            self.get_xpath_text(selector, new_value)
        else:
            self.clear_text(selector)
            log.info("self.d({}='{}').set_text('{}')".format(self.element_type.get(element_by_),
                                                             selector, new_value))
            eval("self.d({}='{}').set_text('{}')".format(self.element_type.get(element_by_),
                                                         selector, new_value))

    def get_xpath_text(self, selector, new_value):
        # last_xpath_text = gl.get_value("last_xpath", None)
        self.wait_for_ready_state_done()
        log.info(self.get_page_source())
        el = self.d.xpath(selector, self.get_page_source()).all()
        if len(el) > 0:
            last_match = el[0]
            try:
                log.info("开始执行==== {}, {} ====".format(el, new_value))
                self.d.set_fastinput_ime()
                last_match.click()  # focus input-area
                self.d.clear_text()
                self.d.send_keys(new_value)
            except Exception as E:
                log.error("输入失败，失败原因：{}".format(E))
        else:
            log.error("输入失败，失败原因：通过xpath ：{} 未定位到与元素".format(selector))
            raise "输入失败，失败原因：通过xpath ：{} 未定位到与元素".format(selector)

    def get_text(self, selector):
        # 判断页面是否加载完成
        self.wait_for_ready_state_done()
        # 根据输入的值 转为 响应的定位类型
        element_by_ = self.selector_convert_type(selector)
        # 先清空输入框clear
        self.clear_text(selector)
        if self.element_type.get(element_by_) == "xpath":
            try:
                self.d.xpath(selector).get_text()
            except:
                yy = self.d.xpath(selector).info()
        else:
            exec_str = "self.d({}='{}').get_text({})".format(self.element_type.get(element_by_),
                                                             selector)
            eval(exec_str)

    def get_toast(self):
        # 判断页面是否加载完成
        self.wait_for_ready_state_done()
        return self.d.toast.get_message(5.0, default="未获取到")

    def get_page_source(self):
        return self.d.dump_hierarchy()

    def is_elemnet_action(self, by, selector, action="clickable"):
        # 是否支持指定的 元素
        xml_soup = BeautifulSoup(self.get_page_source(), "xml")
        for node in xml_soup.findChildren():
            if node.attrs.get(by) == selector:
                return node.attrs[action]

    def is_xpath_selector(self, selector):
        """
        确定选择器是否是xpath选择器的基本方法。
        """
        if selector.startswith('/') or selector.startswith('./'):
            return True
        return False

    def wait_for_ready_state_done(self):
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (self.timeout * 1000.0)
        for x in range(int(self.timeout * 10)):
            page_source = self.get_page_source()
            elements = self.d.xpath(
                '//*[re:match(name(), "\.(TextView|Button|ImageView)$")]',
                self.get_page_source()).all()
            log.info("============ {}".format(elements))
            if len(elements)>1:
                # xml_soup = BeautifulSoup(page_source, "xml")
                # if len(xml_soup.findChildren()) > 1:
                return True
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
        raise Exception("Page elements never fully loaded after %s seconds!" % self.timeout)

    def selector_convert_type(self, selector):
        if self.is_xpath_selector(selector):
            return "xpath"
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (self.timeout * 1000.0)
        self.wait_for_ready_state_done()
        for x in range(int(self.timeout * 10)):
            xml_soup = BeautifulSoup(self.get_page_source(), "xml")
            for node in xml_soup.findChildren():
                if node.attrs.get("class", None) == selector:
                    return "class"
                elif node.attrs.get("resource-id") == selector:
                    return "resource-id"
                elif node.attrs.get("text", None) == selector:
                    return "text"
                elif node.attrs.get("content-desc", None) == selector:
                    return "content-desc"
            now_ms = time.time()
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
        log.error("未找到你输入的元素-- {}".format(selector))
        raise Exception("未找到你输入的元素-- {}".format(selector))

    def save_screen_shot(self):
        fail_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        fail_pic = str(fail_time) + "错误截图"
        if self.imgfile :
            if  not os.path.exists(self.imgfile) :
                os.makedirs(self.imgfile)
            pic_name = "{}{}".format(self.imgfile, fail_pic)
        else:
            pic_name = "file/{}".format(fail_pic)
        file_info = None
        try:
            self.d.screenshot("{}.jpg".format(pic_name))
            with open(pic_name+".jpg", 'rb') as f:
                file_info = f.read()
        except Exception as e:
            log.error("{}截图失败!{}".format(pic_name, e))
        finally:
            return file_info

    def assert_toast(self, excepts):
        self.wait_for_ready_state_done()
        message = self.get_toast()
        if isinstance(excepts, list):
            excepts_ = excepts
        elif isinstance(excepts, str) and excepts.startswith("["):
            excepts_ = eval(excepts)
        else:
            excepts_ = [excepts]
        log.info("开始进行断言: 获取到toast_message: {} , 期望结果{} ".format(message, str(excepts_)))
        if message in excepts_:
            allure.attach("执行成功: 弹框消息{} 在 {} 之内".format(message, excepts_), "执行成功")
            assert True
        else:
            allure.attach(self.save_screen_shot(), "失败截图", allure.attachment_type.JPG)
            assert message in excepts_, "断言失败: 获取到toast_message: {} 不在 期望结果{}之内 ".\
                format(message, str(excepts_))

    def assert_text(self, excepts):
        self.wait_for_ready_state_done()
        log.info("开始进行断言: {}".format(json.dumps(self.find_element_or_text(excepts),
                                                ensure_ascii=False, indent=4)))
        if len(self.find_element_or_text(excepts)) > 0:
            allure.attach(self.save_screen_shot(), "失败截图", allure.attachment_type.JPG)
            assert False, "断言失败: /n {}".format(json.dumps(self.find_element_or_text(excepts),
                                                          ensure_ascii=False, indent=4))
        else:
            allure.attach("执行成功: {}".format(json.dumps(self.find_element_or_text(excepts),
                                                       ensure_ascii=False, indent=4)), "执行成功")
            assert True

    def find_element_or_text(self, texts):
        timeout = 5
        result_ = dict()
        try:
            while timeout > 0:
                xml = self.get_page_source()
                for element in texts:
                    if re.findall(element, xml):
                        log.info("查询到{}".format(element))
                    else:
                        timeout -= 1
                        result_[element] = False
                break
        except Exception as e:
            log.error("{}查找失败!{}".format(element, e))
        finally:
            return result_


# a = time.time()
# d = u2.connect("127.0.0.1:62001")
# ub = Ui2Base(d)
# ub.app_start("com.nl.android.ecgviewer")
# ub.click("取消")
# ub.click("com.nl.android.ecgviewer:id/rb_cloud_case_list")
# ub.send_keys("身份证号", "123456789")
# ub.click("获 取")
# ub.get_toast()
# b = time.time()
# print(b-a)


