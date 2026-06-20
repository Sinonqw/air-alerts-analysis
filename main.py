import os
from src.data_loader import load_and_filter_alerts, clean_and_transform

def main():
    # Шлях до нашого сирого файлу
    raw_data_path = os.path.join("data", "raw", "official_data_uk.csv")
    
    if not os.path.exists(raw_data_path):
        print(f"Помилка: Файл не знайдено за шляхом {raw_data_path}")
        print("Будь ласка, перевірте, чи правильно ви назвали та поклали CSV-файл.")
        return

    # 1. Завантаження та фільтрація
    df_2026 = load_and_filter_alerts(raw_data_path)
    
    # 2. Очищення та трансформація
    df_cleaned = clean_and_transform(df_2026)
    
    # 3. Перевірка результату (Первинний аналіз)
    print("\n" + "="*50)
    print("БАЗОВА СТАТИСТИКА ДАТАСЕТУ ЗА 2026 РІК:")
    print("="*50)
    print(f"Загальна кількість записів про тривоги: {len(df_cleaned)}")
    print(f"Часовий діапазон: з {df_cleaned['started_at'].min()} по {df_cleaned['finished_at'].max()}")
    print("\nРозподіл за рівнями тривоги (level):")
    print(df_cleaned['level'].value_counts())
    print("\nТоп-5 областей за кількістю записів:")
    print(df_cleaned['oblast'].value_counts().head(5))
    print("="*50 + "\n")
    
    # Збережемо проміжний результат, щоб не парсити гігантський файл щоразу
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    processed_path = os.path.join(processed_dir, "alerts_2026_processed.csv")
    print(f"Зберігаємо очищені дані у {processed_path}...")
    df_cleaned.to_csv(processed_path, index=False)
    print("Збереження завершено успішно!")

if __name__ == "__main__":
    main()