import pandas as pd

def extract_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Додає нові часові ознаки до датасету для подальшого аналізу часових рядів.
    """
    print("Генерація часових ознак...")
    df_features = df.copy()
    
    # ВИПРАВЛЕННЯ: додаємо utc=True, щоб Pandas спочатку звів усе до UTC,
    # а потім конвертуємо назад у Europe/Kyiv, щоб зберегти правильний місцевий час
    df_features['started_at'] = pd.to_datetime(df_features['started_at'], utc=True).dt.tz_convert('Europe/Kyiv')
    
    # Витягуємо часові компоненти
    df_features['date'] = df_features['started_at'].dt.date
    df_features['month'] = df_features['started_at'].dt.month
    df_features['day_of_week'] = df_features['started_at'].dt.dayofweek  # 0 = Понеділок, 6 = Неділя
    df_features['hour'] = df_features['started_at'].dt.hour
    
    # Назва дня тижня
    days_mapping = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Нд'}
    df_features['day_name'] = df_features['day_of_week'].map(days_mapping)
    
    # Ознака вихідного дня
    df_features['is_weekend'] = df_features['day_of_week'].isin([5, 6]).astype(int)
    
    return df_features