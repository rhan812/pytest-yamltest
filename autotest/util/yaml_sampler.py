import yaml

from autotest.util.ToObjecrDict import ObjectDict


class YamlSampler:
    @classmethod
    def read_yaml(cls, filename):
        if not filename:
            return {}
        with open(filename, encoding='UTF-8') as f:
            doc = yaml.safe_load(f)
        if isinstance(doc, dict):
            return ObjectDict(doc)
        else:
            return doc

    @classmethod
    def read_json(cls, filename):
        return cls.read_yaml(filename)
