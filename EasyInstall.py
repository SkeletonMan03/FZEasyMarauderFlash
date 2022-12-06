#!/bin/python3
import os
import platform
from git import Repo
import glob
import time
import shutil
import serial.tools.list_ports
import requests
import json
import esptool
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
#	Thanks to Scorp for compiling	#
#	Needed bins for the ESP32-WROOM	#
#########################################
'''
print(OPENASCII)
print("Make sure your ESP32 is plugged in!")
BR=str("115200")

def checkfordevboardserialport():
	global serialport
	serialport=''
	vid="303A"
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for port in ports:
		if vid in port.hwid:
			serialport=port.device
	if serialport=='':
		print("WiFi Devboard or ESP32-S2 was not detected!")
		checkforotheresp32s2()
	return

def checkforotheresp32s2():
	print("Checking for other ESP32-S2")
	global serialport
	serialport=''
	vid="10C4"
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for port in ports:
		if vid in port.hwid:
			serialport=port.device
	if serialport=='':
		print("No ESP32-S2 was detected!")
		checkforknockoffesp32s2()
	else:
		print("You are using some other ESP chip. Hopefully an S2 chip with 4MB of flash")
	return

def checkforknockoffesp32s2():
	print("Checking for knock-off ESP32-S2")
	global serialport
	serialport=''
	vid="1A86"
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for port in ports:
		if vid in port.hwid:
			serialport=port.device
	if serialport=='':
		print("No ESP32-S2 was detected!")
		print("Please plug in a WiFi Devboard or ESP32-S2 and try again")
		choose_fw()
	else:
		print("You are using a knockoff ESP32 of some kind (hopefully an S2 or an S2-WROVER)! Success is not guaranteed!")
	return

def checkforesp32serialport():
	global serialport
	serialport=''
	vid="10C4"
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for port in ports:
		if vid in port.hwid:
			serialport=port.device
	if serialport=='':
		print("ESP32-WROOM is not plugged in!")
		print("Checking for knockoff ESP32-WROOM")
		checkforknockoffesp32serialport()
	return

def checkforknockoffesp32serialport():
	print("Checking for knock-off ESP32-WROOM")
	global serialport
	serialport=''
	vid="1A86"
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for port in ports:
		if vid in port.hwid:
			serialport=port.device
	if serialport=='':
		print("ESP32-WROOM is not plugged in!")
		print("Please plug in an ESP32-WROOM then try again")
		choose_fw()
	else:
		print("Warning! You are using a knockoff ESP32-WROOM! Success is not guaranteed!")
	return

def checkforscorpbins():
	global scorpbins
	scorpbins=(extraesp32bins+"/Marauder/WROOM")
	if os.path.exists(scorpbins):
		print("ScorpBins exists!")
	else:
		print("The ScorpBins folder does not exist!")
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
	checkforscorpbins()
	return

def choose_fw():
	choices='''
