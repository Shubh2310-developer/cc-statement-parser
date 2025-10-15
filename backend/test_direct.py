"""Direct test of parsing service."""
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/home/ghost/cc-statement-parser/backend')

from app.services.parsing_service import ParsingService

async def test_pdf(pdf_path: str, bank_name: str):
    """Test parsing a PDF directly."""
    print(f"\n{'='*60}")
    print(f"Testing {bank_name} PDF: {pdf_path}")
    print('='*60)

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False

    try:
        # Read PDF
        with open(pdf_file, 'rb') as f:
            pdf_bytes = f.read()

        # Create service
        service = ParsingService()

        # Parse document
        print("🔄 Parsing document...")
        result = await service.parse_document(pdf_bytes, pdf_file.name)

        print(f"\n✅ Parsing successful!")
        print(f"\nJob ID: {result.id}")
        print(f"Status: {result.status.value}")

        if result.extraction_result:
            res = result.extraction_result
            print(f"\n📊 Extraction Results:")
            print(f"  - Field Count: {res.field_count}")
            print(f"  - Overall Confidence: {res.overall_confidence:.2%}")
            print(f"  - Issuer: {res.issuer.value if res.issuer else 'Unknown'}")

            print(f"\n📋 Extracted Fields ({len(res.fields)}):")
            for field_name, field in res.fields.items():
                print(f"  - {field_name}: {field.value} (confidence: {field.confidence:.2%})")

        else:
            print(f"❌ No extraction result")
            if result.error_message:
                print(f"Error: {result.error_message}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Test all PDFs."""
    base_dir = Path("/home/ghost/cc-statement-parser")

    pdfs = [
        (base_dir / "HDFCCCSAMPLE.pdf", "HDFC"),
        # (base_dir / "ICICICCSAMPLE.pdf", "ICICI"),
        # (base_dir / "AXISCCSAMPLE.pdf", "Axis"),
        # (base_dir / "AmexCCSample.pdf", "Amex"),
    ]

    results = []
    for pdf_path, bank_name in pdfs:
        success = await test_pdf(str(pdf_path), bank_name)
        results.append((bank_name, success))

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for bank_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{bank_name:10} {status}")

    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
