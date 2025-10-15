"""
Color utilities and bank-specific color schemes
"""
from reportlab.lib import colors

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple (0-1 range for ReportLab)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (r/255, g/255, b/255)

def get_color(hex_color):
    """Get ReportLab Color object from hex string"""
    r, g, b = hex_to_rgb(hex_color)
    return colors.Color(r, g, b)

# Standard colors (matching MD Bank reference)
COLOR_NAVY = get_color('#003366')
COLOR_LIGHT_BLUE = get_color('#E6EEF5')
COLOR_ORANGE = get_color('#FF6B35')
COLOR_WHITE = colors.white
COLOR_BLACK = colors.black
COLOR_GRAY_LIGHT = get_color('#F5F5F5')
COLOR_GRAY_MEDIUM = get_color('#CCCCCC')
COLOR_GRAY_DARK = get_color('#666666')
COLOR_TEXT_PRIMARY = get_color('#1A1A1A')
COLOR_TEXT_SECONDARY = get_color('#4A4A4A')
COLOR_GREEN = get_color('#28A745')
COLOR_RED = get_color('#DC3545')

class BankColors:
    """Bank-specific color schemes"""
    
    @staticmethod
    def get_scheme(bank_code):
        """Get color scheme for specific bank"""
        schemes = {
            'hdfc': {
                'primary': get_color('#004C8F'),
                'secondary': get_color('#ED232A'),
                'accent': COLOR_ORANGE,
                'light_bg': COLOR_LIGHT_BLUE
            },
            'icici': {
                'primary': get_color('#F37021'),
                'secondary': get_color('#522D6D'),
                'accent': COLOR_ORANGE,
                'light_bg': get_color('#FFF5E6')
            },
            'sbi': {
                'primary': get_color('#22409A'),
                'secondary': get_color('#009B77'),
                'accent': COLOR_ORANGE,
                'light_bg': get_color('#E8F4F8')
            },
            'axis': {
                'primary': get_color('#800000'),
                'secondary': get_color('#8B0000'),
                'accent': COLOR_ORANGE,
                'light_bg': get_color('#FFF0F0')
            },
            'amex': {
                'primary': get_color('#006FCF'),
                'secondary': get_color('#006FCF'),
                'accent': COLOR_ORANGE,
                'light_bg': get_color('#E6F2FF')
            }
        }
        return schemes.get(bank_code, schemes['hdfc'])
