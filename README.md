# Easy Flipper Zero Marauder Flash
This is for easily flashing Marauder on an ESP32 or WiFi Devboard for a Flipper Zero!
![Screenshot of EasyInstall](https://raw.githubusercontent.com/SkeletonMan03/FZEasyMarauderFlash/main/EasyInstall_Screenshot.png)

## Windows Users:
You have two prerequisites. 
You must install [Git for Windows from here](https://gitforwindows.org/).  
If you are flashing an ESP32 board, you need to install the [driver from here](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads) in order for your device to be recognized

## It is now simple to install or update Marauder on Linux, Mac OS X, or Windows.
# How to use: 
* Step 0 only has to be ran once. (That doesn't mean it's okay to skip it unless you're running it again after having just used it)
0) run `pip3 install -r requirements.txt`. 
1) Press and hold the `BOOT` button on the module
2) While still holding `BOOT`, connect the devboard or ESP32 board via USB.
3) Press and release the `RESET` button.
4) Release the `BOOT` button. 
5) run `python3 EasyInstall.py`. 
6) Select the option of what you want to do

* Important note: You may need to run this script with `sudo` or as Administrator in Windows   

## This project is based on the Windows Marauder flasher batch script

You can find it [here in UberGuidoZ's repo](https://github.com/UberGuidoZ/Flipper/blob/main/Wifi_DevBoard/FZ_Marauder_Flasher)

## About this script
This script pulls all of its resources from the proper Github repositories in order to make sure you are up-to-date.  
The only dependencies it does not get by itself are the required Python modules and Windows tools.  
This script should work on most devices that can run Python 3 and can access serial ports via USB.  
Thanks to Marauder update v0.10.2 and [Marauder Companion Flipper Zero app](https://github.com/0xchocolate/flipperzero-firmware-with-wifi-marauder-companion/releases) fork/update from [tcpassos](https://github.com/tcpassos) PCAPs can now be directly saved to your Flipper Zero's SD Card!

## Compatible boards
* Flipper Zero WiFi Devboard  
* ESP32-S2 (The ESP32 chip that is on the WiFi Devboard)  
* ESP32-S2-WROVER
* ESP32-WROOM
* ESP32-WROOM D1 Mini 
* ESP32-S3 

## How to connect an ESP32-WROOM, WROVER, etc to the Flipper Zero
ESP32 -> Flipper Zero  
TX0 -> RX  
RX0 -> TX  
GND -> GND  
3v3 -> 3v3  

## Optional parameters
There are now optional parameters
* `-h` or `--help` - Show help
* `-s` or `--serialport` <Serial Port>
For example, if you have a device you know is on `/dev/ttyUSB0`, you could specify it with `python3 EasyInstall.py -s /dev/ttyUSB0` 
* Using this option will skip automatic detection of the serial port and will not try to identify the device
* By using this option, you accept full responsibility in the event that you brick your device and understand that I can't help you fix it

## Issues with flashing?
Here are some steps to try:  
* Ensure you have followed the steps above and installed any necessary prerequisites
* Check that your computer can see the device. In Linux, run `lsusb`, on Mac run `system_profiler SPUSBDataType`, on Windows, open your Device Manager and look for it
* Try a different cable
* Try a different USB port
* Check your permissions. On Linux, you may have to change ownership of the serial port, for example, /dev/ttyUSB0 is typically owned by root, so you may need to run something like `chown user:group /dev/ttyUSB0`
* If you're using Windows, don't use Git Bash, it doesn't work well with this script. Instead, use Powershell, Windows Terminal, or even CMD
* On Windows and Python is acting strange? Uninstall it then re-install it via the Microsoft Store.
* Make sure you're running the latest Python release! If you're on 3.8 when current is 3.11.3 for example, don't bother opening an issue, just upgrade. Don't try to use old stuff.

## TODO:
* Code cleanup.  
* Add more chip compatibility.
* Attempt to accommodate more boards that can be used with Marauder

## Acknowledgements:
Disclaimer: Includes Acknowledgements from the above linked repo from UberGuidoz as this wouldn't exist without the original project
* [justcallmekoko](https://github.com/justcallmekoko/ESP32Marauder) for the AWESOME work in developing Marauder and porting it to the Flipper.
* [0xchocolate](https://github.com/0xchocolate) for the Marauder companion plugin (now in [Unleashed](https://github.com/DarkFlippers/unleashed-firmware) and [RogueMaster](https://github.com/RogueMaster/flipperzero-firmware-wPlugins).)
* [Frog](https://github.com/FroggMaster) For initial scripting under the [Wifi Pentest Tool](https://github.com/FroggMaster/ESP32-Wi-Fi-Penetration-Tool) and inspiring the idea.<br>
* [ImprovingRigmarole](https://github.com/Improving-Rigmarole) Initial (and continued) scripting of the batch Windows Marauder flasher and lots of  testing.<br>
* [UberGuidoZ](https://github.com/UberGuidoZ) Tweaking/Automating Frog's original, continued scripting, development, and testing.
* [L0rd_K0nda](https://github.com/L0rdK0nda) from the Unleashed Flipper Zero Discord for testing this script for me
* [SkeletonMan](https://github.com/SkeletonMan03) Creating this Python flasher in order to try to make a multi-os flasher since the Batch script obviously could not run on Linux or Mac OS X
* [CorbanR](https://github.com/CorbanR) Forking and fixing instructions and adding a requirement needed for Mac OS X
* [dchalm](https://github.com/dchalm) Forking and fixing mistakes I should have noticed. Thank you!
* [Scorp](https://github.com/scorpion44/FZEasyMarauderFlash_ScorpBins) Compiling needed bins to be able to flash to ESP32-WROOM
* [jacklythgoee](https://github.com/jacklythgoee) For getting a knockoff ESP32-WROOM and giving me info to be able to try to detect it so it could be flashed. 
* [Der Skythe](https://github.com/derskythe) For fixing extra quotes I added without noticing and his awesome work on Flipper Zero Firmware
* [seeker7r4c3r](https://github.com/seeker7r4c3r) For adding the VID of the DrB0rk S3 Multiboard
* [aafksab](https://github.com/aafksab) For fixing the Windows bug with the update option that was confusing me
