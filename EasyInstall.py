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
from pathlib import Path
import git
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-s', '--serialport', type=str, help="Define serial port", default='')
parser.add_argument('-ps', '--preselect', type=int, help="Preselect flashing option", default=None)
args=parser.parse_args()
serialport=args.serialport
fwchoice=args.preselect

OPENASCII=Fore.GREEN+'''
#################################################################################
#                          ESP32 FZEasyFlasher					#
#                          by Lord SkeletonMan                                  #
#			NOW INCLUDING EVIL PORTAL!				#
#		Originally Based off of a Windows Batch script			#
#    		by Frog, UberGuidoz, and ImprovingRigamarole			#
#										#
#       Thanks to everyone who has done testing on various chips for me		#
#        Thanks to Scorp for compiling needed bins for the ESP32-WROOM		#
#    Thanks to AWOK for pointing out bugs, adding his boards, and testing  	#
#################################################################################
'''+Style.RESET_ALL

print(OPENASCII)
print("Make sure your ESP32 or WiFi devboard is plugged in!")
BR=str("115200")

def checkforserialport():
	global serialport
	if serialport!='':
		print("Will not check for serial port or possible chip type since it is specified as", serialport)
		return
	else:
		serialport=''
	print("Checking for serial port...")
	vids=['303A','10C4','1A86', '0483']
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
		if fwchoicepreselect==False:
			choose_fw()
		elif fwchoicepreselect==True:
			exit()
	if device=='':
		return
	elif device=='303A':
		print(Fore.BLUE+"You are most likely using a Flipper Zero WiFi Devboard or an ESP32-S2"+Style.RESET_ALL)
	elif device=='10C4':
		print(Fore.BLUE+"You are most likely using an ESP32-WROOM, an ESP32-S2-WROVER, or an ESP32-S3-WROOM"+Style.RESET_ALL)
	elif device=='1A86':
		print(Fore.MAGENTA+"You are most likely using a knock-off ESP32 chip! Success is not guaranteed!"+Style.RESET_ALL)
	elif device== '0483':
		print(Fore.BLUE+"You are most likely using an DrB0rk S3 Multiboard"+Style.RESET_ALL)
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
//==================================================================\\\ 
|| Options:						            ||
||  1) Flash Marauder on WiFi Devboard or ESP32-S2	            ||
||  2) Flash SD Serial Marauder on WiFi Devboard or ESP32-S2        ||
||  3) Save Flipper Blackmagic WiFi settings		            ||
||  4) Flash Flipper Blackmagic				            ||
||  5) Flash Marauder on ESP32-WROOM			            ||
||  6) Flash Marauder on ESP32 Marauder Mini		            ||
||  7) Flash Marauder on ESP32-S3			            ||
||  8) Flash Marauder on AWOK v1-3 or Duoboard                      ||
||  9) Flash Marauder on AWOK v4 Chungus Board                      ||
|| 10) Flash Marauder on AWOK v5 ESP32                              ||
|| 11) Flash Marauder on AWOK Dual ESP32 (Orange Port)              ||
|| 12) Flash Marauder on AWOK Dual ESP32 Touch Screen (White Port)  ||
|| 13) Flash Marauder on AWOK Dual ESP32 Mini (White Port)          ||
|| 14) Flash Evil Portal on ESP32-WROOM				    ||
|| 15) Flash Evil Portal on ESP32-S2 or WiFi Devboard		    ||
|| 16) Just Erase ESP32 - Try this if you think you bricked it	    ||
|| 17) Update all files					            ||
|| 18) Exit						            ||
\\\==================================================================//
'''
	#Still not perfect, but better
	global selectedfw
	global selectedboard
	global fwchoice
	global fwchoicepreselect
	hardresetlist=[5, 6, 8, 9, 10, 11, 12, 13]

	if fwchoice!=None:
		print("Fwchoice", fwchoice)
		fwchoicepreselect=True
		print(Fore.BLUE+"You have preselected option", fwchoice,Style.RESET_ALL)
		print("If you didn't mean to do this, CTRL-C now!")
		print("Waiting 5 seconds before continuing...")
		time.sleep(5)
	else:
		fwchoicepreselect=False
		print(choices)
		fwchoice=int(input("Please enter the number of your choice: "))
	if fwchoice in hardresetlist:
		reset='hard_reset'
	else:
		reset='no_reset'
	if fwchoice==1:
		print("You have chosen to flash Marauder on a WiFi devboard or ESP32-S2")
		chip="esp32s2"
		selectedfw="Marauder"
		selectedboard="ESP32-S2"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Marauder/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Marauder/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32marauderfw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, '-a', 'no_reset', 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==2:
		print("You have chosen to flash Marauder on a WiFi devboard or ESP32-S2 with SD Serial Support")
		chip="esp32s2"
		selectedfw="Marauder with SD Serial Support"
		selectedboard="ESP32-S2"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Marauder/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Marauder/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32marauderfwserial
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, '-a', 'no_reset', 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==3:
		print("You have chosen to save Flipper Blackmagic WiFi settings")
		chip="esp32s2"
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		savebmset=['-p', serialport, '-b', BR, '-c', chip, '-a', 'no_reset', 'read_flash', '0x9000', '0x6000', extraesp32bins+'/Blackmagic/nvs.bin']
		save_flipperbmsettings(savebmset)
	elif fwchoice==4:
		print("You have chosen to flash Flipper Blackmagic")
		chip="esp32s2"
		selectedfw="Blackmagic"
		selectedboard="ESP32-S2"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Blackmagic/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Blackmagic/partition-table.bin'
		fwbin=extraesp32bins+'/Blackmagic/blackmagic.bin'
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		if os.path.exists(extraesp32bins+"/Blackmagic/nvs.bin"):
			offset_three='0x9000'
			wifisettings=extraesp32bins+'/Blackmagic/nvs.bin'
			offset_four='0x10000'
			flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, wifisettings, offset_four, fwbin]
		else:
			offset_three='0x10000'
			flashparams=esptool.main['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==5:
		print("You have chosen to flash Marauder onto an ESP32-WROOM")
		chip="esp32"
		selectedfw="Marauder"
		selectedboard="ESP32-WROOM"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=scorpbins+'/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=scorpbins+'/partitions.bin'
		offset_three='0x10000'
		fwbin=espoldhardwarefw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]		
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==6:
		print("You have chosen to flash Marauder onto an ESP32 Marauder Mini")
		chip="esp32"
		selectedfw="Marauder"
		selectedboard="ESP32 Marauder Mini"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=scorpbins+'/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=scorpbins+'/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32minifw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==7:
		print("You have chosen to flash Marauder onto an ESP32-S3")
		chip="esp32s3"
		selectedfw="Marauder"
		selectedboard="ESP32-S3"
		flashsize='8MB'
		offset_one='0x0'
		bootloader_bin=extraesp32bins+'/S3/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/S3/partitions.bin'
		offset_three='0xE000'
		boot_app=extraesp32bins+'/S3/boot_app0.bin'
		offset_four='0x10000'
		fwbin=esp32s3fw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'no_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, boot_app, offset_four, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==8:
		print("You have chosen to flash Marauder onto an AWOK v1-3 or Duoboard")
		chip="esp32"
		selectedfw="Marauder"
		selectedboard="AWOK v1-3 or Duoboard"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=scorpbins+'/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=scorpbins+'/partitions.bin'
		offset_three='0x10000'
		fwbin=espoldhardwarefw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==9:
		print("You have chosen to flash Marauder on an AWOK v4 Chungus Board")
		chip="esp32s2"
		selectedfw="Marauder"
		selectedboard="AWOK v4 Chungus Board"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Marauder/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Marauder/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32marauderfw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==10:
		print("You have chosen to flash Marauder on an AWOK v5 ESP32")
		chip="esp32s2"
		selectedfw="Marauder with SD Serial Support"
		selectedboard="AWOK v5 ESP32"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Marauder/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Marauder/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32marauderfwserial
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==11:
		print("You have chosen to flash Marauder on an AWOK Dual ESP32 (Orange Port)")
		chip="esp32s2"
		selectedfw="Marauder with SD Serial Support"
		selectedboard="AWOK Dual ESP32 (Orange Port)"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=extraesp32bins+'/Marauder/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=extraesp32bins+'/Marauder/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32marauderfwserial
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==12: 
		print("You have chosen to flash Marauder onto an AWOK Dual ESP32 Touch Screen (White Port)")
		chip="esp32"
		selectedfw="Marauder"
		selectedboard="AWOK Dual ESP32 Touch Screen (White Port)"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=scorpbins+'/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=scorpbins+'/partitions.bin'
		offset_three='0x10000'
		fwbin=espnewhardwarefw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==13:
		print("You have chosen to flash Marauder onto an AWOK Dual ESP32 Mini (White Port)")
		chip="esp32"
		selectedfw="Marauder Mini"
		selectedboard="AWOK Dual ESP32 Mini (White Port)"
		flashsize='4MB'
		offset_one='0x1000'
		bootloader_bin=scorpbins+'/bootloader.bin'
		offset_two='0x8000'
		partitions_bin=scorpbins+'/partitions.bin'
		offset_three='0x10000'
		fwbin=esp32minifw
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', reset, 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, bootloader_bin, offset_two, partitions_bin, offset_three, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==14:
		print("You have chosen to flash Evil Portal on an ESP32-WROOM")
		chip="esp32"
		selectedfw="Evil Portal"
		selectedboard="ESP32-WROOM"
		flashsize='4MB'
		offset_one='0x1000'
		fwbin=evilportalfwwroom
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'hard_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==15:
		print("You have chosen to flash Evil Portal on an ESP32-S2 or WiFi Devboard")
		chip="esp32s2"
		selectedfw="Evil Portal"
		selectedboard="ESP32-S2"
		flashsize='4MB'
		offset_one='0x1000'
		fwbin=evilportalfws2
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR,  '-a', 'no_reset', 'erase_flash']
		flashparams=['-p', serialport, '-b', BR, '-c', chip, '--before', 'default_reset', '-a', 'hard_reset', 'write_flash', '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', flashsize, offset_one, fwbin]
		flashtheboard(eraseparams, flashparams)
	elif fwchoice==16:
		print("You have chosen to just erase the ESP32")
		checkforserialport()
		eraseparams=['-p', serialport, '-b', BR, 'erase_flash']
		erase_esp32(eraseparams)
	elif fwchoice==17:
		print("You have chosen to update all of the files")
		fwchoicepreselect=False
		fwchoice=None
		update_option()
	elif fwchoice==18:
		print("You have chosen to exit")
		print("Exiting!")
		exit()
	else:
		print(Fore.RED+"Invalid option!"+Style.RESET_ALL)
		exit()
	return

def erase_esp32(eraseparams):
	tries=3
	attempts=0
	for i in range(tries):
		try:
			attempts+=1
			print("Erasing firmware...")
			esptool.main(eraseparams)
		except Exception as err:
			print(err)
			if attempts==3:
				print("Unable to erase the firmware")
				exit()
			print("Waiting 5 seconds and trying again...")
			time.sleep(5)
			continue
		print("Successfully erased!")
		break
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
		assetdls=range(0,11)
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

def checkforevilportal():
	print("Checking for Evil portal")
	if os.path.exists('EvilPortal'):
		print("Great, you have the Evil Portal folder!")
	else:
		print("Evil Portal folder not found, but that's okay, downloading it now")
		os.makedirs('EvilPortal')
		evilportalwroomurl="https://github.com/bigbrodude6119/flipper-zero-evil-portal/raw/main/Single%20File%20Bins/Evil%20Portal%20WROOM.bin"
		downloadfile=requests.get(evilportalwroomurl)
		open("EvilPortal/EvilPortalWROOM.bin", 'wb').write(downloadfile.content)
		evilportals2url="https://github.com/bigbrodude6119/flipper-zero-evil-portal/raw/main/Single%20File%20Bins/Evil%20Portal%20WiFi%20Board%20or%20S2.bin"
		downloadfile=requests.get(evilportals2url)
		open("EvilPortal/EvilPortalS2.bin", 'wb').write(downloadfile.content)
	global evilportalfwwroom
	global evilportalfws2
	evilportalfwwroom="EvilPortal/EvilPortalWROOM.bin"
	evilportalfws2="EvilPortal/EvilPortalS2.bin"
	if os.path.exists(evilportalfwwroom):
		print("WROOM Evil Portal FW exists at", evilportalfwwroom)
	else:
		print("Somehow, the Evil Portal WROOM bin does not exist!")
	if os.path.exists(evilportalfws2):
		print("S2 Evil Portal FW exists at", evilportalfws2)
	else:
		print("Somehow, the Evil Portal S2 bin does not exist!")
	return

def checkforesp32marauderserial():
	esp32marauderfwserialc=('ESP32Marauder/releases/esp32_marauder_v*_flipper_sd_serial.bin')
	if not glob.glob(esp32marauderfwserialc):
		print("No ESP32 Marauder Flipper SD Serial firmware exists somehow!")
	global esp32marauderfwserial
	for esp32marauderfwserial in glob.glob(esp32marauderfwserialc):
		if os.path.exists(esp32marauderfwserial):
			print("ESP32 Marauder firmware exists at", esp32marauderfwserial)
	return

def checkfors3bin():
	esp32s3fwc=('ESP32Marauder/releases/esp32_marauder_v*ultiboardS3.bin')
	if not glob.glob(esp32s3fwc):
		print("mutliboards3 bin does not exist!")
	global esp32s3fw
	for esp32s3fw in glob.glob(esp32s3fwc):
		if os.path.exists(esp32s3fw):
			print("ESP32-S3 firmware bin exists at", esp32s3fw)
		else:
			print("Somehow, the multiboardS3.bin file does not exist!")
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

def checkforminibin():
	esp32minifwc=('ESP32Marauder/releases/esp32_marauder_v*_mini.bin')
	if not glob.glob(esp32minifwc):
		print("mini bin does not exist!")
	global esp32minifw
	for esp32minifw in glob.glob(esp32minifwc):
		if os.path.exists(esp32minifw):
			print("Mini bin exists at", esp32minifw)
		else:
			print("Somehow, the mini bin does not exist!")
	return

def checkfornewhardwarebin():
	espnewhardwarefwc=('ESP32Marauder/releases/esp32_marauder_v*_v6.bin')
	if not glob.glob(espnewhardwarefwc):
		print("new_hardware bin does not exist!")
	global espnewhardwarefw
	for espnewhardwarefw in glob.glob(espnewhardwarefwc):
		if os.path.exists(espnewhardwarefw):
			print("New Hardware bin exists at", espnewhardwarefw)
		else:
			print("Somehow, the new_hardware.bin file does not exist!")
	return

def prereqcheck():
	print("Checking for prerequisites...")
	checkforextrabins()
	checkforesp32marauder()
	checkforesp32marauderserial()
	checkfors3bin()
	checkforoldhardwarebin()
	checkforminibin()
	checkfornewhardwarebin()
	checkforevilportal()
	return

def flashtheboard(eraseparams, flashparams):
	erase_esp32(eraseparams)
	tries=3
	attempts=0
	for i in range(tries):
		try:
			attempts+=1
			print("Flashing", selectedfw, "on", selectedboard)
			esptool.main(flashparams)
		except Exception as err:
			print(err)
			if attempts==3:
				print("Could not flash", selectedfw, "on", selectedboard)
				exit()
			print("Waiting 5 seconds and trying again...")
			time.sleep(5)
			continue
		print(Fore.GREEN+selectedboard, "has been flashed with", selectedfw+Style.RESET_ALL)
		break
	return

def save_flipperbmsettings(savebmset):
	tries=3
	attempts=0
	for i in range(tries):
		try:
			attempts +=1
			print("Saving Flipper Blackmagic WiFi Settings to Extra_ESP32_Bins/Blackmagic/nvs.bin")
			esptool.main(savebmset)
		except Exception as err:
			print(err)
			if attempts==3:
				print("Could not save Flipper Blackmagic WiFi Settings")
				exit()
			print("Waiting 5 seconds and trying again...")
			time.sleep(5)
			continue
		print(Fore.GREEN+"Flipper Blackmagic Wifi Settings have been saved to ", extraesp32bins+"/Blackmagic/nvs.bin!"+Style.RESET_ALL)
		break
	return

def update_option():
	print("Checking for and deleting the files before replacing them...")
	cwd = os.getcwd()
	for paths in Path(cwd).rglob('ESP32Marauder/*/*'):
		os.remove(paths)
	for paths in Path(cwd).rglob('EvilPortal/*'):
		os.remove(paths)
	os.rmdir('ESP32Marauder/releases')
	os.rmdir('ESP32Marauder')
	os.rmdir('EvilPortal')
	extrarepo = os.path.join(cwd, "Extra_ESP32_Bins")
	repo = Repo(extrarepo)
	repo.git.reset('--hard')
	repo.git.clean('-xdf')
	repo.remotes.origin.pull()
	prereqcheck()
	choose_fw()
	return

prereqcheck()
choose_fw()
