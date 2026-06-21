import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from src.ai_analyst import get_ai_prediction_data
from src.data_loader import load_and_filter_alerts, clean_and_transform
from src.processing import extract_time_features

st.set_page_config(page_title="UA Alerts Strategic Map", layout="wide", page_icon="🛡️")

# Кешування гео-даних
@st.cache_data
def load_geojson(filename):
    geojson_path = os.path.join("data", "raw", filename)
    with open(geojson_path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def get_data():
    raw_path = os.path.join("data", "raw", "official_data_uk.csv")
    df = load_and_filter_alerts(raw_path)
    df = clean_and_transform(df)
    df = extract_time_features(df)
    return df

st.title("🛡️ Ситуаційний центр повітряних тривог України (2026)")
st.markdown("---")

try:
    df = get_data()

    # --- БІЧНА ПАНЕЛЬ (ФІЛЬТРИ) ---
    st.sidebar.header("Налаштування моніторингу")
    
    # 1. Вибір рівня деталізації мапи
    map_level = st.sidebar.radio(
        "Рівень деталізації мапи:",
        options=["Області (Регіони)", "Нові райони (136)"]
    )
    
    # 2. Мультиселект областей для фільтрації графіків
    all_oblasts = sorted(df['oblast'].unique())
    selected_oblasts = st.sidebar.multiselect(
        "Фільтр за областями для часових графіків:",
        options=all_oblasts,
        default=[]  # Якщо порожньо — показуємо всю Україну
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 Налаштування AI")
    # Поле типу password приховає символи кружечками
    api_key_input = st.sidebar.text_input("Введіть OpenRouter API Key:", type="password")
    
    # Застосовуємо гео-фільтр до загального датасету
    filtered_df = df[df['oblast'].isin(selected_oblasts)] if selected_oblasts else df

    # --- СЕКЦІЯ KPI МЕТРИК ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всього інцидентів у вибірці", f"{len(filtered_df):,}")
    with col2:
        top_reg = filtered_df.groupby('oblast').size().reset_index(name='c').sort_values('c', ascending=False).iloc[0]
        st.metric("Найбільш активна область", top_reg['oblast'])
    with col3:
        avg_dur = filtered_df['duration_min'].mean()
        st.metric("Сер. тривалість тривоги", f"{avg_dur:.1f} хв")

    # --- СЕКЦІЯ ГЕОПРОСТОРОВОГО АНАЛІЗУ ---
    st.markdown(f"### Географія загроз: рівень {map_level}")
    
    if map_level == "Області (Регіони)":
        geojson_data = load_geojson("regiony.geojson")
        
        # Агрегуємо дані по областях
        oblast_map_data = df.groupby('oblast').size().reset_index(name='count')
        
        # Робимо копію оригінальних назв
        oblast_map_data['map_name'] = oblast_map_data['oblast']
        
        # Єдина можлива розбіжність — Київ. Перевіримо, як він у GeoJSON.
        # Якщо мапа злетить, а Києва не буде — за потреби розкоментуй рядок нижче:
        # oblast_map_data['map_name'] = oblast_map_data['map_name'].replace({'м. Київ': 'Київська область'})
        
        fig_map = px.choropleth(
            oblast_map_data,
            geojson=geojson_data,
            locations='map_name',             # Використовуємо чисті оригінальні назви
            featureidkey="properties.region",   # Ключ 'region' з твого GeoJSON
            color='count',
            color_continuous_scale="Reds",
            range_color=(0, oblast_map_data['count'].max()),
            labels={'count': 'Кількість тривог'},
            projection="mercator"
        )
        
    else:  # Рівень районів
        geojson_data = load_geojson("rayony.geojson")
        raion_alerts = df[df['raion'] != 'Вся область'].copy()
        raion_map_data = raion_alerts.groupby('raion').size().reset_index(name='count')
        
        fig_map = px.choropleth(
            raion_map_data,
            geojson=geojson_data,
            locations='raion',
            featureidkey="properties.rayon",
            color='count',
            color_continuous_scale="YlOrRd",
            projection="mercator"
        )

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # --- ЧАСОВІ ГРАФІКИ (ВРАХОВУЮТЬ ФІЛЬТР З СЛАЙДБАРУ) ---
    st.markdown("### Часова аналітика для обраної вибірки")
    c1, c2 = st.columns(2)
    with c1:
        hourly_data = filtered_df.groupby('hour').size().reset_index(name='count')
        fig_h = px.bar(hourly_data, x='hour', y='count', title="Розподіл за годинами доби",
                       color='count', color_continuous_scale='Viridis')
        st.plotly_chart(fig_h, use_container_width=True)
    with c2:
        daily_data = filtered_df.groupby('date').size().reset_index(name='count')
        fig_d = px.line(daily_data, x='date', y='count', title="Динаміка інтенсивності за часом")
        fig_d.update_traces(line_color='#e74c3c')
        st.plotly_chart(fig_d, use_container_width=True)

        # --- НОВА СЕКЦІЯ: ГЛИБОКА АНАЛІТИКА ---
    st.markdown("---")
    
    col_dur, col_days = st.columns(2)

    with col_dur:
        st.markdown("#### Топ-10 областей за сумарним часом (год)")
        # Групуємо, сумуємо хвилини та переводимо в години
        dur_data = filtered_df.groupby('oblast')['duration_min'].sum().reset_index()
        dur_data['duration_hours'] = dur_data['duration_min'] / 60
        dur_data = dur_data.sort_values('duration_hours', ascending=True).tail(10) # Беремо топ-10 для зручності

        fig_dur = px.bar(
            dur_data, 
            x='duration_hours', 
            y='oblast', 
            orientation='h',
            color='duration_hours',
            color_continuous_scale='Reds',
            labels={'duration_hours': 'Сумарно годин', 'oblast': 'Область'}
        )
        fig_dur.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_dur, use_container_width=True)

    with col_days:
        st.markdown("#### Розподіл тривог за днями тижня")
        
        # 1. Рахуємо кількість тривог для кожного дня
        days_count = filtered_df['day_name'].value_counts().reset_index()
        days_count.columns = ['day_name', 'count']
        
        # 2. Правильний порядок українських днів, щоб графік йшов від Пн до Нд
        ukr_order = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд']
        
        # Встановлюємо категоріальний тип для правильного сортування на графіку
        days_count['day_name'] = pd.Categorical(days_count['day_name'], categories=ukr_order, ordered=True)
        days_count = days_count.sort_values('day_name')

        # 3. Будуємо графік
        fig_days = px.bar(
            days_count, 
            x='day_name', 
            y='count',
            color='count',
            color_continuous_scale='Blues',
            labels={'day_name': 'День тижня', 'count': 'Кількість тривог'}
        )
        fig_days.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_days, use_container_width=True)


