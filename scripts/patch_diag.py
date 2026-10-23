with open('scripts/vision_comparison_pipeline.py', 'rb') as f:
    content = f.read()

old = b'''except Exception as e:
            logger.warning(f'Recogntion failed: {e}')
            return None, 0.0, 'recognition_error''''

new = b'''except Exception as e:
            import traceback
            logger.warning(f'Recogntion failed: {e}')
            traceback.print_exc()
            print(f'DEBUG_EXC: {e}')
            return None, 0.0, 'recognition_error''''

if old in content:
    content = content.replace(old, new)
    with open('scripts/vision_comparison_pipeline.py', 'wb') as f:
        f.write(content)
    print('Patched successfully')
else:
    print('Pattern not found')
