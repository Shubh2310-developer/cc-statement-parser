"""
Main entry point for CC statement PDF generation
"""
import sys
import os
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generators.hdfc_generator import HDFCGenerator
from generators.icici_generator import ICICIGenerator
from generators.sbi_generator import SBIGenerator
from generators.axis_generator import AxisGenerator
from generators.amex_generator import AmexGenerator
import config

GENERATORS = {
    'hdfc': HDFCGenerator,
    'icici': ICICIGenerator,
    'sbi': SBIGenerator,
    'axis': AxisGenerator,
    'amex': AmexGenerator
}

def generate_statement(bank_code, data_file=None, output_dir=None):
    """Generate statement for any bank"""
    bank_code = bank_code.lower()

    if bank_code not in GENERATORS:
        raise ValueError(f"Unknown bank: {bank_code}")

    if data_file is None:
        data_file = os.path.join(config.DATA_DIR, 'samples', f'{bank_code}_sample.json')

    if output_dir is None:
        output_dir = os.path.join(config.OUTPUT_DIR, bank_code)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f'{bank_code}_statement.pdf')

    print(f"Generating {bank_code.upper()} statement from {data_file}")
    generator = GENERATORS[bank_code](data_file)
    generator.create_pdf(output_file)

    return output_file

def generate_all_statements():
    """Generate statements for all banks"""
    results = []
    for bank_code in GENERATORS.keys():
        try:
            output_file = generate_statement(bank_code)
            results.append((bank_code, output_file, True))
            print(f"✓ {bank_code.upper()}: {output_file}")
        except Exception as e:
            results.append((bank_code, str(e), False))
            print(f"✗ {bank_code.upper()}: {e}")
    return results

def main():
    parser = argparse.ArgumentParser(description='Generate Credit Card Statement PDFs')
    parser.add_argument('--bank', type=str, default=None,
                       help='Bank code (hdfc, icici, sbi, axis, amex) or "all" for all banks')
    parser.add_argument('--data', type=str, default=None,
                       help='Path to JSON data file')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory')
    parser.add_argument('--all', action='store_true',
                       help='Generate statements for all banks')

    args = parser.parse_args()

    if args.all or (args.bank and args.bank.lower() == 'all'):
        print("Generating statements for all banks...\n")
        results = generate_all_statements()
        print(f"\n{'='*60}")
        print(f"Generated {sum(1 for r in results if r[2])}/{len(results)} statements successfully")
    elif args.bank:
        try:
            output_file = generate_statement(args.bank, args.data, args.output)
            print(f"\n✓ Successfully generated: {output_file}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    else:
        # Default: generate HDFC
        output_file = generate_statement('hdfc', args.data, args.output)
        print(f"\n✓ Successfully generated: {output_file}")

if __name__ == '__main__':
    main()
