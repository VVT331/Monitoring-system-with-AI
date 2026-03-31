import json
import requests
import logging
import time
from plyer import notification

# ===================== НАСТРОЙКИ =====================
LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "Qwen3.5-4B-GGUF"
ANALYSIS_FILE = "analysis.txt"
REPORT_FILE = "report.json"
CHUNK_SIZE = 30                    # ← уменьшено для слабого ПК
LAST_CHUNK_FILE = "last_chunk.txt"
TIMEOUT_SECONDS = 800              # ← 10 минут — достаточно даже на слабом ПК

SYSTEM_PROMPT = """
Ты строгий аналитик информационной безопасности. 
Проанализируй последние события из лога (это период последних ~10 минут):

{events_data}

Ответ строго по шаблону:

- Период: последние 10 минут
- Оценка: [безопасно/средний риск/высокий риск]
- Объяснение: [1-2 предложения]
- Рекомендации: [1-2 пункта]
"""

def analyze_report():
    start_time = time.time()
    try:
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        events = report_data.get("events", [])
        recent_events = events[-CHUNK_SIZE:]   # последние 30 событий
        
        events_data = json.dumps(recent_events, ensure_ascii=False, indent=None)
        
        prompt = SYSTEM_PROMPT.format(events_data=events_data)
        
        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Отвечай ТОЛЬКО по шаблону. Никаких размышлений."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        logging.info(f"Отправка на анализ AI: последние {len(recent_events)} событий...")
        response = requests.post(LMSTUDIO_URL, json=data, timeout=TIMEOUT_SECONDS)
        
        ai_response = response.json()["choices"][0]["message"]["content"].strip()
        
        with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
            f.write(ai_response)
        
        elapsed = round(time.time() - start_time, 1)
        logging.info(f"✅ AI проанализировал последние {len(recent_events)} событий за {elapsed} сек")
        
        # Уведомления
        lower = ai_response.lower()
        if "высокий риск" in lower:
            notification.notify(title="⚠ ВЫСОКИЙ РИСК!", message="Обнаружена критическая угроза!", timeout=12)
        elif "средний риск" in lower:
            notification.notify(title="⚠ Средний риск", message="Проверьте систему", timeout=8)
        else:
            notification.notify(title="✅ Анализ готов", message="За последние 10 минут", timeout=6)
        
    except Exception as e:
        logging.error(f"Ошибка AI: {e}")