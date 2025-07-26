import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import cm

# ==============================
# تنظیمات و مقادیر پیش‌فرض
# ==============================

DEFAULT_YEAR = 2024
DEFAULT_GRAND_PRIX = 'Canada'
DEFAULT_SESSION_TYPE = 'R'  # Race

# ==============================
# توابع کمکی
# ==============================

def load_session_data(year, grand_prix, session_type):
    """Load the F1 session data."""
    session = ff1.get_session(year, grand_prix, session_type)
    session.load()
    return session

def calculate_tire_performance(session):
    """Calculate tire performance metrics for all drivers."""
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

        # Metrics calculation
        speed_data = telemetry['Speed']
        acceleration_data = speed_data.diff() / telemetry['Distance'].diff()
        braking_data = telemetry['Brake']

        # Tire Stress Index (Speed * Acceleration * Braking Factor)
        braking_factor = braking_data.mean()  # 1: Constant braking, 0: No braking
        tire_stress_index = (speed_data * acceleration_data.abs()).mean() * (1 + braking_factor)

        # Tire Temperature (Simulated using Speed and Braking)
        tire_temperature = speed_data.mean() * (1 + braking_factor) * 0.1  # Example scaling

        # Tire Efficiency
        tire_efficiency = speed_data.mean() / (1 + tire_stress_index)

        # Tire Wear Index
        tire_wear_index = tire_stress_index * 0.8 + braking_factor * 0.2

        driver_name = session.get_driver(driver)['LastName'][:3].upper()
        results.append({
            'Driver': driver_name,
            'Tire Stress Index': tire_stress_index,
            'Tire Temperature': tire_temperature,
            'Tire Efficiency': tire_efficiency,
            'Tire Wear Index': tire_wear_index
        })

    return pd.DataFrame(results)

# ==============================
# توابع رسم نمودارها
# ==============================

def plot_tire_performance(df_tires, grand_prix, year):
    """Plot tire performance analysis charts."""
    fig, axs = plt.subplots(2, 2, figsize=(18, 12), facecolor='black')
    fig.suptitle(f'{grand_prix} {year} Tire Performance Analysis', color='white', fontsize=18, y=0.96)

    # اضافه کردن واترمارک
    fig.text(0.5, 0.5, 'F1 DATA IQ', fontsize=70, color='white', ha='center', va='center', alpha=0.55)

    # تنظیم رنگ‌بندی محور‌ها
    for ax in axs.flatten():
        ax.set_facecolor('black')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(colors='white')

    # Tire Stress Index
    axs[0, 0].bar(df_tires['Driver'], df_tires['Tire Stress Index'], color=cm.plasma(df_tires['Tire Stress Index'] / df_tires['Tire Stress Index'].max()))
    axs[0, 0].set_title('Tire Stress Index', color='white', fontsize=12)
    axs[0, 0].set_xlabel('', color='white', fontsize=10)
    axs[0, 0].set_ylabel('Stress Index', color='white', fontsize=10)
    axs[0, 0].axhline(df_tires['Tire Stress Index'].mean(), color='red', linestyle='--', label='Mean')
    axs[0, 0].legend(facecolor='black', edgecolor='white', fontsize=8)

    # Tire Temperature
    axs[0, 1].bar(df_tires['Driver'], df_tires['Tire Temperature'], color=cm.inferno(df_tires['Tire Temperature'] / df_tires['Tire Temperature'].max()))
    axs[0, 1].set_title('Tire Temperature', color='white', fontsize=12)
    axs[0, 1].set_xlabel('', color='white', fontsize=10)
    axs[0, 1].set_ylabel('Temperature (°C)', color='white', fontsize=10)
    axs[0, 1].axhline(df_tires['Tire Temperature'].mean(), color='red', linestyle='--', label='Mean')
    axs[0, 1].legend(facecolor='black', edgecolor='white', fontsize=8)

    # Tire Efficiency
    axs[1, 0].bar(df_tires['Driver'], df_tires['Tire Efficiency'], color=cm.Greens(df_tires['Tire Efficiency'] / df_tires['Tire Efficiency'].max()))
    axs[1, 0].set_title('Tire Efficiency', color='white', fontsize=12)
    axs[1, 0].set_xlabel('', color='white', fontsize=10)
    axs[1, 0].set_ylabel('Efficiency', color='white', fontsize=10)
    axs[1, 0].axhline(df_tires['Tire Efficiency'].mean(), color='red', linestyle='--', label='Mean')
    axs[1, 0].legend(facecolor='black', edgecolor='white', fontsize=8)

    # Tire Wear Index
    axs[1, 1].bar(df_tires['Driver'], df_tires['Tire Wear Index'], color=cm.Purples(df_tires['Tire Wear Index'] / df_tires['Tire Wear Index'].max()))
    axs[1, 1].set_title('Tire Wear Index', color='white', fontsize=12)
    axs[1, 1].set_xlabel('', color='white', fontsize=10)
    axs[1, 1].set_ylabel('Wear Index', color='white', fontsize=10)
    axs[1, 1].axhline(df_tires['Tire Wear Index'].mean(), color='red', linestyle='--', label='Mean')
    axs[1, 1].legend(facecolor='black', edgecolor='white', fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.show()

# ==============================
# اجرای اصلی برنامه
# ==============================

session = load_session_data(DEFAULT_YEAR, DEFAULT_GRAND_PRIX, DEFAULT_SESSION_TYPE)
df_tires = calculate_tire_performance(session)

# نمایش نمودارها
plot_tire_performance(df_tires, DEFAULT_GRAND_PRIX, DEFAULT_YEAR)
