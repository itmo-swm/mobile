#!/usr/bin/python

import os.path
import requests
from ConfigParser import ConfigParser
import tarfile
from shutil import rmtree
from datetime import datetime
import json

def get_module(base_url=None, username=None, password=None, platform="android",
               tar = "swm.tgz", config_file='swm.ini'):
    config = get_config(config_file)
    if base_url == None:
        base_url=config.get('login', 'url')
    if username == None:
        username=config.get('login', 'username')
    if password == None:
        password=config.get('login', 'password')

    f=open(tar, "w+")
    url = base_url + '/swm_scripts/mobile_module?platform=' + platform
    r=requests.get(url, auth=(username, password))
    modname = r.text.strip()
    
    url = base_url + '/swm_scripts/mod2time?module=' + modname
    r=requests.get(url, auth=(username, password))
    modtime = r.text.strip()
    try:
        print "J1"
        swmfile = open("swm.json")
        swminfo = json.load(swmfile)
        swmfile.close()
        modinfo = swminfo['module']
        if modinfo["name"] == modname:
            local_time = datetime.strptime(modinfo["time"], "%Y/%m/%d %H:%M:%S.%f UTC")
            portal_time = datetime.strptime(modtime, "%Y/%m/%d %H:%M:%S.%f UTC")
            if portal_time > local_time:
                modinfo["time"] = modtime
            elif os.path.isdir('swm'):
                return
        else:
            swminfo = {"module": {"name": modname, "time": modtime}}
    except:
        swminfo = {"module": {"name": modname, "time": modtime}}
        
    url = base_url + '/swm/modules/' + modname + '/at_download/file'

    r=requests.get(url, auth=(username, password))
    for chunk in r.iter_content(chunk_size=128):
        f.write(chunk)
    f.close()

    t=tarfile.open(tar, 'r:gz')
    if os.path.isdir('swm'):
        rmtree('swm')
    t.extractall()
        
    swmfile = open("swm.json", "w+")
    json.dump(swminfo, swmfile, indent=4)
    swmfile.close()

def get_config(file='swm.ini'):
    config = ConfigParser()
    config.read(file)

    return config

