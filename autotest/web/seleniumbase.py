import time
import re
import os
import pytest
import allure

import autotest.util.globaval as gl
from autotest.web import js_utils
from autotest.web import page_utils
from autotest.web import page_actions
from autotest.web import xpath_to_css

from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,
                                        MoveTargetOutOfBoundsException,
                                        WebDriverException)
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


# log = Log().getlog()


class SeleniumBase:
    def __init__(self, driver):
        self.driver = driver
        self.imgpath = gl.get_value("runconf").get("imgpath")
        self.browser = 'chrome'
        self.__last_page_load_url = "data:,"
        self.__last_url_of_delayed_assert = "data:,"
        self.__delayed_assert_count = 0

    def open(self, url):
        self.__last_page_load_url = None
        self.driver.get(url)
        self.wait_for_ready_state_complete()

    def wait_for_ready_state_complete(self):
        # 等待页面加载完成
        is_ready = js_utils.wait_for_ready_state_complete(self.driver)
        return is_ready

    def click(self, selector, by=By.CSS_SELECTOR, timeout=6):
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
            if not self.is_link_text_visible(selector):
                # 处理下拉框
                self.click_link_text(selector, timeout=timeout)
                return
        element = page_actions.wait_for_element_visible(self.driver, selector, by, timeout=timeout)
        try:
            # 判断是否是 IE ,且 by 是通过 link_text
            if self.browser == 'ie' and by == By.LINK_TEXT:
                pass
            else:
                element.click()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = page_actions.wait_for_element_visible(self.driver, selector, by, timeout=timeout)
            element.click
        except (WebDriverException, MoveTargetOutOfBoundsException):
            self.wait_for_ready_state_complete()
            try:
                self.__js_click(selector, by)
            except Exception:
                try:
                    self.__jquery_click(selector, by=by)
                except Exception:
                    element = page_actions.wait_for_element_visible(
                        self.driver, selector, by, timeout=timeout)
                    element.click()

    def double_click(self, selector, by=By.CSS_SELECTOR, timeout=3):
        from selenium.webdriver import ActionChains
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        element = page_actions.wait_for_element_visible(self.driver, selector,
                                                        by, timeout=timeout)
        try:
            action = ActionChains(self.driver)
            action.move_to_element(element)
            action.double_click(element)
            action.perform()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = page_actions.wait_for_element_visible(self.driver, selector,
                                                            by, timeout=timeout)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.double_click(element)
            actions.perform()
        self.wait_for_ready_state_complete()

    def get_text(self, selector, by=By.CSS_SELECTOR, timeout=3):
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        try:
            self.wait_for_ready_state_complete()
        except:
            pass
        time.sleep(0.01)
        element = page_actions.wait_for_element_visible(self.driver, selector, by, timeout)
        try:
            element_text = element.text
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = page_actions.wait_for_element_visible(self.driver, selector, by, timeout)
            element_text = element.text
        return element_text

    def refresh_page(self):
        self.__last_page_load_url = None
        self.driver.refresh()
        self.wait_for_ready_state_complete()

    def refresh(self):
        """ The shorter version of self.refresh_page() """
        self.refresh_page()

    def get_page_title(self):
        self.wait_for_ready_state_complete()
        return self.driver.title

    def get_title(self):
        """ The shorter version of self.get_page_title() """
        self.wait_for_ready_state_complete()
        return self.driver.title

    def go_back(self):
        # 后退
        self.__last_page_load_url = None
        self.driver.back()
        self.wait_for_ready_state_complete()

    def go_forward(self):
        # 前进
        self.__last_page_load_url = None
        self.driver.forward()
        self.wait_for_ready_state_complete()

    def send_keys(self, selector, new_value, by=By.CSS_SELECTOR, timeout=3):
        # 键入文本
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        self.add_text(selector, new_value, by=by, timeout=timeout)

    def add_text(self, selector, new_value, by=By.CSS_SELECTOR, timeout=3):
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        element = self.wait_for_element_visible(selector, by=by, timeout=timeout)
        try:
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete()
        except StaleElementReferenceException:
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete()

    def update_text(self, selector, new_value, by=By.CSS_SELECTOR, timeout=3):
        """此方法使用新值更新元素的文本值。"""
        if page_utils.is_xpath_selector(selector):
            by =By.XPATH
        element = self.wait_for_element_visible(selector, by=by, timeout=timeout)
        self.__scroll_to_element(element)
        try:
            element.clear()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.wait_for_element_visible(selector, by=by, timeout=timeout)
            element.clear()
        try:
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete()
        except StaleElementReferenceException:
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete()

    def __scroll_to_element(self, element):
        js_utils.scroll_to_element(self.driver, element)

    def click_link_text(self, link_text, timeout=6):
        """点击页面链接"""
        if not self.is_link_text_present(link_text):
            self.wait_for_link_text_present(link_text, timeout=timeout)

        per_action_url = self.get_current_url()

        try:
            element = self.wait_for_link_text_visible(link_text, timeout=0.2)
            try:
                element.click()
            except StaleElementReferenceException:
                self.wait_for_ready_state_complete()
                time.sleep(0.05)
                element = self.wait_for_link_text_visible(link_text, timeout=timeout)
                element.click()
        except Exception:
            found_css =False
            text_id = self.get_link_attribute(link_text, id, False)
            if text_id:
                link_css = '[id="%s"]' % link_text
                found_css =True
            if not found_css:
                href = self.__get_href_from_link_text(link_text, False)
                if href:
                    if href.startswith('/') or page_utils.is_valid_url(href):
                        link_css = '[href="%s"]' % href
                        found_css = True
            if not found_css:
                ngclick = self.get_link_attribute(link_text, 'ng-click', False)
                if ngclick:
                    link_css = '[ng-click="%s"]' % ngclick
                    found_css =True
            if not found_css:
                onclick = self.get_link_attribute(link_text, "onclick", False)
                if onclick:
                    link_css = '[onclick="%s"]' % onclick
                    found_css =True
            success = False
            if found_css:
                if self.is_element_visible(link_css):
                    self.click(link_css)
                    success =True
                else:
                    success = self.__click_dropdown_link_text(link_text, link_css)
            if not success:
                element = self.wait_for_link_text_visible(link_text, timeout=3)
                element.click()

    def __click_dropdown_link_text(self, link_text, link_css):
        """当一个链接可能隐藏在下拉菜单下时，使用这个。"""
        soup = self.get_beautiful_soup()
        drop_down_list = soup.select('[class*=dropdown]')
        for item in soup.select('[class*=HeaderMenu]'):
            drop_down_list.append(item)
        for item in soup.select('[class*=menu-item]'):
            drop_down_list.append(item)
        for item in soup.select('[class*=chevron]'):
            drop_down_list.append(item)
        csstype = link_css.split('[')[1].split('=')[0]
        for item in drop_down_list:
            if link_text in item.text.split('\n') and csstype in item.decode():
                dropdown_css = ""
                for css_class in item['class']:
                    dropdown_css += '.'
                    dropdown_css += css_class
                dropdown_css = item.name + dropdown_css
                matching_dropdowns = self.find_visible_elements(dropdown_css)
                for dropdown in matching_dropdowns:
                    # The same class names might be used for multiple dropdowns
                    try:
                        page_actions.hover_element_and_click(
                            self.driver, dropdown, link_text,
                            click_by=By.LINK_TEXT, timeout=0.2)
                        return True
                    except Exception:
                        pass
        return False

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        if page_utils.is_xpath_selector(selector):
            by =By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        return page_actions.is_element_visible(self.driver, selector, by)

    def __get_href_from_link_text(self, link_text, hard_fail=True):
        href = self.get_link_attribute(link_text, "href", hard_fail)
        if not href:
            return None
        if href.startswith("//"):
            link = "http:" + href
        elif href.startswith('/'):
            url = self.driver.current_url
            domain_url = self.get_domain_url(url)
            link = domain_url +href
        else:
            link = href

        return link

    def domain_url(self, url):

        return page_utils.get_domain_url(url)

    def get_link_attribute(self, link_text, attribute, hard_fail=True):
        """按链接文本输入一个链接，然后返回该属性的值。
        如果无法找到链接文本或属性，则会出现异常
        如果hard_fail为真，则引发(否则不返回任何值)。"""
        soup = self.get_beautiful_soup()
        html_links = soup.fina_all('a')
        for html_link in html_links:
            if html_link.text.strip() == link_text.strip():
                if html_link.has_attr(attribute):
                    attribute_value = html_link.get(attribute)
                    return attribute_value
                if hard_fail:
                    raise Exception(
                        'Unable to find attribute {%s} from link text {%s}!'
                        % (attribute, link_text))
                else:
                    return None
        if hard_fail:
            raise Exception("Link text {%s} was not found!" % link_text)
        else:
            return None

    def wait_for_link_text_visible(self, link_text, timeout):
        return self.wait_for_element_visible(
            link_text, by=By.LINK_TEXT, timeout=timeout)

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """等待元素出现在页面的HTML中。
        元素必须是可见的(不能隐藏)"""
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        return page_actions.wait_for_element_visible(self.driver, selector, by, timeout)

    def get_current_url(self):
        return self.driver.current_url

    def wait_for_link_text_present(self, link_text, timeout):
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        for x in range(int(timeout * 5)):
            try:
                if not self.is_link_text_present(link_text):
                    raise Exception(
                        "Link text {%s} was not found!" % link_text)
                return
            except Exception:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.2)
        raise Exception(
            "Link text {%s} was not present after %s seconds!" % (
                link_text, timeout))

    def is_link_text_present(self, link_text):
        """如果链接文本出现在页面的HTML中，则为True"""
        soup = self.get_beautiful_soup()
        html_links = soup.fina_all('a')
        for html_link in html_links:
            if html_link.text.strip() == link_text.strip():
                return True
        return False

    def get_beautiful_soup(self, source=None):
        """BeautifulSoup是一个剖析HTML文档的工具包 提取你需要的东西"""
        from bs4 import BeautifulSoup
        if not source:
            self.wait_for_ready_state_complete()
            source = self.get_page_source()
        soup = BeautifulSoup(source, 'html.parser')
        return soup

    def get_page_source(self):
        self.wait_for_ready_state_complete()
        return self.driver.page_source

    def is_link_text_visible(self, link_text):
        """
        链接的可见性
        """
        self.wait_for_ready_state_complete()
        time.sleep(0.1)
        return page_actions.is_element_visible(self.driver, link_text, by=By.LINK_TEXT)

    def find_visible_elements(self, selector, by=By.CSS_SELECTOR, limit=0):
        """ Returns a list of matching WebElements that are visible.
            If "limit" is set and > 0, will only return that many elements. """
        self.wait_for_ready_state_complete()
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        v_elems = page_actions.find_visible_elements(self.driver, selector, by)
        if limit and limit > 0 and len(v_elems) > limit:
            v_elems = v_elems[:limit]
        return v_elems

    def __js_click(self, selector, by=By.CSS_SELECTOR):
        """ Clicks an element using pure JS. Does not use jQuery. """
        selector, by = self.__recalculate_selector(selector, by)
        css_selector = self.convert_to_css_selector(selector, by=by)
        css_selector = re.escape(css_selector)
        css_selector = self.__escape_quotes_if_needed(css_selector)
        script = ("""var simulateClick = function (elem) {
                         var evt = new MouseEvent('click', {
                             bubbles: true,
                             cancelable: true,
                             view: window
                         });
                         var canceled = !elem.dispatchEvent(evt);
                     };
                     var someLink = document.querySelector('%s');
                     simulateClick(someLink);"""
                  % css_selector)
        self.execute_script(script)

    def save_element_as_image_file(self):
        """ 获取元素的屏幕快照，并将其保存为图像文件。
        如果没有指定文件夹，则将其保存到当前文件夹。 """

        element_png = self.driver.screenshot_as_png

        fail_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        fail_pic = str(fail_time) + "错误截图"
        if self.imgfile:
            if not os.path.exists(self.imgfile):
                os.makedirs(self.imgfile)
            pic_name = "{}{}".format(self.imgfile, fail_pic)
        else:
            pic_name = "file/{}".format(fail_pic)
        try:
            with open(pic_name+".jpg", 'rb') as f:
                f.write(element_png)
        except Exception as e:
            gl.get_value("log").error("{}截图失败!{}".format(pic_name, e))
        finally:
            return element_png

    def __jquery_click(self, selector, by=By.CSS_SELECTOR):
        """ 使用jQuery单击一个元素。不同于使用纯JS。"""
        selector, by = self.__recalculate_selector(selector, by)
        self.wait_for_element_present(
            selector, by=by, timeout=3)
        selector = self.convert_to_css_selector(selector, by=by)
        selector = page_utils.make_css_match_first_element_only(selector)
        click_script = """jQuery('%s')[0].click()""" % selector
        self.safe_execute_script(click_script)

    def safe_execute_script(self, script):
        """ 当执行包含jQuery命令的脚本时，
        首先加载jQuery库是很重要的。
        如果尚未加载jQuery，此方法将加载它。 """
        try:
            self.execute_script(script)
        except Exception:
            # The likely reason this fails is because: "jQuery is not defined"
            js_utils.activate_jquery(self.driver) # It's a good thing we can define it here
            self.execute_script(script)

    def __recalculate_selector(self, selector, by):
        # Try to determine the type of selector automatically
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        return (selector, by)

    def convert_xpath_to_css(self, xpath):
        return xpath_to_css.convert_xpath_to_css(xpath)

    def convert_to_css_selector(self, selector, by):
        """ This method converts a selector to a CSS_SELECTOR.
            jQuery commands require a CSS_SELECTOR for finding elements.
            This method should only be used for jQuery/JavaScript actions.
            Pure JavaScript doesn't support using a:contains("LINK_TEXT"). """
        if by == By.CSS_SELECTOR:
            return selector
        elif by == By.ID:
            return '#%s' % selector
        elif by == By.CLASS_NAME:
            return '.%s' % selector
        elif by == By.NAME:
            return '[name="%s"]' % selector
        elif by == By.TAG_NAME:
            return selector
        elif by == By.XPATH:
            return self.convert_xpath_to_css(selector)
        elif by == By.LINK_TEXT:
            return 'a:contains("%s")' % selector
        elif by == By.PARTIAL_LINK_TEXT:
            return 'a:contains("%s")' % selector
        else:
            raise Exception(
                "Exception: Could not convert {%s}(by=%s) to CSS_SELECTOR!" % (
                    selector, by))

    def select_option_by_text(self, dropdown_selector, option, by=By.CSS_SELECTOR, timeout=3):
        self.__select_option(dropdown_selector, option, by=by,
                             option_by="text", timeout=timeout)

    def select_option_by_index(self, opdown_selector, option, by=By.CSS_SELECTOR, timeout=3):
        print(self.get_page_source())
        self.__select_option(opdown_selector, option, by=by,
                             option_by="index", timeout=timeout)

    def select_option_by_value(self, opdown_selector, option, by=By.CSS_SELECTOR, timeout=3):
        self.__select_option(opdown_selector, option, by=by,
                             option_by="value", timeout=timeout)

    def switch_to_frame(self, frame, timeout=3):
        """ 切换 frame"""
        page_actions.switch_to_frame(self.driver, frame, timeout)

    def open_new_window(self, switch_to=True):
        """ Opens a new browser tab/window and switches to it by default. """
        self.driver.execute_script("window.open('');")
        time.sleep(0.01)
        if switch_to:
            self.switch_to_window(len(self.driver.window_handles) - 1)

    def find_element(self, selector, by=By.CSS_SELECTOR,
                     timeout=5):
        """ Same as wait_for_element_visible() - returns the element """
        return self.wait_for_element_visible(selector, by=by, timeout=timeout)

    def switch_to_window(self, window, timeout=3):

        page_actions.switch_to_window(self.driver, window, timeout)

    def switch_to_default_window(self):
        self.switch_to_window(0)

    def save_screenshot(self, name, folder=None):
        """ The screenshot will be in PNG format. """
        return page_actions.save_screenshot(self.driver, name, folder)

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def set_window_size(self, width, height):
        self.driver.set_window_size(width, height)

    def __select_option(self,  dropdown_selector, option, by=By.CSS_SELECTOR, option_by="text",timeout=3):
        """根据规范选择HTML <select>选项。
        选项规范由“文本”、“索引”或“值”组成。
        如果option_by未指定或未知，则默认为“text”。"""
        if page_utils.is_xpath_selector(dropdown_selector):
            by = By.XPATH
        element = self.wait_for_element_visible(dropdown_selector, by=by, timeout=timeout)

        try:
            if option_by == "value":
                Select(element).select_by_value(option)
            elif option_by == "index":
                Select(element).deselect_by_index(option)
            else:
                Select(element).select_by_visible_text(option)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.wait_for_element_visible()(dropdown_selector, by=by, timeout=timeout)
            if option_by == "value":
                Select(element).select_by_value(option)
            elif option_by == "index":
                Select(element).deselect_by_index(option)
            else:
                Select(element).select_by_visible_text(option)

    def delayed_assert_text(self, selector, text,  by=By.CSS_SELECTOR,
                            timeout=3):
        """ 页面上元素的文本的不终止断言。
        将保存故障，直到process_delayed_assert ()
        方法从测试内部调用，很可能在测试结束时调用。"""
        if not selector:
            selector = "html"
        self.__delayed_assert_count += 1
        try:
            url = self.get_current_url()
            if url == self.__last_url_of_delayed_assert:
                timeout = 1
            else:
                self.__last_url_of_delayed_assert = url
        except Exception as E:
            gl.get_value("log").error("错误信息：{}".format(str(E)))
            pass
        try:
            self.wait_for_text_visible(text, selector, by=by, timeout=timeout)
            assert True
        except Exception as E:
            gl.get_value("log").error("错误信息：{}".format(str(E)))
            allure.attach(self.save_element_as_image_file(), "失败截图", allure.attachment_type.JPG)
            assert False, "断言失败，期望结果--{}--不包含在页面内".format(text)

    def wait_for_text_visible(self, text, selector="html", by=By.CSS_SELECTOR,
                              timeout=10):
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        return page_actions.wait_for_text_visible(
            self.driver, text, selector, by, timeout)

    def delayed_assert_element(self, selector, by=By.CSS_SELECTOR,
                               timeout=3):
        """ 页上元素的不终止断言。
        将保存故障，直到process_delayed_assert ()
        方法从测试内部调用，很可能在测试结束时调用。"""
        self.__delayed_assert_count += 1
        try:
            url = self.get_current_url()
            if url == self.__last_url_of_delayed_assert:
                timeout = 1
            else:
                self.__last_url_of_delayed_assert = url
        except Exception as e:
            gl.get_value("log").error("错误信息：{}".format(str(e)))
            pass
        try:
            self.wait_for_element_visible(selector, by=by, timeout=timeout)
            assert True
            # return True
        except Exception as E:
            gl.get_value("log").error("错误信息：{}".format(str(E)))
            allure.attach(self.save_element_as_image_file(), "失败截图", allure.attachment_type.JPG)
            assert False, "断言失败：[{}] -- 元素不存下".format(selector)
            # return False

    def assert_true(self, expr, msg=None):
        """
        expr : 表达式  in
        :param expr:
        :param msg:
        :return:
        """
        self.assertTrue(expr, msg=msg)

    def assertTrue(self, expr, msg=None):
        """检查表达式是否为真。"""
        if not expr:
            msg = self._formatMessage(msg, "%s is not true" % self.safe_repr(expr))
            raise self.failureException(msg)

    def safe_repr(self, obj, short=False):
        try:
            result = repr(obj)
        except Exception:
            result = object.__repr__(obj)
        if not short or len(result) < 80:
            return result
        return result[:80] + ' [truncated]...'

    def _formatMessage(self, msg, standardMsg):
        """在生成失败消息时使用longMessage属性。
        如果longMessage是假的，这意味着:
        *如果提供了显式消息，则只使用该消息
        *否则为断言使用标准消息
        如果longMessage为真:
        使用标准信息
        *如果提供了显式消息，加上':'和显式消息
        """
        if not self.longMessage:
            return msg or standardMsg
        if msg is None:
            return standardMsg
        try:
            # don't switch to '{}' formatting in Python 2.X
            # it changes the way unicode input is handled
            return '%s : %s' % (standardMsg, msg)
        except UnicodeDecodeError:
            return '%s : %s' % (self.safe_repr(standardMsg), self.safe_repr(msg))

    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR,
                      timeout=10):
        """ This method uses JavaScript to get the value of an attribute. """
        if page_utils.is_xpath_selector(selector):
            by = By.XPATH
        if page_utils.is_link_text_selector(selector):
            selector = page_utils.get_link_text_from_selector(selector)
            by = By.LINK_TEXT
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        element = page_actions.wait_for_element_present(
            self.driver, selector, by, timeout)
        try:
            attribute_value = element.get_attribute(attribute)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = page_actions.wait_for_element_present(
                self.driver, selector, by, timeout)
            attribute_value = element.get_attribute(attribute)
        if attribute_value is not None:
            return attribute_value
        else:
            raise Exception("Element {%s} has no attribute {%s}!" % (
                selector, attribute))

    def assert_text(self, selector, text, by=By.CSS_SELECTOR,
                    timeout=3):
        """ 类似于wait_for_text_visible ()
        如果没有找到元素或文本，则引发异常。"""
        self.wait_for_text_visible(text, selector, by=by, timeout=timeout)
        return True

    def __highlight_with_assert_success(self, selector, message, by=By.CSS_SELECTOR):
        selector, by = self.__recalculate_selector(selector, by)
        element = self.find_element(selector, by=by, timeout=3)
        try:
            selector = self.convert_to_css_selector(selector, by=by)
        except Exception:
            # Don't highlight if can't convert to CSS_SELECTOR
            return
        self.__slow_scroll_to_element(element)

        o_bs = ''  # original_box_shadow
        style = element.get_attribute('style')
        if style:
            if 'box-shadow: ' in style:
                box_start = style.find('box-shadow: ')
                box_end = style.find(';', box_start) + 1
                original_box_shadow = style[box_start:box_end]
                o_bs = original_box_shadow

        if ":contains" not in selector and ":first" not in selector:
            selector = re.escape(selector)
            selector = self.__escape_quotes_if_needed(selector)
            self.__highlight_with_js_2(message, selector, o_bs)
        else:
            selector = self.__make_css_match_first_element_only(selector)
            selector = re.escape(selector)
            selector = self.__escape_quotes_if_needed(selector)
            try:
                self.__highlight_with_jquery_2(message, selector, o_bs)
            except Exception:
                pass  # JQuery probably couldn't load. Skip highlighting.
        time.sleep(0.065)


# driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
#
# driver.implicitly_wait(20)
# #
# sb = SeleniumBase(driver)
#
# sb.open("http://101.132.99.147:9002/#/login")
#
# sb.update_text('//*[@id="ais-app"]/div/div/form/div/input[1]', "admin")
#
# sb.update_text('//*[@id="ais-app"]/div/div/form/div/input[2]', 'password')
#
# sb.click("#ais-app > div > div > form > div > button")
# try:
#     new_list = sb.find_visible_elements("[class='event-search mb-2 relative ng-scope']")
#     print(len(new_list))
#     new_list_notop = []
#     for new_ in new_list:
#         try:
#             SeleniumBase(new_).find_element("[class='tagTop tag-darkylw']", timeout=0.5)
#             continue
#         except:
#             new_list_notop.append(new_)
#             continue
# except Exception as E:
#     print(E)
# finally:
#     print(len(new_list_notop))
#     for b in new_list_notop:
#         print(SeleniumBase(b).get_text("[class='ng-binding']"))
#     driver.quit()


# 点击链接的用法 (隐藏的下拉列表还是 显示可以定位的)
# 1. link=
# sb.click("link=视频")
# sb.click('link=音乐')
# 2. link_text= 
# sb.click("link_text=新闻")
# 点击按钮用法 如果 classname 唯一
# sb.click(".soutu-btn")
# 点击按钮用法 如果 id 唯一
# sb.click("#su")
# 如果 name 唯一就使用 [name="%s"]
# sb.click('[name="tj_briicon"]')
# 键入文本

# sb.send_keys("#kw", "测试")
# sb.click("#su")
# sb.update_text("#kw", "click")
# time.sleep(5)
# driver.close()
