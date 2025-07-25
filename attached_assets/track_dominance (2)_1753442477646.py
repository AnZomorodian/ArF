import fastf1
from fastf1 import plotting
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.filedialog import asksaveasfilename
import os
import matplotlib.font_manager as fm
from scipy.interpolate import interp1d

# DARK MODE & FONT
KALAMEH_FONT_NAME = "Kalameh"
font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
kalameh_path = None
for path in font_paths:
    if "Kalameh" in os.path.basename(path):
        kalameh_path = path
        break

if kalameh_path:
    plt.rcParams['font.family'] = KALAMEH_FONT_NAME
    fm.fontManager.addfont(kalameh_path)
else:
    plt.rcParams['font.family'] = 'sans-serif'

plt.style.use('dark_background')
plt.rcParams.update({
    'axes.facecolor': '#18191A',
    'figure.facecolor': '#18191A',
    'axes.edgecolor': '#404040',
    'axes.labelcolor': 'white',
    'text.color': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'legend.facecolor': '#23272F',
    'legend.edgecolor': '#404040',
    'savefig.facecolor': '#18191A',
    'savefig.edgecolor': '#18191A'
})

DARK_BG = "#18191A"
DARK_FG = "#FFFFFF"
DARK_ENTRY_BG = "#23272F"
DARK_HL = "#323232"
FONT_FAMILY = (KALAMEH_FONT_NAME, 13) if kalameh_path else ("Arial", 13)
TITLE_FONT = (KALAMEH_FONT_NAME, 15, "bold") if kalameh_path else ("Arial", 15, "bold")

cache_folder = r"C:\Users\AMYV\Desktop\AF\f1_analysis\Cache"
os.makedirs(cache_folder, exist_ok=True)
os.environ['FASTF1_CACHE'] = cache_folder
plotting.setup_mpl(color_scheme=None, misc_mpl_mods=False)

years = list(range(2020, 2026))
sessions = ['Q', 'R', 'FP1', 'FP2', 'FP3', 'Sprint', 'Sprint Qualifying', 'Practice 1', 'Practice 2', 'Practice 3']
grands_prix = [
    'Australian Grand Prix', 'Chinese Grand Prix', 'Japanese Grand Prix', 'Bahrain Grand Prix', 'Saudi Arabian Grand Prix',
    'Miami Grand Prix', 'Emilia Romagna Grand Prix', 'Monaco Grand Prix', 'Spanish Grand Prix', 'Canadian Grand Prix',
    'Austrian Grand Prix', 'British Grand Prix', 'Belgian Grand Prix', 'Hungarian Grand Prix', 'Dutch Grand Prix',
    'Italian Grand Prix', 'Azerbaijan Grand Prix', 'Singapore Grand Prix', 'United States Grand Prix', 'Mexico City Grand Prix',
    'São Paulo Grand Prix', 'Las Vegas Grand Prix', 'Qatar Grand Prix', 'Abu Dhabi Grand Prix'
]

team_colors = {
    'Mercedes': '#00D2BE',
    'Red Bull Racing': '#1E41FF',
    'Ferrari': '#DC0000',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'Aston Martin': '#006F62',
    'Haas': '#808080',
    'Racing Bulls': '#1660AD',
    'Williams': '#87cefa',
    'Kick Sauber': '#00e701'
}

def get_driver_team(driver):
    driver_teams = {
        'VER': 'Red Bull Racing',
        'LAW': 'Red Bull Racing',
        'LEC': 'Ferrari',
        'HAM': 'Ferrari',
        'NOR': 'McLaren',
        'PIA': 'McLaren',
        'RUS': 'Mercedes',
        'ANT': 'Mercedes',
        'ALO': 'Aston Martin',
        'STR': 'Aston Martin',
        'GAS': 'Alpine',
        'DOO': 'Alpine',
        'OCO': 'Haas',
        'BEA': 'Haas',
        'TSU': 'Racing Bulls',
        'HAD': 'Racing Bulls',
        'ALB': 'Williams',
        'SAI': 'Williams',
        'HUL': 'Kick Sauber',
        'BOR': 'Kick Sauber'
    }
    return driver_teams.get(driver, 'Unknown')

