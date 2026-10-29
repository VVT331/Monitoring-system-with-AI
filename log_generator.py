import json
import logging
import time
from collections import deque

MAX_EVENTS = 100
REPORT_FILE = "report.json"
COUNTER_FILE = "event_counter.txt"
eventQueue = deque(maxlen=MAX_EVENTS)
lastEventId = 0

def resetLogs():
    global lastEventId
    lastEventId = 0
    eventQueue.clear()
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"report_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'), "events": []}, f, indent=4)
    
    with open(COUNTER_FILE, 'w') as f:
        f.write("0")
        
    logging.info("✅ Логи и счётчик ID сброшены")

def addEvent(eventType, details):
    global lastEventId
    lastEventId += 1
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    event = {
        "id": lastEventId,
        "timestamp": timestamp,
        "type": eventType,
        "details": details
    }
    
    eventQueue.append(event)
    logging.info(f"Событие #{lastEventId}: {eventType} - {details}")

def generateReport(vpnStatus, hardwareData):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    report = {
        "report_timestamp": timestamp,
        "vpn": vpnStatus,
        "hardware": {
            "cpu": hardwareData[0],
            "ram": hardwareData[1],
            "cpu_temp": hardwareData[3],
            "disks": hardwareData[2]
        },
        "events": list(eventQueue)
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Отчёт обновлён ({len(eventQueue)} событий)")