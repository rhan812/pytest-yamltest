#!/usr/bin/python
# -*- coding: utf-8 -*-
import string
from autotest.webview import webviewConfig


class WebviewPageOperator:

    def isElementExist(self, location_value, location_type='XPATH'):
        if location_type == 'XPATH':
            params = {"xpath": location_value}
        else:
            params = {"css": location_value}
        # 获取对应的数据
        return self.doCommandWithElement(location_type, "IS_ELEMENT_EXIST", **params)

    # def isElementExistCss(self, css):
    #     params = {"css": css}
    #     return self.doCommandWithElement('CSS', "IS_ELEMENT_EXIST", **params)

    def getWindowHeight(self):
        return self.doCommandWithoutElement("GET_WINDOW_HEIGHT")

    def getWindowWidth(self):
        return self.doCommandWithoutElement("GET_WINDOW_WIDTH")

    def getElementRect(self, location_value, location_type='XPATH'):
        if location_type == 'XPATH':
            params = {"xpath": location_value}
        else:
            params = {"css": location_value}

        return self.doCommandWithElement(location_type, "GET_ELEMENT_RECT", **params)

    def getDocument(self):
        return self.doCommandWithoutElement("GET_DOCUMENT")

    def getHtml(self, nodeId):
        params = {"nodeId": nodeId}
        return self.doCommandWithoutElement("GET_HTML", **params)

    def getElementTextByXpath(self, xpath):
        params = {"xpath": xpath}
        return self.doCommandWithElement("XPATH", "GET_ELEMENT_TEXT",
                                         **params)

    def getElementSrcByXpath(self, xpath):
        params = {"xpath": xpath}
        return self.doCommandWithElement("XPATH", "GET_ELEMENT_SRC",
                                         **params)

    def changeDp2Px(self):
        pass

    def doCommandWithoutElement(self, actionType, **kw):
        #  actionType  = getJsValue
        # kwResult  $value
        # jsonResult: {"expression": "$value"}
        kwResult = webviewConfig._expressionMap.get(actionType)
        if kwResult is not None:
            # getValue的时候会传入value值
            if kw is not None:
                paramsCat = string.Template(kwResult)
                kwResult = paramsCat.substitute(**kw)
            return kwResult
        else:
            return None

    def doCommandWithElement(self, byType, actionType, text=None, **domType):

        jsActionType = webviewConfig._jsActionMap.get(actionType, None)

        if jsActionType is not None:
            # 找到控件dom
            domTemplate = webviewConfig._elementMap.get(byType)
            domTemplateType = string.Template(domTemplate)
            domResult = domTemplateType.substitute(**domType)
            # 使用xpath找控件,需要先转义成\\\",在json中会转义成\",在js中执行"
            # if byType == "XPATH":
            #     domResult = domResult.replace('"', '\\\"')
            # 组装json命令
            if actionType == "TEXT":
                if text is None:
                    raise TypeError('请输入要设置的text值')
                jsActionTemplate = string.Template(jsActionType)
                jsActionResult = jsActionTemplate.substitute({"text": text})
            else:
                jsActionResult = jsActionType
            jsCommand = domResult + jsActionResult
            return jsCommand
        else:
            raise TypeError('ActionType错误')
