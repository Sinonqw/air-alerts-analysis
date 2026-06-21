import json
from openai import OpenAI
import pandas as pd
import streamlit as st

def get_ai_prediction_data(region_name, total_alerts, top_hour, top_day, avg_duration, custom_api_key):
    """
    Отримує статистичні дані та повертає DataFrame з погодинним прогнозом ймовірності.
    """

    if not custom_api_key:
        st.error("Будь ласка, введіть ваш OpenRouter API Key у боковому меню (сайдбарі)!")
        return None
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=custom_api_key, # Використовуємо переданий ключ
    )
    system_prompt = (
        "Ти — математичний модуль прогнозування повітряних загроз. Твоє завдання — розрахувати "
        "ймовірність (від 0% до 100%) тривоги для кожної з наступних 24 годин на основі статистики. "
        "Поверни ВИКЛЮЧНО валідний JSON-масив без жодного тексту чи markdown-обгорток. "
        "Формат: [{\"hour\": 0, \"probability\": 15}, ...]"
    )

    user_prompt = f"""
    Локація: {region_name}
    Історичні дані за 2026 рік:
    - Всього тривог: {total_alerts}
    - Пік активності: {top_hour}:00
    - Найгірший день: {top_day}
    - Сер. тривалість: {avg_duration:.1f} хв.
    """

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Очищення від можливих обгорток ```json ... ```
        if raw_content.startswith("```"):
            raw_content = raw_content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if raw_content.startswith("json"):
                raw_content = raw_content[4:].strip()

        data = json.loads(raw_content)
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Помилка всередині модуля AI: {e}")
        return None