# --- СЕКЦІЯ AI ПРОГНОЗУВАННЯ (ГРАФІЧНА) ---
    st.markdown("---")
    st.markdown("### 🔮 Математичний AI-прогноз ризиків на наступні 24 години")
    
    current_location = selected_oblasts[0] if selected_oblasts else "Україна (загальний зріз)"
    
    if st.button("📊 Розрахувати ймовірність загрози по годинах"):
        with st.spinner("Нейромережа прораховує математичну модель ризиків..."):
            total_alerts = len(filtered_df)
            
            if total_alerts > 0:
                top_hour = filtered_df['hour'].mode()[0] if not filtered_df['hour'].empty else 0
                top_day = filtered_df['day_name'].mode()[0] if not filtered_df['day_name'].empty else "Невідомо"
                avg_duration = filtered_df['duration_min'].mean()
                
                # Отримуємо DataFrame від AI
                forecast_df = get_ai_prediction_data(
                region_name=current_location,
                total_alerts=total_alerts,
                top_hour=top_hour,
                top_day=top_day,
                avg_duration=avg_duration,
                custom_api_key=api_key_input
)
                
                if forecast_df is not None and not forecast_df.empty:
                    # Будуємо красиву лінійну діаграму з областями (Area chart)
                    fig_forecast = px.area(
                        forecast_df, 
                        x='hour', 
                        y='probability',
                        title=f"Ймовірність початку тривоги протягом доби для: {current_location}",
                        labels={'hour': 'Година доби', 'probability': 'Шанс атаки (%)'},
                        markers=True
                    )
                    
                    fig_forecast.update_traces(line_color='#e74c3c', fillcolor='rgba(231, 76, 60, 0.2)')
                    fig_forecast.update_yaxes(range=[0, 100])
                    fig_forecast.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
                    
                    st.plotly_chart(fig_forecast, use_container_width=True)
            else:
                st.warning("Немає даних для моделювання.")

except Exception as e:
    st.error(f"Помилка інтерфейсу: {e}")