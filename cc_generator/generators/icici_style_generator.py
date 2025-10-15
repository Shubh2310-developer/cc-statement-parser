"""
ICICI Bank style credit card statement generator
Matches exact ICICI reference format
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.platypus import Table, TableStyle
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.colors import BankColors, get_color
from utils.formatters import format_indian_currency

class ICICIStyleGenerator:
    """ICICI Bank style statement generator - exact match to reference"""
    
    def __init__(self, bank_code, data_file):
        self.bank_code = bank_code
        self.bank_config = config.BANK_CONFIGS.get(bank_code, config.BANK_CONFIGS['hdfc'])
        self.colors_scheme = BankColors.get_scheme(bank_code)
        
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.page_width = 595.27  # A4
        self.page_height = 841.89
        self.canvas = None
        
        # Colors matching ICICI
        self.orange = get_color('#F47920')
        self.grey = get_color('#F5F5F5')
        self.dark_grey = get_color('#4A4A4A')
        self.light_grey = get_color('#E8E8E8')
        
    def create_pdf(self, output_path):
        """Generate PDF matching ICICI format"""
        self.canvas = canvas.Canvas(output_path, pagesize=A4)
        
        # Draw all sections
        self.draw_header()
        self.draw_top_summary()
        self.draw_statement_summary()
        self.draw_credit_summary()
        self.draw_transactions()
        self.draw_sidebar()
        self.draw_footer()
        
        self.canvas.save()
        print(f"Generated: {output_path}")
        
    def draw_header(self):
        """Draw top header with logo and title"""
        y = self.page_height - 40
        
        # ICICI Bank logo area (simplified text)
        self.canvas.setFillColor(self.colors_scheme['primary'])
        self.canvas.setFont('Helvetica-Bold', 16)
        self.canvas.drawString(40, y, self.bank_config['name'])
        
        # Platinum / Credit Cards
        self.canvas.setFont('Helvetica-Oblique', 12)
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.drawString(140, y, "Platinum")
        
        # Right side - Credit Cards
        self.canvas.setFont('Helvetica-Bold', 10)
        self.canvas.drawString(self.page_width - 140, y, "Credit Cards")
        
        # Barcode area
        y -= 25
        self.canvas.setFont('Helvetica', 7)
        self.canvas.drawString(40, y, "18042025_1")
        
        # Customer name and address
        y -= 20
        self.canvas.setFont('Helvetica-Bold', 9)
        self.canvas.drawString(40, y, self.data['cardholder']['name'])
        
        y -= 12
        self.canvas.setFont('Helvetica', 8)
        for line in self.data['cardholder']['address'].split('\n'):
            self.canvas.drawString(40, y, line)
            y -= 10
            
    def draw_top_summary(self):
        """Draw statement date, payment due date, and amounts on left"""
        y = 650
        
        # Left box - grey background
        box_width = 200
        box_height = 100
        self.canvas.setFillColor(self.grey)
        self.canvas.rect(40, y - box_height, box_width, box_height, fill=1, stroke=0)
        
        # STATEMENT DATE
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.drawString(50, y - 15, "STATEMENT DATE")
        self.canvas.setFont('Helvetica-Bold', 11)
        self.canvas.drawString(50, y - 30, self.data['statement_info']['statement_date'])
        
        # PAYMENT DUE DATE
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.drawString(50, y - 50, "PAYMENT DUE DATE")
        self.canvas.setFont('Helvetica-Bold', 11)
        self.canvas.drawString(50, y - 65, self.data['statement_info']['payment_due_date'])
        
        # Total Amount due
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.drawString(50, y - 82, "Total Amount due")
        self.canvas.setFont('Helvetica-Bold', 12)
        self.canvas.drawString(50, y - 97, format_indian_currency(self.data['statement_info']['statement_balance']))
        
        # Right side - SPENDS OVERVIEW
        circle_x = self.page_width - 150
        circle_y = y - 50
        
        # Draw circle (simplified - just text for now)
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.circle(circle_x, circle_y, 40, fill=0, stroke=1)
        
        self.canvas.setFont('Helvetica-Bold', 9)
        self.canvas.drawString(circle_x - 35, y - 15, "SPENDS OVERVIEW")
        
        self.canvas.setFont('Helvetica', 8)
        self.canvas.drawString(circle_x - 20, circle_y, "Others-100%")
        
        # Minimum Amount due
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.drawString(50, y - 112, "Minimum Amount due")
        self.canvas.setFont('Helvetica-Bold', 10)
        summary = self.data['account_summary']
        self.canvas.drawString(50, y - 125, format_indian_currency(summary['minimum_payment']))
        
    def draw_statement_summary(self):
        """Draw STATEMENT SUMMARY with formula"""
        y = 520
        
        self.canvas.setFont('Helvetica-Bold', 11)
        self.canvas.setFillColor(rl_colors.black)
        self.canvas.drawString(40, y, "STATEMENT SUMMARY")
        
        y -= 20
        
        # Formula with boxes
        summary = self.data['account_summary']
        
        box_width = 120
        box_height = 40
        spacing = 20
        x_start = 60
        
        # Previous Balance
        self.draw_summary_box(x_start, y, box_width, box_height, 
                            "Previous Balance", summary['previous_balance'])
        
        # Plus sign
        self.canvas.setFont('Helvetica-Bold', 16)
        self.canvas.drawString(x_start + box_width + 5, y - 20, "+")
        
        # Purchases / Charges
        x_start += box_width + spacing
        self.draw_summary_box(x_start, y, box_width, box_height,
                            "Purchases / Charges", summary['purchases'])
        
        # Plus sign
        self.canvas.drawString(x_start + box_width + 5, y - 20, "+")
        
        # Cash Advances
        x_start += box_width + spacing
        self.draw_summary_box(x_start, y, box_width, box_height,
                            "Cash Advances", summary['cash_advances'])
        
        # Minus sign
        self.canvas.drawString(x_start + box_width + 5, y - 20, "-")
        
        # Payments / Credits
        x_start += box_width + spacing
        self.draw_summary_box(x_start, y, box_width, box_height,
                            "Payments / Credits", summary['payments'])
        
    def draw_summary_box(self, x, y, width, height, label, amount):
        """Draw individual summary box"""
        # Circle with symbol
        circle_y = y - height/2
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.circle(x - 10, circle_y, 8, fill=1, stroke=0)
        
        # Box
        self.canvas.setStrokeColor(self.light_grey)
        self.canvas.setLineWidth(1)
        self.canvas.rect(x, y - height, width, height, fill=0, stroke=1)
        
        # Label
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.setFont('Helvetica', 7)
        self.canvas.drawString(x + 5, y - 15, label)
        
        # Amount
        self.canvas.setFont('Helvetica-Bold', 10)
        self.canvas.drawString(x + 5, y - 30, format_indian_currency(amount))
        
    def draw_credit_summary(self):
        """Draw CREDIT SUMMARY table"""
        y = 430
        
        self.canvas.setFont('Helvetica-Bold', 11)
        self.canvas.setFillColor(rl_colors.black)
        self.canvas.drawString(40, y, "CREDIT SUMMARY")
        
        y -= 15
        
        summary = self.data['account_summary']
        
        # Table data
        data = [[
            'Credit Limit (Including cash)',
            'Available Credit (Including cash)',
            'Cash Limit',
            'Available Cash'
        ], [
            format_indian_currency(summary['credit_limit']),
            format_indian_currency(summary['available_credit']),
            format_indian_currency(15000.00),  # Sample cash limit
            format_indian_currency(0.00)
        ]]
        
        # Simple table drawing
        col_width = 120
        row_height = 15
        x_start = 40
        
        # Headers
        self.canvas.setFont('Helvetica-Bold', 7)
        for i, header in enumerate(data[0]):
            self.canvas.drawString(x_start + i * col_width, y, header)
        
        # Values
        y -= row_height
        self.canvas.setFont('Helvetica-Bold', 9)
        for i, value in enumerate(data[1]):
            self.canvas.drawString(x_start + i * col_width, y, value)
        
    def draw_transactions(self):
        """Draw transaction table"""
        y = 380
        
        # Table headers
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.setFillColor(rl_colors.black)
        
        headers = ['Date', 'SerNo.', 'Transaction Details', 'Reward\nPoints', 'Intl.#\namount', 'Amount (in ₹)']
        x_positions = [40, 80, 140, 360, 420, 480]
        
        for i, header in enumerate(headers):
            lines = header.split('\n')
            y_offset = y
            for line in lines:
                self.canvas.drawString(x_positions[i], y_offset, line)
                y_offset -= 8
        
        y -= 25
        
        # Card number header
        self.canvas.setFont('Helvetica', 7)
        self.canvas.setFillColor(self.dark_grey)
        
        # Sample card number
        card_num = "4375XXXXXXXX9013"
        self.canvas.drawString(40, y, card_num)
        
        y -= 15
        
        # Transactions
        self.canvas.setFont('Helvetica', 7)
        for idx, trans in enumerate(self.data['transactions'][:10]):  # First 10
            if y < 150:
                break
                
            # Alternating background
            if idx % 2 == 0:
                self.canvas.setFillColor(self.grey)
                self.canvas.rect(38, y - 2, 520, 12, fill=1, stroke=0)
            
            self.canvas.setFillColor(rl_colors.black)
            
            # Date
            self.canvas.drawString(40, y, trans['transaction_date'])
            
            # SerNo (generate dummy)
            ser_no = f"110{31708167 + idx}"
            self.canvas.drawString(80, y, ser_no)
            
            # Description
            desc = trans['description']
            if len(desc) > 45:
                desc = desc[:42] + "..."
            self.canvas.drawString(140, y, desc)
            
            # Reward Points
            reward = trans.get('reward_points', 0)
            self.canvas.drawString(370, y, str(reward))
            
            # Amount
            amount_str = format_indian_currency(trans['amount'])
            if trans['amount'] < 0:
                amount_str += " CR"
            amount_width = self.canvas.stringWidth(amount_str, 'Helvetica', 7)
            self.canvas.drawString(540 - amount_width, y, amount_str)
            
            y -= 12
        
    def draw_sidebar(self):
        """Draw orange OFFER ZONE sidebar"""
        # Orange sidebar on right
        sidebar_width = 80
        sidebar_x = self.page_width - sidebar_width - 20
        sidebar_y = 200
        sidebar_height = 150
        
        self.canvas.setFillColor(self.orange)
        self.canvas.rect(sidebar_x, sidebar_y, sidebar_width, sidebar_height, fill=1, stroke=0)
        
        # White circle for logo
        self.canvas.setFillColor(rl_colors.white)
        self.canvas.circle(sidebar_x + sidebar_width/2, sidebar_y + sidebar_height - 30, 20, fill=1, stroke=0)
        
        # Text
        self.canvas.setFillColor(rl_colors.white)
        self.canvas.setFont('Helvetica-Bold', 10)
        
        # Rotate text vertically
        self.canvas.saveState()
        self.canvas.translate(sidebar_x + 20, sidebar_y + 60)
        self.canvas.rotate(90)
        self.canvas.drawString(0, 0, "OFFER ZONE")
        self.canvas.restoreState()
        
        # ICICI Bank Rewards box below
        y = sidebar_y - 80
        self.canvas.setFillColor(self.dark_grey)
        self.canvas.rect(sidebar_x, y, sidebar_width, 70, fill=1, stroke=0)
        
        self.canvas.setFillColor(rl_colors.white)
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.drawString(sidebar_x + 5, y + 55, "ICICI Bank")
        self.canvas.drawString(sidebar_x + 5, y + 45, "Rewards")
        
        self.canvas.setFont('Helvetica', 7)
        self.canvas.drawString(sidebar_x + 5, y + 30, "Points Earned")
        
        # Points value
        self.canvas.setFont('Helvetica-Bold', 14)
        rewards = self.data.get('rewards_points', 132)
        self.canvas.drawString(sidebar_x + 15, y + 15, str(rewards))
        
    def draw_footer(self):
        """Draw footer"""
        y = 50
        
        self.canvas.setFont('Helvetica', 6)
        self.canvas.setFillColor(self.dark_grey)
        
        footer_text = "Page 1 of 8"
        self.canvas.drawString(self.page_width - 100, y, footer_text)
        
        # Bank details
        y -= 10
        self.canvas.drawString(40, y, "ICICI Bank Credit Card GST Number: 27AAACI1195H3ZK")
