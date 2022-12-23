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
from colorama import Fore, Back, Style

OPENASCII=Fore.GREEN+'''
#########################################
#    Marauder Flasher Script		#
#    Python edition by SkeletonMan	#
#    based off of a Windows based	#
#    script by Frog, UberGuidoz,	#
#    and ImprovingRigamarole		#
#					#
#    Thanks to everyone who has done	#
#    testing on various chips for me	#
#    Thanks to Scorp for compiling	#
#    needed bins for the ESP32-WROOM	#
#########################################
'''+Style.RESET_ALL

print(OPENASCII)
print("Make sure your ESP32 or WiFi devboard is plugged in!")
BR=str("115200")

def checkforserialport():
	global serialport
	serialport=''
	vids=['303A','10C4','1A86']
	com_port=None
	ports=list(serial.tools.list_ports.comports())
	for vid in vids:
		for port in ports:
			if vid in port.hwid:
				serialport=port.device
				device=vid
	if serialport=='':
		print(Fore.RED+"No ESP32 device was detected!"+Style.RESET_ALL)
		print(Fore.RED+"Please plug in a Flipper WiFi devboard or an ESP32 chip and try again"+Style.RESET_ALL)
		choose_fw()
	if device=='':
		return
	elif device=='303A':
		print(Fore.BLUE+"You are most likely using a Flipper Zero WiFi Devboard or an ESP32-S2"+Style.RESET_ALL)
	elif device=='10C4':
		print(Fore.BLUE+"You are most likely using an ESP32-WROOM, an ESP32-S2-WROVER, or an ESP32-S3-WROOM"+Style.RESET_ALL)
	elif device=='1A86':
		print(Fore.MAGENTA+"You are most likely using a knock-off ESP32 chip! Success is not guaranteed!"+Style.RESET_ALL)

	return

def checkforextrabins():
	extraesp32binsrepo="https://github.com/UberGuidoZ/Marauder_BINs.git"
	global extraesp32bins
	extraesp32bins=("Extra_ESP32_Bins")
	global scorpbins
	scorpbins=(extraesp32bins+"/Marauder/WROOM")
	if os.path.exists(extraesp32bins):
		print("The extra ESP32 bins folder exists!")
	else:
		print("The extra ESP32 bins folder does not exist!")
		print("That's okay, downloading them now...")
		Repo.clone_from(extraesp32binsrepo, extraesp32bins)
	return

def choose_fw():
	choices='''
//======================================================\\\ 
|| Options:						||
|| 1) Flash Marauder on WiFi Devboard or ESP32-S2	||
|| 2) Save Flipper Blackmagic WiFi settings		||
|| 3) Flash Flipper Blackmagic				||
|| 4) Flash Marauder on ESP32-WROOM			||
|| 5) Flash Marauder on ESP32-S3			||
|| 6) Update all files					||
|| 7) Exit						||
\\\======================================================//
'''
	global chip
	print(choices)
	fwchoice=int(input("Please enter the number of your choice: "))
	if fwchoice==1:
		print("You have chosen to flash Marauder on a WiFi devboard or ESP32-S2")
		chip="esp32s2"
		checkforserialport()
		flash_esp32marauder()
	elif fwchoice==2:
		print("You have chosen to save Flipper Blackmagic WiFi settings")
		chip="esp32s2"
		checkforserialport()
		save_flipperbmsettings()
	elif fwchoice==3:
		print("You have chosen to flash Flipper Blackmagic")
		chip="esp32s2"
		checkforserialport()
		flash_flipperbm()
	elif fwchoice==4:
		print("You have chosen to flash Marauder onto an ESP32-WROOM")
		chip="esp32"
		checkforserialport()
		flash_esp32wroom()
	elif fwchoice==5:
		print("You have chosen to flash Marauder onto an ESP32-S3")
		chip="esp32s3"
		checkforserialport()
		flash_esp32s3()
	elif fwchoice==6:
		print("You have chosen to update all of the files")
		update_option()
	elif fwchoice==7:
		print("You have chosen to exit")
		print("Exiting!")
		exit()
	else:
		print(Fore.RED+"Invalid option!"+Style.RESET_ALL)
		exit()
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
		assetdls=range(0,7)
		for assetdl in assetdls:
			marauderasset=jsondata['assets'][assetdl]['browser_download_url']
			if marauderasset.find('/'):
				filename=(marauderasset.rsplit('/', 1)[1])
			downloadfile=requests.get(marauderasset, allow_redirects=True)
			open('ESP32Marauder/releases/'+filename, 'wb').write(downloadfile.content)
	esp32marauderfwc=('ESP32Marauder/releases/esp32_marauder_v*_flipper.bin')
	if not glob.glob(esp32marauderfwc):
		print("No ESP32 Marauder Flipper firmware exists somehow!")
	global esp32marauderfw
	for esp32marauderfw in glob.glob(esp32marauderfwc):
		if os.path.exists(esp32marauderfw):
			print("ESP32 Marauder firmware exists at", esp32marauderfw)
	return

