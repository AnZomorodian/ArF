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

# Circuit aliases for better display names
CIRCUIT_ALIASES = {
    'Austrian Grand Prix': 'Red Bull Ring',
    'Abu Dhabi Grand Prix': 'Yas Marina Circuit',
    'Australian Grand Prix': 'Albert Park Circuit',
    'Azerbaijan Grand Prix': 'Baku City Circuit',
    'Bahrain Grand Prix': 'Bahrain International Circuit',
    'Belgian Grand Prix': 'Circuit de Spa-Francorchamps',
    'British Grand Prix': 'Silverstone Circuit',
    'Canadian Grand Prix': 'Circuit Gilles Villeneuve',
    'Chinese Grand Prix': 'Shanghai International Circuit',
    'Dutch Grand Prix': 'Circuit Zandvoort',
    'Emilia Romagna Grand Prix': 'Autodromo Enzo e Dino Ferrari',
    'Hungarian Grand Prix': 'Hungaroring',
    'Italian Grand Prix': 'Autodromo Nazionale di Monza',
    'Japanese Grand Prix': 'Suzuka International Racing Course',
    'Las Vegas Grand Prix': 'Las Vegas Strip Circuit',
    'Miami Grand Prix': 'Miami International Autodrome',
    'Mexico City Grand Prix': 'Autodromo Hermanos Rodriguez',
    'Monaco Grand Prix': 'Circuit de Monaco',
    'Qatar Grand Prix': 'Lusail International Circuit',
    'São Paulo Grand Prix': 'Autodromo Jose Carlos Pace',
    'Saudi Arabian Grand Prix': 'Jeddah Corniche Circuit',
    'Singapore Grand Prix': 'Marina Bay Street Circuit',
    'Spanish Grand Prix': 'Circuit de Barcelona-Catalunya',
    'United States Grand Prix': 'Circuit of The Americas'
}

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
