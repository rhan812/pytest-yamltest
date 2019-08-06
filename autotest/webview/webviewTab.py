#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import platform

from autotest.webview.commondHelp import runCommand
from autotest.util.attachedChrome import AttachedChrome


_ADB_GET_TOP_ACTIVITY_CMD ={
    "Windows": "adb shell dumpsys activity top | findstr ACTIVITY"  # windows 获取
}

_ADB_GET_WEBVIEW_TOOLES_CMD = {
    "Windows": "adb shell cat /proc/net/unix | findstr webview_devtools_remote_%s"  # windows 获取
}


class WebViewTab:

    DEFAULT_LOCAL_REMOTE_PORT = 9223  # 默认端口

    def __init__(self, device, remote_port=None):
        """
        :param device:  设备号 或 ip 地址  如果为ip 首次需要连接usb 设置 port ： adb tcpip 5555
        :param remote_port: 端口号
        """
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", device)
        if m and m.group(1) != "127.0.0.1":
            self._device = device+":5555"
        else:
            self._device = device

        self._wxtabs = None
        self._wxattachedtab = None
        self._remote_port = remote_port if remote_port is not None \
            else WebViewTab.DEFAULT_LOCAL_REMOTE_PORT
        self._chrome = AttachedChrome("http://localhost:%s" % self._remote_port)

    def _getTabs(self, refetch=False):
        if self._wxtabs is None:
            # 进行获取 tabs
            self._fetchInner()

        if refetch:
            # 重新获取tabs
            self._wxtabs = self._chrome.list_tab()

    def _getAttachedTab(self, refetch=False):
        if self._wxattachedtab is None:
            self._fetchInner('attached')
        if refetch:
            self._wxattachedtab = self._chrome.attached_tab()
        if len(self._wxattachedtab) >=1:
            return self._wxattachedtab[0]
        else:
            raise("无打开的webview tab")

    def _fetchInner(self, tab_type='all'):

        # 先获取 微信appbrand 进程Pid
        pid = WebViewTab._fetchWeixinToolsProcessPid(device=self._device)

        # 重定向端口
        self._forwardLocalPort(self._remote_port, pid, device=self._device)

        # 获取本地 http://localhost:{重定向端口}/json返回的json数据，提取里面的webSocketDebuggerUrl字段值、
        if tab_type == 'all':
            self._wxtabs = self._chrome.list_tab()
        elif tab_type == 'attached':
            self._wxattachedtab = self._chrome.attached_tab()

    def _forwardLocalPort(self, remote_port, pid, device):
        cmd = "adb forward tcp:%s localabstract:webview_devtools_remote_%s" % (remote_port, pid)
        runCommand(WebViewTab.specifyDeviceOnCmd(cmd, device))

    @staticmethod
    def _fetchWeixinToolsProcessPid(device):
        osName = platform.system()  # 获取当前运行的 平台号
        cmd = _ADB_GET_TOP_ACTIVITY_CMD[osName]  # 获取该平台下对应的命令行

        stdout, stdErroe = runCommand(WebViewTab.specifyDeviceOnCmd(cmd, device))
        # 拆分
        strlist = str(stdout).split('pid=')
        pid = strlist[1].split('\\r\\n')[0]  # 获取pid
        webviewCmd = _ADB_GET_WEBVIEW_TOOLES_CMD[osName] % (pid)

        try:
            _, _ = runCommand(WebViewTab.specifyDeviceOnCmd(webviewCmd, device))
        except Exception as E:
            print(E)
        return pid

    @staticmethod
    def specifyDeviceOnCmd(cmd, device):
        return cmd if device is None else cmd.replace("adb", "adb -s %s" % device)