def checkfors3bin():
	esp32s3fwc=('ESP32Marauder/releases/esp32_marauder_v*_mutliboardS3.bin')
	if not glob.glob(esp32s3fwc):
		print("mutliboards3 bin does not exist!")
	global esp32s3fw
	for esp32s3fw in glob.glob(esp32s3fwc):
		if os.path.exists(esp32s3fw):
			print("ESP32-S3 firmware bin exists at", esp32s3fw)
		else:
			print("Somehow, the mutliboardS3.bin file does not exist!")
	return

def checkforoldhardwarebin():
	espoldhardwarefwc=('ESP32Marauder/releases/esp32_marauder_v*_old_hardware.bin')
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
	checkfors3bin()
	checkforoldhardwarebin()
	return

def flash_esp32marauder():
	global serialport
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware on a WiFi Devboard or ESP32-S2...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Marauder/bootloader.bin', '0x8000', extraesp32bins+'/Marauder/partitions.bin', '0x10000', esp32marauderfw])
	print(Fore.GREEN+"ESP32-S2 has been flashed with Marauder!"+Style.RESET_ALL)
	return

def flash_esp32wroom():
	global serialport
	print("Flashing ESP32 Marauder Firmware onto ESP32-WROOM...")
	erase_esp32fw()
	esptool.main(['-p', serialport, '-b', BR, '--before', 'default_reset', '--after', 'hard_reset', '-c', chip, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '2MB', '0x8000', scorpbins+'/partitions.bin', '0x1000', scorpbins+'/bootloader.bin', '0x10000', espoldhardwarefw])
	print(Fore.GREEN+"ESP32-WROOM has been flashed with Marauder!"+Style.RESET_ALL)
	return

def save_flipperbmsettings():
	global serialport
	print("Saving Flipper Blackmagic WiFi Settings to Extra_ESP32_Bins/Blackmagic/nvs.bin")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '-a', 'no_reset', 'read_flash', '0x9000', '0x6000', extraesp32bins+'/Blackmagic/nvs.bin'])
	print(Fore.GREEN+"Flipper Blackmagic Wifi Settings have been saved to ", extraesp32bins+"/Blackmagic/nvs.bin!"+Style.RESET_ALL)
	return

def flash_flipperbm():
	if os.path.exists(extraesp32bins+"/Blackmagic/nvs.bin"):
		print("Flashing Flipper Blackmagic with WiFi Settings restore")
		erase_esp32fw()
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x9000', extraesp32bins+'/Blackmagic/nvs.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
		print(Fore.GREEN+"Flipper Blackmagic has been flashed with the WiFi Settings restored"+Style.RESET_ALL)
	else:
		print("Flashing Flipper Blackmagic without WiFi Settings restore")
		erase_esp32fw()
		esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '4MB', '0x1000', extraesp32bins+'/Blackmagic/bootloader.bin', '0x8000', extraesp32bins+'/Blackmagic/partition-table.bin', '0x10000', extraesp32bins+'/Blackmagic/blackmagic.bin'])
		print(Fore.GREEN+"Flipper Blackmagic has been flashed without WiFi Settings restored"+Style.RESET_ALL)
	return

def flash_esp32s3():
	global serialport
	erase_esp32fw()
	print("Flashing ESP32 Marauder Firmware onto ESP32-S3...")
	esptool.main(['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '8MB', '0x0', extraesp32bins+'/S3/bootloader.bin', '0x8000', extraesp32bins+'/S3/partitions.bin', '0xE000', extraesp32bins+'/S3/boot_app0.bin', '0x10000', esp32s3fw])
	print(Fore.GREEN+"ESP32-S3 has been flashed with Marauder!"+Style.RESET_ALL)
	return

def update_option():
	print("Checking for and deleting the files before replacing them...")
	if os.path.exists("ESP32Marauder"):
		shutil.rmtree("ESP32Marauder")
	if os.path.exists("Extra_ESP32_Bins"):
		shutil.rmtree("Extra_ESP32_Bins")
	prereqcheck()
	return

prereqcheck()
choose_fw()
