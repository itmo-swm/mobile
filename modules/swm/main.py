#!/usr/bin/python

from config import *

import kivy
kivy.require('1.9.1')

import os
import requests
#import json
import time
from math import *

from portal import PortalApp

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Translate, Scale
from kivy.garden.mapview import MapView, MapMarker, MapLayer
from mapview import MIN_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE, MAX_LONGITUDE
from mapview.utils import clamp
#from mapview.geojson import GeoJsonMapLayer
import kivy.properties
from kivy.lang import Builder
from kivy.uix.widget import Widget

#from connected import Connected
#from swm import MapViewApp
from kivy.core.window import Window
Window.softinput_mode = 'below_target'
#Window.softinput_mode = 'pan'

from plyer import gps
from geojson import GeoJsonMapLayer

class SWMApp(PortalApp):
    mapview = None
 
    def __init__(self, **kwargs):
        super(SWMApp, self).__init__(**kwargs)
        self.center = map_center
        self.get_config()
        try:
             gps.configure(on_location=self.on_location,
                           on_status=self.on_status)
             gps.start(1000, 0)
             self.gps = self.center         
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'
            self.gps = None
        Clock.schedule_once(self.post, 0)
 
        
    def build(self):
        layout = BoxLayout(orientation='vertical')
        return FloatLayout()
    
    def post(self, *args):
        self.show()
        
    def show(self):
        if self.root:
            self.root.clear_widgets()
        print "Show!!!"
        self.layout = FloatLayout()
        self.mapview = MapView(zoom=map_zoom,
                               lat=self.center[0], lon=self.center[1])
        self.layout.add_widget(self.mapview)
        self.root.add_widget(self.layout)
        
        self.buttons = BoxLayout(orientation='horizontal',
                                 height='32dp',size_hint_y=None)
        self.msg_btn = Button(text="Message",
                              on_press=lambda a: self.message())
        self.buttons.add_widget(self.msg_btn)
        self.cfg_btn = Button(text="Configure",
                              on_press=lambda a: self.portal())
        self.buttons.add_widget(self.cfg_btn)
        self.root.add_widget(self.buttons)

        # Running functions from configure.py
        for f in functions:
            getattr(self, f)()
        
    def message(self):
        print "Message!!!"

    def connect(self):
        print "Connect!!!"
        self.config_save()
        self.show()

    def portal(self):
        print "Portal!!!"
        #self.stop()
        if self.root:
            self.root.clear_widgets()

        self.portal_setup(message="Portal access",
                          buttons=self.setup_buttons(save="Save", cancel="Cancel"))

    def setup_buttons(self, save="Connect", cancel="Cancel"):
        font_large=32
        buttons = BoxLayout(orientation='horizontal',
                            height='32dp',size_hint_y=None)
        msg_btn = Button(text=save,on_press=lambda a: self.connect())
        msg_btn.font_size=font_large
        buttons.add_widget(msg_btn)
        cfg_btn = Button(text=cancel,
                         on_press=lambda a: self.show())
        cfg_btn.font_size=font_large
        buttons.add_widget(cfg_btn)

        return buttons
        
    def show_sgbs(self):
        region = self.url + '/swm/map/waste-management-operator-1/region-1'
        region = region.replace("//","/")
        region = region.replace(":/","://")
        url = self.url + '/swm_scripts/get_sgb?region=' + region
        print url
        r=requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            j=r.json()
            for sgb in j:
                r=requests.get(sgb['geometry'],
                               auth=(self.username, self.password))
                if r.status_code == 200:
                    j = r.json()
                    point = j['features'][0]['geometry']['coordinates']
                    mpoint = MapMarker(lon=point[0], lat=point[1],
                                       source='swm/sgb.png')
                    self.mapview.add_marker(mpoint)
                else:
                    self.portal_setup(buttons=self.setup_buttons())
        else:
            self.portal_setup(buttons=self.setup_buttons())
                    
    def show_routes(self):
        url = self.url + '/swm_scripts/drivers_routes?driver=' + self.username
        print url
        r=requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            j=r.json()
            url = j['region'] + j['route'] + '/@@geo-json.json'
            print url
            r = requests.get(url, auth=(self.username, self.password))
            if r.status_code == 200:
                j=r.json()
                #print "j: " + `j`
                gjm=GeoJsonMapLayer()
                gjm.geojson = r.json()
                #print gjm.geojson
                self.mapview.add_layer(gjm)
            else:
                self.portal_setup(buttons=self.setup_buttons())
        else:
            self.portal_setup(buttons=self.setup_buttons())

    def show_regions(self):
        url = self.url + '/swm_scripts/get_regions'
        print url
        r=requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            j=r.json()
            for rj in j:
                r=requests.get(rj['geometry'],
                               auth=(self.username, self.password))
                if r.status_code == 200:
                    gjm=GeoJsonMapLayer()
                    gjm.geojson = r.json()
                    self.mapview.add_layer(gjm)
                else:
                    self.portal_setup(buttons=self.setup_buttons())
        else:
            self.portal_setup(buttons=self.setup_buttons())

    def show_gps(self):
        if self.gps:
            self.mgps = MapMarker(lat=self.gps[0], lon=self.gps[1],
                                  source=gps_image)
            self.mapview.add_marker(self.mgps)
        

    @mainthread
    def on_location(self, **kwargs):
        self.mapview.remove_marker(self.mgps)
        self.gps = [kwargs['lat'], kwargs['lon']]
        self.mgps = MapMarker(lat=self.gps[0], lon=self.gps[1],
                              source=gps_image)
        self.mapview.add_marker(self.mgps)

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

if __name__ == '__main__':
    SWMApp().run()
    #LoginApp().run()
