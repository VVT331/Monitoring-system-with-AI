import psutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log_generator import add_event

# Настройки
IGNORE_C_DRIVE = True

# Глобальные переменные
previous_disks = set()
fs_observers = {}

class FsEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        
        path_lower = event.src_path.lower()
        
        # === ФИЛЬТР НАШИХ СЛУЖЕБНЫХ ФАЙЛОВ ===
        if any(f in path_lower for f in ['report.json', 'analysis.txt', 'last_chunk.txt', 'event_counter.txt']):
            return
        
        # Старые фильтры (системные папки и расширения)
        ignored_dirs = ['\\windows\\', '\\program files', '\\program files (x86)\\', '\\appdata\\', '\\temp\\', '\\tmp\\', '\\$recycle.bin\\', '\\system volume information\\']
        ignored_exts = ['.log', '.tmp', '.swp']
        if any(d in path_lower for d in ignored_dirs) or any(path_lower.endswith(ext) for ext in ignored_exts):
            return
        
        details = f"{event.event_type} {event.src_path}"
        add_event("fs_event", details)

# Функция обновления мониторинга
def update_fs_monitoring():
    global previous_disks, fs_observers
    current_partitions = psutil.disk_partitions()
    current_disks = set(p.mountpoint for p in current_partitions if p.opts != 'cdrom' and p.mountpoint)
    
    new_disks = current_disks - previous_disks
    for disk in new_disks:
        if IGNORE_C_DRIVE and disk.upper() == 'C:\\':
            continue
        details = f"подключен: {disk}"
        add_event("disk_connect", details)
        observer = Observer()
        handler = FsEventHandler()
        observer.schedule(handler, disk, recursive=True)
        observer.start()
        fs_observers[disk] = observer
    
    removed_disks = previous_disks - current_disks
    for disk in removed_disks:
        if IGNORE_C_DRIVE and disk.upper() == 'C:\\':
            continue
        details = f"отключен: {disk}"
        add_event("disk_disconnect", details)
        if disk in fs_observers:
            fs_observers[disk].stop()
            fs_observers[disk].join()
            del fs_observers[disk]
    
    previous_disks = current_disks

def stop_fs_observers():
    global fs_observers
    for observer in list(fs_observers.values()):
        observer.stop()
        observer.join()
    fs_observers.clear()