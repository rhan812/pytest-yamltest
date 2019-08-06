#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.errorhandler import ElementNotVisibleException
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.webdriver.remote.errorhandler import NoAlertPresentException
from selenium.webdriver.remote.errorhandler import NoSuchFrameException
from selenium.webdriver.remote.errorhandler import NoSuchWindowException


def is_element_visible(driver, selector, by=By.CSS_SELECTOR):
    """
    返回指定的元素选择器在页上是否可见。
    """
    try:
        element = driver.find_element(by=by, value=selector)
        return element.is_displayed()
    except Exception:
        return False


def wait_for_element_visible(driver, selector, by, timeout, element_child=None):
    """通过给定的选择器搜索指定的元素。返回
    元素对象，如果该元素在页面上存在且可见。
    如果元素未出现在指定的超时。"""
    element = None
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            if element_child is None:

                element = driver.find_element(by=by, value=selector)
            else:
                element = element_child.find_element(by=by, value=selector)

            if element.is_displayed():
                return element
            else:
                element = None
                raise Exception()
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    if not element and by != By.LINK_TEXT:
        raise ElementNotVisibleException(
            "Element {%s} was not visible after %s second%s!" % (
                selector, timeout, plural))
    if not element and by == By.LINK_TEXT:
        raise ElementNotVisibleException(
            "Link text {%s} was not visible after %s second%s!" % (
                selector, timeout, plural))


def hover_element_and_click(driver, element, click_selector,
                            click_by=By.CSS_SELECTOR,
                            timeout=1):
    """"""
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    hover = ActionChains(driver).move_to_element(element)
    hover.perform()
    for x in range(int(timeout * 10)):
        try:
            element = driver.find_element(by=click_by, value=click_selector)
            element.click()
            return element
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise NoSuchElementException(
        "Element {%s} was not present after %s seconds!" %
        (click_selector, timeout))


def switch_to_frame(driver, frame, timeout=3):
    """
    等待iframe出现，然后切换到它。这应该是有用的
    @Params
    driver - the webdriver object (required)
    frame - the frame element, name, or index
    timeout - the time to wait for the alert in seconds
    """

    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            driver.switch_to.frame(frame)
            return True
        except NoSuchFrameException:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception("Frame was not present after %s seconds!" % timeout)


def switch_to_window(driver, window, timeout=3):
    """
    等待一个窗口出现，然后切换到它
    @Params
    driver - the webdriver object (required)
    window - the window index or window handle
    timeout - the time to wait for the window in seconds
    """

    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    if isinstance(window, int):
        for x in range(int(timeout * 10)):
            try:
                window_handle = driver.window_handles[window]
                driver.switch_to.window(window_handle)
                return True
            except IndexError:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        raise Exception("Window was not present after %s seconds!" % timeout)
    else:
        window_handle = window
        for x in range(int(timeout * 10)):
            try:
                driver.switch_to.window(window_handle)
                return True
            except NoSuchWindowException:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        raise Exception("Window was not present after %s seconds!" % timeout)


def save_screenshot(driver, name, folder=None):
    import os
    """
    将屏幕截图保存到当前目录(如果提供，则保存到子文件夹)
    如果提供的文件夹不存在，将创建它。
    截图将采用PNG格式。
    """
    if "." not in name:
        name = name + ".png"
    if folder:
        abs_path = os.path.abspath('.')
        file_path = abs_path + "/%s" % folder
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        screenshot_path = "%s/%s" % (file_path, name)
    else:
        screenshot_path = name
    try:
        element = driver.find_element_by_tag_name('body')
        element_png = element.screenshot_as_png
        with open(screenshot_path, "wb") as file:
            file.write(element_png)
    except Exception:
        if driver:
            driver.get_screenshot_as_file(screenshot_path)
        else:
            pass


def wait_for_text_visible(driver, text, selector, by=By.CSS_SELECTOR,
                          timeout=10):
    """通过给定的选择器搜索指定的元素。返回
    元素对象，如果文本出现在元素中并且是可见的
    在页面上。如果文本或元素没有出现，则引发异常
    """

    element = None
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            element = driver.find_element(by=by, value=selector)
            if element.is_displayed() and text in element.text:
                return element
            else:
                element = None
                raise Exception()
        except Exception:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    plural = "s"
    if timeout == 1:
        plural = ""
    if not element:
        raise ElementNotVisibleException(
            "Expected text {%s} for {%s} was not visible after %s second%s!" %
            (text, selector, timeout, plural))


def find_visible_elements(driver, selector, by=By.CSS_SELECTOR):
    """
    找到所有匹配选择器且可见的WebElements。
    类似于webdriver.find_elements。
    """
    elements = driver.find_elements(by=by, value=selector)
    return [element for element in elements if element.is_displayed()]
