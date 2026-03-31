import logging
from usb_monitor import stop_fs_observers
from log_generator import generate_report, add_event, reset_logs
from ai_analyzer import analyze_report
from vpn_monitor import check_vpn
from hardware_monitor import monitor_hardware
from usb_monitor import update_fs_monitoring

stop_flag = False

def run_monitor():
    if stop_flag:
        return
    logging.info("=== Сбор телеметрии ===")
    update_fs_monitoring()
    vpn_status = check_vpn()
    hardware_data = monitor_hardware()
    
    add_event("vpn_check", vpn_status)
    add_event("hardware_check", f"CPU: {hardware_data[0]}%, RAM: {hardware_data[1]}%")
    
    generate_report(vpn_status, hardware_data)
    logging.info("=== Данные собраны ===")

def start_ai_analysis():
    if stop_flag:
        return
    logging.info("=== === ЗАПУСК АНАЛИЗА AI (каждые 10 минут) === ===")
    analyze_report()
    logging.info("=== Анализ AI завершён ===")

def stop_monitoring():
    global stop_flag
    stop_flag = True
    stop_fs_observers()
    logging.info("Мониторинг полностью остановлен")