//======================================================\\\ 
|| Options:						||
|| 1) Flash Marauder on WiFi Devboard or ESP32-S2	||
|| 2) Save Flipper Blackmagic WiFi settings		||
|| 3) Flash Flipper Blackmagic				||
|| 4) Flash Marauder on ESP32-WROOM			||
|| 5) Update all files					||
|| 6) Exit						||
\\\======================================================//
'''
	global chip
	print(choices)
	fwchoice=int(input("Please enter the number of your choice: "))
	if fwchoice==1:
		print("You have chosen to flash Marauder on a WiFi devboard or ESP32-S2!")
		chip="esp32s2"
		checkfordevboardserialport()
		flash_esp32marauder()
	elif fwchoice==2:
		print("You have chosen to save Flipper Blackmagic WiFi settings")
		chip="esp32s2"
		checkfordevboardserialport()
		save_flipperbmsettings()
	elif fwchoice==3:
		print("You have chosen to flash Flipper Blackmagic")
		chip="esp32s2"
		checkfordevboardserialport()
		flash_flipperbm()
	elif fwchoice==4:
		print("You have chosen to flash Marauder onto an ESP32-WROOM")
		chip="esp32"
		checkforesp32serialport()
		flash_esp32wroom()
	elif fwchoice==5:
		print("You have chosen to update all of the files")
		update_option()
	elif fwchoice==6:
		print("You have chosen to exit")
		print("Exiting!")
		exit()
	else:
		print("Invalid option!")
	return

def erase_esp32fw():
	global serialport
	print("Erasing firmware...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'erase_region', '0x9000', '0x6000'])
	print("Firmware erased!")
	print("Waiting 5 seconds...")
	time.sleep(5)
	return

def checkforesp32marauder():
	print("Checking for Marauder releases")
	if os.path.exists("ESP32Marauder/releases"):
		print("Great, you have the Marauder releases folder!")
	else:
		print("Marauder releases folder does not exist, but that's okay, downloading them now...")
		os.makedirs('ESP32Marauder/releases')
		marauderapi="https://api.github.com/repos/justcallmekoko/ESP32Marauder/releases/latest"
		response=requests.get(marauderapi)
		jsondata=response.json()
		assetdls=range(0,5)
		for assetdl in assetdls:
			marauderasset=jsondata['assets'][assetdl]['browser_download_url']
			if marauderasset.find('/'):
				filename=(marauderasset.rsplit('/', 1)[1])
			downloadfile=requests.get(marauderasset, allow_redirects=True)
			open('ESP32Marauder/releases/'+filename, 'wb').write(downloadfile.content)
	esp32marauderfwc=('ESP32Marauder/releases/esp32_marauder_v[0-9]_[0-9]_[0-9][0-9]_*_flipper.bin')
	if not glob.glob(esp32marauderfwc):
		print("No ESP32 Marauder firmware exists somehow!")
	global esp32marauderfw
	for esp32marauderfw in glob.glob(esp32marauderfwc):
		if os.path.exists(esp32marauderfw):
			print("ESP32 Marauder firmware exists at", esp32marauderfw)
	return


def checkforoldhardwarebin():
	espoldhardwarefwc=('ESP32Marauder/releases/esp32_marauder_v[0-9]_[0-9]_[0-9][0-9]_*_old_hardware.bin')
	if not glob.glob(espoldhardwarefwc):
		print("old_hardware bin does not exist!")
	global espoldhardwarefw
	for espoldhardwarefw in glob.glob(espoldhardwarefwc):
		if os.path.exists(espoldhardwarefw):
			print("Old Hardware bin exists at", espoldhardwarefw)
		else:
			print("Somehow, the old_hardware.bin file does not exist!")
	return

def prereqcheck():
	print("Checking for prerequisites...")
	checkforextrabins()
	checkforesp32marauder()
	checkforoldhardwarebin()
	return

def flash_esp32marauder():
	global serialport
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Marauder/bootloader.bin', '0x8000', extraesp32bins+'/Marauder/partitions.bin', '0x10000', esp32marauderfw])
	print("ESP32 has been flashed with Marauder!")
	return

def flash_esp32wroom():
	global serialport
	print("Flashing ESP32 Marauder Firmware onto ESP32-WROOM...")
	erase_esp32fw()
	esptool.main(['-p', serialport, '-b', BR, '--before', 'default_reset', '--after', 'hard_reset', '-c', chip, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '2MB', '0x8000', scorpbins+'/partitions.bin', '0x1000', scorpbins+'/bootloader.bin', '0x10000', espoldhardwarefw])
	print("ESP32-WROOM has been flashed with Marauder!")
	return

def save_flipperbmsettings():
	global serialport
	print("Saving Flipper Blackmagic WiFi Settings to Extra_ESP32_Bins/Blackmagic/nvs.bin")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '-a', 'no_reset', 'read_flash', '0x9000', '0x6000', extraesp32bins+'/Blackmagic/nvs.bin'])
	return

def flash_flipperbm():
	if os.path.exists(extraesp32bins+"/Blackmagic/nvs.bin"):
		print("Flashing Flipper Blackmagic with WiFi Settings restore")
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x9000', extraesp32bins+'/Blackmagic/nvs.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
	else:
		print("Flashing Flipper Blackmagic without WiFi Settings restore")
		erase_esp32fw()
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
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
