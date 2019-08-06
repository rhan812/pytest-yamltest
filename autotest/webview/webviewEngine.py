#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
from xml import etree

from autotest.webview.webviewTab import WebViewTab
from autotest.webview.webviewPageOperator import WebviewPageOperator
from autotest.webview import webviewConfig
from autotest.webview import webviewutils

import uiautomator2 as u2


class WebviewDriver:

    def __init__(self, s, remote_port=None):
        """
        :param device: 设备号  to do 直接传入 设备对象
        :param remote_port: chrome remote port
        """

        # self._device = device
        self.s = s

        if isinstance(s, u2.session.Session):
            host = s.server._host
            serial = s.server.device_info.get("serial")

        elif isinstance(s, u2.UIAutomatorServer):
            host = s._host
            serial = s.device_info.get("serial")

        else:
            print("设备运行异常，异常退出")
            sys.exit(1)

        # 判断是否 wifi 连接，还是usb 连接

        if host == '127.0.0.1':
            self._wxtab = WebViewTab(serial)
        else:
            self._wxtab = WebViewTab(host)

        self._attached_tab = self._wxtab._getAttachedTab()  # 只取一个有效的 打开的页面
        self._attached_tab.start()
        self.wpo = WebviewPageOperator()
        # self.s = s
        # print(self.s.info())
        self.selector_type = "CSS"

    def clickElement(self, selector, isUiAutomator=False):

        if webviewutils.is_xpath_selector(selector):
            self.selector_type = "XPATH"
        # 233
        # 126
        if self.isElementExist(selector, self.selector_type):
            # 滑动页面 到可见
            self.scrollToElement(selector, self.selector_type, visibleItemElment=None)
            # 获取
            sendStr = self.wpo.getElementRect(selector, self.selector_type)
            self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_RECT"),
                                           expression=sendStr)
            # 获取中心 定位的中心位置 ,点击
            x = self._getRelativeLocationValue("x")
            y = self._getRelativeLocationValue("y")
            print(x, y)
            self._attached_tab.call_method(webviewConfig._methodMap.get("CLICK"),
                                           x=x, y=y, duration=200, tapCount=1)

    def _getRelativeLocationValue(self, directionKey='topp'):
        """
        获取相对方向的数据参数值
        :param directionKey: 
        :return: 
        """
        ret = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_JS_VALUE"), expression=directionKey)
        directionValue = ret['result']['value']
        return directionValue

    def isElementExist(self, selector, selector_type=None):
        if selector_type is None:
            if webviewutils.is_xpath_selector(selector):
                self.selector_type = "XPATH"

        getExiteValue = self.wpo.isElementExist(selector, self.selector_type)

        ret = self._attached_tab.call_method(webviewConfig._methodMap.get("IS_ELEMENT_EXIST"),
                                             expression=getExiteValue)

        # to do 有多个有效的 tab 时候 需要每个都进行 判断，属于的信息
        return ret["result"]["subtype"] == 'node'

    def getDocument(self):
        """
        获得getHtml中需要的nodeId
        在调用getHtml之前必须先调用这个方法
        :return: 
        """
        value = self.wpo.getDocument()
        return self._attached_tab.call_method(webviewConfig._methodMap.get("GET_DOCUMENT"), expression=value)

    def getHtml(self, nodeId=1):
        self.getDocument()
        sendStr = self.wpo.getHtml(nodeId)
        self.html = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_HTML"), expression=sendStr)['result']['outerHTML']
        return self.html

    def getElementTextByXpath(self, xpath):
        """
        通过 xptah 获取 text
        :param xpath:
        :return:
        """
        time.sleep(1)
        if self.isElementExist(xpath, "XPATH"):
            getTextValue = self.wpo.getElementTextByXpath(xpath)
            resultValueDict = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_TEXT"),
                                                             expression=getTextValue)
            resultValue = resultValueDict['result']['value']
        else:
            resultValue = None
        return resultValue

    def getElementSrcByXpath(self, xpath):
        if self.isElementExist(xpath, "XPATH"):
            getSrcValue = self.wpo.getElementSrcByXpath(xpath)
            resultValueDict = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_SRC"),
                                                             expression=getSrcValue)
            resultValue = resultValueDict['result']['value']
        else:
            resultValue = None
        return resultValue

    def getElementByXpath(self, xpath):
        """
        :param xpath: 目标的 xpath
        :return: 返回xml 包装过的 element对象，可以使用 lxml 语法获得对象的信息
        例如可以使用 element.text 拿到它的文字
        当element 中含有列表时, 使用循环读取每个 item
        """
        htmlData = self.getHtml()
        if htmlData is not None:
            html = etree.HTML(htmlData)
            elementList = html.xpath(xpath)
            if len(elementList) != 0:
                return elementList[0]
            else:
                self.logger.info('找不到xpath为: ' + xpath + ' 的控件')
                return ''
        else:
            self.logger.info('获取到的html为空')
            return ''

    def textElement(self, selector, text):
        """
        定位到后先点击，获取焦点然后输入
        :param selector: 目标selector
        :param text:  输入值
        :return: None
        """

        if webviewutils.is_xpath_selector(selector):
            self.selector_type = "XPATH"
        try:
            self.clickElement(selector, self.selector_type)
            self.s.clear_text()
            self.s.send_keys(text)
        except Exception as e:
            print(e)

    def clickFirstElementByText(self, text, byUiAutomator=False):
        """
        通过text来搜索，点击第一个text相符合的控件。参数同clickElementByXpath()
        """
        self.clickElement('.//*[text()="' + text + '"]', byUiAutomator)

    def getElementCoordinateByXpath(self, xpath):
        """
        获得Element的坐标
        :param elementXpath:待获取坐标的元素的xpath
        :return:element相对于整个屏幕的x、y坐标，单位为px
        """
        if self.isElementExist(xpath):
            sendStr = self.wpo.getElementRect(xpath)
            self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_RECT"),
                                           expression=sendStr)
            # 获取中心 定位的中心位置 ,点击
            x = self._getRelativeLocationValue("x")
            y = self._getRelativeLocationValue("y")
            # xPx, yPx = self.changeDp2Px(x, y)
            return x, y

    def getWindowHeight(self):
        """
        :return:手机屏幕的高度
        """
        getWindowHeight = self.wpo.getWindowHeight()
        resultValueDict = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_WINDOW_HEIGHT"),
                                                         expression=getWindowHeight)
        resultValue = resultValueDict['result']['value']
        return resultValue

    def getWindowWidth(self):
        """
        :return:手机屏幕的宽度
        """
        getWindowWidth = self.wpo.getWindowWidth()
        resultValueDict = self._attached_tab.call_method(webviewConfig._methodMap.get("GET_WINDOW_WIDTH"),
                                                         expression=getWindowWidth)
        resultValue = resultValueDict['result']['value']
        return resultValue

    def scrollToElement(self, selector, selector_type='XPATH', visibleItemElment=None, speed=600):
        """
        默认滑动点为屏幕的中心，且边距为整个屏幕。当有container时，传入container中任意一个当前可见item的 element，之后会将目标滑到该可见item的位置
        :param selector: 要滑动到屏幕中控件的xpath
        :param selector_type: 定位方式
        :param visibleItemElment:container中当前可见的一个xpath
        :param speed:
        :return:
        """
        sendstr = self.wpo.getElementRect(selector, selector_type)
        self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_RECT"),
                                       expression=sendstr)
        top = self._getRelativeLocationValue('topp')
        bottom = self._getRelativeLocationValue('bottom')
        left = self._getRelativeLocationValue('left')
        right = self._getRelativeLocationValue('right')
        # self.logger.debug('scrollToElementByXpath -> top:bottom:left:right = ' + str(top) + " :" + str(bottom) \
        #                   + " :" + str(left) + " :" + str(right))
        if visibleItemElment is None:
            endTop = 0
            endLeft = 0
            endBottom = self.getWindowHeight()
            endRight = self.getWindowWidth()
        else:
            sendstr = self.wpo.getElementRect(visibleItemElment, selector_type)
            self._attached_tab.call_method(webviewConfig._methodMap.get("GET_ELEMENT_RECT"),
                                            expression=sendstr)
            endTop = self._getRelativeLocationValue('topp')
            endBottom = self._getRelativeLocationValue('bottom')
            endLeft = self._getRelativeLocationValue('left')
            endRight = self._getRelativeLocationValue('right')
            # self.logger.debug(
            #     'scrollToElementByXpath -> toendTop:endBottom:endLeft:endRight = ' + str(endTop) + " :" + str(
            #         endBottom) \
            #     + " :" + str(endLeft) + " :" + str(endRight))
        '''
        竖直方向的滑动
        '''

        if endBottom < bottom:
            scrollYDistance = endBottom - bottom
        elif top < 0:
            scrollYDistance = -(top - endTop)
        else:
            scrollYDistance = 0

        if scrollYDistance < 0:
           self._attached_tab.call_method(webviewConfig._methodMap.get("SCROLL"), x=int((endLeft + endRight) / 2),
                                          y=int((endTop + endBottom) / 2), xDistance=0, yDistance=scrollYDistance - 80,
                                          speed=speed)
        elif scrollYDistance > 0:
            self._attached_tab.call_method(webviewConfig._methodMap.get("SCROLL"), x=int((endLeft + endRight) / 2),
                                           y=int((endTop + endBottom) / 2), xDistance=0, yDistance=scrollYDistance + 80,
                                           speed=speed)

        else:
            print("'y方向不需要滑动'")
            # self.logger.debug('y方向不需要滑动')
        '''
        水平方向的滑动
        '''
        if right > endRight:
            scrollXDistance = endRight - right
        elif left < 0:
            scrollXDistance = -(left - endLeft)
        else:
            scrollXDistance = 0

        if scrollXDistance != 0:

            self._attached_tab.call_method(webviewConfig._methodMap.get("SCROLL"), x=int((endLeft + endRight) / 2),
                                           y=int((endTop + endBottom) / 2), xDistance=scrollXDistance, yDistance=0,
                                           speed=speed)
        else:
            print('x方向不需要滑动')
            # self.logger.debug('x方向不需要滑动')


