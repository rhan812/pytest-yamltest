#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from selenium.common.exceptions import WebDriverException


def wait_for_ready_state_complete(driver, timeout=10):
    """
    DOM(文档对象模型)有一个名为“readyState”的属性。

    当此值变为“complete”时，将考虑页面资源

    完全加载(尽管AJAX和其他加载可能仍然在进行)。

    此方法将一直等到文档。readyState = =“完成”
    :return: is_
    """
    start_ms = time.time() * 1000.0
    stop_ms = start_ms + (timeout * 1000.0)
    for x in range(int(timeout * 10)):
        try:
            ready_state = driver.execute_script("return document.readyState")
        except WebDriverException:
            # Bug fix for: [Permission denied to access property "document"]
            time.sleep(0.03)
            return True
        if ready_state == u'complete':
            time.sleep(0.01)  # Better be sure everything is done loading
            return True
        else:
            now_ms = time.time() * 1000.0
            if now_ms >= stop_ms:
                break
            time.sleep(0.1)
    raise Exception(
        "Page elements never fully loaded after %s seconds!" % timeout)


def scroll_to_element(driver, element):
    element_location = element.location['y']
    element_location = element_location - 130
    if element_location < 0:
        element_location = 0
    scroll_script = "window.scrollTo(0, %s);" % element_location
    # The old jQuery scroll_script required by=By.CSS_SELECTOR
    # scroll_script = "jQuery('%s')[0].scrollIntoView()" % selector
    try:
        driver.execute_script(scroll_script)
    except WebDriverException:
        pass  # Older versions of Firefox experienced issues here


def activate_jquery(driver):
    """ If "jQuery is not defined", use this method to activate it for use.
        This happens because jQuery is not always defined on web sites. """
    try:
        # Let's first find out if jQuery is already defined.
        driver.execute_script("jQuery('html')")
        # Since that command worked, jQuery is defined. Let's return.
        return
    except Exception:
        # jQuery is not currently defined. Let's proceed by defining it.
        pass
    VER = "3.4.1"
    MIN_JS = "//cdnjs.cloudflare.com/ajax/libs/jquery/%s/jquery.min.js" % VER
    jquery_js = MIN_JS
    activate_jquery_script = (
        '''var script = document.createElement('script');'''
        '''script.src = "%s";document.getElementsByTagName('head')[0]'''
        '''.appendChild(script);''' % jquery_js)
    driver.execute_script(activate_jquery_script)
    for x in range(int(3 * 10.0)):
        # jQuery needs a small amount of time to activate.
        try:
            driver.execute_script("jQuery('html')")
            return
        except Exception:
            time.sleep(0.1)
    # Since jQuery still isn't activating, give up and raise an exception
    raise Exception(
        '''Unable to load jQuery on "%s" due to a possible violation '''
        '''of the website's Content Security Policy directive. '''
        '''To override this policy, add "--disable_csp" on the '''
        '''command-line when running your tests.''' % driver.current_url)