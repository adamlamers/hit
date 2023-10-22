from collections import OrderedDict

import yaml as pyyaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def multiline_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())

pyyaml.add_representer(str, multiline_representer)
pyyaml.add_representer(OrderedDict, ordered_dict_presenter)

yaml = pyyaml
Loader = Loader
Dumper = Dumper
