#!/usr/bin/python

from kivy.garden.mapview import MapView, MapMarker
#from mapview.geojson import GeoJsonMapLayer
from geojson import GeoJsonMapLayer
from kivy.app import App
import requests
from plyer import gps
from kivy.properties import StringProperty
from kivy.clock import Clock, mainthread
import json

map_center = [59.93428, 30.335098]
map_zoom = 14
#auth_data=('sitizen','sitizen')
auth_data=None

class MapViewApp(App):
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
        #mapview = MapView(zoom=11, lat=50.6394, lon=3.057)
        self.mapview = MapView(zoom=map_zoom, lat=self.center[0], lon=self.center[1])
        
        r=requests.get('http://sdn.naulinux.ru:8128/Plone/swm_scripts/get_sgb?region=http://sdn.naulinux.ru:8128/Plone/region-1', auth=auth_data)
        j=r.json()
        for sgb in j:
            r=requests.get(sgb['geometry'], auth=auth_data).json()
            point = r['features'][0]['geometry']['coordinates']
            mpoint = MapMarker(lon=point[0], lat=point[1], source='data/sgb.png')
            self.mapview.add_marker(mpoint)
        #return self.mapview

        r=requests.get('http://sdn.naulinux.ru:8128/Plone/swm_scripts/get_route?region=http://sdn.naulinux.ru:8128/Plone/region-1', auth=auth_data)
        j=r.json()
        for rj in j:
            r=requests.get('http://sdn.naulinux.ru:8128/Plone/sity-dashboard-1/' + rj['id'] + '/@@geo-json.json', auth=auth_data)
            gjm=GeoJsonMapLayer()
            gjm.geojson = r.json()
            self.mapview.add_layer(gjm)
            
        if self.gps:
            self.mgps = MapMarker(lat=self.gps[0], lon=self.gps[1], source='data/track.png')
            self.mapview.add_marker(self.mgps)
        
        return self.mapview

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
