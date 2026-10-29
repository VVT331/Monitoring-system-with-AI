import requests
import logging

# Настройки
ipHome = "192.168.172.1" #Замените на ваш реальный домашний IP
apiUrls = [
    "https://api.ipify.org?format=json",
    "https://api.ipapi.is/?format=json",   # запасной сервис
]

def getCurrentIp():
    for url in apiUrls:
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

def verificationVPN():
    currentIp = getCurrentIp()
    if not currentIp:
        logging.warning("Не удалось получить текущий IP-адрес")
        return "неизвестно"
    
    # Сравниваем с домашним IP
    activeVPN = currentIp != ipHome
    status = "активен" if activeVPN else "отключен"
    
    logging.info(f"Текущий IP: {currentIp} | Домашний IP: {ipHome} | VPN: {status}")
    return status