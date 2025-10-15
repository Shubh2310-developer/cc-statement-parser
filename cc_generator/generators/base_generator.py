"""
Enhanced base PDF generator for credit card statements
Matches MD Bank reference image layout precisely
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
from reportlab.lib.utils import ImageReader
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.colors import BankColors, COLOR_NAVY, COLOR_LIGHT_BLUE, COLOR_WHITE, COLOR_BLACK, COLOR_ORANGE, COLOR_TEXT_PRIMARY, COLOR_GRAY_LIGHT, COLOR_TEXT_SECONDARY
from utils.formatters import format_currency, format_indian_currency
from components.base_component import BaseComponent

class BaseStatementGenerator:
    """Enhanced base class for generating professional credit card statement PDFs"""
    
    def __init__(self, bank_code, data_file):
        self.bank_code = bank_code
        self.bank_config = config.BANK_CONFIGS.get(bank_code, config.BANK_CONFIGS['hdfc'])
        self.colors_scheme = BankColors.get_scheme(bank_code)
        
        # Load data
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        # PDF setup
        self.page_width = config.PAGE_WIDTH
        self.page_height = config.PAGE_HEIGHT
        self.canvas = None
        self.current_y = 0
        
    def create_pdf(self, output_path):
        """Generate the complete PDF statement"""
        self.canvas = canvas.Canvas(output_path, pagesize=A4)
        self.current_y = self.page_height - config.MARGIN_TOP
        
        # Draw all sections
        self.draw_header()
        self.draw_cardholder_info()
        self.draw_key_info_section()
        self.draw_main_content()
        self.draw_interest_rates()
        self.draw_footer()
        
        # Save PDF
        self.canvas.save()
        print(f"Generated: {output_path}")
        
    def draw_header(self):
        """Draw header with bank logo and statement title"""
        header_y = self.page_height - config.HEADER_HEIGHT
        
        # Draw background rectangle
        self.canvas.setFillColor(self.colors_scheme['primary'])
        self.canvas.rect(0, header_y, self.page_width, config.HEADER_HEIGHT, fill=1, stroke=0)
        
        # Try to draw bank logo
        logo_path = os.path.join(config.LOGOS_DIR, f'{self.bank_code}_logo.pdf')
        if os.path.exists(logo_path):
            try:
                self.canvas.drawImage(logo_path, config.MARGIN_LEFT, header_y + 15, 
                                     width=100, height=45, preserveAspectRatio=True, mask='auto')
            except:
                # Fallback to text if logo fails
                self.canvas.setFillColor(COLOR_WHITE)
                self.canvas.setFont(config.DEFAULT_FONT_BOLD, 20)
                self.canvas.drawString(config.MARGIN_LEFT, header_y + 35, self.bank_config['name'])
        else:
            # Fallback to text
            self.canvas.setFillColor(COLOR_WHITE)
            self.canvas.setFont(config.DEFAULT_FONT_BOLD, 20)
            self.canvas.drawString(config.MARGIN_LEFT, header_y + 35, self.bank_config['name'])
        
        # Statement type (right side)
        self.canvas.setFont(config.DEFAULT_FONT, 14)
        statement_type = self.data['issuer']['statement_type']
        text_width = self.canvas.stringWidth(statement_type, config.DEFAULT_FONT, 14)
        self.canvas.drawString(self.page_width - config.MARGIN_RIGHT - text_width, header_y + 35, statement_type)
        
        self.current_y = header_y - 20
        
    def draw_cardholder_info(self):
        """Draw cardholder information and contact details"""
        # Address box
        box_width = 240
        box_height = 70
        box_x = config.MARGIN_LEFT
        box_y = self.current_y - box_height
        
        # Draw box border
        self.canvas.setStrokeColor(COLOR_BLACK)
        self.canvas.setLineWidth(1)
        self.canvas.rect(box_x, box_y, box_width, box_height, fill=0)
        
        # Draw name and address
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 11)
        name_y = box_y + box_height - 18
        self.canvas.drawString(box_x + 10, name_y, self.data['cardholder']['name'])
        
        self.canvas.setFont(config.DEFAULT_FONT, 8)
        address_lines = self.data['cardholder']['address'].split('\n')
        addr_y = name_y - 14
        for line in address_lines:
            self.canvas.drawString(box_x + 10, addr_y, line)
            addr_y -= 11
        
        # Contact information (right side)
        contact_x = self.page_width - config.MARGIN_RIGHT - 180
        contact_y = self.current_y - 15
        
        self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
        self.canvas.setFont(config.DEFAULT_FONT, 9)
        self.canvas.drawString(contact_x, contact_y, "Questions?")
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 10)
        self.canvas.drawString(contact_x, contact_y - 13, f"Call {self.data['issuer']['contact_phone']}")
        
        self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
        self.canvas.setFont(config.DEFAULT_FONT, 8)
        self.canvas.drawString(contact_x, contact_y - 30, "View your statement online:")
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
        self.canvas.drawString(contact_x, contact_y - 42, self.data['issuer']['website'])
        
        self.current_y = box_y - 25
        
    def draw_key_info_section(self):
        """Draw the 4 key information boxes with smaller numbered badges in grey section"""
        section_height = 60  # Reduced height
        bg_y = self.current_y - section_height
        
        # Background
        self.canvas.setFillColor(COLOR_LIGHT_BLUE)
        self.canvas.rect(0, bg_y, self.page_width, section_height, fill=1, stroke=0)
        
        # Calculate positions for 4 boxes (2 rows x 2 columns)
        col_width = (self.page_width - 2 * config.MARGIN_LEFT) / 2
        row_height = section_height / 2
        
        info_items = [
            (1, "Statement date:", self.data['statement_info']['statement_date']),
            (2, "Statement balance:", format_indian_currency(self.data['statement_info']['statement_balance'])),
            (3, "Statement period:", self.data['statement_info']['statement_period']),
            (4, "Payment due date:", self.data['statement_info']['payment_due_date'])
        ]
        
        component = BaseComponent(self.canvas, self.colors_scheme)
        
        for idx, (num, label, value) in enumerate(info_items):
            row = idx // 2
            col = idx % 2
            
            x = config.MARGIN_LEFT + col * col_width + 25
            y = bg_y + section_height - (row + 1) * row_height + 15
            
            # Draw smaller numbered badge
            badge_x = x - 15
            badge_y = y + 8
            component.draw_numbered_badge(badge_x, badge_y, num)
            
            # Draw label and value closer together
            self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
            self.canvas.setFont(config.DEFAULT_FONT_BOLD, 8)
            self.canvas.drawString(x, y + 12, label)
            
            self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
            self.canvas.setFont(config.DEFAULT_FONT_BOLD, 10)
            self.canvas.drawString(x, y, value)
        
        self.current_y = bg_y - 20
        
    def draw_main_content(self):
        """Draw transactions table and account summary side by side"""
        # Section headers
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 13)
        
        left_x = config.MARGIN_LEFT
        right_x = self.page_width / 2 + 10
        
        self.canvas.drawString(left_x, self.current_y, "Statement details")
        self.canvas.drawString(right_x, self.current_y, "Account summary")
        
        self.current_y -= 20
        
        # Store starting Y for both columns
        content_start_y = self.current_y
        
        # Draw transactions table (left side)
        self.draw_transactions_table(left_x, content_start_y)
        
        # Draw account summary (right side)
        self.draw_account_summary(right_x, content_start_y)
        
    def draw_transactions_table(self, x, y):
        """Draw the transactions table"""
        component = BaseComponent(self.canvas, self.colors_scheme)
        
        # Column headers with smaller numbered badges
        col_widths = [60, 60, 160, 75]
        headers = [
            (5, "Transaction\ndate"),
            (6, "Posting\ndate"),
            (7, "Account activity"),
            (None, "Amount")
        ]
        
        current_y = y
        header_y = current_y
        
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 8)
        col_x = x
        
        for (badge_num, header_text), width in zip(headers, col_widths):
            if badge_num:
                component.draw_numbered_badge(col_x + 8, header_y + 3, badge_num)
                text_x = col_x + 22
            else:
                text_x = col_x
            
            lines = header_text.split('\n')
            line_y = header_y
            for line in lines:
                self.canvas.drawString(text_x, line_y, line)
                line_y -= 9
            
            col_x += width
        
        current_y -= 25
        
        # Draw transactions
        self.canvas.setFont(config.DEFAULT_FONT, 8)
        
        for idx, trans in enumerate(self.data['transactions']):
            if idx % 2 == 0:
                self.canvas.setFillColor(COLOR_GRAY_LIGHT)
                self.canvas.rect(x - 3, current_y - 2, sum(col_widths) + 6, 12, fill=1, stroke=0)
            
            self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
            
            self.canvas.drawString(x, current_y, trans['transaction_date'])
            self.canvas.drawString(x + col_widths[0], current_y, trans['posting_date'])
            
            desc = trans['description']
            if len(desc) > 32:
                desc = desc[:29] + "..."
            self.canvas.drawString(x + col_widths[0] + col_widths[1], current_y, desc)
            
            amount_str = format_indian_currency(trans['amount'])
            amount_width = self.canvas.stringWidth(amount_str, config.DEFAULT_FONT, 8)
            self.canvas.drawString(x + sum(col_widths) - amount_width, current_y, amount_str)
            
            current_y -= 13
            
            if current_y < 180:
                break
        
        # Draw total row
        current_y -= 3
        self.canvas.setFillColor(COLOR_LIGHT_BLUE)
        self.canvas.rect(x - 3, current_y - 2, sum(col_widths) + 6, 16, fill=1, stroke=0)
        
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
        self.canvas.drawString(x + col_widths[0] + col_widths[1], current_y + 2, "Total payment activity")
        
        total_str = format_indian_currency(self.data['total_payment_activity'])
        total_width = self.canvas.stringWidth(total_str, config.DEFAULT_FONT_BOLD, 9)
        self.canvas.drawString(x + sum(col_widths) - total_width, current_y + 2, total_str)
        
    def draw_account_summary(self, x, y):
        """Draw the improved account summary section matching reference"""
        component = BaseComponent(self.canvas, self.colors_scheme)
        
        box_width = 260
        current_y = y
        
        # Draw outer border
        box_start_y = current_y
        self.canvas.setStrokeColor(COLOR_TEXT_SECONDARY)
        self.canvas.setLineWidth(0.5)
        
        summary = self.data['account_summary']
        
        # Items with amounts
        items = [
            (8, f"Previous balance", f"As of {summary['previous_balance_date']}", summary['previous_balance'], False),
            (9, "+Purchases", None, summary['purchases'], False),
            (10, "+Cash advances", None, summary['cash_advances'], False),
            (11, "+Interest", None, summary['interest'], False),
            (12, "+Fees", None, summary['fees'], False),
            (13, "+Other charges", None, summary['other_charges'], False),
            (14, "-Payments - Thank you", None, summary['payments'], False),
            (None, "-Other credits", None, summary['other_credits'], False),
        ]
        
        # Draw items
        for badge_num, label, sublabel, amount, highlight in items:
            # Background for alternating rows
            if badge_num and badge_num % 2 == 0:
                self.canvas.setFillColor(rl_colors.Color(0.98, 0.98, 0.98))
                self.canvas.rect(x - 5, current_y - 3, box_width, 16 if sublabel else 14, fill=1, stroke=0)
            
            if badge_num:
                component.draw_numbered_badge(x, current_y + 4, badge_num)
                label_x = x + 18
            else:
                label_x = x + 5
            
            self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
            self.canvas.setFont(config.DEFAULT_FONT, 8)
            self.canvas.drawString(label_x, current_y + 4, label)
            
            if sublabel:
                self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
                self.canvas.setFont(config.DEFAULT_FONT, 7)
                self.canvas.drawString(label_x, current_y - 6, sublabel)
            
            # Amount (right-aligned)
            amount_str = format_indian_currency(amount)
            self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
            self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
            amount_width = self.canvas.stringWidth(amount_str, config.DEFAULT_FONT_BOLD, 9)
            self.canvas.drawString(x + box_width - amount_width - 10, current_y + 4, amount_str)
            
            current_y -= 18 if sublabel else 15
        
        # Statement balance (highlighted)
        current_y -= 5
        self.canvas.setFillColor(COLOR_LIGHT_BLUE)
        self.canvas.rect(x - 5, current_y - 3, box_width, 20, fill=1, stroke=0)
        
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 10)
        self.canvas.drawString(x + 5, current_y + 5, "Statement balance")
        
        balance_str = format_indian_currency(summary['statement_balance'])
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 11)
        balance_width = self.canvas.stringWidth(balance_str, config.DEFAULT_FONT_BOLD, 11)
        self.canvas.drawString(x + box_width - balance_width - 10, current_y + 5, balance_str)
        
        current_y -= 30
        
        # Past due, overlimit
        for badge_num, label, amount in [
            (15, "Past due amount", summary['past_due_amount']),
            (None, "Overlimit amount", summary['overlimit_amount']),
            (16, "Minimum payment", summary['minimum_payment'])
        ]:
            if badge_num:
                component.draw_numbered_badge(x, current_y + 3, badge_num)
                label_x = x + 18
            else:
                label_x = x + 5
            
            self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
            self.canvas.setFont(config.DEFAULT_FONT, 8)
            self.canvas.drawString(label_x, current_y + 3, label)
            
            amount_str = format_indian_currency(amount)
            self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
            amount_width = self.canvas.stringWidth(amount_str, config.DEFAULT_FONT_BOLD, 9)
            self.canvas.drawString(x + box_width - amount_width - 10, current_y + 3, amount_str)
            
            current_y -= 14
        
        # Payment due date box
        current_y -= 8
        self.canvas.setStrokeColor(COLOR_BLACK)
        self.canvas.setLineWidth(1)
        self.canvas.rect(x - 5, current_y - 5, box_width, 30, fill=0, stroke=1)
        
        self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
        self.canvas.setFont(config.DEFAULT_FONT, 8)
        self.canvas.drawString(x + 5, current_y + 15, "Payment due date:")
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 11)
        self.canvas.drawString(x + 5, current_y + 3, self.data['statement_info']['payment_due_date'])
        
        # Credit limit section
        current_y -= 50
        self.canvas.setStrokeColor(COLOR_BLACK)
        self.canvas.rect(x - 5, current_y - 5, box_width, 48, fill=0, stroke=1)
        
        component.draw_numbered_badge(x + 5, current_y + 30, 17)
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
        self.canvas.drawString(x + 23, current_y + 27, "Limit")
        
        limit_str = format_indian_currency(summary['credit_limit'])
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 12)
        self.canvas.setFillColor(self.colors_scheme['primary'])
        limit_width = self.canvas.stringWidth(limit_str, config.DEFAULT_FONT_BOLD, 12)
        self.canvas.drawString(x + box_width - limit_width - 10, current_y + 27, limit_str)
        
        component.draw_numbered_badge(x + 5, current_y + 8, 18)
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 9)
        self.canvas.drawString(x + 23, current_y + 5, "Available")
        
        avail_str = format_indian_currency(summary['available_credit'])
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 12)
        self.canvas.setFillColor(self.colors_scheme['primary'])
        avail_width = self.canvas.stringWidth(avail_str, config.DEFAULT_FONT_BOLD, 12)
        self.canvas.drawString(x + box_width - avail_width - 10, current_y + 5, avail_str)
        
        # Draw final border around entire summary
        box_height = box_start_y - current_y + 10
        self.canvas.setStrokeColor(COLOR_TEXT_SECONDARY)
        self.canvas.setLineWidth(1)
        self.canvas.rect(x - 5, current_y - 5, box_width, box_height, fill=0, stroke=1)
        
    def draw_interest_rates(self):
        """Draw interest rates table at bottom"""
        table_y = 160
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 13)
        self.canvas.drawString(config.MARGIN_LEFT, table_y, "Interest rates")
        
        # Table with yellow background (matching reference)
        table_y -= 20
        table_width = 520
        table_height = 60
        
        # Yellow background
        self.canvas.setFillColor(rl_colors.Color(1, 0.98, 0.9))
        self.canvas.rect(config.MARGIN_LEFT, table_y - table_height, table_width, table_height, fill=1, stroke=0)
        
        # Border
        self.canvas.setStrokeColor(COLOR_TEXT_SECONDARY)
        self.canvas.setLineWidth(0.5)
        self.canvas.rect(config.MARGIN_LEFT, table_y - table_height, table_width, table_height, fill=0, stroke=1)
        
        # Headers
        col_widths = [120, 130, 130, 140]
        headers = ["", "Interest charged\nthis statement", "Annual interest rate", "Daily interest rate"]
        
        x = config.MARGIN_LEFT + 5
        header_y = table_y - 10
        self.canvas.setFillColor(COLOR_TEXT_PRIMARY)
        self.canvas.setFont(config.DEFAULT_FONT_BOLD, 8)
        
        for header, width in zip(headers, col_widths):
            lines = header.split('\n')
            line_y = header_y
            for line in lines:
                self.canvas.drawString(x, line_y, line)
                line_y -= 9
            x += width
        
        # Data rows
        row_y = table_y - 28
        self.canvas.setFont(config.DEFAULT_FONT, 8)
        
        for rate_info in self.data['interest_rates']:
            x = config.MARGIN_LEFT + 5
            
            self.canvas.drawString(x, row_y, rate_info['category'])
            x += col_widths[0]
            
            self.canvas.drawString(x, row_y, format_indian_currency(rate_info['interest_charged']))
            x += col_widths[1]
            
            self.canvas.drawString(x, row_y, f"{rate_info['annual_rate']:.2f} %")
            x += col_widths[2]
            
            self.canvas.drawString(x, row_y, f"{rate_info['daily_rate']:.5f} %")
            
            row_y -= 13
        
    def draw_footer(self):
        """Draw footer with page number"""
        self.canvas.setFillColor(COLOR_TEXT_SECONDARY)
        self.canvas.setFont(config.DEFAULT_FONT, 7)
        
        footer_text = "Page 1"
        text_width = self.canvas.stringWidth(footer_text, config.DEFAULT_FONT, 7)
        self.canvas.drawString((self.page_width - text_width) / 2, 25, footer_text)
