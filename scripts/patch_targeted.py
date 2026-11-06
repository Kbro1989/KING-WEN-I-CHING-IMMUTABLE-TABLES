import re

with open('scripts/targeted_depth_ocr.py', 'r') as f:
    content = f.read()

# 1. Replace detect_tall_regions function
old_detect = '''def detect_tall_regions(depth_img, min_height_px=60, min_width_px=20, max_width_px=200):
    """Detect tall narrow regions in the depth map.

    Tall regions (high vertical extent, moderate width) correspond to
    stretched symbols: large braces, tall fractions, multi-line delimiters.
    Returns list of (x, y, w, h) in depth-image coordinates.
    """
    gray = cv2.cvtColor(depth_img, cv2.COLOR_BGR2GRAY) if len(depth_img.shape) == 3 else depth_img
    h, w = gray.shape[:2]

    # Threshold to find high-depth (foreground) regions
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    # Morphological close to connect nearby vertical strokes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = rh / max(rw, 1)

        # Tall region: height >= min_height, width within range, aspect ratio > 2
        if rh >= min_height_px and min_width_px <= rw <= max_width_px and aspect > 2.0 and area > 200:
            regions.append({
                "bbox": (int(x), int(y), int(rw), int(rh)),
                "area": int(area),
                "aspect_ratio": round(aspect, 2),
                "centroid": (float(centroids[i][0]), float(centroids[i][1])),
            })

    # Sort by vertical position (top to bottom)
    regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
    return regions'''

new_detect = '''def detect_tall_regions(img, min_height_px=60, min_width_px=10, max_width_px=100):
    """Detect tall narrow regions (stretched symbols: braces, delimiters).

    Uses the ORIGINAL page image for region detection. Tall narrow regions
    with high aspect ratio correspond to multi-line symbols that Pix2Text
    struggles with.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape[:2]

    # Detect text lines to compute average line height
    row_sums = np.sum(gray < 128, axis=1)
    lines = []
    in_line = False
    start = 0
    for i, s in enumerate(row_sums):
        if s > 0 and not in_line:
            in_line = True
            start = i
        elif s == 0 and in_line:
            in_line = False
            if i - start > 3:
                lines.append((start, i))
    if in_line and len(row_sums) - start > 3:
        lines.append((start, len(row_sums)))
    avg_lh = np.median([e - s for s, e in lines]) if lines else 20

    text_mask = (gray < 128).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = rh / max(rw, 1)

        if rh > 3 * avg_lh and min_width_px <= rw <= max_width_px and aspect > 2.5 and area > 100:
            regions.append({
                "bbox": (int(x), int(y), int(rw), int(rh)),
                "area": int(area),
                "aspect_ratio": round(aspect, 2),
                "height_lines": round(rh / avg_lh, 1),
                "centroid": (float(centroids[i][0]), float(centroids[i][1])),
                "type": "tall_narrow",
            })

    regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
    return regions, avg_lh


def detect_wide_regions(img, min_width_px=200, min_height_px=20):
    """Detect wide regions (multi-line expressions, fraction bars)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape[:2]

    row_sums = np.sum(gray < 128, axis=1)
    lines = []
    in_line = False
    start = 0
    for i, s in enumerate(row_sums):
        if s > 0 and not in_line:
            in_line = True
            start = i
        elif s == 0 and in_line:
            in_line = False
            if i - start > 3:
                lines.append((start, i))
    if in_line and len(row_sums) - start > 3:
        lines.append((start, len(row_sums)))
    avg_lh = np.median([e - s for s, e in lines]) if lines else 20

    text_mask = (gray < 128).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    closed = cv2.morphologyEx(text_mask, cv2.MORPH_CLOSE, kernel)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)

    regions = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        rw = stats[i, cv2.CC_STAT_WIDTH]
        rh = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 500:
            continue
        if rw > 10 * avg_lh and rh > avg_lh:
            regions.append({
                "bbox": (int(x), int(y), int(rw), int(rh)),
                "area": int(area),
                "aspect_ratio": round(rw / rh, 1),
                "width_lines": round(rw / avg_lh, 1),
                "height_lines": round(rh / avg_lh, 1),
                "centroid": (float(centroids[i][0]), float(centroids[i][1])),
                "type": "wide",
            })

    regions.sort(key=lambda r: (r["bbox"][1], r["bbox"][0]))
    return regions, avg_lh'''

content = content.replace(old_detect, new_detect)

# 2. Replace crop_and_ocr function
old_crop = '''def crop_and_ocr(paper_id, page_num, regions, high_zoom=8):
    pdf_path = PDF_DIR / f"{paper_id}.pdf"
    if not pdf_path.exists():
        print(f"  No PDF: {pdf_path}")
        return []

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_num - 1]
    page_rect = page.rect

    depth_img = load_depth_map(paper_id, page_num)
    if depth_img is None:
        doc.close()
        return []

    results = []
    for idx, region in enumerate(regions):'''

new_crop = '''def crop_and_ocr(paper_id, page_num, regions, high_zoom=8):
    pdf_path = PDF_DIR / f"{paper_id}.pdf"
    if not pdf_path.exists():
        print(f"  No PDF: {pdf_path}")
        return []

    doc = pymupdf.open(str(pdf_path))
    page = doc[page_num - 1]
    page_rect = page.rect

    pix4 = page.get_pixmap(matrix=pymupdf.Matrix(4, 4))
    img4 = np.frombuffer(pix4.tobytes("png"), dtype=np.uint8)
    img4 = cv2.imdecode(img4, cv2.IMREAD_COLOR)

    results = []
    for idx, region in enumerate(regions):'''

content = content.replace(old_crop, new_crop)

# 3. Replace pdf_rect call
content = content.replace(
    '        pdf_rect = pdf_rect_from_depth_bbox(bbox, depth_img.shape, page_rect)',
    '        pdf_rect = pdf_rect_from_depth_bbox(bbox, img4.shape, page_rect)'
)

# 4. Replace main() detection block
old_main = '''        regions = detect_tall_regions(depth_img, min_height_px=args.min_height)
        print(f"  Detected {len(regions)} tall regions in depth map")

        if not regions:
            print("  No tall regions found, skipping")
            continue

        results = crop_and_ocr(paper_id, page_num, regions, high_zoom=args.zoom)'''

new_main = '''        doc = pymupdf.open(str(PDF_DIR / f"{paper_id}.pdf"))
        page = doc[page_num - 1]
        pix4 = page.get_pixmap(matrix=pymupdf.Matrix(4, 4))
        img4 = np.frombuffer(pix4.tobytes("png"), dtype=np.uint8)
        img4 = cv2.imdecode(img4, cv2.IMREAD_COLOR)
        doc.close()

        tall_regions, avg_lh = detect_tall_regions(img4, min_height_px=args.min_height)
        wide_regions, _ = detect_wide_regions(img4)
        all_regions = tall_regions + wide_regions
        print(f"  Detected {len(tall_regions)} tall + {len(wide_regions)} wide regions (avg line height: {avg_lh:.0f}px)")

        if not all_regions:
            print("  No regions found, skipping")
            continue

        results = crop_and_ocr(paper_id, page_num, all_regions, high_zoom=args.zoom)'''

content = content.replace(old_main, new_main)

# 5. Remove load_depth_map usage in crop_and_ocr (already removed above)
content = content.replace(
    '''    depth_img = load_depth_map(paper_id, page_num)
    if depth_img is None:
        doc.close()
        return []

''', '')

with open('scripts/targeted_depth_ocr.py', 'w') as f:
    f.write(content)
print("Patched successfully")
