import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import cm

# ==============================
# تنظیمات اولیه
# ==============================
ff1.Cache.clear_cache()  # پاک‌سازی کش برای اطمینان از داده‌های به‌روز
DEFAULT_YEAR = 2024
DEFAULT_GRAND_PRIX = 'Canada'
DEFAULT_SESSION_TYPE = 'R'  # Race

# ==============================
# توابع تحلیل و محاسبه
# ==============================

def load_session_data(year, grand_prix, session_type):
    """Load the F1 session data."""
    session = ff1.get_session(year, grand_prix, session_type)
    session.load()
    return session

def calculate_driver_stress_index(session):
    """Calculate a Driver Stress Index (DSI) for all drivers."""
    drivers = session.drivers
    results = []

    for driver in drivers:
        driver_laps = session.laps.pick_driver(driver)
        fastest_lap = driver_laps.pick_fastest()

        if fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
            continue

        try:
            telemetry = fastest_lap.get_car_data().add_distance()
        except KeyError:
            continue

        # تحلیل بخش‌های کلیدی
        speed_data = telemetry['Speed']
        brake_data = telemetry['Brake']
        throttle_data = telemetry['Throttle']
        distance_data = telemetry['Distance']

        # بهبودهای جدید:
        # 1. محاسبه دقیق‌تر طول مسیر و فاصله برای تحلیل تنش
        total_distance = distance_data.max() - distance_data.min()

        # 2. وزن‌دهی شتاب‌گیری و ترمزگیری بر اساس طول مسیر
        braking_weighted = (brake_data.sum() * (distance_data.diff().mean())) / total_distance * 100
        high_throttle_weighted = (len(throttle_data[throttle_data > 90]) * distance_data.diff().mean()) / total_distance * 100

        # 3. استفاده از میانه سرعت در مقاطع بحرانی
        critical_speed_median = speed_data[(brake_data > 0) | (throttle_data > 90)].median()

        # شاخص تنش راننده
        stress_index = (braking_weighted + (100 - high_throttle_weighted)) / critical_speed_median

        driver_name = session.get_driver(driver)['LastName'][:3].upper()
        team_name = session.get_driver(driver)['TeamName']

        results.append({
            'Driver': driver_name,
            'Team': team_name,
            'Braking %': braking_weighted,
            'High Throttle %': high_throttle_weighted,
            'Critical Speed Median (km/h)': critical_speed_median,
            'Driver Stress Index': stress_index
        })

    return pd.DataFrame(results)

# ==============================
# توابع رسم نمودار
# ==============================

def plot_stress_index(df_stress_index, grand_prix, year):
    """Plot Driver Stress Index with critical metrics and enhanced UI."""
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='black')
    ax.set_facecolor('black')
    fig.suptitle(f'{grand_prix} {year} - Driver Stress Index', color='white', fontsize=20, y=0.92)

    # افزودن واترمارک
    fig.text(0.5, 0.5, 'F1 DATA IQ', fontsize=80, color='white', ha='center', va='center', alpha=0.2)

    # Bar Chart: Driver Stress Index
    colors = cm.plasma(df_stress_index['Driver Stress Index'] / df_stress_index['Driver Stress Index'].max())
    bars = ax.bar(df_stress_index['Driver'], df_stress_index['Driver Stress Index'], color=colors)

    # Customize appearance
    ax.set_title('Driver Stress Index Analysis', color='white', fontsize=16, pad=10)
    ax.set_xlabel('Driver', color='white', fontsize=12)
    ax.set_ylabel('Stress Index', color='white', fontsize=12)
    ax.tick_params(axis='x', colors='white', rotation=45, labelsize=10)
    ax.tick_params(axis='y', colors='white', labelsize=10)
    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

    # Annotate bars with critical metrics
    for bar, critical_speed in zip(bars, df_stress_index['Critical Speed Median (km/h)']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{critical_speed:.1f} km/h', ha='center', va='bottom', fontsize=9, color='yellow')

    # اضافه کردن میانگین خط
    mean_value = df_stress_index['Driver Stress Index'].mean()
    ax.axhline(mean_value, color='red', linestyle='--', linewidth=1, label=f'Mean: {mean_value:.2f}')
    ax.legend(facecolor='black', edgecolor='white', fontsize=10)

    # اضافه کردن جزئیات بصری بیشتر
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('driver_stress_index_enhanced.png', dpi=300, facecolor=fig.get_facecolor())
    plt.show()

# ==============================
# اجرای اصلی
# ==============================

# بارگذاری داده‌ها
session = load_session_data(DEFAULT_YEAR, DEFAULT_GRAND_PRIX, DEFAULT_SESSION_TYPE)

# محاسبه تنش راننده
df_stress_index = calculate_driver_stress_index(session)
df_stress_index = df_stress_index.sort_values(by='Driver Stress Index', ascending=False)

# نمایش جدول نتایج
print(df_stress_index)

# رسم نمودار
plot_stress_index(df_stress_index, DEFAULT_GRAND_PRIX, DEFAULT_YEAR)
