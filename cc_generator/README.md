# Credit Card Statement PDF Generator

Professional PDF generator for creating realistic credit card statements matching authentic bank formats. Designed for testing, development, and demonstration purposes.

## Features

- **5 Major Indian Banks**: HDFC, ICICI, SBI, Axis, American Express
- **Professional Layout**: Matches real bank statement design with numbered sections (①-⑱)
- **Authentic Details**: 
  - Cardholder information and address
  - Transaction history with dates and descriptions
  - Account summary with all charges and fees
  - Interest rates breakdown
  - Credit limit and available balance
- **Indian Currency Formatting**: Proper ₹ symbol and Indian numbering system
- **Customizable**: Easy to modify data via JSON files
- **Multi-page Support**: Handles long transaction lists automatically

## Project Structure

```
cc_generator/
├── data/
│   └── samples/              # Sample JSON data for each bank
│       ├── hdfc_sample.json
│       ├── icici_sample.json
│       ├── sbi_sample.json
│       ├── axis_sample.json
│       └── amex_sample.json
├── utils/                    # Utility functions
│   ├── formatters.py        # Currency, date formatting
│   ├── colors.py            # Bank color schemes
│   └── styles.py            # Text styles
├── components/              # PDF layout components
│   └── base_component.py   # Base drawing functions
├── generators/              # Bank-specific generators
│   ├── base_generator.py   # Core PDF generation logic
│   ├── hdfc_generator.py
│   ├── icici_generator.py
│   ├── sbi_generator.py
│   ├── axis_generator.py
│   └── amex_generator.py
├── output/                  # Generated PDFs
│   ├── hdfc/
│   ├── icici/
│   ├── sbi/
│   ├── axis/
│   └── amex/
├── config.py               # Central configuration
├── main_generator.py       # CLI entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

1. **Navigate to the generator directory:**
   ```bash
   cd cc_generator
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Generate Single Bank Statement

```bash
# Generate HDFC statement (default)
python3 main_generator.py

# Generate specific bank
python3 main_generator.py --bank hdfc
python3 main_generator.py --bank icici
python3 main_generator.py --bank sbi
python3 main_generator.py --bank axis
python3 main_generator.py --bank amex
```

### Generate All Bank Statements

```bash
# Generate all 5 banks at once
python3 main_generator.py --all
```

### Use Custom Data File

```bash
python3 main_generator.py --bank hdfc --data /path/to/custom_data.json
```

### Specify Output Directory

```bash
python3 main_generator.py --bank hdfc --output /path/to/output/dir
```

## Generated Files

PDFs are saved to:
```
output/
├── hdfc/hdfc_statement.pdf
├── icici/icici_statement.pdf
├── sbi/sbi_statement.pdf
├── axis/axis_statement.pdf
└── amex/amex_statement.pdf
```

## Customization

### Modify Existing Data

Edit JSON files in `data/samples/` to change:
- Cardholder name and address
- Transaction amounts and descriptions
- Account balances
- Interest rates
- Payment dates

### JSON Structure

```json
{
  "issuer": {
    "name": "Bank Name",
    "statement_type": "Card Type",
    "contact_phone": "1800 XXX XXXX",
    "website": "bankname.com"
  },
  "cardholder": {
    "name": "Customer Name",
    "address": "Address Line 1\nAddress Line 2\nCity State Pincode"
  },
  "statement_info": {
    "statement_date": "April 17, 2025",
    "statement_balance": 74251.89,
    "statement_period": "March 18, 2025–April 17, 2025",
    "payment_due_date": "May 8, 2025"
  },
  "account_summary": {
    "previous_balance": 42817.50,
    "purchases": 89456.73,
    "cash_advances": 5000.00,
    "interest": 127.66,
    "fees": 500.00,
    "payments": 63650.00,
    "credit_limit": 250000.00,
    "available_credit": 175748.11
  },
  "transactions": [
    {
      "transaction_date": "19 March",
      "posting_date": "21 March",
      "description": "Merchant Name Location",
      "amount": 1234.56
    }
  ],
  "interest_rates": [
    {
      "category": "Purchases",
      "interest_charged": 0.00,
      "annual_rate": 42.00,
      "daily_rate": 0.11507
    }
  ]
}
```

