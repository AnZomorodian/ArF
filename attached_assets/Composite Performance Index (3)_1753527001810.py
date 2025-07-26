import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd

# Define team colors
team_colors = {
    'Mercedes': '#00D2BE',
    'Red Bull Racing': '#1E41FF',
    'Ferrari': '#DC0000',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'AlphaTauri': '#4E7C9B',
    'Aston Martin': '#006F62',
    'Williams': '#005AFF',
    'Alfa Romeo': '#900000',
    'RB': '#6692FF',
    'Kick Sauber': '#52E252',
    'Haas F1 Team': '#FFFFFF'
}

# Load the session data
year = 2024
grand_prix = 'Canada'
session_type = 'R'  # Race session

session = ff1.get_session(year, grand_prix, session_type)
session.load()

# Get all drivers
drivers = session.drivers

# Create a DataFrame to store results
results = []

for driver in drivers:
    driver_laps = session.laps.pick_driver(driver)
    fastest_lap = driver_laps.pick_fastest()
    
    if fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
        print(f"Skipping driver {driver} due to invalid DriverNumber")
        continue
    
    try:
        telemetry = fastest_lap.get_car_data().add_distance()
    except KeyError as e:
        print(f"Skipping driver {driver} due to KeyError: {e}")
        continue
    
    # Speed, acceleration and brake data
    brake_data = telemetry['Brake']  # 1 when braking, 0 when not
    speed_data = telemetry['Speed']
    acceleration_data = speed_data.diff() / telemetry['Distance'].diff()  # Basic acceleration calculation
    
    # Calculate time spent braking (duration of braking)
    braking_duration = brake_data.sum() * (telemetry['Distance'].diff().mean() / speed_data.mean())
    
    # Total lap time in seconds
    lap_time_seconds = fastest_lap['LapTime'].total_seconds()
    
    # Brake efficiency: percentage of time spent braking
    brake_efficiency = (braking_duration / lap_time_seconds) * 100
    
    # Speed factor
    speed_factor = speed_data.mean()
    
    # Acceleration factor
    acceleration_factor = acceleration_data[acceleration_data > 0].mean()  # Acceleration (positive changes in speed)
    
    # Handling time (time spent at speeds lower than a threshold, indicating cornering)
    handling_threshold = speed_data.mean() * 0.7  # Assuming cornering happens at 70% of the average speed
    handling_time = len(speed_data[speed_data < handling_threshold]) * (telemetry['Distance'].diff().mean() / speed_data.mean())
    
    # Composite Performance Index
    composite_performance_index = (speed_factor * acceleration_factor) / (brake_efficiency + handling_time)
    
    driver_name = session.get_driver(driver)['LastName'][:3].upper()
    team_name = session.get_driver(driver)['TeamName']
    
    results.append({
        'Driver': driver_name,
        'Composite Performance Index': composite_performance_index,
        'Speed Factor': speed_factor,
        'Acceleration Factor': acceleration_factor,
        'Brake Efficiency (%)': brake_efficiency,
        'Handling Time (s)': handling_time,
        'Lap Time (s)': lap_time_seconds,
        'Team': team_name
    })

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Sort the DataFrame by Composite Performance Index
df_results = df_results.sort_values(by='Composite Performance Index', ascending=False)

# Plot the results
fig, ax = plt.subplots(figsize=(16, 10), facecolor='black')
ax.set_facecolor('black')

# Bar chart for Composite Performance Index
bars = plt.bar(df_results['Driver'], df_results['Composite Performance Index'], color=[team_colors[team] for team in df_results['Team']])
plt.xlabel('Driver', color='white', fontsize=12)
plt.ylabel('Composite Performance Index', color='white', fontsize=12)

# Adjust title placement to be closer to the top
plt.title(f'{grand_prix} {year} {session_type} - Composite Performance Index', color='white', fontsize=20, pad=20)
plt.xticks(rotation=45, color='white', fontsize=10)
plt.yticks(color='white', fontsize=10)
plt.grid(color='gray', linestyle='--', linewidth=0.5, axis='y', alpha=0.7)

# Add the composite performance index value on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', color='white')

# Add average line for composite performance index
mean_performance = df_results['Composite Performance Index'].mean()
plt.axhline(mean_performance, color='red', linewidth=1.5, linestyle='--')
plt.text(len(df_results) - 1, mean_performance, f'Mean: {mean_performance:.2f}', color='red', ha='center', va='bottom')

# Add team names below driver names
for i, (driver, team) in enumerate(zip(df_results['Driver'], df_results['Team'])):
    plt.text(i, -2, team, ha='center', va='top', color='white', fontsize=10, rotation=45)

# Display the calculation formula at the bottom of the plot
plt.figtext(0.5, 0.85, "Composite Performance Index = (Speed Factor * Acceleration Factor) / (Brake Efficiency + Handling Time)", wrap=True, horizontalalignment='center', fontsize=12, color='white')

# Update and enlarge watermark
plt.figtext(0.5, 0.5, 'F1 DATA IQ', fontsize=70, color='gray', ha='center', va='center', alpha=0.3, rotation=45)

# Display the plot
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit description text
plt.show()
