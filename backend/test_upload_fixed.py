#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("Testing Document Ingestion...")

try:
    from app.core.document.ingestion import DocumentIngestion
    
    # Read a PDF file
    with open('/home/ghost/cc-statement-parser/HDFCCCSAMPLE.pdf', 'rb') as f:
        pdf_bytes = f.read()
    
    print(f"✓ Read PDF: {len(pdf_bytes)} bytes")
    
    # Test ingestion
    ing = DocumentIngestion()
    doc = ing.ingest_file(pdf_bytes, 'HDFCCCSAMPLE.pdf')
    print(f"✓ Document created successfully!")
    print(f"  ID: {doc.id}")
    print(f"  Filename: {doc.filename}")
    print(f"  Size: {doc.file_size}")
    print(f"  Hash: {doc.file_hash[:16]}...")
    print(f"  Is scanned: {doc.is_scanned}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
