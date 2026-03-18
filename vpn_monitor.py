import requests
import logging

# Настройки (только для VPN)
HOME_IP = "1111111"  # Замени на реальный IP без VPN
API_URL = "https://api.ipify.org?format=json"

# Функция для получения текущего IP
def get_current_ip():
    try:
        response = requests.get(API_URL, timeout=10)
        return response.json().get('ip')
    except Exception as e:
        logging.error(f"Ошибка получения IP: {e}")
        return None

# Функция для проверки VPN
def check_vpn():
    current_ip = get_current_ip()
    if not current_ip:
        logging.warning("Не удалось получить IP-адрес")
        return "неизвестно"
    
    is_vpn = current_ip != HOME_IP
    status = "активен" if is_vpn else "отключен"
    logging.info(f"Текущий IP: {current_ip} | VPN: {status}")
    return status