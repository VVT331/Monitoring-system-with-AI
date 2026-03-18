import json
import logging
import time
from collections import deque

MAX_EVENTS = 100
REPORT_FILE = "report.json"
COUNTER_FILE = "event_counter.txt"

event_queue = deque(maxlen=MAX_EVENTS)

# === НОВАЯ ФУНКЦИЯ: Сброс при запуске ===
def reset_logs():
    global last_event_id
    last_event_id = 0
    event_queue.clear()
    
    # Очищаем report.json
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"report_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'), "events": []}, f, indent=4)
    
    # Сбрасываем счётчик
    with open(COUNTER_FILE, 'w') as f:
        f.write("0")
    
    logging.info("✅ Логи и счётчик ID сброшены (ID начинается с 1)")

last_event_id = 0

def add_event(event_type, details):
    global last_event_id
    last_event_id += 1
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    event = {
        "id": last_event_id,
        "timestamp": timestamp,
        "type": event_type,
        "details": details
    }
    
    event_queue.append(event)
    logging.info(f"Событие добавлено: #{last_event_id} | {event_type} - {details}")

def generate_report(vpn_status, hardware_data):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    report = {
        "report_timestamp": timestamp,
        "vpn": vpn_status,
        "hardware": {
            "cpu": hardware_data[0],
            "ram": hardware_data[1],
            "cpu_temp": hardware_data[3],
            "disks": hardware_data[2]
        },
        "events": list(event_queue)
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    logging.info(f"Отчёт обновлён ({len(event_queue)} событий)")