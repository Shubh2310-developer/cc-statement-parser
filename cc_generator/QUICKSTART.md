# Quick Start Guide

Get started generating professional credit card statement PDFs in 3 simple steps!

## Step 1: Install Dependencies

```bash
cd cc_generator
pip3 install -r requirements.txt
```

**Dependencies:**
- reportlab>=4.0.0 (PDF generation)
- Pillow>=10.0.0 (Image handling)
- python-dateutil>=2.8.0 (Date utilities)

## Step 2: Generate Your First Statement

```bash
# Generate HDFC Bank statement (default)
python3 main_generator.py
```

**Output:** `output/hdfc/hdfc_statement.pdf`

## Step 3: Explore More Options

### Generate Different Banks

```bash
python3 main_generator.py --bank icici   # ICICI Bank
python3 main_generator.py --bank sbi     # SBI Card
python3 main_generator.py --bank axis    # Axis Bank
python3 main_generator.py --bank amex    # American Express
```

### Generate All Banks at Once

```bash
python3 main_generator.py --all
```

Or use the batch script:

```bash
./generate_all.sh
```

**Output:** All 5 PDFs in respective `output/` subdirectories

## Customize Your Data

### Edit Existing Sample

1. Open any JSON file: `data/samples/hdfc_sample.json`
2. Modify values:
   - Change cardholder name
   - Update transaction amounts
   - Add/remove transactions
   - Adjust balances
3. Regenerate PDF: `python3 main_generator.py --bank hdfc`

### Use Custom Data File

```bash
python3 main_generator.py --bank hdfc --data /path/to/my_data.json
```

## What Gets Generated?

Each PDF includes:
- ✅ Professional header with bank branding
- ✅ Cardholder information
- ✅ 4 key info boxes (statement date, balance, period, due date)
- ✅ Complete transaction table with zebra striping
- ✅ Account summary with all charges/credits
- ✅ Credit limit and available balance
- ✅ Interest rates breakdown
- ✅ Numbered indicators (①-⑱) matching real statements

## File Sizes

Typical PDF sizes:
- ~5KB per statement (very lightweight!)
- Fast generation (~0.5 seconds each)

## Verification

Check generated files:

```bash
ls -lh output/*/*.pdf
```

Expected output:
```
output/hdfc/hdfc_statement.pdf   (~5.6KB)
output/icici/icici_statement.pdf (~5.3KB)
output/sbi/sbi_statement.pdf     (~5.0KB)
output/axis/axis_statement.pdf   (~5.1KB)
output/amex/amex_statement.pdf   (~5.2KB)
```

## View PDFs

```bash
# Linux
xdg-open output/hdfc/hdfc_statement.pdf

# macOS
open output/hdfc/hdfc_statement.pdf

# Or use your preferred PDF viewer
```

## Troubleshooting

### "No module named 'reportlab'"

```bash
pip3 install reportlab
```

### "Permission denied"

```bash
chmod +x generate_all.sh
```

### "FileNotFoundError"

Make sure you're in the `cc_generator` directory:

```bash
cd cc_generator
python3 main_generator.py
```

## Next Steps

1. ✅ Generate your first PDF ← You're here!
2. 📝 Customize data in `data/samples/` files
3. 🎨 Modify colors in `config.py` (optional)
4. 🔧 Extend with new banks (see README.md)

## Help

```bash
python3 main_generator.py --help
```

## Summary of Commands

```bash
# Single bank
python3 main_generator.py --bank hdfc

# All banks
python3 main_generator.py --all

# Custom data
python3 main_generator.py --bank hdfc --data custom.json

# Custom output location
python3 main_generator.py --bank hdfc --output /tmp/statements
```

---

**That's it!** You now have professional credit card statement PDFs ready for your project.

For detailed documentation, see [README.md](README.md)
