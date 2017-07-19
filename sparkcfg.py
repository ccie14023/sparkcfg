import os
import sys
from cli import cli
import time
import difflib
from spark import *

SPARK_ROOM = "Catalyst OnBox"

def save_config():

	output = cli('show run')

	timestr = time.strftime("%Y%m%d-%H%M%S")
	filename = "/bootflash/" + timestr + "_shrun"

	f = open(filename,"w")
	f.write(output)
	f.close

	f = open('/bootflash/current_config_name','w')
	f.write(filename)
	f.close

	return filename

def get_cfg_fn():

	try:
		f = open('/bootflash/current_config_name','r')
	except:
		return None
	fn = f.read()
	f.close()
	return fn

def compare_configs(cfg1,cfg2):

	d = difflib.unified_diff(cfg1, cfg2)

	diffstr = ""

	for line in d:
		if line.find('Current configuration') == -1:
			if line.find('Last configuration change') == -1:
				if line.find('length 0') == -1:
					if line.find('login authentication tacplus') == -1:
						if (line.find("+++")==-1) and (line.find("---")==-1):
							if (line.find("-!")==-1) and (line.find('+!')==-1):
								if line.startswith('+'):
									diffstr = diffstr + "\n" + line
								elif line.startswith('-'):
									diffstr = diffstr + "\n" + line

	return diffstr

def do_error(error):
	f = open("/bootflash/last_error", "w")
	f.write(error)
	f.close

if __name__ == '__main__':

	old_cfg_fn = get_cfg_fn()

	if not old_cfg_fn:
		#  First time we are running
		save_config()
		sys.exit()

	new_cfg_fn = save_config()

	f = open(old_cfg_fn)
	old_cfg = f.readlines()
	f.close

	f = open(new_cfg_fn)
	new_cfg = f.readlines()
	f.close

	os.remove(old_cfg_fn)

	d = compare_configs(old_cfg,new_cfg)

	if d != "":
		text = "Configuration change detected:" + "\n" + d
		room = get_room_id(SPARK_ROOM, bot_token)
		if room == "":
			do_error("Unable to get room ID")
        	print text
		if str(post_message(text, room, bot_token).status_code)[0] != '2':
			do_error("Post message failed!")
	else:
		do_error("No configuration change detected!")
