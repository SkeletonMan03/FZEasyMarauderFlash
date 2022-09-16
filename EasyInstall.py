#!/bin/python3
import os
import platform
from git import Repo
import glob
import time
import shutil
OPENASCII='''
#########################################
#	Marauder Flasher Script		#
#	Python edition by SkeletonMan	#
#	based off of a Windows based	#
#	script by Frog, UberGuidoz,	#
#	and ImprovingRigamarole		#
#					#
#	Special thanks to L0rd_K0nda	#
#	for doing testing for me!	#
#########################################
'''
print(OPENASCII)
print("Make sure your ESP32 is plugged in!")
BR=str("115200")

#I think the serialport section could technically be left blank...

runningOS=platform.system()
if runningOS=="Linux":
	serialport="/dev/ttyACM0"
elif runningOS=="Darwin":
	serialport="/dev/cu.usbmodem01"
elif runningOS=="Windows":
	serialport=os.popen('wmic path Win32_SerialPort get DeviceID^,PNPDeviceID^|findstr /i VID_303A')

def checkforesptool():
	esptoolrepo="https://github.com/espressif/esptool.git"
	global esptoolfile
	esptoolfile=("esptool/esptool.py")
	if os.path.exists(esptoolfile):
		print("The esptool folder exists!")
	else:
		print("The esptool folder does not exist!")
		print("That's okay, downloading ESPTool...")
		Repo.clone_from(esptoolrepo, "esptool")
	return

def checkforextrabins():
	extraesp32binsrepo="https://github.com/UberGuidoZ/Marauder_BINs.git"
	global extraesp32bins
	extraesp32bins=("Extra_ESP32_Bins")
	if os.path.exists(extraesp32bins):
		print("The extra ESP32 bins folder exists!")
	else:
		print("The extra ESP32 bins folder does not exist!")
		print("That's okay, downloading them now...")
		Repo.clone_from(extraesp32binsrepo, extraesp32bins)
	return

def choose_fw():
	choices='''
//==============================================\\\ 
|| Options:					||
|| 1) Flash Marauder				||
|| 2) Save Flipper Blackmagic WiFi settings	||
|| 3) Flash Flipper Blackmagic			||
|| 4) Update all files				||
\\\==============================================//
'''
	print(choices)
	fwchoice=int(input("Please enter the number of your choice: "))
	if fwchoice==1:
		print("You have chosen to flash Marauder!")
		flash_esp32marauder()
	elif fwchoice==2:
		print("You have chosen to save Flipper Blackmagic WiFi settings")
		save_flipperbmsettings()
	elif fwchoice==3:
		print("You have chosen to flash Flipper Blackmagic")
		flash_flipperbm()
	elif fwchoice==4:
		print("You have chosen to update all of the files")
		update_option()
	else:
		print("Invalid option!")
	return

def erase_esp32fw():
	print("Erasing firmware...")
	os.system("python3 "+esptoolfile+ " -p "+ serialport+ " -b "+ BR+ " -c esp32s2 --before default_reset -a no_reset erase_region 0x9000 0x6000")
	print("Firmware erased!")
	print("Waiting 5 seconds...")
	time.sleep(5)
	return

def checkforesp32marauder():
	marauderfwrepo="https://github.com/justcallmekoko/ESP32Marauder.git"
	esp32marauderfwc=('ESP32Marauder/esp32_marauder/esp32_marauder_v[0-9]_[0-9]_[0-9][0-9]_*_flipper.bin')
	if not glob.glob(esp32marauderfwc):
		print("No ESP32 Marauder firmware exists!")
		print("But that's okay!")
		print("Downloading Marauder repo...")
		Repo.clone_from(marauderfwrepo, "ESP32Marauder")
	global esp32marauderfw
	for esp32marauderfw in glob.glob(esp32marauderfwc):
		if os.path.exists(esp32marauderfw):
			print("ESP32 Marauder firmware exists at", esp32marauderfw)
		else:
			print("Somehow, the ESP32 Marauder firmware still does not exist!")
		return

def prereqcheck():
	print("Checking for prerequisites...")
	checkforesptool()
	checkforextrabins()
	checkforesp32marauder()
	return

def flash_esp32marauder():
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware...")
	os.system("python3 "+esptoolfile+ " -p "+ serialport+ " -b "+ BR+ " -c esp32s2 --before default_reset -a no_reset write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x1000 "+ extraesp32bins +"/Marauder/bootloader.bin 0x8000 "+ extraesp32bins +"/Marauder/partitions.bin 0x10000 "+ esp32marauderfw)
	print("ESP32 has been flashed with Marauder!")
	return

def save_flipperbmsettings():
	global serialport
	if serialport=="/dev/cu.usbmodem01":
		serialport="/dev/cu.usbmodemblackmagic1"
	print("Saving Flipper Blackmagic WiFi Settings to Extra_ESP32_Bins/Blackmagic/nvs.bin")
	os.system("python3 "+esptoolfile+" -p "+serialport+" -b "+BR+" -c esp32s2 -a no_reset read_flash 0x9000 0x6000 "+extraesp32bins+ "/Blackmagic/nvs.bin")
	return

def flash_flipperbm():
	if os.path.exists(extraesp32bins+"/Blackmagic/nvs.bin"):
		print("Flashing Flipper Blackmagic with WiFi Settings restore")
		os.system("python3"+esptoolfile+" -p "+serialport+" -b "+BR+" -c esp32s2 --before default_reset -a no_reset write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x1000 "+extraesp32bins+"/Blackmagic/bootloader.bin 0x8000 "+extraesp32bins+"/Blackmagic/partition-table.bin 0x9000 "+extraesp32bins+"/Blackmagic/nvs.bin 0x10000 Blackmagic/blackmagic.bin")
	else:
		print("Flashing Flipper Blackmagic without WiFi Settings restore")
		erase_esp32fw()
		os.system("python3 "+esptoolfile+" -p "+serialport+" -b "+BR+" -c esp32s2 --before default_reset -a no_reset write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x1000 "+extraesp32bins+"/Blackmagic/bootloader.bin 0x8000 "+extraesp32bins+"/Blackmagic/partition-table.bin 0x10000 "+extraesp32bins+"/Blackmagic/blackmagic.bin")
	return

def update_option():
	print("Checking for and deleting the files before replacing them...")
	if os.path.exists("ESP32Marauder"):
		shutil.rmtree("ESP32Marauder")
	if os.path.exists("Extra_ESP32_Bins"):
		shutil.rmtree("Extra_ESP32_Bins")
	if os.path.exists("esptool"):
		shutil.rmtree("esptool")
	prereqcheck()
	return

prereqcheck()
choose_fw()
