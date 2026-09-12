#!/usr/bin/python3

import glob
import os
import subprocess


NVIDIA_VENDOR_ID = 0x10DE
DISPLAY_CLASS_ID = 0x03


def _read_hex(path):
    try:
        with open(path, "r", encoding="utf-8") as device_file:
            return int(device_file.read().strip(), 16)
    except (OSError, ValueError):
        return None


def _device_description(address, device_id):
    try:
        result = subprocess.run(
            ["lspci", "-s", address],
            capture_output=True,
            check=False,
            text=True,
        )
        description = result.stdout.strip()
        if result.returncode == 0 and ": " in description:
            return description.split(": ", 1)[1]
    except OSError:
        pass

    return "NVIDIA display device (PCI ID 10de:%04x)" % device_id


def detect_nvidia_gpus(sysfs_root="/sys/bus/pci/devices"):
    """Return descriptions for NVIDIA VGA, 3D, and display controllers."""
    devices = []
    for device_path in sorted(glob.glob(os.path.join(sysfs_root, "*"))):
        vendor_id = _read_hex(os.path.join(device_path, "vendor"))
        class_id = _read_hex(os.path.join(device_path, "class"))
        device_id = _read_hex(os.path.join(device_path, "device"))

        if vendor_id != NVIDIA_VENDOR_ID or class_id is None:
            continue
        if class_id >> 16 != DISPLAY_CLASS_ID:
            continue

        address = os.path.basename(device_path)
        devices.append(_device_description(address, device_id or 0))

    return devices
