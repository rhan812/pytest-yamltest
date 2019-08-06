#!/usr/bin/python
# -*- coding: utf-8 -*-


class ObjectDict(dict):
    def __init__(self, json):
        _json = {k.lower(): v for k, v in json.items()}
        super().__init__(_json)
        for k, v in json.items():
            if isinstance(v, dict):
                if isinstance(k, str):
                    self[k.lower()] = ObjectDict(v)
                else:
                    self[k] = ObjectDict(v)
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        if isinstance(k, str):
                            self[k.lower()][i] = ObjectDict(item)
                        else:
                            self[k][i] = ObjectDict(item)

    def __getattr__(self, key):
        try:
            if isinstance(key, str):
                return self[key.lower()]
            else:
                return self[key]
        except KeyError as k:
            raise AttributeError(k)


