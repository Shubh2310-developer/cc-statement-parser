"""
Text styles and formatting utilities
"""
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import config

class TextStyles:
    """Centralized text style definitions"""
    
    # Header styles
    BANK_NAME = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_TITLE,
        'textColor': 'white',
        'alignment': TA_RIGHT
    }
    
    STATEMENT_TYPE = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_HEADING,
        'textColor': 'white',
        'alignment': TA_RIGHT
    }
    
    # Section headers
    SECTION_HEADER = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_HEADING,
        'textColor': 'primary'
    }
    
    # Body text
    BODY = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'text_primary'
    }
    
    BODY_BOLD = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'text_primary'
    }
    
    # Table styles
    TABLE_HEADER = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_SUBHEADING,
        'textColor': 'text_primary'
    }
    
    TABLE_CELL = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'text_primary'
    }
    
    TABLE_CELL_AMOUNT = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'text_primary',
        'alignment': TA_RIGHT
    }
    
    # Key info styles
    KEY_INFO_LABEL = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_SMALL,
        'textColor': 'text_secondary'
    }
    
    KEY_INFO_VALUE = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.FONT_SIZE_SUBHEADING,
        'textColor': 'text_primary'
    }
    
    # Amount styles
    AMOUNT_LARGE = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': 16,
        'textColor': 'text_primary'
    }
    
    AMOUNT_POSITIVE = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'green'
    }
    
    AMOUNT_NEGATIVE = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_BODY,
        'textColor': 'text_primary'
    }
    
    # Badge/number circle styles
    BADGE_NUMBER = {
        'fontName': config.DEFAULT_FONT_BOLD,
        'fontSize': config.BADGE_FONT_SIZE,
        'textColor': 'white'
    }
    
    # Contact info
    CONTACT_INFO = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_SMALL,
        'textColor': 'text_secondary'
    }
    
    # Footer
    FOOTER = {
        'fontName': config.DEFAULT_FONT,
        'fontSize': config.FONT_SIZE_TINY,
        'textColor': 'text_secondary',
        'alignment': TA_CENTER
    }

def get_paragraph_style(name, **kwargs):
    """Create a ParagraphStyle with given parameters"""
    return ParagraphStyle(name, **kwargs)
