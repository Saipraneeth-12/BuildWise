"""
AI Estimator Service
Uses IBM Granite LLM via Ollama to extract structured data from natural language prompts
"""

import requests
import json
import re

class AIEstimator:
    """
    AI-powered parameter extraction using Granite LLM
    Extracts: area, floors, wage, steel_type, cement_type, location from natural language
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
    
    def extract_parameters(self, prompt: str) -> dict:
        """
        Extract construction parameters from natural language prompt using Granite LLM
        
        Args:
            prompt: Natural language description
            
        Returns:
            dict: Extracted parameters {area, floors, wage, steel_type, cement_type, location}
        """
        
        # Build extraction prompt for Granite
        granite_prompt = self._build_extraction_prompt(prompt)
        
        try:
            # Call Granite LLM
            payload = {
                "model": self.granite_model,
                "prompt": granite_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for precise extraction
                    "top_p": 0.9,
                    "num_predict": 500
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                granite_response = result.get('response', '')
                
                # Parse Granite's response
                extracted = self._parse_granite_response(granite_response)
                
                # Fallback to regex if Granite parsing fails
                if not extracted or not all(k in extracted for k in ['area', 'floors', 'wage']):
                    extracted = self._fallback_extraction(prompt)
                
                return extracted
            else:
                # Fallback to regex extraction
                return self._fallback_extraction(prompt)
                
        except Exception as e:
            print(f"Granite LLM error: {str(e)}")
            # Fallback to regex extraction
            return self._fallback_extraction(prompt)
    
    def _build_extraction_prompt(self, user_prompt: str) -> str:
        """Build extraction prompt for Granite LLM"""
        
        return f"""You are a construction parameter extraction AI. Extract ONLY the following values from the user's prompt:

USER PROMPT: {user_prompt}

Extract these parameters:
1. area: Built-up area in square feet (sqft, sq ft)
2. floors: Number of floors (G+1 means 2 floors, G+2 means 3 floors, etc.)
3. wage: Daily wage per worker in rupees
4. steel_type: Type of steel (Fe415, Fe500, Fe550, TMT Premium)
5. cement_type: Type of cement (OPC 43, OPC 53, PPC, PSC)
6. location: City or location name

IMPORTANT RULES:
- Extract ONLY numbers for area, floors, wage
- For G+X format: floors = X + 1 (e.g., G+2 = 3 floors)
- For steel: look for Fe415, Fe500, Fe550, or TMT Premium
- For cement: look for OPC 43, OPC 53, PPC, or PSC
- If a value is missing, use defaults: area=1500, floors=2, wage=500, steel_type="Fe500", cement_type="OPC 53", location="India"
- Return ONLY in this exact JSON format:

{{"area": <number>, "floors": <number>, "wage": <number>, "steel_type": "<string>", "cement_type": "<string>", "location": "<string>"}}

Extract now:"""

    def _parse_granite_response(self, response: str) -> dict:
        """Parse Granite's JSON response"""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Validate and convert
                return {
                    'area': float(data.get('area', 1500)),
                    'floors': int(data.get('floors', 2)),
                    'wage': float(data.get('wage', 500)),
                    'steel_type': data.get('steel_type', 'Fe500'),
                    'cement_type': data.get('cement_type', 'OPC 53'),
                    'location': data.get('location', 'India')
                }
        except Exception as e:
            print(f"Granite parsing error: {str(e)}")
        
        return None
    
    def _fallback_extraction(self, prompt: str) -> dict:
        """
        Fallback regex-based extraction if Granite fails
        Looks for patterns like: 1500 sqft, G+2, wage 500, Fe500, OPC 53
        """
        
        prompt_lower = prompt.lower()
        
        # Extract area (now in sqft)
        area = 1500  # default
        area_patterns = [
            r'(\d+)\s*(?:sq\s*ft|sqft|square\s*feet)',
            r'area[:\s]+(\d+)',
        ]
        for pattern in area_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                area = float(match.group(1))
                break
        
        # Extract floors (G+X format or direct number)
        floors = 2  # default
        # Try G+X format first
        g_plus_match = re.search(r'g\+(\d+)', prompt_lower)
        if g_plus_match:
            floors = int(g_plus_match.group(1)) + 1  # G+2 = 3 floors
        else:
            # Try direct floor number
            floor_patterns = [
                r'(\d+)\s*floors?',
                r'floors?[:\s]+(\d+)',
            ]
            for pattern in floor_patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    floors = int(match.group(1))
                    break
        
        # Extract wage
        wage = 500  # default
        wage_patterns = [
            r'wage[:\s]+(\d+)',
            r'(\d+)\s*(?:per\s*day|daily)',
            r'worker[:\s]+(\d+)',
        ]
        for pattern in wage_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                wage = float(match.group(1))
                break
        
        # Extract steel type
        steel_type = 'Fe500'  # default
        steel_patterns = [
            r'(fe\s*415|fe415)',
            r'(fe\s*500|fe500)',
            r'(fe\s*550|fe550)',
            r'(tmt\s*premium)',
        ]
        steel_map = {
            'fe415': 'Fe415',
            'fe 415': 'Fe415',
            'fe500': 'Fe500',
            'fe 500': 'Fe500',
            'fe550': 'Fe550',
            'fe 550': 'Fe550',
            'tmt premium': 'TMT Premium',
        }
        for pattern in steel_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                steel_type = steel_map.get(match.group(1).replace(' ', ''), 'Fe500')
                break
        
        # Extract cement type
        cement_type = 'OPC 53'  # default
        cement_patterns = [
            r'(opc\s*43|opc43)',
            r'(opc\s*53|opc53)',
            r'(ppc)',
            r'(psc)',
        ]
        cement_map = {
            'opc43': 'OPC 43',
            'opc 43': 'OPC 43',
            'opc53': 'OPC 53',
            'opc 53': 'OPC 53',
            'ppc': 'PPC',
            'psc': 'PSC',
        }
        for pattern in cement_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                cement_type = cement_map.get(match.group(1).replace(' ', ''), 'OPC 53')
                break
        
        # Extract location
        location = 'India'  # default
        location_patterns = [
            r'(?:in|at|location)\s+([a-z]+)',
            r'([a-z]+)\s+city',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                location = match.group(1).capitalize()
                break
        
        return {
            'area': area,
            'floors': floors,
            'wage': wage,
            'steel_type': steel_type,
            'cement_type': cement_type,
            'location': location
        }
