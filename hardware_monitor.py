import psutil
import logging

# Функция для мониторинга hardware
def monitor_hardware():
    cpu_usage = psutil.cpu_percent(interval=1)  # % CPU
    ram_usage = psutil.virtual_memory().percent  # % RAM
    
    # Диски: % использования для каждого
    disks = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint).percent
            disks[partition.mountpoint] = usage
        except PermissionError:
            disks[partition.mountpoint] = "нет доступа"
    
    # Температура: с try-except
    cpu_temp = "не доступно"
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            cpu_temps = [t.current for t in temps['coretemp'] if t.current is not None]
            cpu_temp = sum(cpu_temps) / len(cpu_temps) if cpu_temps else "не доступно"
        elif 'cpu_thermal' in temps:
            cpu_temp = temps['cpu_thermal'][0].current if temps['cpu_thermal'] else "не доступно"
    except (AttributeError, PermissionError):
        pass
    
    return cpu_usage, ram_usage, disks, cpu_temp