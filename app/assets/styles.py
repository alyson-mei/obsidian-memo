from pathlib import Path

# Paths
CONSTANTS_DIR = Path(__file__).parent
FONTS_DIR = CONSTANTS_DIR / 'fonts'

# Fonts
POPPINS_REGULAR = FONTS_DIR / 'Poppins-Regular.ttf'

# Colors
TIME_PROGRESS_COLORS = {
    'year': '#f2a8a8',
    'season': '#d6a8d1', 
    'month': '#f3d6ba',
    'week': '#90c3d4',
    'day': '#a8d5ba'
}

TEXT_COLOR = "#000000"