if __name__ == "__main__":

    # '//*[@id="app"]/section/div[3]/div/div[2]/div/div[2]/div'
    # wx.clickElementByXpath('//*[@id="app"]/section/div[4]/div/div[1]/div/div[2]/div')
    # wx.isEiseElementExitCSSxitId("""var aa=document.querySelector("ui-input-8vas5")
    #             ;left=Math.round(aa.getBoundingClientRect().left);
    #             right=Math.round(aa.getBoundingClientRect().right);
    #             """) //*[@id="app"]/section/div[4]/div/div[1]/div/div[2]/div  af4b4c5c
    d = u2.connect(addr="af4b4c5c")
    # s = d.session("com.tencent.mm")
    d.app_start("com.tencent.mm", stop=True)
    time.sleep(1)
    d(resourceId="com.tencent.mm:id/jb").click()
    time.sleep(1)
    d(text="搜索").send_keys("乔融科技服务运营版")
    time.sleep(1)
    d(resourceId='com.tencent.mm:id/qm').click()
    d(text="简称_不要修改").click()
    time.sleep(10)
    # wx = WxDriver("af4b4c5c", d)
    wx = WebviewDriver(d)

    wx.clickElement('//*[@id="app"]/section/div[4]/div/div[1]/div')
    wx.scrollToElement('//*[contains(@id,"vux-picker-")]', visibleItemElment='//*[text()="妇科"]')
    wx.clickFirstElementByText("完成")
    time.sleep(1)
    wx.textElement('//*[contains(@id,"ui-input-")]', '1000')
    time.sleep(1)
    wx.clickElement('//*[@id="app"]/section/div[4]/div/div[3]/div[3]/span')
    time.sleep(1)
    wx.clickElement('//*[@id="app"]/section/div[4]/div/section/div[1]/div/div/div[2]/div[2]/div[1]')
    time.sleep(1)

    # wx.clickElement("#app > section > div:nth-child(6) > div > div.takePhoto-nav > div > div.upload-blank")
    # time.sleep(1)
    # d(text='拍摄照片').click()
    # d(resourceId="com.android.camera:id/shutter_button").click()
    # d(text='确定').click()
    # d(text='完成').click()

    wx.clickFirstElementByText("下一步")
    time.sleep(2)
    # wx.clickElement('//*[@id="app"]/section/div[2]/div/div')
    wx.clickElement('//*[@id="app"]/section/div[8]/button')
