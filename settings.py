# Screen Dimensions
WIDTH = 800
HEIGHT = 600
FPS = 60

# Game Settings & Constants
HIGH_SCORE_FILE = "highscore.json"
INITIAL_LIVES = 3

# Energy & Boost Balances
MAX_ENERGY = 100.0
ENERGY_DRAIN_RATE = 2.5        # Energy loss per second
ENERGY_CORE_RECHARGE = 35.0

MAX_BOOST = 100.0
BOOST_CONSUMPTION = 30.0       # Boost cost per second when active
BOOST_RECHARGE = 15.0          # Boost regeneration per second when inactive

# Player Configuration
PLAYER_SPEED = 6
MAGNET_RADIUS = 120

# Progression Thresholds
LEVEL_2_DIST = 1000
LEVEL_3_DIST = 2500
LEVEL_4_DIST = 5000

# Color Palette (RGB)
COLOR_BG = (10, 12, 24)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GRAY = (20, 20, 30)
COLOR_CYAN = (0, 230, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_GREEN = (0, 255, 120)
COLOR_RED = (255, 60, 80)
COLOR_PURPLE = (180, 70, 255)

# settings.py

# Add environment definitions
ENVIRONMENTS = [
    {
        "name": "URBAN SKYLINE",
        "bg_color": (10, 15, 30),        # Dark blue city night
        "accent_color": (0, 240, 255),    # Cyan HUD accent
        "drone_speed_mult": 1.0
    },
    {
        "name": "STARK LABS",
        "bg_color": (25, 20, 10),        # Gold / industrial brown
        "accent_color": (255, 215, 0),    # Gold HUD accent
        "drone_speed_mult": 1.25
    },
    {
        "name": "DEEP SPACE",
        "bg_color": (5, 2, 12),          # Pitch black / deep purple space
        "accent_color": (255, 50, 80),    # Red / magenta HUD accent
        "drone_speed_mult": 1.5
    }
]

# Distance required to loop into the next environment
ZONE_DISTANCE_THRESHOLD = 500  # Loops every 500 meters