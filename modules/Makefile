all: citizens.tgz drivers.tgz janitors.tgz 

citizens.tgz: swm/main.py citizen_config.py 
	cp citizen_config.py swm/config.py
	tar cvzf citizens.tgz swm
	rm swm/config.py

drivers.tgz: swm/main.py driver_config.py 
	cp driver_config.py swm/config.py
	tar cvzf drivers.tgz swm
	rm swm/config.py

janitors.tgz: swm/main.py janitor_config.py
	cp janitor_config.py swm/config.py
	tar cvzf janitors.tgz swm
	rm swm/config.py



