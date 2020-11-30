#!/usr/bin/env python

import sys
import subprocess
import datetime
import time
import signal

WIRELESS_DEVICE_NAME = "wlp1s10"

BATTERY_FULL =          "\uf240"
BATTERY_THREE_QUARTER = "\uf241"
BATTERY_HALF =          "\uf242"
BATTERY_QUARTER =       "\uf243"
BATTERY_EMPTY =         "\uf244"
BATTERY_CHARGING =      "\uf584"

WIFI_ON = "\ufaa8"
WIFI_OFF = "\ufaa9"

def get_battery_status():
    # get the current battery status

    with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
        battery_percentage = f.read().strip()

    with open("/sys/class/power_supply/BAT0/status", "r") as f:
        r = f.read().strip()
        charging = True if r == "Charging" else False

    if charging:
        return (battery_percentage, BATTERY_CHARGING)

    if int(battery_percentage) >= 75:
        return (battery_percentage, BATTERY_FULL)

    if int(battery_percentage) >= 50:
        return (battery_percentage, BATTERY_THREE_QUARTER)

    if int(battery_percentage) >= 25:
        return (battery_percentage, BATTERY_HALF)

    if int(battery_percentage) >= 5:
        return (battery_percentage, BATTERY_QUARTER)

    if int(battery_percentage) < 5:
        return (battery_percentage, BATTERY_EMPTY)

def get_cur_time():
    # get the current time
    t = datetime.datetime.now()
    t = t.strftime("%d.%m.%y %H:%M")
    return t

def get_wireless_state():
    # get the state of wls1
    with open(f"/sys/class/net/{WIRELESS_DEVICE_NAME}/operstate", "r") as f:
        w_state = f.read().strip()
    if w_state == "up":
        return (w_state, WIFI_ON)
    return (w_state, WIFI_OFF)



def sig_handler(signal, frame):
    # Handle a SIGINT or SIGTERM gracefully by setting the status text
    # to: "no status input"

    p = subprocess.Popen(["xsetroot", "-name", "no status input"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

while True:

    wireless_state, wifi_glyph = get_wireless_state()
    t = get_cur_time()


    output_str = f" {wifi_glyph}  {wireless_state} | {t}"

    # set the output of the "status bar"
    p = subprocess.Popen(["xsetroot", "-name", output_str], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()
    time.sleep(30)
