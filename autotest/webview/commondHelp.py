#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess


def runCommand(cmd, printDetails=False, cwd=None):
    """

    :param cmd: 命令行
    :param printDetails: 是否打详细信息
    :param cwd: 设置工作目录
    :return:
    """

    p = subprocess.Popen(cmd, cwd=cwd,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stdError = p.communicate()
    if printDetails:
        print("runCommand --> " + stdout)

    if printDetails and stdError:
        print(stdError)

    if p.returncode != 0:

        raise RuntimeError(cmd)

    return stdout, stdError