import pandas as pd

def load_and_filter_alerts(file_path: str) -> pd.DataFrame:
    """
    Завантажує датасет повітряних тривог та фільтрує його, 
    залишаючи дані лише з 1 січня 2026 року.
    """
    print("Починаємо завантаження даних...")
    
    # Оскільки файл великий, ми можемо читати його частинами (chunks) 
    # або завантажити повністю, якщо дозволяє RAM, але з правильним парсингом дат.
    df = pd.read_csv(
        file_path,
        parse_dates=['started_at', 'finished_at'],
        low_memory=False
    )
    
    print("Початкова фільтрація за датою (з 2026-01-01)...")
    # Відсікаємо все, що було до 2026 року
    df_2026 = df[df['started_at'] >= '2026-01-01'].copy()
    
    print(f"Завантажено {len(df_2026)} записів для 2026 року.")
    return df_2026

def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Базова очистка та конвертація таймзон.
    """
    print("Конвертація таймзон у Europe/Kyiv...")
    # Переводимо UTC в київський час
    df['started_at'] = df['started_at'].dt.tz_convert('Europe/Kyiv')
    df['finished_at'] = df['finished_at'].dt.tz_convert('Europe/Kyiv')
    
    print("Розрахунок тривалості тривог...")
    # Рахуємо тривалість в хвилинах
    df['duration_min'] = (df['finished_at'] - df['started_at']).dt.total_seconds() / 60.0
    
    # Заповнюємо пусті значення в географії для уникнення проблем з NaN
    df['raion'] = df['raion'].fillna('Вся область')
    df['hromada'] = df['hromada'].fillna('Весь район')
    
    return df