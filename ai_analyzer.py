import json
import requests
import logging
import time
from plyer import notification

# НАСТРОЙКИ (CamelCase для переменных)
LMStudioUrl = "http://localhost:1234/v1/chat/completions"
model = "Qwen3.5-4B-GGUF"
analysisFile = "analysis.txt"
reportFile = "report.json"
chunkSize = 30
timeoutSeconds = 800

systemPrompt = """
Ты строгий аналитик информационной безопасности.
Проанализируй последние события из лога (это период последних ~10 минут):
{eventsData}
Ответ строго по шаблону:
Период: последние 10 минут
Оценка: [безопасно/средний риск/высокий риск]
Объяснение: [1-2 предложения]
Рекомендации: [1-2 пункта]
"""

def analyzeReport():
    startTime = time.time()
    try:
        with open(reportFile, 'r', encoding='utf-8') as f:
            reportData = json.load(f)

        events = reportData.get("events", [])
        recentEvents = events[-chunkSize:]

        eventsData = json.dumps(recentEvents, ensure_ascii=False, indent=None)

        prompt = systemPrompt.format(eventsData=eventsData)

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Отвечай ТОЛЬКО по шаблону. Никаких размышлений."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        logging.info(f"Отправка на анализ AI: последние {len(recentEvents)} событий...")
        response = requests.post(LMStudioUrl, json=data, timeout=timeoutSeconds)

        aiResponse = response.json()["choices"][0]["message"]["content"].strip()

        with open(analysisFile, 'w', encoding='utf-8') as f:
            f.write(aiResponse)

        elapsed = round(time.time() - startTime, 1)
        logging.info(f"✅ AI проанализировал последние {len(recentEvents)} событий за {elapsed} сек")

        # Уведомления
        lower = aiResponse.lower()
        if "высокий риск" in lower:
            notification.notify(title=" ВЫСОКИЙ РИСК!", message="Обнаружена критическая угроза!", timeout=12)
        elif "средний риск" in lower:
            notification.notify(title="⚠ Средний риск", message="Проверьте систему", timeout=8)
        else:
            notification.notify(title="✅ Анализ готов", message="За последние 10 минут", timeout=6)

    except Exception as e:
        logging.error(f"Ошибка AI: {e}")