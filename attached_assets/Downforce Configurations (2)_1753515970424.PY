import fastf1 as ff1
import matplotlib.pyplot as plt
import pandas as pd

# Define team colors (example colors, you might need to adjust them based on real team colors)
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
    
    speed_data = telemetry['Speed']
    
    average_speed = speed_data.mean()
    top_speed = speed_data.max()
    
    result = 100 * (average_speed / top_speed)
    
    driver_name = session.get_driver(driver)['LastName'][:3].upper()
    team_name = session.get_driver(driver)['TeamName']
    
    results.append({
        'Driver': driver_name,
        'Average Speed': average_speed,
        'Top Speed': top_speed,
        'Result': result,
        'Team': team_name
    })

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Sort the DataFrame by the Result column
df_results = df_results.sort_values(by='Result', ascending=False)

# Plot the results
plt.figure(figsize=(14, 9), facecolor='black')
ax = plt.gca()
ax.set_facecolor('black')

bars = plt.bar(df_results['Driver'], df_results['Result'], color=[team_colors[team] for team in df_results['Team']])
plt.xlabel('Driver', color='white')
plt.ylabel('Result', color='white')
plt.title(f'{grand_prix} {year} {session_type}', color='white')
plt.xticks(rotation=45, color='white')
plt.yticks(color='white')
plt.grid(color='gray', linestyle='--', linewidth=0.5, axis='y', alpha=0.7)

# Add the result value on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.2f}', ha='center', va='bottom', color='white')

# Add average line
mean_result = df_results['Result'].mean()
plt.axhline(mean_result, color='red', linewidth=1.5, linestyle='--')
plt.text(len(df_results) - 1, mean_result, f'Mean: {mean_result:.2f}', color='red', ha='center', va='bottom')

# Add team names below driver names
for i, (driver, team) in enumerate(zip(df_results['Driver'], df_results['Team'])):
    plt.text(i, -2, team, ha='center', va='top', color='white', fontsize=8, rotation=45)

# Add description text below the plot
plt.figtext(0.5, -0.15, f"Data obtained from fastest lap telemetry in the {year} {grand_prix} GP race session using FAST F1 library", wrap=True, horizontalalignment='center', fontsize=10, color='white')
plt.figtext(0.5, -0.2, "The plot shows the 100 * (Average Speed Of Fastest Lap / Top Speed Reached On Fastest Lap) for each driver", wrap=True, horizontalalignment='center', fontsize=10, color='white')

# Add watermark
plt.figtext(0.95, 0.05, 'F1 DATA IQ', fontsize=30, color='gray', ha='right', va='bottom', alpha=0.5, rotation=30)

# Display the plot
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit description text
plt.show()
