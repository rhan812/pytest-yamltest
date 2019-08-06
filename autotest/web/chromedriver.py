#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# extension for https://sites.google.com/a/chromium.org/chromedriver/
# Experimental, maybe change in the future
# Created by <hzsunshx> 2017-01-20

from __future__ import absolute_import

import atexit
import six
from selenium import webdriver

if six.PY3:
    import subprocess
    from urllib.error import URLError
else:
    from urllib2 import URLError
    import subprocess32 as subprocess


class ChromeDriver(object):
    def __init__(self, d, port=9515):
        self._d = d
        self._port = port

    def _launch_webdriver(self):
        print("start chromedriver instance")
        p = subprocess.Popen(['chromedriver', '--port=' + str(self._port)])
        try:
            p.wait(timeout=2.0)
            return False
        except subprocess.TimeoutExpired:
            return True

    def driver(self, device_ip=None, package=None, attach=True, activity=None, process=None):
        """
        Args:
            - package(string): default current running app
            - attach(bool): default true, Attach to an already-running app instead of launching the app with a clear data directory
            - activity(string): Name of the Activity hosting the WebView.
            - process(string): Process name of the Activity hosting the WebView (as given by ps).
                If not given, the process name is assumed to be the same as androidPackage.
        Returns:
            selenium driver
        """
        if not device_ip:
            subprocess.call(['adb', 'tcpip', '5555'])
            subprocess.Popen(['adb', 'connect', str(device_ip)])
        app = self._d.current_app()
        print(app)
        capabilities = {
            'chromeOptions': {
                'androidDeviceSerial': device_ip or self._d.serial,
                'androidPackage': package or app.get("package"),
                'androidUseRunningApp': attach,
                'androidProcess': process or app.get("package"),
                'androidActivity': activity or app.get("activity"),
            }
        }

        try:
            dr = webdriver.Remote('http://localhost:%d' % self._port, capabilities)

        except URLError:
            self._launch_webdriver()
            dr = webdriver.Remote('http://localhost:%d' % self._port, capabilities)

        # always quit driver when done
        atexit.register(dr.quit)
        return dr

    def windows_kill(self):
        subprocess.call(['taskkill', '/F', '/IM', 'chromedriver.exe', '/T'])


if __name__ == '__main__':
    import uiautomator2 as u2
    import time
    d = u2.connect(addr='192.168.3.247')
    d.app_start("com.tencent.mm", stop=True)
    time.sleep(1)
    d(resourceId="com.tencent.mm:id/jb").click()
    time.sleep(1)
    d(text="搜索").send_keys("乔融科技服务运营版")
    time.sleep(1)
    d(resourceId='com.tencent.mm:id/qm').click()
    d(text="简称_不要修改").click()
    time.sleep(10)
    # d(text="我的").click()
    # d(text="我的申请").click()
    driver = ChromeDriver(d).driver(device_ip='192.168.3.247:5555', process='com.tencent.mm:tools')
    # print(driver.getWindowHandles())
    from seleniumbase import SeleniumBase
    sb = SeleniumBase(driver)
    sb.select_option_by_index("class=['vux-popup-picker-select']", 2)
    sb.update_text("class=['weui-input']", "2000")

    # print(driver.find_element_by_class_name("weui-input").send_keys("11111111"))
    # sb.click("class =['weui-cell required ui-tap-active weui-cell_access']")


    # elem = driver.find_element_by_link_text(u"登录")
    # elem.click()
    # driver.quit()