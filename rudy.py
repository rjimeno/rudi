#!/usr/bin/env python3

import os
import sys
import yaml
import subprocess

CHGRP = "/bin/chgrp "
CHMOD = "/bin/chmod "
CHOWN = "/bin/chown "
DEFAULT_CONF = "rudy.yaml"
DPKG_INSTALL = "/usr/bin/apt-get install -y "
DPKG_AUTOPURGE = "/usr/bin/apt-get remove --auto-remove --purge -y "
MKDIR_P_M = "/bin/mkdir -p -m "
SERVICE = "/usr/sbin/service "
START = " start"
STOP = " stop"


def do_file(file):
    fn = file["base"] + file["name"]
    print("Deploying " + fn + "...")
    os.system(MKDIR_P_M + file["mode"] + " " + file["base"])
    with open(fn, "w") as to_file:
        try:
            to_file.write(file["content"])
        except Exception as w_exc:
            print(w_exc)
            exit(-2)
    os.system(CHOWN + file["owner"] + " " + fn)
    os.system(CHGRP + file["group"] + " " + fn)
    os.system(CHMOD + file["mode"] + " " + fn)
    print("File " + fn + " deployed successfully.")


def converge(data):
    def do_service(service):

        def do_package(package):
            print("Reinstalling " + package + " ...")
            # Run purge then install and check return codes so failures are detected
            purge_cmd = DPKG_AUTOPURGE + package
            install_cmd = DPKG_INSTALL + package

            purge_proc = subprocess.run(purge_cmd, shell=True)
            if purge_proc.returncode != 0:
                # Purge may fail if package not installed; warn but continue
                print(f"Warning: purge command for '{package}' returned exit code {purge_proc.returncode}")

            install_proc = subprocess.run(install_cmd, shell=True)
            if install_proc.returncode != 0:
                print(f"ERROR: Installation of package '{package}' failed (exit code {install_proc.returncode}).")
                # Do not proceed to deploy files for a failed install
                return

            print("Package " + package + " installed successfully.")
            if "Packages" in data and \
                    package in data["Packages"] and \
                    "files" in data["Packages"][package]:
                for f in data["Packages"][package]["files"]:
                    if f in data["Files"]:
                        do_file(data["Files"][f])
                    else:
                        print("\n\nWARNING: File '" + f +
                              "' required by package '" + package +
                              "' was not found amongst Files:.\n\n")

        print("Cycling service " + service + ".")
        os.system(SERVICE + service + STOP)
        for p in data["Services"][service]["packages"]:
            do_package(p)
        os.system(SERVICE + service + START)
        print("Service '" + service + "' is now up & running.")

    if "Services" in data:
        for s in data["Services"]:
            do_service(s)
    if "Evictions" in data:
        print("Removing final packages...")
        os.system(DPKG_AUTOPURGE + " ".join(data["Evictions"]))
        print("Packages removed successfully.")


if '__main__' == __name__:
    input_file = DEFAULT_CONF
    if 2 == len(sys.argv):
        input_file = sys.argv[1]
    elif 2 < len(sys.argv):
        print("\nUsage:\n\n" + sys.argv[0] +
              " [ configuration_file ]  # " + DEFAULT_CONF +
              " if configuration_file is omitted.\n\n", sys.stderr)
        exit(-1)
    with open(input_file, 'r') as stream:
        try:
            yaml_data = yaml.safe_load(stream)
        except yaml.YAMLError as r_exc:
            print(r_exc)
            exit(-2)
    converge(yaml_data)