### Create Custom Bank

1. Create new JSON file in `data/samples/`
2. Add bank config to `config.py` BANK_CONFIGS
3. Create generator class in `generators/` extending `BaseStatementGenerator`
4. Add to `main_generator.py` GENERATORS dictionary

## Statement Features

All generated statements include:

### Header Section
- ✓ Bank logo placeholder and name
- ✓ Statement type (e.g., "Cashback credit card statement")

### Key Information Boxes (①-④)
1. Statement date
2. Statement balance
3. Statement period
4. Payment due date

### Statement Details Table (⑤-⑦)
5. Transaction date column
6. Posting date column
7. Account activity (description) column
- Amount column (right-aligned)
- Zebra-striped rows
- Total payment activity row

### Account Summary (⑧-⑯)
8. Previous balance with date
9. +Purchases
10. +Cash advances
11. +Interest
12. +Fees
13. +Other charges
14. -Payments
15. Past due amount
16. Minimum payment
- Statement balance (highlighted)
- Payment due date (boxed)

### Credit Limit Section (⑰-⑱)
17. Credit limit
18. Available credit

### Interest Rates Table
- Category breakdown (Purchases, Cash advances, Fees)
- Interest charged this statement
- Annual interest rate
- Daily interest rate

## Technical Details

### Technology Stack
- **ReportLab**: PDF generation library
- **Python 3.10+**: Core language
- **Pillow**: Image handling (for logos)

### Design Principles
- **Pixel-perfect layout**: Matches reference MD Bank statement
- **Professional typography**: Proper fonts, sizes, and spacing
- **Color consistency**: Bank-specific color schemes
- **Responsive pagination**: Handles variable transaction counts

### Performance
- Generates single statement: ~0.5 seconds
- Generates all 5 banks: ~2 seconds
- Supports 100+ transactions per statement

## System Requirements

**Verified on:**
- OS: Linux (Ubuntu 22.04+)
- Python: 3.10.12
- RAM: 512MB minimum (tested on 14GB system)
- CPU: Any modern processor (tested on 16-core)

## Use Cases

### Development & Testing
- Test transaction parsing algorithms
- Validate data extraction pipelines
- UI/UX mockups for banking apps

### Educational & Training
- Demonstrate credit card statements
- Financial literacy programs
- Banking software training

### Research & Analysis
- Compare statement formats across banks
- Study financial document layouts
- Machine learning training data

## Important Notes

⚠️ **For Development/Testing Only**
- These PDFs are for legitimate development and testing purposes
- Do not use for fraudulent activities
- Generated statements are synthetic and for demonstration only

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the correct directory
cd cc_generator
python3 main_generator.py
```

### Missing Dependencies
```bash
pip3 install --upgrade reportlab Pillow python-dateutil
```

### Permission Errors
```bash
# Ensure output directory is writable
chmod -R 755 output/
```

## Contributing

To add more banks or features:

1. Add sample data JSON
2. Configure bank colors in `config.py`
3. Create generator class (can inherit from BaseStatementGenerator)
4. Update `main_generator.py` to register new bank

## License

This project is for educational and development purposes.

## Support

For issues or questions:
- Check existing sample JSON files for format reference
- Review `config.py` for customization options
- Examine `generators/base_generator.py` for layout logic

## Version

**v1.0.0** - April 2025
- Initial release with 5 major Indian banks
- Complete feature set matching reference design
- Professional-quality PDF output

---

**Note**: Always use this tool responsibly and ethically. The generated PDFs are for testing and development purposes only.
