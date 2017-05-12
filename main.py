#!/usr/bin/python

import requests
#import json
import time
from math import *

from kivy.app import App
from plyer import gps
from kivy.properties import StringProperty
from kivy.clock import Clock, mainthread

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Translate, Scale
from kivy.garden.mapview import MapView, MapMarker, MapLayer
from mapview import MIN_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE, MAX_LONGITUDE
from mapview.utils import clamp
#from mapview.geojson import GeoJsonMapLayer
from geojson import GeoJsonMapLayer
import kivy.properties

map_center = [59.93428, 30.335098]
map_zoom = 12
auth_data=('citizen','citizen')
#auth_data=None

class MapViewApp(App):
    mapview = None
 
    def __init__(self, **kwargs):
        super(MapViewApp, self).__init__(**kwargs)
        Clock.schedule_once(self.post, 0)
 
    def build(self):
        self.center = map_center
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

        layout = BoxLayout(orientation='vertical')

        return layout
 
    def post(self, *args):
        layout = FloatLayout()
        #mapview = MapView(zoom=11, lat=50.6394, lon=3.057)
        self.mapview = MapView(zoom=map_zoom, lat=self.center[0], lon=self.center[1])
        layout.add_widget(self.mapview)
        
        self.root.add_widget(layout)

        self.show_regions()
        self.show_routes()
        self.show_sgbs()
        self.show_gps()

    def show_sgbs(self):
        r=requests.get('http://sdn.naulinux.ru:8128/Plone/swm_scripts/get_sgb?region=http://sdn.naulinux.ru:8128/Plone/swm/map/waste-management-operator-1/region-1', auth=auth_data)
        j=r.json()
        for sgb in j:
            r=requests.get(sgb['geometry'], auth=auth_data).json()
            point = r['features'][0]['geometry']['coordinates']
            mpoint = MapMarker(lon=point[0], lat=point[1], source='data/sgb.png')
            self.mapview.add_marker(mpoint)

    def show_routes(self):
        r=requests.get('http://sdn.naulinux.ru:8128/Plone/swm_scripts/get_route?region=http://sdn.naulinux.ru:8128/Plone/swm/map/waste-management-operator-1/region-1', auth=auth_data)
        j=r.json()
        #print "j: " + `j`
        for rj in j:
            r=requests.get(rj['geometry'], auth=auth_data)
            gjm=GeoJsonMapLayer()
            gjm.geojson = r.json()
            #print "gjm: " + `gjm.geojson`
            self.mapview.add_layer(gjm)

    def show_regions(self):
        r=requests.get('http://sdn.naulinux.ru:8128/Plone/swm_scripts/get_regions', auth=auth_data)
        j=r.json()
        for rj in j:
            r=requests.get(rj['geometry'], auth=auth_data)
            gjm=GeoJsonMapLayer()
            gjm.geojson = r.json()
            self.mapview.add_layer(gjm)

    def show_gps(self):
        if self.gps:
            self.mgps = MapMarker(lat=self.gps[0], lon=self.gps[1], source='data/track.png')
            self.mapview.add_marker(self.mgps)
        

    @mainthread
    def on_location(self, **kwargs):
        self.mapview.remove_marker(self.mgps)
        self.gps = [kwargs['lat'], kwargs['lon']]
        self.mgps = MapMarker(lat=self.gps[0], lon=self.gps[1], source='data/track.png')
        self.mapview.add_marker(self.mgps)

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

if __name__ == '__main__':
    MapViewApp().run()
