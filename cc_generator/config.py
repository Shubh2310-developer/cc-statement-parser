"""
Central configuration for CC Statement Generator
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOGOS_DIR = os.path.join(ASSETS_DIR, 'logos')

# PDF settings
PAGE_WIDTH = 595.27  # A4 width in points (210mm)
PAGE_HEIGHT = 841.89  # A4 height in points (297mm)
MARGIN_LEFT = 40
MARGIN_RIGHT = 40
MARGIN_TOP = 60
MARGIN_BOTTOM = 60

# Layout dimensions (matching MD Bank reference)
HEADER_HEIGHT = 75
KEY_INFO_SECTION_HEIGHT = 80
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Font settings
DEFAULT_FONT = 'Helvetica'
DEFAULT_FONT_BOLD = 'Helvetica-Bold'
DEFAULT_FONT_OBLIQUE = 'Helvetica-Oblique'
MONOSPACE_FONT = 'Courier'

# Font sizes
FONT_SIZE_TITLE = 20
FONT_SIZE_HEADING = 14
FONT_SIZE_SUBHEADING = 11
FONT_SIZE_BODY = 9
FONT_SIZE_SMALL = 8
FONT_SIZE_TINY = 7

# Numbered badge settings
BADGE_RADIUS = 9  # Smaller, more professional
BADGE_FONT_SIZE = 8

# Currency symbol
CURRENCY_SYMBOL = '₹'  # Rupee for Indian banks
CURRENCY_SYMBOL_ALT = '$'  # Dollar (for reference compatibility)

# Bank configurations
BANK_CONFIGS = {
    'hdfc': {
        'name': 'HDFC Bank',
        'color_primary': '#004C8F',  # Navy blue
        'color_secondary': '#ED232A',  # Red
        'color_accent': '#FF6B35',  # Orange
        'logo_file': 'hdfc_logo.png'
    },
    'icici': {
        'name': 'ICICI Bank',
        'color_primary': '#F37021',  # Orange
        'color_secondary': '#522D6D',  # Purple
        'color_accent': '#FF6B35',
        'logo_file': 'icici_logo.png'
    },
    'sbi': {
        'name': 'SBI Card',
        'color_primary': '#22409A',  # Blue
        'color_secondary': '#009B77',  # Green
        'color_accent': '#FF6B35',
        'logo_file': 'sbi_logo.png'
    },
    'axis': {
        'name': 'Axis Bank',
        'color_primary': '#800000',  # Burgundy
        'color_secondary': '#8B0000',
        'color_accent': '#FF6B35',
        'logo_file': 'axis_logo.png'
    },
    'amex': {
        'name': 'American Express',
        'color_primary': '#006FCF',  # Amex blue
        'color_secondary': '#006FCF',
        'color_accent': '#FF6B35',
        'logo_file': 'amex_logo.png'
    }
}
