import easyocr
import cv2
import re

class CardOCR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract_set_code(self, frame):
        """Extract set code from card image"""
        try:
            # Resize frame for better OCR
            frame = cv2.resize(frame, (800, 600))

            # Convert to grayscale and increase contrast
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # Run OCR
            results = self.reader.readtext(enhanced)

            if not results:
                return None, []

            # Extract text from results
            extracted_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.2:
                    cleaned_text = text.strip()
                    extracted_texts.append((cleaned_text, confidence))
                    print(f"OCR: '{cleaned_text}' (confidence: {confidence:.2f})")

            # Look for set code pattern (e.g., "BP01-EN123")
            set_code = self._find_set_code(extracted_texts)

            return set_code, extracted_texts
        except Exception as e:
            print(f"OCR Error: {e}")
            return None, []

    @staticmethod
    def _correct_ocr_errors(text):
        """Fix common OCR mistakes"""
        text = text.upper()
        # Common OCR confusions
        text = text.replace('O', '0')  # O -> 0
        text = text.replace('I', '1')  # I -> 1
        text = text.replace('L', '1')  # L -> 1
        text = text.replace('S', '5')  # S -> 5
        text = text.replace('B', '8')  # B -> 8
        text = text.replace('Z', '2')  # Z -> 2
        return text

    @staticmethod
    def _find_set_code(texts):
        """Find set code pattern in extracted text"""
        print("Searching for set code in extracted text...")

        for text, confidence in texts:
            text_upper = text.upper()

            # Try exact match first (with common corrections)
            if '-' in text_upper:
                parts = text_upper.split('-')
                if len(parts) >= 2:
                    first = parts[0].strip()
                    second = parts[1].strip()

                    # Correct OCR errors
                    first = CardOCR._correct_ocr_errors(first)
                    second = CardOCR._correct_ocr_errors(second)

                    # First part: 2-4 chars (set code + year, e.g., "BP01")
                    # Second part: 5-6 chars (language code + number, e.g., "EN064")
                    if 2 <= len(first) <= 4 and 5 <= len(second) <= 6:
                        # Validate first part has letters and numbers
                        if any(c.isalpha() for c in first) and any(c.isdigit() for c in first):
                            # Validate second part has letters and numbers
                            if any(c.isalpha() for c in second) and any(c.isdigit() for c in second):
                                code = f"{first}-{second}"
                                print(f"✓ Found set code: {code}")
                                return code

        # Try regex patterns as fallback
        print("Trying regex patterns...")
        full_text = " ".join([text for text, _ in texts])
        full_text_corrected = CardOCR._correct_ocr_errors(full_text)

        # Pattern: 2-4 alphanumeric chars, dash, 2 letters, 3-4 digits
        # More forgiving regex
        patterns = [
            r'([A-Z]{2,4}\d{1,3})[^\w\d]*([A-Z]{2})\s*(\d{3,4})',  # BP01 EN 064
            r'([A-Z]{2,4}\d{1,3})\s*[-/]\s*([A-Z]{2}\d{3,4})',     # Standard format
            r'([A-Z]{2,4}\d{1,3})-([A-Z]{2}\d{3,4})',              # Strict format
        ]

        for pattern in patterns:
            matches = re.findall(pattern, full_text_corrected)
            if matches:
                for match in matches:
                    if len(match) == 3:
                        code = f"{match[0]}-{match[1]}{match[2]}"
                    else:
                        code = f"{match[0]}-{match[1]}"
                    print(f"✓ Found set code (regex): {code}")
                    return code

        print("No set code found")
        return None

