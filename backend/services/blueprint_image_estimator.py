"""
Blueprint Image Estimator Service
Uses OCR and Vision models to extract dimensions from blueprint images
"""

import re
import base64
import requests
from PIL import Image
from io import BytesIO
import pytesseract

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
        """
        
        floors = len(image_files)
        floor_areas = []
        dimensions_per_floor = []
        
        for idx, image_file in enumerate(image_files):
            try:
                # Try vision model first (LLaVA)
                dimensions = self._extract_with_vision_model(image_file)
                
                # Fallback to OCR if vision model fails
                if not dimensions:
                    dimensions = self._extract_with_ocr(image_file)
                
                # Calculate floor area from dimensions
                floor_area = self._calculate_floor_area(dimensions)
                
                floor_areas.append(floor_area)
                dimensions_per_floor.append({
                    'floor': idx + 1,
                    'dimensions': dimensions,
                    'area_sqft': floor_area
                })
                
            except Exception as e:
                print(f"Error processing floor {idx + 1}: {str(e)}")
                # Use default area if extraction fails
                floor_areas.append(1000)  # Default 1000 sqft per floor
                dimensions_per_floor.append({
                    'floor': idx + 1,
                    'dimensions': [],
                    'area_sqft': 1000,
                    'error': str(e)
                })
        
        # CRITICAL: Calculate average area per floor
        area_per_floor_sqft = sum(floor_areas) / floors if floors > 0 else 1000
        
        # Total area is sum of all floors (already calculated)
        total_area_sqft = sum(floor_areas)
        
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
        Fallback: Use OCR (pytesseract) to extract text and find dimensions
        """
        try:
            # Open image with PIL
            image = Image.open(image_file)
            image_file.seek(0)  # Reset file pointer
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Parse dimensions from OCR text
            dimensions = self._parse_dimensions(text)
            
            return dimensions
            
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return []
    
    def _parse_dimensions(self, text: str) -> list:
        """
        Parse dimensions from text
        Looks for patterns like: 16 x 20, 14x13, 23 × 33
        """
        dimensions = []
        
        # Patterns to match dimensions
        patterns = [
            r'(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)',  # 16 x 20 or 16×20
            r'(\d+\.?\d*)\s*[*]\s*(\d+\.?\d*)',   # 16 * 20
            r'(\d+\.?\d*)\s+by\s+(\d+\.?\d*)',    # 16 by 20
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    length = float(match[0])
                    width = float(match[1])
                    
                    # Filter out unrealistic dimensions
                    if 5 <= length <= 100 and 5 <= width <= 100:
                        dimensions.append({
                            'length': length,
                            'width': width
                        })
                except ValueError:
                    continue
        
        return dimensions
    
    def _calculate_floor_area(self, dimensions: list) -> float:
        """
        Calculate total floor area from room dimensions
        Assumes dimensions are in feet
        """
        if not dimensions:
            return 1000  # Default area if no dimensions found
        
        total_area = 0
        for dim in dimensions:
            room_area = dim['length'] * dim['width']
            total_area += room_area
        
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
