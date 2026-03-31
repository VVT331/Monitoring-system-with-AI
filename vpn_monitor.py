import requests
import logging

# Настройки
HOME_IP = "111.111.111.111"          # Корреной IP
API_URLS = [
    "https://api.ipify.org?format=json",
    "https://api.ipapi.is/?format=json",   # запасной сервис
]

def get_current_ip():
    for url in API_URLS:
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                ip = data.get('ip') or data.get('ipAddress')
                if ip:
                    logging.info(f"Получен IP от {url}: {ip}")
                    return ip
        except Exception as e:
            logging.warning(f"Не удалось получить IP от {url}: {e}")
            continue
    logging.error("Не удалось получить IP ни от одного сервиса")
    return None

def check_vpn():
    current_ip = get_current_ip()
    if not current_ip:
        logging.warning("Не удалось получить текущий IP-адрес")
        return "неизвестно"
    
    # Сравниваем с домашним IP
    is_vpn_active = current_ip != HOME_IP
    
    status = "активен" if is_vpn_active else "отключен"
    
    logging.info(f"Текущий IP: {current_ip} | Домашний IP: {HOME_IP} | VPN: {status}")
    
    return status