"""
Blueprint Image Estimator Service
Uses OCR and Vision models to extract dimensions from blueprint images
"""

import re
import base64
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import pytesseract
import cv2
import numpy as np

class BlueprintImageEstimator:
    """
    Extract dimensions from blueprint images using OCR and Vision models
    Each image represents one floor
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.llava_model = "llava:latest"  # Vision model
    
    def extract_dimensions_from_images(self, image_files: list) -> dict:
        """
        Extract dimensions from multiple blueprint images
        Each image represents ONE FLOOR
        
        Args:
            image_files: List of image file objects (one per floor)
            
        Returns:
            dict: {
                'floors': number of images,
                'area_per_floor_sqft': average area per floor,
                'total_area_sqft': CRITICAL - this is already total (area_per_floor × floors),
                'dimensions_extracted': list of dimensions per floor
            }
            
        Raises:
            ValueError: If dimensions cannot be extracted from any image
        """
        
        floors = len(image_files)
        floor_areas = []
        dimensions_per_floor = []
        extraction_failures = []
        
        for idx, image_file in enumerate(image_files):
            try:
                # Try OCR first (primary method)
                dimensions = self._extract_with_ocr(image_file)
                
                # Fallback to vision model if OCR fails
                if not dimensions:
                    dimensions = self._extract_with_vision_model(image_file)
                
                # If both methods fail, try contour detection
                if not dimensions:
                    dimensions = self._extract_with_contours(image_file)
                
                # If all methods fail, raise error
                if not dimensions:
                    extraction_failures.append(f"Floor {idx + 1}: No dimensions found")
                    continue
                
                # Calculate floor area from dimensions
                floor_area = self._calculate_floor_area(dimensions)
                
                print(f"Floor {idx + 1} - Extracted floor area: {floor_area} sqft")
                
                floor_areas.append(floor_area)
                dimensions_per_floor.append({
                    'floor': idx + 1,
                    'dimensions': dimensions,
                    'area_sqft': floor_area
                })
                
            except Exception as e:
                print(f"Error processing floor {idx + 1}: {str(e)}")
                extraction_failures.append(f"Floor {idx + 1}: {str(e)}")
        
        # If no dimensions were extracted from any image, raise error
        if not floor_areas:
            error_msg = "Blueprint dimensions could not be extracted. Please upload clearer blueprints. " + \
                       "Errors: " + "; ".join(extraction_failures)
            raise ValueError(error_msg)
        
        # CRITICAL: Calculate average area per floor
        area_per_floor_sqft = sum(floor_areas) / len(floor_areas)
        
        # Total area is sum of all floors (already calculated)
        total_area_sqft = sum(floor_areas)
        
        print(f"Total sqft: {total_area_sqft}")
        
        return {
            'floors': floors,
            'area_per_floor_sqft': round(area_per_floor_sqft, 2),
            'total_area_sqft': round(total_area_sqft, 2),
            'dimensions_extracted': dimensions_per_floor
        }
    
    def _extract_with_vision_model(self, image_file) -> list:
        """
        Use LLaVA vision model to extract dimensions from blueprint
        """
        try:
            # Read image and convert to base64
            image_data = image_file.read()
            image_file.seek(0)  # Reset file pointer
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prompt for LLaVA
            prompt = """Analyze this construction blueprint image and extract ALL room dimensions.
Look for measurements like:
- 16 x 20 (feet)
- 14 x 13
- 23 x 33
- Any numbers followed by 'x' or '×' and another number

