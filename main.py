import logging
from usb_monitor import stopFsObservers, updateFsMonitor
from log_generator import generateReport, addEvent, resetLogs
from ai_analyzer import analyzeReport
from vpn_monitor import verificationVPN
from hardware_monitor import monitoringMetric

stopFlag = False

def runMonitor():
    if stopFlag:
        return
    
    logging.info("=== Сбор телеметрии ===")
    
    updateFsMonitor()
    vpnStatus = verificationVPN()
    hardwareData = monitoringMetric()
    
    # Формируем строку с дисками для лога (Решение проблемы №1)
    disksInfo = ", ".join([f"{k}:{v}%" for k, v in hardwareData[2].items()])
    
    addEvent("vpn_check", vpnStatus)
    addEvent("hardware_check", f"CPU: {hardwareData[0]}%, RAM: {hardwareData[1]}%, Диски: [{disksInfo}]")
    
    generateReport(vpnStatus, hardwareData)
    logging.info("=== Данные собраны ===")

def startAiAnalysis():
    if stopFlag:
        return
    logging.info("=== ЗАПУСК АНАЛИЗА AI ===")
    analyzeReport()
    logging.info("=== Анализ AI завершён ===")

def stopMonitoring():
    global stopFlag
    stopFlag = True
    stopFsObservers()
    logging.info("Мониторинг полностью остановлен")