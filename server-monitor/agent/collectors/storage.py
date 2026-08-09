import os
import json
import subprocess
from typing import Dict, Any, List

def run_command(cmd: List[str]) -> str:
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""

def get_smart_health(device_path: str) -> Dict[str, Any]:
    """
    Executes smartctl -a -j /dev/sdX to retrieve SMART health status and temperature.
    Returns status "Not supported" or "Unavailable" if smartctl fails or device doesn't support SMART.
    """
    cmd = ["sudo", "smartctl", "-a", "-j", device_path]
    output = run_command(cmd)
    if not output:
        cmd = ["smartctl", "-a", "-j", device_path]
        output = run_command(cmd)

    if output:
        try:
            data = json.loads(output)
            smart_status = "PASSED" if data.get("smart_status", {}).get("passed", False) else "FAILED"
            if "smart_status" not in data and "smartctl" in data and not data["smartctl"].get("exit_status", 0):
                smart_status = "PASSED"
            
            temp_celsius = None
            if "temperature" in data and "current" in data["temperature"]:
                temp_celsius = data["temperature"]["current"]
            elif "ata_smart_attributes" in data and "table" in data["ata_smart_attributes"]:
                for attr in data["ata_smart_attributes"]["table"]:
                    if attr.get("name") == "Temperature_Celsius":
                        temp_celsius = attr.get("raw", {}).get("value")

            return {
                "smart_supported": True,
                "health": smart_status,
                "temperature_celsius": temp_celsius if temp_celsius is not None else "Unavailable"
            }
        except Exception:
            pass

    return {
        "smart_supported": False,
        "health": "Not supported",
        "temperature_celsius": "Unavailable"
    }

def get_lvm_info() -> Dict[str, Any]:
    """
    Gathers LVM physical volumes, volume groups, and logical volumes.
    """
    pvs, vgs, lvs = [], [], []

    pvs_raw = run_command(["sudo", "pvs", "--reportformat", "json"]) or run_command(["pvs", "--reportformat", "json"])
    if pvs_raw:
        try:
            pvs = json.loads(pvs_raw).get("report", [{}])[0].get("pv", [])
        except Exception:
            pass

    vgs_raw = run_command(["sudo", "vgs", "--reportformat", "json"]) or run_command(["vgs", "--reportformat", "json"])
    if vgs_raw:
        try:
            vgs = json.loads(vgs_raw).get("report", [{}])[0].get("vg", [])
        except Exception:
            pass

    lvs_raw = run_command(["sudo", "lvs", "--reportformat", "json"]) or run_command(["lvs", "--reportformat", "json"])
    if lvs_raw:
        try:
            lvs = json.loads(lvs_raw).get("report", [{}])[0].get("lv", [])
        except Exception:
            pass

    return {
        "physical_volumes": pvs,
        "volume_groups": vgs,
        "logical_volumes": lvs
    }

def get_storage_info() -> Dict[str, Any]:
    """
    Automatically discovers physical disks (HDD, SSD, NVMe, USB), partitions, filesystems,
    inodes, LVM structure, and SMART health.
    """
    disks: List[Dict[str, Any]] = []
    partitions: List[Dict[str, Any]] = []

    # Parse physical disks and partitions via lsblk
    lsblk_output = run_command(["lsblk", "-b", "--json", "-o", "NAME,MODEL,SERIAL,SIZE,TYPE,ROTA,TRAN,MOUNTPOINT,FSTYPE"])
    if lsblk_output:
        try:
            block_devices = json.loads(lsblk_output).get("blockdevices", [])
            for dev in block_devices:
                dev_type = dev.get("type", "").lower()
                name = dev.get("name", "")
                dev_path = f"/dev/{name}"
                
                # Check rotational: 1 -> HDD, 0 -> SSD / NVMe
                rota = dev.get("rota", True)
                tran = dev.get("tran", "").lower() if dev.get("tran") else ""
                media_type = "NVMe" if "nvme" in name or tran == "nvme" else ("HDD" if rota else "SSD")
                if tran == "usb":
                    media_type = f"USB ({media_type})"

                smart_info = get_smart_health(dev_path) if dev_type == "disk" else {"smart_supported": False, "health": "N/A", "temperature_celsius": "Unavailable"}

                disk_entry = {
                    "device": dev_path,
                    "name": name,
                    "model": dev.get("model") or "Unknown Disk",
                    "serial": dev.get("serial") or "N/A",
                    "size_bytes": dev.get("size", 0),
                    "type": media_type,
                    "rotational": rota,
                    "transport": tran or "sata/internal",
                    "smart_health": smart_info["health"],
                    "temperature_celsius": smart_info["temperature_celsius"],
                    "partitions_count": len(dev.get("children", []))
                }
                if dev_type == "disk":
                    disks.append(disk_entry)

        except Exception:
            pass

    # Read mount points and inode usage via df -P -B1 and df -i
    df_data: Dict[str, Dict[str, Any]] = {}
    df_bytes = run_command(["df", "-P", "-B1"])
    if df_bytes:
        lines = df_bytes.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                fs, total, used, avail, pct, mount = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                try:
                    df_data[mount] = {
                        "filesystem": fs,
                        "total_bytes": int(total),
                        "used_bytes": int(used),
                        "available_bytes": int(avail),
                        "usage_percent": float(pct.rstrip("%")),
                        "inodes_total": 0,
                        "inodes_used": 0,
                        "inodes_percent": 0.0
                    }
                except Exception:
                    pass

    df_inodes = run_command(["df", "-P", "-i"])
    if df_inodes:
        lines = df_inodes.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                mount = parts[5]
                if mount in df_data:
                    try:
                        df_data[mount]["inodes_total"] = int(parts[1])
                        df_data[mount]["inodes_used"] = int(parts[2])
                        df_data[mount]["inodes_percent"] = float(parts[4].rstrip("%"))
                    except Exception:
                        pass

    for mount, data in df_data.items():
        partitions.append({
            "mount_point": mount,
            "filesystem": data["filesystem"],
            "total_bytes": data["total_bytes"],
            "used_bytes": data["used_bytes"],
            "available_bytes": data["available_bytes"],
            "usage_percent": data["usage_percent"],
            "inodes_total": data["inodes_total"],
            "inodes_used": data["inodes_used"],
            "inodes_percent": data["inodes_percent"]
        })

    lvm_info = get_lvm_info()

    return {
        "disks": disks,
        "partitions": partitions,
        "lvm": lvm_info
    }
