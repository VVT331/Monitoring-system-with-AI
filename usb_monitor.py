import psutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log_generator import addEvent

# Настройки
IGNORE_C_DRIVE = True

# Глобальные переменные
previousDisks = set()
fsObservers = {}

class FsEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        
        path_lower = event.src_path.lower()
        
        # Фильтр служебных файлов программы
        if any(f in path_lower for f in ['report.json', 'analysis.txt', 'last_chunk.txt', 'event_counter.txt']):
            return
        
        # Фильтр системных папок и расширений
        ignoredDirs = [
            '\\windows\\', 
            '\\program files', 
            '\\program files (x86)\\', 
            '\\appdata\\', 
            '\\temp\\', 
            '\\tmp\\', 
            '\\$recycle.bin\\', 
            '\\system volume information\\'
        ]
        ignoredExts = ['.log', '.tmp', '.swp']
        
        if any(d in path_lower for d in ignoredDirs) or any(path_lower.endswith(ext) for ext in ignoredExts):
            return
        
        details = f"{event.event_type} {event.src_path}"
        addEvent("fs_event", details)

def updateFsMonitor():
    global previousDisks, fsObservers
    
    try:
        currentPartitions = psutil.disk_partitions()
        currentDisks = set(p.mountpoint for p in currentPartitions if p.opts != 'cdrom' and p.mountpoint)
    except Exception as e:
        logging.error(f"Ошибка получения списка дисков: {e}")
        return

    newDisks = currentDisks - previousDisks
    for disk in newDisks:
        if IGNORE_C_DRIVE and disk.upper() == 'C:\\':
            continue
        
        details = f"подключен: {disk}"
        addEvent("disk_connect", details)
        
        try:
            observer = Observer()
            handler = FsEventHandler()
            observer.schedule(handler, disk, recursive=True)
            observer.start()
            fsObservers[disk] = observer
            logging.info(f"🔌 Наблюдатель запущен: {disk}")
        except Exception as e:
            logging.error(f"Не удалось запустить наблюдатель для {disk}: {e}")

    removedDisks = previousDisks - currentDisks
    for disk in removedDisks:
        if IGNORE_C_DRIVE and disk.upper() == 'C:\\':
            continue
            
        details = f"отключен: {disk}"
        addEvent("disk_disconnect", details)
        
        if disk in fsObservers:
            try:
                fsObservers[disk].stop()
                fsObservers[disk].join()
                del fsObservers[disk]
                logging.info(f"🔌 Наблюдатель остановлен: {disk}")
            except Exception as e:
                logging.error(f"Ошибка остановки наблюдателя {disk}: {e}")

    previousDisks = currentDisks

def stopFsObservers():
    global fsObservers
    for disk, observer in list(fsObservers.items()):
        try:
            observer.stop()
            observer.join(timeout=2)
        except Exception as e:
            logging.error(f"Ошибка при остановке наблюдателя {disk}: {e}")
    fsObservers.clear()