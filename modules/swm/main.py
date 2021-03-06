#!/usr/bin/python

from config import *

import kivy
kivy.require('1.9.1')

import os
import requests
import base64
import time
from datetime import datetime
from math import *

from portal import PortalApp

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
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
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

from plyer import camera, audio
#from plyer.facades import Audio


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

    def on_pause(self):
	#when the app open the camera, it will need to pause this script. So we need to enable the pause mode with this method
	return True

    def on_resume(self):
	#after close the camera, we need to resume our app.
	pass

    def send_file(self, url, ftype=None, filename=None, name=None):
        #with open("swm/man.png", "rb") as src_file:
        with open(filename, "rb") as src_file:
            encoded_string = base64.b64encode(src_file.read())


        fjson={'@type': 'File', 'title': name,
              "file": {
                  "data": encoded_string,
                  "encoding": "base64",
                  "filename": filename,
                  "content-type": ftype}}

        print "URL: " + url
        print "FJSON: " + `fjson`
        
        r=requests.post(url,
                        headers={'Accept': 'application/json'},
                        json = fjson,
                        auth=(self.username, self.password))

        self.show()
        return r

    def msg_send(self):
        self.message_type=getattr(self.type_btn, 'text')
        self.message_text=self.msg_descr_txt

        url = self.url + msg_path

        print "URL: " + url
        print "Type: " + self.message_type
        print "Text: " + self.message_text
        print "Photo: " + self.message_photo
        print "Video: " + self.message_video
        print "Audio: " + self.message_audio

        folder_name = self.username + "_" + \
                      datetime.now().strftime("%Y%m%d%H%M")
        
        r=requests.post(url,
                        headers={'Accept': 'application/json'},
                        json={'@type': 'Folder',
                              'id': folder_name,
                              'title': self.message_type,
                              "description": self.message_text},
                        auth=(self.username, self.password))
        print "R1: " + `r`

        url += "/" + folder_name
        
        if self.message_photo:
            r = self.send_file(url, ftype="image/jpg",
                               filename=self.message_photo, name="photo")
            print "R2: " + `r`
        if self.message_video:
            r = self.send_file(url, ftype="video/mp4",
                               filename=self.message_video, name="video")
            print "R3: " + `r`

        if self.message_audio:
            r = self.send_file(url, ftype="audio/3gpp",
                               filename=self.message_audio, name="audio")
            print "R4: " + `r`

        return r
        
    def mm_callback(self, filepath):
        if(exists(filepath)):
            print "Saved " + filepath
        else:
            print "Unable to save." + filepath
        #self.message()

    def photo(self):
        self.message_photo=self.user_data_dir + "/photo.jpg"
        camera.take_picture(self.message_photo, self.mm_callback)
        print "!!! Photo: " + self.message_photo

    def video(self):
        self.message_video=self.user_data_dir + "/video.mp4"
        camera.take_video(self.message_video, self.mm_callback)
        print "!!! Video: " + self.message_video

    def audio(self):
        self.message_audio=self.user_data_dir + "/audio.3gp"
        audio.file_path = self.message_audio
        state = audio.state
        if state == 'ready':
            print "!!! Audio start: " + self.message_audio
            self.aud_btn.text = "Stop audio recording"
            audio.start()

        if state == 'recording':
            print "!!! Audio start: " + self.message_audio
            self.aud_btn.text = "Audio"
            audio.stop()

        
    def message(self):
        if self.root:
            self.root.clear_widgets()
        print "Message!!!"

        self.message_type=""
        self.message_text=""
        self.message_photo=""
        self.message_video=""
        self.message_audio=""

        self.types = msg_types
        #self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=40)
        layout = BoxLayout(orientation='vertical')
        
        layout.add_widget(Label(text="Message writing",
                                size_hint_y=0.1,
                                #size_hint_x=None, size_hint_y=None,
                                height=40, font_size=32,
                                halign='center', valign='middle'))
        
        grid = GridLayout(cols=3)
        grid.add_widget(Label(text="Type:",
                              size_hint_x=None, width=100,
                              size_hint_y=None, height=40))
        self.msg_type = DropDown()
        for t in self.types:
            btn = Button(text=t, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.msg_type.select(btn.text))
            self.msg_type.add_widget(btn)

        self.type_btn = Button(text="Select type of message...",
                               size_hint_y=None, height=40)
        grid.add_widget(self.type_btn)

        self.type_btn.bind(on_release=self.msg_type.open)

        self.msg_type.bind(on_select=lambda instance,
                          x: setattr(self.type_btn, 'text', x))

        self.rec_buttons = BoxLayout(orientation='horizontal',
                                 height='32dp',size_hint_y=None)
        self.pht_btn = Button(text="Photo",
                              on_press=lambda a: self.photo())
        self.rec_buttons.add_widget(self.pht_btn)

        self.aud_btn = Button(text="Audio",
                              on_press=lambda a: self.audio())
        self.rec_buttons.add_widget(self.aud_btn)

        self.vid_btn = Button(text="Video",
                              on_press=lambda a: self.video())
        self.rec_buttons.add_widget(self.vid_btn)

        grid.add_widget(self.rec_buttons)
            
        grid.add_widget(Label(text="Description:",
                              size_hint_x=None, width=200,valign='top',
                              size_hint_y=0.1, height=40))
        self.msg_descr = TextInput()
        def msg_descr_txt_set(i, v):
            self.msg_descr_txt = v
        self.msg_descr.bind(text=msg_descr_txt_set)
        grid.add_widget(self.msg_descr)

        layout.add_widget(grid)
        
        self.buttons = BoxLayout(orientation='horizontal',
                                 height='32dp',size_hint_y=None,valign='top')
        self.msg_btn = Button(text="Send", font_size=32,
                              on_press=lambda a: self.msg_send())
        self.buttons.add_widget(self.msg_btn)
        self.cfg_btn = Button(text="Cancel", font_size=32,
                              on_press=lambda a: self.show())
        self.buttons.add_widget(self.cfg_btn)

        layout.add_widget(self.buttons)
        self.root.add_widget(layout)

        # Running functions from configure.py
        for f in functions:
            getattr(self, f)()

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
                          buttons=self.setup_buttons(save="Save",
                                                     cancel="Cancel"))

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
        if hasattr(self, "mgps"):
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
