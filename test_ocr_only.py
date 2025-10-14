#!/usr/bin/env python3
"""
Test OCR functionality directly
"""

import sys
import os
sys.path.append('.')

from src.pdf_parser import extract_text_with_ocr

def test_ocr_directly():
    """Test OCR extraction directly on a PDF"""
    
    # Look for any PDF in the uploads directory
    upload_dir = "./data/uploads"
    if not os.path.exists(upload_dir):
        print("❌ No uploads directory found")
        return
    
    pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in uploads directory")
        print("Please upload a PDF through the web interface first")
        return
    
    pdf_path = os.path.join(upload_dir, pdf_files[0])
    print(f"🔍 Testing OCR on: {pdf_files[0]}")
    print("=" * 50)
    
    def status_callback(message):
        print(f"📝 {message}")
    
    try:
        # Test OCR directly
        result = extract_text_with_ocr(pdf_path, status_callback)
        
        if result:
            print(f"\n✅ OCR Success! Extracted {len(result)} characters")
            print("First 200 characters:")
            print("-" * 30)
            print(result[:200] + "..." if len(result) > 200 else result)
        else:
            print("\n❌ OCR failed to extract any text")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_ocr_directly()