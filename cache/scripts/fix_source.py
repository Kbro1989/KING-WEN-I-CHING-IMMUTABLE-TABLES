import os
os.chdir(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

# Find the exact source path discovery block
old = '''        source_path = PDF_DIR / f"{paper}.pdf"
        if not source_path.exists():
            # Try HTML version
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if html_path.exists():
                source_path = html_path
            else:
                # Search for any file matching paper ID (including zotero directory)
                search_paths = [
                    REPO_ROOT,
                    Path("C:/Users/krist/Desktop/zotero"),
                    Path("C:/Users/krist/Desktop/zotero/learning-corpus"),
                ]
                for search_path in search_paths:
                    if search_path.exists():
                        for f in search_path.glob('**/*' + paper + '*'):
                            if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                                source_path = f
                                break
                    if source_path.exists():
                        break
                    logger.info(f"Source search for {paper}: PDF_DIR={PDF_DIR}")
                    logger.info(f"Using source path: {source_path}")'''

new = '''        source_path = PDF_DIR / f"{paper}.pdf"
        if not source_path.exists():
            # Try HTML version
            html_path = REPO_ROOT / 'DATASETS' / f"{paper}.html"
            if html_path.exists():
                source_path = html_path
            else:
                # Search for any file matching paper ID (including zotero directory)
                search_paths = [
                    REPO_ROOT,
                    Path("C:/Users/krist/Desktop/zotero"),
                    Path("C:/Users/krist/Desktop/zotero/learning-corpus"),
                ]
                for search_path in search_paths:
                    if search_path.exists():
                        for f in search_path.glob('**/*' + paper + '*'):
                            if f.is_file() and f.suffix.lower() in ['.pdf', '.html']:
                                source_path = f
                                break
                        if source_path.exists():
                            break
        logger.info(f"Source search for {paper}: PDF_DIR={PDF_DIR}")
        logger.info(f"Using source path: {source_path}")'''

if old in content:
    content = content.replace(old, new)
    with open('scripts/vision_comparison_pipeline.py', 'w') as f:
        f.write(content)
    print('Fixed source path discovery')
else:
    print('Old code not found')
