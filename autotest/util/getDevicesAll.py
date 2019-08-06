#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


# 获取设备usb 连接的设备信息
def getDevicesAll():
    #获取所有的设备列表
    devices = []
    try:
        for dName_ in os.popen("adb devices"):
            if "\t" in dName_:
                if dName_.find("emulator") < 0:
                    devices.append(dName_.split("\t")[0])
        devices.sort(cmp=None, key=None, reverse=False)
    except Exception as E:
        print(E)
    print("获取USB设备名称: %s 总数量:%s台" % (devices, len(devices)))
    return devices
