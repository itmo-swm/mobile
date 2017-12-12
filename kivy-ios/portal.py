#!/usr/bin/python

from ConfigParser import ConfigParser

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import platform
from os.path import join
import os.path
from shutil import copyfile
import utils

class PortalApp(App):
    url = StringProperty(None)
    username = StringProperty(None)
    password = StringProperty(None)

    def __init__(self, **kwargs):
        super(PortalApp, self).__init__(**kwargs)
        self.config = ConfigParser()
	user_data_dir = App.get_running_app().user_data_dir
    	filename = join(user_data_dir, "swm.ini")      
        if os.path.exists(filename):
            print "No config" 
        else:
            copyfile("swm.ini", filename)
        self.config.read(filename)
        Clock.schedule_once(self.post, 0)
 
    def build_config(self, config):
        config.setdefaults('login',
                           {'url': '', 'username': '', 'password': ''})

    def get_application_config(self):
	user_data_dir = App.get_running_app().user_data_dir
    	filename = join(user_data_dir, "swm.ini")
        return (filename)
        
    def get_config(self):
        app = App.get_running_app()
        self.config = app.config
        config = self.config
        self.url = config.get('login', 'url')
        self.username = config.get('login', 'username')
        self.password = config.get('login', 'password')

    def post(self, *args):
        self.portal_setup()
        
    def portal_setup(self, message="Portal access error!!!", buttons=None):
        self.get_config()
        font_large=32
        font_middle=20
        font_small=18
        print "Setup!!!"

        if self.root:
            self.root.clear_widgets()

        self.setup_form = BoxLayout(orientation='vertical')
                                    #height='32dp',size_hint_y=None)
        #self.setup_form.spacing = 40
        #self.setup_form.padding = [10,50,10,50]

        l = Label(text=message) #, font_size=32)
        l.halign = 'center'
        #l.font_size=font_large
        self.setup_form.add_widget(l)

        b = BoxLayout(orientation='vertical',size_hint_y=None, height=150)
        l = Label(text="URL:")
        l.halign = 'left'
        #l.font_size=font_small
        b.add_widget(l)
        self.input_url = TextInput(text=self.url)
        #self.input_url.font_size=font_middle
        b.add_widget(self.input_url)
        self.setup_form.add_widget(b)

        b = BoxLayout(orientation='vertical',size_hint_y=None, height=150)
        l = Label(text="Login:")
        l.halign = 'left'

        #l.font_size=font_small
        b.add_widget(l)
        self.input_login = TextInput(text=self.username)
        #self.input_login.font_size=font_middle
        b.add_widget(self.input_login)
        self.setup_form.add_widget(b)

        b = BoxLayout(orientation='vertical',size_hint_y=None, height=150)
        l = Label(text="Password:")
        l.halign = 'left'
        #l.font_size=font_small
        b.add_widget(l)
        self.input_passwd = TextInput(text=self.password)
        #self.input_passwd.font_size=font_middle
        self.input_passwd.password=True
        b.add_widget(self.input_passwd)
        self.setup_form.add_widget(b)

        self.setup_form.add_widget(BoxLayout(orientation='vertical',
                                             size_hint_y=None, height=300))

        if buttons:
            self.buttons = buttons
        else:
            self.buttons = BoxLayout(orientation='horizontal',
                                     height='32dp',size_hint_y=None)
            self.msg_btn = Button(text="Connect",
                                  on_press=lambda a: self.config_save_stop())
            self.msg_btn.font_size=font_large
            self.buttons.add_widget(self.msg_btn)
            self.cfg_btn = Button(text="Reset",
                                  on_press=lambda a: self.portal_setup())
            self.cfg_btn.font_size=font_large
            self.buttons.add_widget(self.cfg_btn)
            
        self.setup_form.add_widget(self.buttons)
        self.root.add_widget(self.setup_form)

        return self.setup_form

    def build(self):
        layout = BoxLayout(orientation='vertical')
        return layout
        
    def config_save_stop(self):
        self.url = self.input_url.text
        self.username = self.input_login.text
        self.password = self.input_passwd.text
        self.config.set('login', 'url', self.url)
        self.config.set('login', 'username', self.username)
        self.config.set('login', 'password', self.password)
        self.config.write()
        self.get_module()
        try:
            self.get_module()
            self.stop()
        except:
            print "Unexpected error [config_save_stop]:", sys.exc_info()[0]
            self.portal_setup()
        
    def config_save(self):
        self.url = self.input_url.text
        self.username = self.input_login.text
        self.password = self.input_passwd.text
        self.config.set('login', 'url', self.url)
        self.config.set('login', 'username', self.username)
        self.config.set('login', 'password', self.password)
        self.config.write()

    def get_module(self, base_url=None, username=None, password=None):
        if base_url == None:
            base_url=self.url
        if username == None:
            username=self.username
        if password == None:
            password=self.password
	user_data_dir = App.get_running_app().user_data_dir
    	tar = join(user_data_dir, "swm.tgz")
    	ini = join(user_data_dir, "swm.ini")
    	swm_json = join(user_data_dir, "swm.json")
    	swm_dir = join(user_data_dir, "swm")
        utils.get_module(base_url, username, password, str(platform), tar, ini, swm_json, swm_dir, user_data_dir)
        
if __name__ == '__main__':
    print "LoadMain"
    PortalApp().run()
