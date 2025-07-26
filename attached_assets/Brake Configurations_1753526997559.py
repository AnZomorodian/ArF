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
    
    # Brake and speed data
    brake_data = telemetry['Brake']  # 1 when braking, 0 when not
    speed_data = telemetry['Speed']
    
    # Calculate time spent braking (duration of braking)
    braking_duration = brake_data.sum() * (telemetry['Distance'].diff().mean() / speed_data.mean())
    
    # Total lap time in seconds
    lap_time_seconds = fastest_lap['LapTime'].total_seconds()
    
    # Brake efficiency: percentage of time spent braking
    brake_efficiency = (braking_duration / lap_time_seconds) * 100
    
    driver_name = session.get_driver(driver)['LastName'][:3].upper()
    team_name = session.get_driver(driver)['TeamName']
    
    results.append({
        'Driver': driver_name,
        'Brake Efficiency (%)': brake_efficiency,
        'Lap Time (s)': lap_time_seconds,
        'Team': team_name
    })

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Sort the DataFrame by Brake Efficiency
df_results = df_results.sort_values(by='Brake Efficiency (%)', ascending=False)

# Plot the results
plt.figure(figsize=(16, 10), facecolor='black')
ax = plt.gca()
ax.set_facecolor('black')

bars = plt.bar(df_results['Driver'], df_results['Brake Efficiency (%)'], color=[team_colors[team] for team in df_results['Team']])
plt.xlabel('Driver', color='white')
plt.ylabel('Brake Efficiency (%)', color='white')
plt.title(f'{grand_prix} {year} {session_type} Brake Efficiency Comparison', color='white', fontsize=18)
plt.xticks(rotation=45, color='white')
plt.yticks(color='white')
plt.grid(color='gray', linestyle='--', linewidth=0.5, axis='y', alpha=0.7)

# Add the brake efficiency value on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', color='white')

# Add average line
mean_efficiency = df_results['Brake Efficiency (%)'].mean()
plt.axhline(mean_efficiency, color='red', linewidth=1.5, linestyle='--')
plt.text(len(df_results) - 1, mean_efficiency, f'Mean: {mean_efficiency:.2f}', color='red', ha='center', va='bottom')

# Add team names below driver names
for i, (driver, team) in enumerate(zip(df_results['Driver'], df_results['Team'])):
    plt.text(i, -2, team, ha='center', va='top', color='white', fontsize=10, rotation=45)

# Add description text below the plot
plt.figtext(0.5, -0.1, f"Data obtained from fastest lap telemetry in the {year} {grand_prix} GP race session using FAST F1 library", wrap=True, horizontalalignment='center', fontsize=12, color='white')
plt.figtext(0.5, -0.15, "The plot shows the percentage of time each driver spent braking during their fastest lap", wrap=True, horizontalalignment='center', fontsize=10, color='white')

# Update and enlarge watermark
plt.figtext(0.5, 0.5, 'F1 DATA IQ', fontsize=70, color='gray', ha='center', va='center', alpha=0.5, rotation=45)

# Display the plot
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit description text
plt.show()
