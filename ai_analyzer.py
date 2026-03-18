import json
import requests
import logging
import time
from plyer import notification

# ===================== НАСТРОЙКИ LM STUDIO =====================
LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen3.5-4b"          # ← точное имя твоей модели
ANALYSIS_FILE = "analysis.txt"
REPORT_FILE = "report.json"
CHUNK_SIZE = 50                    # ← Уменьшено с 200 до 50 (чтобы быстрее отвечала)
LAST_CHUNK_FILE = "last_chunk.txt"
TIMEOUT_SECONDS = 600              # ← 5 минут

SYSTEM_PROMPT = """
Ты аналитик ИБ. Кратко проанализируй отрезок лога (события № {start}-{end}):
{chunk_data}

Ответ строго по шаблону:
- Отрезок: события № {start}-{end}
- Оценка: [безопасно/средний риск/высокий риск]
- Объяснение: [1-2 предложения]
- Рекомендации: [1-2 пункта]
"""

def get_last_index():
    try:
        with open(LAST_CHUNK_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def save_last_index(index):
    with open(LAST_CHUNK_FILE, 'w') as f:
        f.write(str(index))

def analyze_report():
    start_time = time.time()
    try:
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        events = report_data.get("events", [])
        total = len(events)
        
        start_idx = get_last_index()
        end_idx = min(start_idx + CHUNK_SIZE, total)
        
        if start_idx >= total and total > 0:
            start_idx = 0
            end_idx = total
        
        chunk = events[start_idx:end_idx]
        chunk_data = json.dumps(chunk, ensure_ascii=False, indent=None)
        
        prompt = SYSTEM_PROMPT.format(start=start_idx+1, end=end_idx, chunk_data=chunk_data)
        
        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Ты строгий аналитик ИБ."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        logging.info(f"Отправка запроса в LM Studio (модель {MODEL})...")
        response = requests.post(LMSTUDIO_URL, json=data, timeout=TIMEOUT_SECONDS)
        
        ai_response = response.json()["choices"][0]["message"]["content"]
        
        with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
            f.write(ai_response)
        
        elapsed = round(time.time() - start_time, 1)
        logging.info(f"✅ AI проанализировал отрезок №{start_idx+1}-{end_idx} за {elapsed} сек")
        
        save_last_index(end_idx)
        
        lower = ai_response.lower()
        if "высокий риск" in lower:
            notification.notify(title="⚠ ВЫСОКИЙ РИСК!", message=f"Отрезок {start_idx+1}-{end_idx}", timeout=12)
        elif "средний риск" in lower:
            notification.notify(title="⚠ Средний риск", message=f"Отрезок {start_idx+1}-{end_idx}", timeout=8)
        else:
            notification.notify(title="✅ Анализ готов", message=f"Отрезок {start_idx+1}-{end_idx}", timeout=6)
        
    except Exception as e:
        logging.error(f"Ошибка AI: {e}")