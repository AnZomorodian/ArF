"""
Constants for F1 data analysis platform
"""

# Team colors (2024 season)
TEAM_COLORS = {
    'Mercedes': '#00D2BE',
    'Red Bull Racing': '#1E41FF',
    'Ferrari': '#DC0000',
    'McLaren': '#FF8700',
    'Alpine': '#0090FF',
    'Aston Martin': '#006F62',
    'Haas': '#808080',
    'RB': '#1660AD',
    'Williams': '#87CEEB',
    'Kick Sauber': '#00E701'
}

# Driver team mappings (2024 season)
DRIVER_TEAMS = {
    'VER': 'Red Bull Racing',
    'PER': 'Red Bull Racing',
    'LEC': 'Ferrari',
    'SAI': 'Ferrari',
    'HAM': 'Mercedes',
    'RUS': 'Mercedes',
    'NOR': 'McLaren',
    'PIA': 'McLaren',
    'ALO': 'Aston Martin',
    'STR': 'Aston Martin',
    'GAS': 'Alpine',
    'OCO': 'Alpine',
    'MAG': 'Haas',
    'HUL': 'Haas',
    'TSU': 'RB',
    'RIC': 'RB',
    'ALB': 'Williams',
    'SAR': 'Williams',
    'ZHO': 'Kick Sauber',
    'BOT': 'Kick Sauber'
}

# Grand Prix list
GRANDS_PRIX = [
    'Australian Grand Prix',
    'Chinese Grand Prix', 
    'Japanese Grand Prix',
    'Bahrain Grand Prix',
    'Saudi Arabian Grand Prix',
    'Miami Grand Prix',
    'Emilia Romagna Grand Prix',
    'Monaco Grand Prix',
    'Spanish Grand Prix',
    'Canadian Grand Prix',
    'Austrian Grand Prix',
    'British Grand Prix',
    'Belgian Grand Prix',
    'Hungarian Grand Prix',
    'Dutch Grand Prix',
    'Italian Grand Prix',
    'Azerbaijan Grand Prix',
    'Singapore Grand Prix',
    'United States Grand Prix',
    'Mexico City Grand Prix',
    'São Paulo Grand Prix',
    'Las Vegas Grand Prix',
    'Qatar Grand Prix',
    'Abu Dhabi Grand Prix'
]

# Session types
SESSIONS = {
    'Practice 1': 'FP1',
    'Practice 2': 'FP2', 
    'Practice 3': 'FP3',
    'Qualifying': 'Q',
    'Sprint': 'Sprint',
    'Sprint Qualifying': 'SQ',
    'Race': 'R'
}

# Tire compound colors
TIRE_COLORS = {
    'SOFT': '#DC0000',
    'MEDIUM': '#FFD700',
    'HARD': '#FFFFFF',
    'INTERMEDIATE': '#00FF00',
    'WET': '#0000FF'
}

# Circuit aliases for better display names
CIRCUIT_ALIASES = {
    'Albert Park Grand Prix Circuit': 'Albert Park',
    'Bahrain International Circuit': 'Bahrain',
    'Jeddah Corniche Circuit': 'Jeddah',
    'Suzuka Circuit': 'Suzuka',
    'Shanghai International Circuit': 'Shanghai',
    'Miami International Autodrome': 'Miami',
    'Autodromo Enzo e Dino Ferrari': 'Imola',
    'Circuit de Monaco': 'Monaco',
    'Circuit de Barcelona-Catalunya': 'Barcelona',
    'Circuit Gilles Villeneuve': 'Montreal',
    'Red Bull Ring': 'Spielberg',
    'Silverstone Circuit': 'Silverstone',
    'Hungaroring': 'Budapest',
    'Circuit de Spa-Francorchamps': 'Spa',
    'Circuit Zandvoort': 'Zandvoort',
    'Autodromo Nazionale di Monza': 'Monza',
    'Baku City Circuit': 'Baku',
    'Marina Bay Street Circuit': 'Singapore',
    'Circuit of the Americas': 'Austin',
    'Autódromo Hermanos Rodríguez': 'Mexico City',
    'Autódromo José Carlos Pace': 'Interlagos',
    'Las Vegas Strip Street Circuit': 'Las Vegas',
    'Losail International Circuit': 'Losail',
    'Yas Marina Circuit': 'Abu Dhabi'
}
