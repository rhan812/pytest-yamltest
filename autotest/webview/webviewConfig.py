#!/usr/bin/python
# -*- coding: utf-8 -*-


# 定位方式 使用$$可以作为格式化时的转义
_elementMap = {
    # "ID": "$$('#$id')[0]",
    # "NAME": "$$('.$name')[$index]",
    "CSS": 'var button = document.querySelector("$css")',
    "XPATH": """var xpath ='$xpath';
                xpath_obj = document.evaluate(xpath,document,null, XPathResult.ANY_TYPE, null);
                var button = xpath_obj.iterateNext() """
}

# doCommandWithElement中执行的参数
_jsActionMap = {

    "GET_ELEMENT_RECT": """
    ;left=Math.round(button.getBoundingClientRect().left);
    right=Math.round(button.getBoundingClientRect().right);
    bottom=Math.round(button.getBoundingClientRect().bottom);
    topp=Math.round(button.getBoundingClientRect().top);
    x=Math.round((left+right)/2);
    y=Math.round((topp+bottom)/2);
    """,
    "IS_ELEMENT_EXIST": ";button",
    "GET_ELEMENT_TEXT": ";button.textContent;",
    "GET_ELEMENT_SRC": ";button.getAttribute('src')",
}

# doCommandWithoutElement 中执行的参数
_expressionMap = {
    "GET_PAGE_HEIGHT": 'document.body.scrollHeight',
    "GET_JS_VALUE": '$value',
    "GET_WINDOW_HEIGHT": 'document.documentElement.clientHeight',
    "GET_WINDOW_WIDTH": "document.documentElement.clientWidth"
}


# 对应的操作函数
_methodMap = {
    "GET_DOCUMENT": "DOM.getDocument",
    "GET_HTML": "DOM.getOuterHTML",
    "SCROLL": "Input.synthesizeScrollGesture",
    "CLICK": "Input.synthesizeTapGesture",
    "GET_ELEMENT_RECT": "Runtime.evaluate",
    "GET_PICKER_RECT": "Runtime.evaluate",
    "GET_ELEMENT_TEXT": "Runtime.evaluate",
    "GET_ELEMENT_SRC": "Runtime.evaluate",
    "GET_PAGE_HEIGHT": "Runtime.evaluate",
    "GET_JS_VALUE": "Runtime.evaluate",
    "TEXT": "Input.dispatchKeyEvent",
    "IS_ELEMENT_EXIST": "Runtime.evaluate",
    "GET_WINDOW_HEIGHT": "Runtime.evaluate",
    "GET_WINDOW_WIDTH": "Runtime.evaluate"

}