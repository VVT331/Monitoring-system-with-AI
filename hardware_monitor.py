import psutil
import logging

def monitoringMetric():
    cpuUsage = psutil.cpu_percent(interval=1)
    ramUsage = psutil.virtual_memory().percent

    disks = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint).percent
            disks[partition.mountpoint] = usage
        except PermissionError:
            disks[partition.mountpoint] = "нет доступа"

    cpuTemp = "не доступно"
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            cpuTemps = [t.current for t in temps['coretemp'] if t.current is not None]
            cpuTemp = sum(cpuTemps) / len(cpuTemps) if cpuTemps else "не доступно"
        elif 'cpu_thermal' in temps:
            cpuTemp = temps['cpu_thermal'][0].current if temps['cpu_thermal'] else "не доступно"
    except (AttributeError, PermissionError):
        pass

    return cpuUsage, ramUsage, disks, cpuTemp