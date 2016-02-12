import sys
from configparser import SafeConfigParser
from doit.doit_cmd import DoitMain
from .loader import MakeItLoader

makeit_cfg = 'makeit.cfg'

def cfg_to_dict(cfg):
    d = {}
    for section in cfg.sections():
        d[section] = dict(cfg[section])
    return d

def main():
    cfg = SafeConfigParser()
    if makeit_cfg not in cfg.read(makeit_cfg):
        sys.exit('Failed to load %s' % makeit_cfg)
    as_dict = cfg_to_dict(cfg)
    sys.exit(DoitMain(MakeItLoader(as_dict)).run(sys.argv[1:]))

if __name__ == '__main__':
    main()