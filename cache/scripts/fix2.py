import os
os.chdir('C:/Users/krist/Desktop/KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Fix the broken section
old = """        # Crop PDF region or render HTML page using bbox coordinates
        source_path = pdf_path  # this is actually the source path (PDF or HTML)
        
        # Locate actual source file (PDF or HTML)
        if source_path == PDF_DIR / f"{paper}.pdf" and not source_path.exists():
            # Find HTML version
            html_candidates = sorted(REPO_ROOT.glob('DATASETS/*.html'))
            for eh in html_candidates:
                if paper.lower() in eh.name.lower() or eh.name.lower().startswith(paper.lower()):
                    source_path = eh
                    break
            
            # Also check exact paper.html if PDF doesn't exist
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if source_path == PDF_DIR / f"{paper}.pdf" and html_path.exists():
                source_path = html_path
        
        if not source_path.exists():
            logger.warning(f"Source not found: {source_path}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'source_missing',
                'method': 'source_missing'
            }
        
        # PyMuPDF can render HTML pages but coordinates differ from PDF
        # For HTML: use PyMuPDF page.get_pixmap() with matrix to scale coordinates
        try:
            is_html = source_path.suffix.lower() == '.html'
            is_pdf = source_path.suffix.lower() == '.pdf'
            
            if not is_pdf and not is_html:
                return {
                    'paper': paper,
                    'page': page,
                    'bbox': bbox,
                    'source_text': source_text,
                    'classification': classification,
                    'crop': None,
                    'recognized': '',
                    'confidence': 0.0,
                    'alignment': 'source_missing',
                    'method': 'source_missing'
                }
            
            # Convert bbox from PDF points to PyMuPDF coordinates
            # PDF coordinates are 72 pts per inch
            scale = 1.0  # adjustment factor for rendering quality
            rect = fitz.Rect(bbox['x0'] * scale, bbox['y0'] * scale,
                           bbox['x1'] * scale, bbox['y1'] * scale)
            
            if is_pdf and source_path.suffix.lower() == '.pdf':
                doc = fitz.open(str(source_path))
                page = doc[0]  # assume single page for now
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=rect)
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    doc.close()
                    return img
                except Exception as e:
                    doc.close()
                    logger.warning(f"Crop failed for PDF: {e}")
                    return None
            else:
                # HTML: render page at specific coordinates
                # Use PyMuPDF to parse HTML and render specific region
                # HTML coordinates are CSS pixels, need to account for scaling
                doc = fitz.open(str(source_path))
                if doc.page_count > 0:
                    page = doc[0]
                    # Render at higher resolution for better OCR
                    zoom = 4.0  # 4x zoom
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                    img_array = np.frombuffer(pix.samples, dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    doc.close()
                    return img
                doc.close()
                logger.warning(f"Failed to render HTML: {source_path}")
                return None
                
        except Exception as e:
            logger.warning(f"Crop failed: {e}")
            return None
        
        crop = self.crop_pdf_region(pdf_path, bbox)
        if crop is None:
            logger.warning(f"Failed to crop region for {paper} p{page}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'crop_failed',
                'method': 'crop_failed'
            }
        
        # Run Pix2Text
        recognized_text, confidence, method = self.recognize_formula(crop)
        
        # Classify alignment
        alignment_class, description = self.classify_alignment(source_text, recognized_text, bbox)
        
        # Cross-reference with symbols.zip catalog
        matched_glyphs = []
        for glyph in self.glyph_catalog:
            if glyph.get('name') and source_text in glyph['name']:
                matched_glyphs.append(glyph['name'])
        
        result = {
            'paper': paper,
            'page': page,
            'bbox': bbox,
            'source_text': source_text,
            'classification': classification,
            'crop': crop,
            'recognized': recognized_text,
            'confidence': confidence,
            'alignment': alignment_class,
            'method': method,
            'matched_glyphs': matched_glyphs,
            'surveyed': 0
        }
        
        self.comparisons.append(result)
        self.success += 1
        
        return result"""

new = """        # Locate actual source file (PDF or HTML)
        source_path = PDF_DIR / f"{paper}.pdf"
        if not source_path.exists():
            # Try HTML version
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if html_path.exists():
                source_path = html_path
            else:
                # Search for any file matching paper ID
                for f in REPO_ROOT.glob('**/*' + paper + '*'):
                    if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                        source_path = f
                        break
        
        if not source_path.exists():
            logger.warning(f"Source not found: {source_path}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'source_missing',
                'method': 'source_missing'
            }
        
        # Crop PDF region using bbox coordinates (PDF points)
        crop = self.crop_pdf_region(source_path, bbox, padding=15, zoom=8)
        if crop is None:
            logger.warning(f"Failed to crop region for {paper} p{page}")
            return {
                'paper': paper,
                'page': page,
                'bbox': bbox,
                'source_text': source_text,
                'classification': classification,
                'crop': None,
                'recognized': '',
                'confidence': 0.0,
                'alignment': 'crop_failed',
                'method': 'crop_failed'
            }
        
        # Run Pix2Text
        recognized_text, confidence, method = self.recognize_formula(crop)
        
        # Classify alignment
        alignment_class, description = self.classify_alignment(source_text, recognized_text, bbox)
        
        # Cross-reference with symbols.zip catalog
        matched_glyphs = []
        if source_text:
            # Extract individual symbols from the line text
            symbols = self._extract_symbols(source_text)
            for symbol, symbol_type, catalog_match in symbols:
                if catalog_match and catalog_match in self.by_name:
                    glyph = self.by_name[catalog_match]
                    matched_glyphs.append(glyph['name'])
        if not matched_glyphs:
            # Check for simple name match (e.g., source_text is a catalog name)
            src_lower = source_text.strip().lower()
            if src_lower in self.by_name:
                matched_glyphs.append(self.by_name[src_lower]['name'])
        if not matched_glyphs:
            # Try alt field match
            src_lower = source_text.strip().lower()
            if src_lower in self.by_alt:
                matched_glyphs.append(self.by_alt[src_lower]['name'])
        
        result = {
            'paper': paper,
            'page': page,
            'bbox': bbox,
            'source_text': source_text,
            'classification': classification,
            'crop': crop,
            'recognized': recognized_text,
            'confidence': confidence,
            'alignment': alignment_class,
            'method': method,
            'matched_glyphs': matched_glyphs,
            'surveyed': 0
        }
        
        self.comparisons.append(result)
        self.success += 1
        
        return result"""

if old in content:
    content = content.replace(old, new)
    print("Replaced")
else:
    print("old not found!")

with open('scripts/vision_comparison_pipeline.py', 'w') as f:
    f.write(content)
