#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pytest
import allure

from autotest.testclassification.caserun import fixtur_executor, case_run
from autotest.util.yaml_sampler import YamlSampler
import autotest.util.globaval as gl
from autotest.util.Log import Log


gl._init()


def pytest_addoption(parser):
    group = parser.getgroup("collect")

    group.addoption(
        "--dv",
        action="store",
        default="",
        help="设备号",
        dest="device"
    )
    group.addoption(
        "--br",
        action="store",
        default="",
        metavar="pat",
        help="浏览器类型",
        dest="browser"
    )


def pytest_collect_file(path, parent):
    # 收集传入的 路径下的 测试用例 and path.basename.startswith("test")
    config = parent.config
    gl.set_value("device", config.getoption("device"))
    gl.set_value("browser", config.getoption("browser"))
    if path.ext in (".yml", ".yaml") and path.basename not in("fixture.yml", "fixture.yaml",
                                                              "runconf.yml", "runconf.yaml",
                                                              "objpage.yml", "objpage.yaml"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def setup(self):
        # 收集 该文件的测试集是否 setup, 有进行执行setup ，否则不作任何处理 运行测试用例
        with pytest.allure.step("用例集级别前置"):
            if not gl.get_value("objpage"):  # 判断是否已经收集过 objpage 数据
                for key in ("fixture", "runconf", "objpage"):  # 判断是否有全局变量
                    if not gl.get_value(key):
                        _setGlobValue(os.path.dirname(self.fspath), key)
                gl.set_value("log", Log().getlog())
            # 判断是否需要 进行 用例级别前置条件
            if gl.get_value("fixture").get(os.path.basename(self.fspath).rsplit(".", 1)[0]):
                fixtur_executor(gl.get_value("fixture").get(os.path.basename(self.fspath).rsplit(".", 1)[0],
                                                         {}).get("setup", None))

    def teardown(self):
        # 判断是否 需要执行 teardown
        with pytest.allure.step("用例集级别后置"):
            if gl.get_value("fixture").get(os.path.basename(self.fspath).rsplit(".", 1)[0]):
                fixtur_executor(gl.get_value("fixture").get(os.path.basename(self.fspath).rsplit(".", 1)[0],
                                                         {}).get("setup", None), False)

    def collect(self):
        raw = YamlSampler.read_json(self.fspath)

        # 把每个用例文件作为一个整体 传入 TestItem
        # 原因 是 每个文件是 一个用例集 , 处理前置条件
        # 传入文件目录名 , 文件内容 已文件作为一个用例集， 不拆分内部用例
        # yield YamlTestItem(os.path.dirname(self.fspath),
        #                    os.path.basename(self.fspath).rsplit(".", 1)[0], self, raw)
        # 单个测试用例
        # surplus_case_count = len(raw)

        for name, spec in sorted(raw.items()):
            # surplus_case_count -= 1  , surplus_case_count

            yield YamlTestItem(name, self, spec)


class YamlTestItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlTestItem, self).__init__(name, parent)

        self.dirname = os.path.dirname(self.fspath)
        self.spec = spec  # 用例内容
        self.add_marker(allure.feature(os.path.basename(self.fspath).rsplit(".", 1)[0]))
        #
        # 处理 用例集 没有 setup
        if not gl.get_value("objpage"):  # 判断是否已经收集过 objpage 数据
            for key in ("fixture", "runconf", "objpage"):  # 判断是否有全局变量
                if not gl.get_value(key):
                    _setGlobValue(os.path.dirname(self.fspath), key)
        if not gl.get_value("log"):
            gl.set_value("log", Log().getlog())

        self.run_type = gl.get_value("runconf").get("runtype")
        # 拆但用例需要
        self.caseName = name

    def setup(self):
        # 每个用例里面的 setup
        pass

    def teardown(self):
        pass

    def runtest(self):
        case_run(self.spec, self.run_type)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, Exception):

            return '测试用例名称：{} \n' \
                   '输入参数：{} \n' \
                   '错误信息：{}'.format(self.caseName, self.spec, excinfo.value.args)

            # return '测试用例名称：{} \n' \
            #        '输入参数：{} \n' \
            #        '错误信息：{}'.format(self.caseName, self.caseInfo, excinfo.value.args)

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


def _setGlobValue(path, key=None):
    # 获取当前目录
    dirandfile = list(os.walk(path))
    for filename in dirandfile[0][-1]:
        if key + ".yml" == filename or key + '.yaml' == filename:
            gl.set_value(key, YamlSampler.read_json(os.path.join(dirandfile[0][0], filename)))
            return
    _setGlobValue(os.path.dirname(path), key)


# if __name__ == '__main__':
#     pytest.main(['-v', './Demo/web/百度设置/', '--br', "chrome", "--alluredir", "./report"])
