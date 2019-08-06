#!/usr/bin/python
# -*- coding: utf-8 -*-


def is_xpath_selector(selector):
    """
    确定选择器是否是xpath选择器的基本方法。
    """
    if (selector.startswith('/') or selector.startswith('./') or (
            selector.startswith('('))):
        return True
    return False


