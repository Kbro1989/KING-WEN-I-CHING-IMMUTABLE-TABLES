import os
os.chdir(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    lines = f.readlines()

# Find the line with 'crop_rgb'
start = None
end = None
for i, line in enumerate(lines):
    if 'crop_rgb = cv2.cvtColor' in line:
        start = i
    if 'recognition_error' in line and i > start:
        end = i + 1
        break

print(f'Replacing lines {start+1} to {end} ({end - start} lines)')

# New lines to replace
new_lines = [
    '        import tempfile\n',
    '        try:\n',
    '            # Save crop as temp image file\n',
    '            tmpfile = tempfile.NamedTemporaryFile(suffix=\'.png\', delete=False)\n',
    '            tmpfile_path = tmpfile.name\n',
    '            tmpfile.close()\n',
    '            cv2.imwrite(tmpfile_path, crop)\n',
    '            result = self.pix2text.recognize_formula(tmpfile_path)\n',
    '            os.remove(tmpfile_path)\n',
    "            if result:\n",
    "                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'\n",
    "            else:\n",
    "                return '', 0.0, 'empty'\n",
    '        except Exception as e:\n',
    "        logger.warning(f'Recogntion failed: {{e}}')\n",
    "        return None, 0.0, 'recognition_error'\n",
]

# Replace the lines
lines = lines[:start] + new_lines + lines[end+1:]

with open('scripts/vision_comparison_pipeline.py', 'w') as f:
    f.writelines(lines)

print('Fixed recognize_formula successfully')
