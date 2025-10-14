import fitz  # pip install pymupdf
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import numpy as np

def extract_text_with_ocr(pdf_path, status_callback=None):
    """Extract text from PDF using PaddleOCR as fallback"""
    try:
        if status_callback:
            status_callback(" Initializing PaddleOCR (this may take a moment on first run)...")
        
        # Initialize PaddleOCR
        # use_angle_cls=True to enable text direction classification
        # lang='en' for English
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
        # Convert PDF pages to images
        if status_callback:
            status_callback("Converting PDF pages to images...")
        images = convert_from_path(pdf_path)
        
        if status_callback:
            status_callback(f" Converted {len(images)} pages to images")
        
        extracted_texts = []
        total_detections = 0
        low_confidence_count = 0
        pages_with_text = 0
        
        for i, image in enumerate(images):
            if status_callback:
                status_callback(f" Processing page {i+1}/{len(images)} with OCR...")
            
            # Convert PIL image to numpy array for PaddleOCR
            image_array = np.array(image)
            
            # Use PaddleOCR to extract text
            results = ocr.ocr(image_array)
            
            # Extract text from results
            page_text = []
            page_detections = 0
            page_low_confidence = 0
            
            if results and results[0]:  # Check if results exist
                for line in results[0]:
                    if line and len(line) >= 2:  # Each line should have bbox and text info
                        text_info = line[1]
                        if text_info and len(text_info) >= 2:
                            text = text_info[0]
                            confidence = text_info[1]
                            page_detections += 1
                            total_detections += 1
                            
                            # Only include text with reasonable confidence (>0.5)
                            if confidence > 0.5 and text.strip():
                                page_text.append(text)
                            else:
                                page_low_confidence += 1
                                low_confidence_count += 1
            
            if page_text:
                extracted_texts.append(' '.join(page_text))
                pages_with_text += 1
                if status_callback:
                    status_callback(f"  Page {i+1}: Found {len(page_text)} text segments")
            else:
                if page_detections > 0:
                    if status_callback:
                        status_callback(f"  Page {i+1}: Found {page_detections} detections but all had low confidence")
                else:
                    if status_callback:
                        status_callback(f"   Page {i+1}: No text detected")
        
        # Join all text
        full_text = "\n".join(extracted_texts)
        
        # Provide detailed feedback
        if status_callback:
            status_callback(f"OCR Results: {pages_with_text}/{len(images)} pages had readable text")
            if total_detections > 0:
                status_callback(f" Found {total_detections} total detections ({low_confidence_count} low confidence)")
        
        # Check if we extracted any meaningful text
        if not full_text.strip():
            if status_callback:
                if total_detections == 0:
                    status_callback(" No text detected in any page - document may contain only images")
                else:
                    status_callback(f" All {total_detections} detections had low confidence - text may be unclear")
            return None
            
        if status_callback:
            status_callback(f" Successfully extracted {len(full_text)} characters using OCR")
        return full_text
        
    except Exception as e:
        if status_callback:
            status_callback(f" OCR extraction failed: {str(e)}")
        return None

def extract_text_from_pdf(path, status_callback=None):
    """Extract text from PDF file with OCR fallback and error handling"""
    
    if status_callback:
        status_callback(f" Processing PDF: {os.path.basename(path)}")
    
    # First attempt: Standard text extraction
    try:
        if status_callback:
            status_callback(" Step 1: Trying standard text extraction...")
            
        doc = fitz.open(path)
        texts = []
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():  # Only add non-empty pages
                texts.append(page_text)
        
        doc.close()
        
        # Join all text and clean it up
        full_text = "\n".join(texts)
        
        if status_callback:
            status_callback(f" Standard method found {len(texts)} pages with text, {len(full_text)} total characters")
        
        # Check if we extracted meaningful text (more than just whitespace/minimal content)
        if full_text.strip() and len(full_text.strip()) > 10:
            if status_callback:
                status_callback(f" Standard extraction successful! Using extracted text.")
            return full_text
        else:
            if status_callback:
                status_callback(f" Standard method yielded minimal text, proceeding to OCR...")
            
    except Exception as e:
        if status_callback:
            status_callback(f" Standard method failed ({str(e)}), proceeding to OCR...")
    
    # Second attempt: OCR fallback
    if status_callback:
        status_callback("🔍 Step 2: Trying OCR to extract text from images...")
        
    ocr_text = extract_text_with_ocr(path, status_callback)
    if ocr_text and len(ocr_text.strip()) > 10:
        if status_callback:
            status_callback(" OCR extraction successful! Using OCR text.")
        return ocr_text
    
    # Both methods failed
    if status_callback:
        status_callback(" Both standard and OCR methods failed - no readable text found")
    return None
