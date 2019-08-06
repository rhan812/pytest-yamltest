#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests
import pychrome
from pychrome.tab import Tab


class AttachedChrome(pychrome.Browser):

    def __init__(self, url='http://127.0.0.1:9222'):
        super(AttachedChrome, self).__init__(url)

    def attached_tab(self, url=None, timeout=None):
        rp = requests.get("%s/json" % self.dev_url, json=True, timeout=timeout)
        tabs_map = {}
        for tab_json in rp.json():
            description = json.loads(tab_json["description"])

            if tab_json['type'] != 'page':  # pragma: no cover
                continue
            if description.get("attached") and description.get("visible"):
                tabs_map[tab_json['id']] = Tab(**tab_json)
        self._tabs = tabs_map
        return list(self._tabs.values())

