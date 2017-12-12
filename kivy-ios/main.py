#!/usr/bin/python

import sys
from os.path import join
reload(sys)  
sys.setdefaultencoding('utf-8')
from kivy.app import App
from kivy.utils import platform

import utils
try:
	user_data_dir = App.get_running_app().user_data_dir
    	tar = join(user_data_dir, "swm.tgz")
    	ini = join(user_data_dir, "swm.ini")
    	swm_json = join(user_data_dir, "swm.json")
    	swm_dir = join(user_data_dir, "swm")
        utils.get_module(None, None, None, str(platform), tar, ini, swm_json, swm_dir, user_data_dir)
        #utils.get_module()
except:
    print "Unexpected error:", sys.exc_info()[0]
    from portal import PortalApp
    PortalApp().run()

user_data_dir = App.get_running_app().user_data_dir
sys.path.append(user_data_dir)
print "!!!!"
print user_data_dir
print "!!!!"
reload(sys)
from swm.main import SWMApp
SWMApp().run()


