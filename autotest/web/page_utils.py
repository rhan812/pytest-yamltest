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


def is_link_text_selector(selector):
    """
    确定选择器是否是链接文本选择器的基本方法。
    """
    if selector.startswith('link=') or selector.startswith('link_text='):
        return True
    return False


def get_link_text_from_selector(selector):
    """
    从链接文本选择器获取链接文本的基本方法。
    """
    if selector.startswith('link='):
        return selector.split('link=')[1]
    elif selector.startswith('link_text='):
        return selector.split('link_text=')[1]
    return selector


def get_domain_url(url):
    """使用这个转换url如下:
    https://blog.xkcd.com/2014/07/22/what-if-book-tour/
    到这个:
    https://blog.xkcd.com"""
    if "http://" not in url and  "https://" not in url:
        return url

    # 此处可以用别的方法
    url_header = url.split('://')[0]
    simple_url = url.split('://')[1]
    base_url = simple_url.split('/')[0]
    domain_url = url_header + '://' + base_url
    return domain_url


def make_css_match_first_element_only(selector):
    # Only get the first match
    last_syllable = selector.split(' ')[-1]
    if ':' not in last_syllable and ':contains' not in selector:
        selector += ':first'
    return selector