def interpolate_track(X, Y, num_points=2000):
    mask = ~(np.isnan(X) | np.isnan(Y))
    X = X[mask]
    Y = Y[mask]
    dist = np.sqrt(np.diff(X)**2 + np.diff(Y)**2)
    cumdist = np.insert(np.cumsum(dist), 0, 0)
    fx = interp1d(cumdist, X, kind='cubic')
    fy = interp1d(cumdist, Y, kind='cubic')
    uniform_dist = np.linspace(cumdist[0], cumdist[-1], num_points)
    X_new = fx(uniform_dist)
    Y_new = fy(uniform_dist)
    return X_new, Y_new, uniform_dist

def plot_telemetry(year, grand_prix, session_name, selected_drivers, for_export=False):
    if grand_prix == 'Pre-Season Testing':
        session = fastf1.get_testing_session(year, 1, session_name)
    else:
        session = fastf1.get_session(year, grand_prix, session_name)
    session.load()

    fig, ax = plt.subplots(figsize=(18, 10) if for_export else (10, 6))
    num_minisectors = 200
    mini_sectors = np.linspace(0, 1, num_minisectors)
    all_telemetry = {}
    fastest_laps = {}
    driver_colors = {}

    for driver in selected_drivers:
        laps = session.laps.pick_drivers(driver)
        fastest_lap = laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry().copy()
        fastest_laps[driver] = fastest_lap
        X_new, Y_new, dist = interpolate_track(telemetry['X'].values, telemetry['Y'].values)
        speed_interp = interp1d(np.linspace(0, 1, len(telemetry)), telemetry['Speed'].values, kind='cubic')
        speed_new = speed_interp(np.linspace(0, 1, len(X_new)))
        telemetry_interp = {
            'X': X_new,
            'Y': Y_new,
            'Speed': speed_new,
            'Distance': np.linspace(0, 1, len(X_new)),
        }
        all_telemetry[driver] = telemetry_interp

    for driver in selected_drivers:
        driver_colors[driver] = team_colors.get(get_driver_team(driver), "#DDDDDD")

    team_times = {}
    for driver in selected_drivers:
        team = get_driver_team(driver)
        if team not in team_times:
            team_times[team] = []
        team_times[team].append(driver)
    for team, drivers in team_times.items():
        if len(drivers) > 1:
            drivers_with_times = [(driver, fastest_laps[driver]['LapTime']) for driver in drivers]
            drivers_with_times.sort(key=lambda x: x[1])
            for i in range(1, len(drivers_with_times)):
                driver_colors[drivers_with_times[i][0]] = '#ED3EF7'

    for i in range(num_minisectors - 1):
        fastest_driver = None
        fastest_speed = -1
        fastest_sector = None
        for driver, tel in all_telemetry.items():
            mask = (tel['Distance'] >= mini_sectors[i]) & (tel['Distance'] < mini_sectors[i+1])
            if not np.any(mask):
                continue
            mean_speed = tel['Speed'][mask].mean()
            if mean_speed > fastest_speed:
                fastest_speed = mean_speed
                fastest_driver = driver
                fastest_sector = (tel['X'][mask], tel['Y'][mask])
        if fastest_sector is not None and fastest_driver is not None:
            color = driver_colors[fastest_driver]
            ax.plot(fastest_sector[0], fastest_sector[1], color=color, linewidth=4 if for_export else 2.5, alpha=0.92, solid_capstyle='round')

    for driver, tel in all_telemetry.items():
        ax.plot(tel['X'], tel['Y'], color=driver_colors[driver], linewidth=1.5, alpha=0.2, zorder=-1)

    ax.set_aspect('equal', adjustable='datalim')
    ax.axis('off')

    title_font = {'fontsize': 28 if for_export else 20, 'fontweight': 'bold'}
    if kalameh_path:
        title_font['fontname'] = KALAMEH_FONT_NAME
    plt.title("Track Dominance Map of Fastest Mini-Sectors", color='white', **title_font, pad=22)
    plt.suptitle(f"Track Dominance by Mini Sectors ({year}) - {grand_prix} - {session_name}", color='white', fontsize=15 if for_export else 12, fontname=KALAMEH_FONT_NAME if kalameh_path else None)

    # Enhanced Fastest Lap Box
    annotation = ""
    for driver, lap in fastest_laps.items():
        lap_time = lap['LapTime']
        lap_time_str = f"{int(lap_time.total_seconds() // 60)}:{int(lap_time.total_seconds() % 60):02}.{int((lap_time.total_seconds() * 1000) % 1000):03}"
        annotation += f"{driver}  |  {lap_time_str}\n"

    # FASTEST LAP BOX DESIGN: Reduced size, modern box, thin colored border.
    boxprops = dict(
        boxstyle="round,pad=0.25", 
        facecolor="#24242A", 
        edgecolor="#00D2BE", 
        linewidth=2, 
        alpha=0.92
    )
    ax.text(
        -0.05, 0.97, annotation.strip(),
        fontsize=18 if for_export else 17,
        fontweight='bold',
        bbox=boxprops,
        verticalalignment='top',
        horizontalalignment='left',
        transform=ax.transAxes,
        fontname=KALAMEH_FONT_NAME if kalameh_path else None,
        color='#F0F0F0',
        linespacing=1.3
    )

    legend_lines = [Line2D([0], [0], color=driver_colors[driver], lw=7 if for_export else 4) for driver in selected_drivers]
    legend_labels = selected_drivers
    leg = ax.legend(legend_lines, legend_labels, loc='lower center', bbox_to_anchor=(0.5, -0.08), fontsize=18 if for_export else 12,
                    ncol=4, facecolor='#23272F', edgecolor='#404040', labelcolor='white', framealpha=0.7)
    plt.setp(leg.get_texts(), fontname=KALAMEH_FONT_NAME if kalameh_path else None)

    # --------- WATERMARK: smaller, bolder, less width ---------
    watermark_text = "@Amir_Formula"
    if kalameh_path:
        watermark_font = fm.FontProperties(fname=kalameh_path, size=80 if for_export else 60, weight='bold')
    else:
        watermark_font = fm.FontProperties(size=80 if for_export else 60, weight='bold')
    ax.text(0.5, 0.5, watermark_text,
            color='#FFFFFF', alpha=0.25,
            fontsize=80 if for_export else 60,
            fontproperties=watermark_font,
            ha='center', va='center', rotation=0, zorder=999,
            transform=ax.transAxes, clip_on=False,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.6", fc="none", ec="none", alpha=0))

    return fig

def update_drivers():
    year = int(year_var.get())
    grand_prix = grand_prix_var.get()
    session_name = session_var.get()
    try:
        if grand_prix == 'Pre-Season Testing':
            session = fastf1.get_testing_session(year, 1, session_name)
        else:
            session = fastf1.get_session(year, grand_prix, session_name)
        session.load()
        available_drivers = session.results['Abbreviation'].tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Could not load session: {e}")
        return

    for widget in drivers_frame.winfo_children():
        widget.destroy()

    driver_vars.clear()
    for driver in available_drivers:
        var = IntVar()
        chk = Checkbutton(drivers_frame, text=driver, variable=var,
                          bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ENTRY_BG, font=FONT_FAMILY, activebackground=DARK_HL,
                          highlightthickness=0, bd=0)
        chk.var = var
        chk.pack(anchor=W, pady=2)
        driver_vars[driver] = var

def show_plot_page(selected_drivers):
    plot_window = Toplevel(root)
    plot_window.title("Track Dominance Map")
    plot_window.configure(bg=DARK_BG)
    plot_window.geometry("1650x900")

    fig = plot_telemetry(int(year_var.get()), grand_prix_var.get(), session_var.get(), selected_drivers)
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(side=TOP, fill=BOTH, expand=1)
    widget.configure(bg=DARK_BG)

    footer = Frame(plot_window, bg=DARK_BG)
    footer.pack(fill=X, side=BOTTOM)
    Button(footer, text="Close", command=plot_window.destroy, bg="#ED3EF7", fg=DARK_BG, font=FONT_FAMILY, activebackground="#bb29b6", width=9, height=1).pack(side=RIGHT, padx=28, pady=12)
    Button(footer, text="Export as PNG (Full Screen)", command=lambda: export_as_png(selected_drivers), bg="#00D2BE", fg=DARK_BG, font=FONT_FAMILY, activebackground="#00AFA3", width=22, height=1).pack(side=RIGHT, padx=18, pady=12)

def export_as_png(selected_drivers):
    fig_export = plot_telemetry(int(year_var.get()), grand_prix_var.get(), session_var.get(), selected_drivers, for_export=True)
    year = year_var.get()
    grand_prix = grand_prix_var.get()
    session = session_var.get()
    drivers = " & ".join(selected_drivers)
    default_filename = f"{year}-{grand_prix}-{session}-track-dominance-{drivers}.png".replace(" ", "_")
    export_dir = r"C:\Users\AMYV\Desktop\AF\Exports"
    os.makedirs(export_dir, exist_ok=True)
    file_path = os.path.join(export_dir, default_filename)
    fig_export.savefig(file_path, dpi=200, bbox_inches='tight', pad_inches=0.1, facecolor='#18191A')
    plt.close(fig_export)
    messagebox.showinfo("Exported", f"Plot saved at:\n{file_path}")

def update_plot():
    selected_drivers = [driver for driver, var in driver_vars.items() if var.get() == 1]
    if len(selected_drivers) < 2:
        messagebox.showerror("Error", "Please select at least two drivers.")
        return
    show_plot_page(selected_drivers)

# --------- TKINTER GUI ---------
driver_vars = {}

root = Tk()
root.title("Track Dominance Map of Fastest Mini-Sectors")
root.configure(bg=DARK_BG)
root.geometry("1100x680")
root.option_add("*Font", FONT_FAMILY)
root.option_add("*Background", DARK_BG)
root.option_add("*Foreground", DARK_FG)

style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox",
                fieldbackground=DARK_ENTRY_BG,
                background=DARK_ENTRY_BG,
                foreground=DARK_FG,
                selectbackground=DARK_ENTRY_BG,
                selectforeground=DARK_FG,
                font=FONT_FAMILY)
