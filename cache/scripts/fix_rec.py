import os
os.chdir(r'C:\Users\krist\Desktop\KING-WEN-I-CHING-IMMUTABLE-TABLES')

with open('scripts/vision_comparison_pipeline.py', 'r') as f:
    content = f.read()

old = '''    def recognize_formula(self, crop):
        """
        Run Pix2Text on the crop and get reconstructed LaTeX.
        Returns: (reconstructed_text, confidence, method)
        """
        if crop is None:
            return None, 0.0, 'crop_failed'
        
        try:
            # Pix2Text recognize_formula expects a numpy array
            # Convert BGR to RGB for pix2text
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            result = self.pix2text.recognize_formula(crop_rgb)
            if result:
                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'
            else:
                return '', 0.0, 'empty'
        except Exception as e:
            logger.warning(f"Recognition failed: {e}")
            return None, 0.0, 'recognition_error' '''

new = '''    def recognize_formula(self, crop):
        """
        Run Pix2Text on the crop and get reconstructed LaTeX.
        Returns: (reconstructed_text, confidence, method)
        """
        if crop is None:
            return None, 0.0, 'crop_failed'
        
        try:
            # Pix2Text recognize_formula expects a filename, not numpy array
            import tempfile
            tmpfile = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            tmpfile_path = tmpfile.name
            tmpfile.close()
            cv2.imwrite(tmpfile_path, crop)
            result = self.pix2text.recognize_formula(tmpfile_path)
            os.remove(tmpfile_path)
            if result:
                return result.get('text', ''), result.get('confidence', 0.0), 'pix2text'
            else:
                return '', 0.0, 'empty'
        except Exception as e:
            logger.warning(f'Recogntion failed: {e}')
            return None, 0.0, 'recognition_error' '''

if old in content:
    content = content.replace(old, new)
    with open('scripts/vision_comparison_pipeline.py', 'w') as f:
        f.write(content)
    print('Fixed recognize_formula')
else:
    print('old_code not found')
