"""Test extraction orchestrator directly."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/home/ghost/cc-statement-parser/backend')

from app.core.extraction.orchestrator import ExtractionOrchestrator

def test_pdf(pdf_path: str, bank_name: str):
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

        # Create orchestrator
        orchestrator = ExtractionOrchestrator()

        # Extract
        print("🔄 Extracting fields...")
        result = orchestrator.orchestrate(pdf_bytes)

        print(f"\n✅ Extraction successful!")
        print(f"\n📊 Extraction Results:")
        print(f"  - Field Count: {result.field_count}")
        print(f"  - Overall Confidence: {result.overall_confidence:.2%}")
        print(f"  - Issuer: {result.issuer.value if result.issuer else 'Unknown'}")

        print(f"\n📋 Extracted Fields ({len(result.fields)}):")
        for field_name, field in result.fields.items():
            print(f"  - {field_name}: {field.value} (confidence: {field.confidence:.2%})")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all PDFs."""
    base_dir = Path("/home/ghost/cc-statement-parser")

    pdfs = [
        (base_dir / "HDFCCCSAMPLE.pdf", "HDFC"),
        (base_dir / "ICICICCSAMPLE.pdf", "ICICI"),
        (base_dir / "AXISCCSAMPLE.pdf", "Axis"),
        (base_dir / "AmexCCSample.pdf", "Amex"),
    ]

    results = []
    for pdf_path, bank_name in pdfs:
        success = test_pdf(str(pdf_path), bank_name)
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
    sys.exit(main())
