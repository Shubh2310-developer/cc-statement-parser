"""
Base component class for drawing statement elements
"""
from reportlab.lib import colors as rl_colors
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.colors import COLOR_ORANGE, COLOR_WHITE
import config

class BaseComponent:
    """Base class for all statement components"""
    
    def __init__(self, canvas, colors_scheme):
        """
        Args:
            canvas: ReportLab canvas object
            colors_scheme: Bank-specific color scheme dictionary
        """
        self.canvas = canvas
        self.colors = colors_scheme
        
    def draw_numbered_badge(self, x, y, number):
        """Draw circular numbered badge (like ①②③ in reference)"""
        self.canvas.saveState()
        
        # Draw circle
        self.canvas.setFillColor(COLOR_ORANGE)
        self.canvas.setStrokeColor(COLOR_ORANGE)
        self.canvas.circle(x, y, config.BADGE_RADIUS, fill=1)
        
        # Draw number
        self.canvas.setFillColor(COLOR_WHITE)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, config.BADGE_FONT_SIZE)
        
        # Center text in circle
        text_width = self.canvas.stringWidth(str(number), config.DEFAULT_FONT_BOLD, config.BADGE_FONT_SIZE)
        text_x = x - text_width / 2
        text_y = y - config.BADGE_FONT_SIZE / 3  # Slight adjustment for vertical centering
        
        self.canvas.drawString(text_x, text_y, str(number))
        self.canvas.restoreState()
    
    def draw_box(self, x, y, width, height, fill_color=None, stroke_color=None, line_width=1):
        """Draw a rectangular box"""
        self.canvas.saveState()
        
        if fill_color:
            self.canvas.setFillColor(fill_color)
        if stroke_color:
            self.canvas.setStrokeColor(stroke_color)
        self.canvas.setLineWidth(line_width)
        
        self.canvas.rect(x, y, width, height, fill=1 if fill_color else 0)
        self.canvas.restoreState()
