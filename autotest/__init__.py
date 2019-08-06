#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import realpath, join, dirname


templates_dir = realpath(join(dirname(__file__), "templates"))
jar_dir = join(dirname(__file__), "jars").replace('\\', '/')