style.map("TCombobox", fieldbackground=[('readonly', DARK_ENTRY_BG)])
style.configure('TLabel', background=DARK_BG, foreground=DARK_FG, font=FONT_FAMILY)
style.configure('TButton', background=DARK_ENTRY_BG, foreground=DARK_FG, font=FONT_FAMILY)
style.configure('TFrame', background=DARK_BG)

app_title = Label(root, text="Track Dominance Map of Fastest Mini-Sectors", font=TITLE_FONT, bg=DARK_BG, fg="#00D2BE")
app_title.pack(pady=(14, 2))

controls_frame = Frame(root, bg=DARK_BG)
controls_frame.pack(side=LEFT, fill=Y, padx=18, pady=16)

drivers_frame = Frame(root, bg=DARK_BG)
drivers_frame.pack(side=RIGHT, fill=Y, padx=18, pady=16, expand=True)

year_var = StringVar()
grand_prix_var = StringVar()
session_var = StringVar()

Label(controls_frame, text="Year:", bg=DARK_BG, fg=DARK_FG, font=FONT_FAMILY).grid(row=0, column=0, padx=5, pady=12, sticky=E)
year_menu = ttk.Combobox(controls_frame, textvariable=year_var, values=years, font=FONT_FAMILY, state="readonly", width=18)
year_menu.grid(row=0, column=1, padx=5, pady=12, sticky=W)

