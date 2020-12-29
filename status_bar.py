#!/usr/bin/env python

# TODO:
#       2. make the status bar able to receive commands
#       3. make a dmenu script which lets you take a short note like an IP address for thm
#          for example and show the note when a command is entered.

import sys
import re
import subprocess
import datetime
import time
import signal
import datetime

BATTERY_FULL =          "\uf240"
BATTERY_THREE_QUARTER = "\uf241"
BATTERY_HALF =          "\uf242"
BATTERY_QUARTER =       "\uf243"
BATTERY_EMPTY =         "\uf244"
BATTERY_CHARGING =      "\uf584"

WIFI_ON = "\ufaa8"
WIFI_OFF = "\ufaa9"

def get_network_interfaces():
    cmd_output = subprocess.run("ip a".split(" "), capture_output=True).stdout.decode("utf-8")
    cmd_lines = cmd_output.split("\n")
    interfaces = {}
    for line in cmd_lines:
        if line != '':
            if line[0].isdigit():
                current_key = line[:2]
                interfaces.update({current_key: [line]})
            else:
                interfaces[current_key].append(line)
    res = {}
    for value in interfaces.values():
        interface = re.findall(r"\d: (.*):", value[0])
        ip = re.findall(r"inet (\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3})", "\n".join(value))
        if interface and ip:
            res[interface[0]] = ip[0]
    return res

def get_battery_status():
    # get the current battery status
    try:
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
    except FileNotFoundError as e:
        return None, None

def get_cur_time():
    # get the current time
    t = datetime.datetime.now()
    t = t.strftime("%d.%m.%y %H:%M")
    return t

def get_wireless_state():
    interfaces = get_network_interfaces()
    wlan_interface = [i for i in interfaces.keys() if i.startswith("wl")]
    if wlan_interface != []:
        wlan_interface = wlan_interface[0]
        with open(f"/sys/class/net/{wlan_interface}/operstate", "r") as f:
            w_state = f.read().strip()
        if w_state == "up":
            return (w_state, WIFI_ON)
    return (w_state, WIFI_OFF)

def get_vpn_state():
    interfaces = get_network_interfaces()
    vpn_interface = [i for i in interfaces.keys() if i.startswith("tun")]
    if vpn_interface != []:
        vpn_interface = vpn_interface[0]
        return (vpn_interface, interfaces[vpn_interface])
    return None, None

def mk_status_bar_string():
    t = get_cur_time()
    battery_percentage, battery_glyph = get_battery_status()
    wifi_state, wifi_glyph = get_wireless_state()
    vpn_interface, vpn_address = get_vpn_state()

    time_block = f" {t} "
    battery_block = f" {battery_glyph}  {battery_percentage}% " if battery_percentage is not None else ""
    wifi_block = f" {wifi_glyph} {wifi_state} "
    vpn_block = f" {vpn_interface}: {vpn_address} " if vpn_interface is not None else ""

    # DEBUG
    with open("/home/patrick/log", "a") as log:
        log.write(f"VPN: \"{vpn_block}\"\n")
    # DEBUG


    status_bar_string = "|".join([vpn_block, wifi_block, battery_block, time_block])
    return status_bar_string

def print_status_output(string):
    # set the output of the "status bar"
    p = subprocess.Popen(["xsetroot", "-name", string], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate()


def kill_sig_handler(signal, frame):
    # Handle a SIGINT or SIGTERM gracefully by setting the status text
    # to: "no status input"
    print_status_output("no status output")
    sys.exit(0)

def sigusr1_sig_handler(signal, frame):
    status = mk_status_bar_string()
    print_status_output(status)

    # DEBUG
    with open("/home/patrick/log", "a") as log:
        log.write(f"SIGUSR1 handled\n{datetime.datetime.today()}\n{status}\n")
    # DEBUG

signal.signal(signal.SIGINT, kill_sig_handler)
signal.signal(signal.SIGTERM, kill_sig_handler)
signal.signal(signal.SIGUSR1, sigusr1_sig_handler)

while True:
    status = mk_status_bar_string()
    print_status_output(status)
    time.sleep(30)

