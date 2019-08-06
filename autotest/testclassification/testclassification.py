#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import pytest
import allure

from autotest.web.seleniumbase import SeleniumBase
from autotest.app.ui2base import Ui2Base
from autotest.util import globaval as gl
from autotest.web import page_utils

from bs4 import BeautifulSoup
from operator import methodcaller


class TestClassification:
    """
    测试分类基类
    """
    def __init__(self, driver, kwd, kw_selector, is_selector=True):
        self.driver = driver
        self.log = gl.get_value("log")
        self.kwd = kwd
        self.kw_selector = kw_selector
        self.is_selector = is_selector

    def run_setup_ui(self, step):
        # selector 与 参数值 之间 通过 @@ 区分
        kw = step.split("|")[0].strip()
        selector_value = step.split("|")[1].strip()
        desc = step.split("|")[-1].strip()
        self.log.info("开始执行步骤：{} \n 使用关键字：{} \n 选择器以及参数：{}".format(desc, kw, selector_value))
        with pytest.allure.step(desc):
            if kw not in self.kwd:
                self.log.error("{} -- 关键字未定义, 请检查".format(kw))
                assert False, "{} -- 关键字未定义, 请检查".format(kw)
            if "@@" in selector_value:
                selector__ = selector_value.split("@@")[0].strip()
                value = selector_value.split("@@")[1].strip()
            else:
                value = selector_value
                selector__ = selector_value
            if kw in self.kw_selector:
                self.log.info("关键字{} 的参数中包含选择器, 有选择器的关键字 {}".format(kw, str(self.kw_selector)))

                params_ = list(getattr(self.driver, self.kwd[kw]).__code__.co_varnames)
                params_count = len(params_[1:])
                self.log.info("关键字：{}, 需要传入参数：{}， 传入个数： {}".format(kw, str(params_), str(params_count)))
                if self.is_selector:
                    selector = self.selector_visible(selector__)
                else:
                    selector = selector__

                if selector:
                    try:
                        if params_count > 1:
                            allure.attach("执行步骤--{0}".format(step), "执行步骤")
                            methodcaller(self.kwd[kw], selector, value)(self.driver)
                            self.log.info("执行步骤：{} 成功".format(desc))
                        else:
                            allure.attach("执行步骤--{0}".format(step), "执行步骤")
                            methodcaller(self.kwd[kw], selector__)(self.driver)
                            self.log.info("执行步骤：{} 成功".format(desc))
                    except Exception as E:
                        self.log.error("执行步骤{}失败， 失败原因: {}".format(desc, str(E)))
                        assert False, "执行步骤{}失败， 失败原因: {}".format(desc, str(E))
                else:
                    self.log.info("测试步骤:{}, 未定位到关键字: {}".format(desc, selector__))
                    assert False, "测试步骤:{}, 未定位到关键字: {}".format(desc, selector__)
            else:
                self.log.info("关键字{} 的参数中不包含选择器, 有选择器的关键字 {}".format(kw, str(self.kw_selector)))
                try:
                    allure.attach("执行步骤--{0}".format(step), "执行步骤")
                    methodcaller(self.kwd[kw], selector__)(self.driver)
                    self.log.info("执行步骤：{} 成功".format(desc))
                except Exception as E:
                    # allure.attach("", "失败截图", allure.attachment_type.JPG)
                    self.log.error("执行步骤{}失败， 失败原因: {}".format(desc, str(E)))
                    assert False, "执行步骤{}失败， 失败原因: {}".format(desc, str(E))

    def selector_visible(self, selector):
        if page_utils.is_xpath_selector(selector):
            return selector
        if page_utils.is_link_text_selector(selector):
            return selector

        convert_css = [selector, '#%s' % selector, '[name="%s"]' % selector, '[class="%s"]' % selector,
                       'a:contains("%s")' % selector, 'a:contains("%s")' % selector]
        __selector = None
        a = time.time()
        page_source = self.driver.get_page_source()

        soup = BeautifulSoup(page_source, 'html.parser')

        for selector_ in convert_css:
            self.log.info("开始判断---【{}】转为css选择器的元素是否在页面中".format(selector_))
            if soup.select_one(selector_):
                __selector = selector_
                break
        b = time.time()
        self.log.info("转换后的---【{}】转为css选择器的元素".format(selector_))
        return __selector


class WebTest(TestClassification):
    """
    web 测试
    """
    def __init__(self, driver):
        kwd = {"单击": "click",
                "打开": "open",
                "双击": "double_click",
                "获取文本": "get_text",
                "刷新页面": "refresh",
                "获取标题": "get_title",
                "后退": "go_back",
                "前进": "go_forward",
                "键入": "update_text",  # 先清空 在输入
                "设置窗体": "set_window_size",
                "执行Script": "execute_script",
                "下拉选择_值": "select_option_by_text",
                "下拉选择_索引": "select_option_by_index",
                "下拉选择_value": "select_option_by_value",
                "切换frame": "switch_to_frame",
                "切换窗体": "switch_to_window",
                "截图并保存": "save_element_as_image_file",
                "断言元素存在": "delayed_assert_element",
                "断言文本存在": "delayed_assert_text",
               }
        kw_selector = ["单击", "双击", "获取文本", "键入", "下拉选择_值",
                       "下拉选择_索引", "下拉选择_value", "断言元素存在", "断言文本存在",
                       ""]
        super(WebTest, self).__init__(SeleniumBase(driver), kwd, kw_selector)


class APPTest(TestClassification):
    """
    APP 测试
    """
    def __init__(self, driver):
        kwd = {"单击": "one_click",
               "双击": "double_click",
               "长按": "long_click",
               "键入": "send_keys",
               "获取Toast": "get_toast",
               "获取文本": "get_text",
               "断言Toast": "assert_toast",
               "断言存在": "assert_text",
               "观察": "watcher_click"
               }
        kw_selector = {"单击", "双击", "长按", "键入", "获取文本"}
        super(APPTest, self).__init__(Ui2Base(driver), kwd, kw_selector, False)


class WebViewTest(TestClassification):
    """
    webview 测试
    """
    pass


class TestClassFactory:
    """
    工厂类
    """
    @staticmethod
    def product(name, driver):
        if name == "web":
            return WebTest(driver)

        if name == 'app':
            return APPTest(driver)

        if name == 'webview':
            return WebViewTest(driver)