List ALL dimensions you find in the format: length x width
Return ONLY the dimensions, one per line, no explanations."""

            payload = {
                "model": self.llava_model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                vision_response = result.get('response', '')
                
                # Parse dimensions from response
                dimensions = self._parse_dimensions(vision_response)
                
                if dimensions:
                    return dimensions
                    
        except Exception as e:
            print(f"Vision model error: {str(e)}")
        
        return []
    
    def _extract_with_ocr(self, image_file) -> list:
        """
        Primary method: Use OCR (pytesseract) to extract text and find dimensions
        Enhanced with image preprocessing for better accuracy
        """
        try:
            # Open image with PIL
            image = Image.open(image_file)
            image_file.seek(0)  # Reset file pointer
            
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Enhance contrast
            gray = cv2.equalizeHist(gray)
            
            # Apply thresholding to make text clearer
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Convert back to PIL for pytesseract
            enhanced_image = Image.fromarray(denoised)
            
            # Extract text using OCR with custom config
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(enhanced_image, config=custom_config)
            
            print(f"OCR extracted text: {text[:200]}...")  # Debug logging
            
            # Parse dimensions from OCR text
            dimensions = self._parse_dimensions(text)
            
            if dimensions:
                print(f"OCR found {len(dimensions)} room dimensions")
            
            return dimensions
            
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return []
    
    def _parse_dimensions(self, text: str) -> list:
        """
        Parse dimensions from text
        Looks for patterns like: 16 x 20, 14x13, 23 × 33, 13' 2" × 14' 2"
        """
        dimensions = []
        
        # Pattern 1: Feet and inches format with various OCR variations
        # OCR often reads ' as ° or other symbols, and may concatenate numbers
        # Examples: "13° 2" x 142"", "27 11" x 31° 4"", "16 0" x 20° 0""
        
        feet_inches_patterns = [
            # Pattern for "30° 0" x 50° 0"" (space between degree and number)
            r"(\d+)['\°′`]\s+(\d{1,2})[\"″]?\s*[xX×]\s*(\d+)['\°′`]\s+(\d{1,2})[\"″]?",
            # Standard: 13' 2" x 14' 2" (with various quote symbols)
            r"(\d+)['\°′`]\s*(\d{1,2})?[\"″]?\s*[xX×]\s*(\d+)['\°′`]\s*(\d{1,2})?[\"″]?",
            # Concatenated: 13° 2" x 142" (second part concatenated)
            r"(\d+)['\°′`]\s*(\d{1,2})?[\"″]?\s*[xX×]\s*(\d{1,2})(\d{1,2})[\"″]",
            # Space separated: 13 2 x 14 2 or 27 11 x 31 4
            r"(\d+)\s+(\d{1,2})\s*[xX×]\s*(\d+)\s+(\d{1,2})",
            # Mixed: 27 11" x 31° 4"
            r"(\d+)\s+(\d{1,2})[\"″]?\s*[xX×]\s*(\d+)['\°′`]\s*(\d{1,2})?[\"″]?",
            # Another mixed: 16 0" x 20° 0" or 30° 0" x 50° 0"
            r"(\d+)['\°′`]?\s*(\d{1,2})[\"″°′`]?\s*[xX×]\s*(\d+)['\°′`]?\s*(\d{1,2})[\"″°′`]?",
        ]
        
        for pattern in feet_inches_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    # Convert feet and inches to decimal feet
                    feet1 = int(match[0])
                    inches1 = int(match[1]) if match[1] and match[1].strip() else 0
                    feet2 = int(match[2])
                    inches2 = int(match[3]) if match[3] and match[3].strip() else 0
                    
                    length = feet1 + (inches1 / 12)
                    width = feet2 + (inches2 / 12)
                    
                    # Filter out unrealistic dimensions
                    if 5 <= length <= 100 and 5 <= width <= 100:
                        # Check if this dimension is already added (avoid duplicates)
                        is_duplicate = any(
                            abs(d['length'] - length) < 0.5 and abs(d['width'] - width) < 0.5
                            for d in dimensions
                        )
                        
                        if not is_duplicate:
                            dimensions.append({
                                'length': round(length, 2),
                                'width': round(width, 2)
                            })
                            print(f"Found dimension (feet-inches): {length:.2f} × {width:.2f} ft")
                except (ValueError, IndexError, AttributeError):
                    continue
        
        # Pattern 2: Simple decimal format (16 x 20, 14.5×13)
        simple_patterns = [
            r'(\d+\.?\d*)\s*[xX×]\s*(\d+\.?\d*)',  # 16 x 20 or 16×20
            r'(\d+\.?\d*)\s*[*]\s*(\d+\.?\d*)',   # 16 * 20
            r'(\d+\.?\d*)\s+by\s+(\d+\.?\d*)',    # 16 by 20
        ]
        
        for pattern in simple_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    length = float(match[0])
                    width = float(match[1])
                    
                    # Filter out unrealistic dimensions
                    if 5 <= length <= 100 and 5 <= width <= 100:
                        # Check if this dimension is already added (avoid duplicates)
                        is_duplicate = any(
                            abs(d['length'] - length) < 0.5 and abs(d['width'] - width) < 0.5
                            for d in dimensions
                        )
                        
                        if not is_duplicate:
                            dimensions.append({
                                'length': length,
                                'width': width
                            })
                            print(f"Found dimension (simple): {length} × {width} ft")
                except ValueError:
                    continue
        
        return dimensions
    
    def _extract_with_contours(self, image_file) -> list:
        """
        Secondary fallback: Use OpenCV contour detection if OCR fails
        Detects room boundaries and calculates areas
        """
        try:
            # Open image with PIL and convert to OpenCV format
            image = Image.open(image_file)
            image_file.seek(0)  # Reset file pointer
            
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and analyze contours
            dimensions = []
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small or very large contours
                if w > 50 and h > 50 and w < img_array.shape[1] * 0.8 and h < img_array.shape[0] * 0.8:
                    # Assume a scale (this is approximate)
                    # Typical blueprint scale: 1/4" = 1 ft means 1 pixel ≈ 0.1 ft (rough estimate)
                    scale_factor = 0.1  # Adjust based on typical blueprint scales
                    
                    length_ft = w * scale_factor
                    width_ft = h * scale_factor
                    
                    if 5 <= length_ft <= 100 and 5 <= width_ft <= 100:
                        dimensions.append({
                            'length': round(length_ft, 2),
                            'width': round(width_ft, 2)
                        })
                        print(f"Found dimension (contour): {length_ft:.2f} × {width_ft:.2f} ft")
            
            return dimensions
            
        except Exception as e:
            print(f"Contour detection error: {str(e)}")
            return []
    
    def _calculate_floor_area(self, dimensions: list) -> float:
        """
        Calculate total floor area from room dimensions
        Assumes dimensions are in feet
        
        Raises:
            ValueError: If no dimensions provided
        """
        if not dimensions:
            raise ValueError("No dimensions available to calculate area")
        
        total_area = 0
        for dim in dimensions:
            room_area = dim['length'] * dim['width']
            total_area += room_area
            print(f"Room: {dim['length']} × {dim['width']} ft = {room_area} sqft")
        
        return round(total_area, 2)
    
    def estimate_from_images(self, image_files: list, wage_per_day: float, cost_per_sqyard: float) -> dict:
        """
        Complete estimation from blueprint images
        
        Args:
            image_files: List of image files (one per floor)
            wage_per_day: Daily wage per worker
            cost_per_sqyard: Material cost per square yard
            
        Returns:
            dict: Extracted data ready for calculation engine
        """
        # Extract dimensions from images
        extraction_result = self.extract_dimensions_from_images(image_files)
        
        # Convert sqft to sq yards
        total_sqft = extraction_result['total_area_sqft']
        area_sqyards = total_sqft / 9
        floors = extraction_result['floors']
        
        return {
            'area': area_sqyards,
            'floors': floors,
            'wage': wage_per_day,
            'cost_per_sqyard': cost_per_sqyard,
            'extraction_details': extraction_result
        }
