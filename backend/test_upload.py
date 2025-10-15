#!/usr/bin/env python3
import sys
import traceback
sys.path.insert(0, '.')

# Test the full import chain
try:
    print("Testing imports...")
    from app.core.document.ingestion import DocumentIngestion
    from app.utils.file_utils import validate_pdf_file, get_file_hash, is_pdf_scanned
    
    print("✓ Imports successful")
    
    # Read a PDF file
    with open('/home/ghost/cc-statement-parser/HDFCCCSAMPLE.pdf', 'rb') as f:
        pdf_bytes = f.read()
    
    print(f"✓ Read PDF: {len(pdf_bytes)} bytes")
    
    # Test validation
    is_valid, error = validate_pdf_file(pdf_bytes)
    print(f"✓ Validation: {is_valid}, error: {error}")
    
    # Test hash
    file_hash = get_file_hash(pdf_bytes)
    print(f"✓ Hash: {file_hash[:16]}...")
    
    # Test scanned detection
    is_scanned = is_pdf_scanned(pdf_bytes)
    print(f"✓ Is scanned: {is_scanned}")
    
    # Test ingestion
    ing = DocumentIngestion()
    doc = ing.ingest_file(pdf_bytes, 'test.pdf')
    print(f"✓ Document created: {doc.id}")
    print(f"  Filename: {doc.filename}")
    print(f"  Size: {doc.file_size}")
    print(f"  Hash: {doc.file_hash[:16]}...")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All tests passed!")
