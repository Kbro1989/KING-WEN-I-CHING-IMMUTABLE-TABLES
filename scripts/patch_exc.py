with open('scripts/vision_comparison_pipeline.py', 'rb') as f:
    content = f.read()

# Exact bytes from the file (with CRLF line endings)
old = b"except Exception as e:\r\n            logger.warning(f'Recogntion failed: {e}')\r\n            return None, 0.0, 'recognition_error'\r\n    \r\n    def classify_alignment"

new = b"except Exception as e:\r\n            import traceback\r\n            logger.warning(f'Recogntion failed: {e}')\r\n            traceback.print_exc()\r\n            print(f'DEBUG_EXC: {e}')\r\n            return None, 0.0, 'recognition_error'\r\n    \r\n    def classify_alignment"

if old in content:
    content = content.replace(old, new)
    with open('scripts/vision_comparison_pipeline.py', 'wb') as f:
        f.write(content)
    print('Patched successfully')
else:
    print('Pattern not found')
    print('Looking for:', repr(old[:100]))
