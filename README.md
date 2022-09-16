# Easy Flipper Zero Marauder Flash
This is for easily flashing Marauder on an ESP32 or WiFi Devboard for a Flipper Zero!
![Screenshot of EasyInstall](https://raw.githubusercontent.com/SkeletonMan03/FZEasyMarauderFlash/main/EasyInstall_Screenshot.png)
## It is now simple to install or update Marauder on Linux, Mac OS X, or Windows.

1) Connect the devboard via USB.
2) Press and hold the `BOOT` button on the module, press and release the `RESET` button.
3) Release the BOOT button.
4) run `pip3 install -r requirements.txt`. 
5) run `python3 EasyInstall.py`. 
6) Select the option of what you want to do

* Important note: You may need to run this script with `sudo`

## This project is based on the Windows Marauder flasher batch script

You can find it [here in UberGuidoZ's repo](https://github.com/UberGuidoZ/Flipper/blob/main/Wifi_DevBoard/FZ_Marauder_Flasher)

## Improvements over the batch script
This script pulls all of its resources from the proper Github repositories in order to make sure you are up-to-date. 
The only dependencies it does not get by itself are the required Python modules


## Acknoledgements:
Disclaimer: Includes Acknowledgements from the above linked repo from UberGuidoz as this wouldn't exist without the original project
* [justcallmekoko](https://github.com/justcallmekoko/ESP32Marauder) for the AWESOME work in developing Marauder and porting it to the Flipper.
* [0xchocolate](https://github.com/0xchocolate) for the Marauder companion plugin (now in [Unleashed](https://github.com/Eng1n33r/flipperzero-firmware) and [RogueMaster](https://github.com/RogueMaster/flipperzero-firmware-wPlugins).)
* [Frog](https://github.com/FroggMaster) For initial scripting under the [Wifi Pentest Tool](https://github.com/FroggMaster/ESP32-Wi-Fi-Penetration-Tool) and inspiring the idea.<br>
* [ImprovingRigmarole](https://github.com/Improving-Rigmarole) Initial (and continued) scripting of the batch Windows Marauder flasher and lots of  testing.<br>
* [UberGuidoZ](https://github.com/UberGuidoZ) Tweaking/Automating Frog's original, continued scripting, development, and testing.
* [L0rd_K0nda](https://github.com/L0rdK0nda) from the Unleashed Flipper Zero Discord for testing this script for me
* [SkeletonMan](https://github.com/SkeletonMan03) Creating this Python flasher in order to try to make a multi-os flasher since the Batch script obviously could not run on Linux or Mac OS X
* [CorbanR](https://github.com/CorbanR) Forking and fixing instructions and adding a requirement needed for Mac OS X
