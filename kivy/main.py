#!/usr/bin/python

import sys
reload(sys)  
sys.setdefaultencoding('utf-8')

import utils

try:
    utils.get_module()
except:
    from portal import PortalApp
    PortalApp().run()

from swm.main import SWMApp
SWMApp().run()