Label(controls_frame, text="Grand Prix:", bg=DARK_BG, fg=DARK_FG, font=FONT_FAMILY).grid(row=1, column=0, padx=5, pady=12, sticky=E)
grand_prix_menu = ttk.Combobox(controls_frame, textvariable=grand_prix_var, values=grands_prix, font=FONT_FAMILY, state="readonly", width=18)
grand_prix_menu.grid(row=1, column=1, padx=5, pady=12, sticky=W)

Label(controls_frame, text="Session:", bg=DARK_BG, fg=DARK_FG, font=FONT_FAMILY).grid(row=2, column=0, padx=5, pady=12, sticky=E)
session_menu = ttk.Combobox(controls_frame, textvariable=session_var, values=sessions, font=FONT_FAMILY, state="readonly", width=18)
session_menu.grid(row=2, column=1, padx=5, pady=12, sticky=W)

Button(controls_frame, text="Update Drivers", command=update_drivers, bg=DARK_ENTRY_BG, fg=DARK_FG, font=FONT_FAMILY, activebackground=DARK_HL, width=18, height=1).grid(row=3, column=0, columnspan=2, pady=16)
Button(controls_frame, text="Generate Plot", command=update_plot, bg="#00D2BE", fg=DARK_BG, font=FONT_FAMILY, activebackground="#00AFA3", width=18, height=1).grid(row=4, column=0, columnspan=2, pady=10)

Label(drivers_frame, text="Select Drivers:", bg=DARK_BG, fg="#00D2BE", font=TITLE_FONT).pack(pady=(2, 8), anchor=W)

root.mainloop()