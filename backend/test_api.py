"""Test API endpoint with sample PDFs."""
import requests
import sys
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/api/v1/parse"

def test_pdf(pdf_path: str, bank_name: str):
    """Test parsing a PDF."""
    print(f"\n{'='*60}")
    print(f"Testing {bank_name} PDF: {pdf_path}")
    print('='*60)

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False

    try:
        # Upload PDF
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            response = requests.post(API_URL, files=files, timeout=120)

        if response.status_code != 200:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        result = response.json()

        # Display results
        print(f"\n✅ Parsing successful!")
        print(f"\nJob ID: {result.get('job_id')}")
        print(f"Status: {result.get('status')}")

        if 'result' in result and result['result']:
            res = result['result']
            print(f"\n📊 Extraction Results:")
            print(f"  - Field Count: {res.get('field_count', 0)}")
            print(f"  - Overall Confidence: {res.get('overall_confidence', 0):.2%}")
            print(f"  - Issuer: {res.get('issuer', 'Unknown')}")

            if 'fields' in res:
                print(f"\n📋 Extracted Fields:")
                for field_name, field_data in res['fields'].items():
                    if isinstance(field_data, dict):
                        value = field_data.get('value', 'N/A')
                        conf = field_data.get('confidence', 0)
                        print(f"  - {field_name}: {value} (confidence: {conf:.2%})")
                    else:
                        print(f"  - {field_name}: {field_data}")

            if 'summary' in res:
                print(f"\n💰 Summary:")
                summary = res['summary']
                for key, value in summary.items():
                    print(f"  - {key}: {value}")

        return True

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API at {API_URL}")
        print("Make sure the backend server is running!")
        return False
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
