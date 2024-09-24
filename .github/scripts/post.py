#!/usr/bin/env python
#
# Python code which automatically posts Message in a Telegram Group if any new update is found.
# Intended to be run on every push
# USAGE : python3 post.py
# See README for more.
#
# Copyright (C) 2024 PrajjuS <theprajjus@gmail.com>
#
# Credits: Ashwin DS <astroashwin@outlook.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import telebot
import os
import json
import datetime
from time import sleep

# Get configs from workflow secrets
def getConfig(config_name: str):
    return os.getenv(config_name)
try:
    BOT_TOKEN = getConfig("BOT_TOKEN")
    CHAT_ID = getConfig("CHAT_ID")
except KeyError:
    print("Fill all the configs plox..\nExiting...")
    exit(0)

BANNER_PATH = "./assets/banner.png"

# Init bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# File directories
jsonDir = {
    "Gapps": "builds/Gapps",
    "Vanilla": "builds/Vanilla"
} 
idDir = ".github/scripts"

# Store IDs in a file to compare
def update(IDs):
    with open(f"{idDir}/file_ids.txt", "w+") as log:
        for ids in IDs:
            log.write(f"{str(ids)}\n")

# Return IDs of all latest files from json files
def get_new_id():
    files = []
    file_id = []
    for type, dirName in jsonDir.items():
        for all in os.listdir(dirName):
            if all.endswith('.json'):
                files.append({"type": type, "dir": dirName, "file": all})
    for all_files in files:
        with open(f"{all_files['dir']}/{all_files['file']}", "r") as file:
            data = json.loads(file.read())['response'][0]
            file_id.append(data['md5'])
    return file_id

# Return previous IDs
def get_old_id():
    old_id = []
    with open(f"{idDir}/file_ids.txt", "r") as log:
        for ids in log.readlines():
            old_id.append(ids.replace("\n", ""))
    return old_id

# Remove elements in 2nd list from 1st, helps to find out which device got an update
def get_diff(new_id, old_id):
    first_set = set(new_id)
    sec_set = set(old_id)
    return list(first_set - sec_set)

# Grab needed info using ID of the file
def get_info(ID):
    files = []
    for type, dirName in jsonDir.items():
        for all in os.listdir(dirName):
            if all.endswith('.json'):
                files.append({"type": type, "dir": dirName, "file": all})
    for all_files in files:
        with open(f"{all_files['dir']}/{all_files['file']}", "r") as file:
            data = json.loads(file.read())['response'][0]
            if data['md5'] == ID:
                device = all_files['file']
                build_type = all_files['type']
                break
    with open(f"{jsonDir[build_type]}/{device}") as device_file:
        info = json.loads(device_file.read())['response'][0]
        EUCLID_VERSION = info['version']
        OEM = info['oem']
        DEVICE_NAME = info['device']
        DEVICE_CODENAME = device.split('.')[0]
        MAINTAINER = info['maintainer']
        DATE_TIME = datetime.datetime.fromtimestamp(int(info['timestamp']))
        FILENAME = info['filename']
        DOWNLOAD_URL = info['download']
        BUILD_TYPE = info['buildtype']
        SIZE = round(int(info['size'])/1000000000, 2)
        MD5 = info['md5']
        SHA256 = info['sha256']
        XDA = info['forum']
        TELEGRAM = info['telegram']
        msg = ""
        msg += f"Euclid-OS {EUCLID_VERSION}\n"
        msg += f"Device Name: {OEM} {DEVICE_NAME} ({DEVICE_CODENAME})\n"
        msg += f"Maintainer: {MAINTAINER}\n"
        msg += f"Date Time: {DATE_TIME}\n"
        # msg += f"Download URL: {DOWNLOAD_URL}\n"
        msg += f"Build Type: {BUILD_TYPE}\n"
        msg += f"Size: {SIZE}G\n"
        msg += f"MD5: {MD5}\n"
        msg += f"SHA256: {SHA256}\n"
        msg += f"XDA: {XDA}\n"
        msg += f"Telegram: {TELEGRAM}\n\n"
        print(msg)
        return {
            "version": EUCLID_VERSION,
            "oem": OEM,
            "device_name": DEVICE_NAME,
            "codename": DEVICE_CODENAME,
            "maintainer": MAINTAINER,
            "datetime": DATE_TIME,
            "filename": FILENAME,
            "download": DOWNLOAD_URL,
            "buildtype": BUILD_TYPE,
            "size": SIZE,
            "md5": MD5,
            "sha256": SHA256,
            "xda": XDA,
            "telegram": TELEGRAM
        }

# Prepare function for posting message in channel
def send_post(chat_id, image, caption):
    return bot.send_photo(chat_id=chat_id, photo=image, caption=caption)

# Prepare message format for channel
def message_content(information):
    msg = ""
    msg += f"<b>EuclidOS {information['version']} - OFFICIAL | Android 14</b>\n"
    msg += f"<b>📲 :</b> <b>{information['oem']} {information['device_name']}</b> <b>(</b><code>{information['codename']}</code><b>)</b>\n"
    msg += f"<b>👤 :</b> <a href='https://t.me/{information['maintainer']}'>{information['maintainer']}</a>\n"
    msg += f"<b>🗓 :</b> <code>{information['datetime']} UTC</code>\n\n"
    msg += f"<b>▪️ Build Variant:</b> <code>{information['buildtype']}</code>\n"
     # Change changelog links based on build type
    if information['build_type'] == "Gapps":
        msg += f"<b>▪️ Changelog:</b> <a href='https://raw.githubusercontent.com/euclid-Devices/vendor_euclidOTA/14/changelogs.md'>Source</a> <b>|</b> <a href='https://raw.githubusercontent.com/euclid-Devices/vendor_euclidOTA/14/changelogs/Gapps/{information['''codename''']}.txt'>Device</a>\n"
    else:  # Assume it's Vanilla
        msg += f"<b>▪️ Changelog:</b> <a href='https://raw.githubusercontent.com/euclid-Devices/vendor_euclidOTA/14/changelogs.md'>Source</a> <b>|</b> <a href='https://raw.githubusercontent.com/euclid-Devices/vendor_euclidOTA/14/changelogs/Vanilla/{information['''codename''']}.txt'>Device</a>\n"
    msg += f"<b>▪️ Download:</b> <a href='{information['download']}'>Here</a>\n\n"
    msg += f"<b>▪️ Rom Support:</b> <a href='https://t.me/euclidoschat'>Here</a>\n"
    msg += f"<b>▪️ Device Support:</b> <a href='{information['telegram']}'>Here</a>\n"
    msg += f"\n#euclidOS #{information['codename']} #Android14 #Official"
    return msg

# Send updates to channel and commit changes in repo
def tg_message():
    commit_message = "Update new IDs and push OTA"
    commit_description = "Data for following device(s) were changed:\n"
    if len(get_diff(get_new_id(), get_old_id())) == 0:
        print("All are Updated\nNothing to do\nExiting...")
        sleep(2)
        exit(1)
    else:
        print(f"IDs Changed:\n{get_diff(get_new_id(), get_old_id())}\n\n")
        for devices in get_diff(get_new_id(), get_old_id()):
            info = get_info(devices)
            with open(BANNER_PATH, "rb") as image:
                send_post(CHAT_ID, image, message_content(info))
            commit_description += f"- {info['device_name']} ({info['codename']})\n"
            sleep(5)
    update(get_new_id())
    open("commit_mesg.txt", "w+").write(f"EuclidOTA: {commit_message} [BOT]\n\n{commit_description}")

# Final stuffs
tg_message()
print("Successful")
sleep(2)
