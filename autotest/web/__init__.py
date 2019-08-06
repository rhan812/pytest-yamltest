#!/usr/bin/python
# -*- coding: utf-8 -*-
from selenium.common.exceptions import (StaleElementReferenceException,
                                        MoveTargetOutOfBoundsException,
                                        WebDriverException)
from selenium.common import exceptions as selenium_exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


class seleniumBase():
    def __init__(self):
        self.driver = None
        self.__last_url_of_delayed_assert = "data:,"
        self.__last_page_load_url = "data:,"
        self.EXTREME_TIMEOUT = 30

    def open(self, url):
        self.__last_page_load_url = None
        self.driver.get(url)
        if True:
            self.wait_for_ready_state_complete()
        self.__demo_mode_pause_if_active()

    def open_url(self):
        pass