#!/usr/bin/env python3
import subprocess
import time
import os

import logging

# Path pattern to block (corresponds to arguments for: xdotool search)
xdotool_search_args = ['--classname', '^crx_haiffjcadagjlijoggckpgfnoeiflnem$']

# Write a backup that can restore the settings at the
# start of the script.
# Leave empty to not write a backup.
backupfile = "~/.keymap_backup"

# Add the keys to be disabled below.
shortcuts = {
    "org.cinnamon.desktop.keybindings.wm/close": "gsettings",
    "org.cinnamon.desktop.keybindings.wm/switch-group": "gsettings",
    "org.cinnamon.desktop.keybindings.wm/switch-windows": "gsettings",
    "org.cinnamon.desktop.keybindings.wm/activate-window-menu": "gsettings",
    "org.cinnamon.desktop.keybindings.wm/show-desktop": "gsettings",
    "org.cinnamon.desktop.keybindings.media-keys/logout": "gsettings",
}

#
# Helper functions
#

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
LOG = logging.getLogger(__name__)


# Run a command on the shell
def run(cmd):
    subprocess.Popen(cmd)


# Run a command on the shell and return the
# stripped result
def get(cmd):
    try:
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        if "invalid Window parameter" in output:
            LOG.info("command %s returned error", " ".join(cmd))
            LOG.error(output)
        return output
    except:
        return ""


# Get the PID of the currently active window
def getactive():
    xdoid = get(["xdotool", "getactivewindow"])
    if xdoid:
        return xdoid

    # Something went wrong
    LOG.warning("Could not obtain id of current window; xdoid(xdotool getactivewindow)=%s", xdoid)
    return ""


def readkey(key):
    if shortcuts[key] == "gsettings":
        return get(["gsettings", "get"] + key.split("/"))
    elif shortcuts[key] == "dconf":
        return get(["dconf", "read", key])


def writekey(key, val):
    if val == "":
        val = "['']"
    if shortcuts[key] == "gsettings":
        run(["gsettings", "set"] + key.split("/") + [val])
    elif shortcuts[key] == "dconf":
        run(["dconf", "write", key, val])


def resetkey(key):
    if shortcuts[key] == "gsettings":
        run(["gsettings", "reset"] + key.split("/"))
    elif shortcuts[key] == "dconf":
        run(["dconf", "reset", key])


# If val == True, disables all shortcuts.
# If val == False, resets all shortcuts.
def setkeys(flag):
    for key, val in shortcutmap.items():
        if flag == True:
            # Read current value again; user may change
            # settings, after all!
            shortcutmap[key] = readkey(key)
            writekey(key, "")
        elif flag == False:
            if val:
                writekey(key, val)
            else:
                resetkey(key)


#
# Main script
#

# Store current shortcuts in case they are non-default
# Note: if the default is set, dconf returns an empty string!
# Optionally, create a backup script to restore the value in case
# this script crashes at an inopportune time.
shortcutmap = {}
if backupfile:
    f = open(os.path.expanduser(backupfile), 'w+')
    f.write('#!/bin/sh\n')

for key, val in shortcuts.items():
    if shortcuts[key] == "gsettings":
        shortcutmap[key] = get(["gsettings", "get"] + key.split("/"))

        if backupfile:
            if shortcutmap[key]:
                f.write("gsettings set " + " ".join(key.split("/")) + " " +
                        shortcutmap[key] + "\n")
            else:
                f.write("gsettings reset " + " ".join(key.split("/")) + "\n")
    elif shortcuts[key] == "dconf":
        shortcutmap[key] = get(["dconf", "read", key])

        if backupfile:
            if shortcutmap[key]:
                f.write("dconf write " + key + " " + shortcutmap[key] + "\n")
            else:
                f.write("dconf reset " + key + "\n")

if backupfile: f.close()

# Check every half second if the window changed form or to a
# matching application.
front1 = None
while True:
    time.sleep(0.5)

    checkpids = get(["xdotool", "search"] + xdotool_search_args)

    if checkpids:
        checkpids = checkpids.splitlines()
        activepid = getactive()

        if activepid:
            front2 = True if activepid in checkpids else False
        else:
            front2 = False
    else:
        front2 = False

    if front2 != front1:
        if front2:
            LOG.info("Requested app gained focus, disabling shortcuts")
            setkeys(True)
        else:
            LOG.info("Requested app lost focus, enabling shortcuts")
            setkeys(False)
    front1 = front2
