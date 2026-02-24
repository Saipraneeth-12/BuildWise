"""
AI Blueprint Generator Service
Uses IBM Granite LLM via Ollama to generate architectural blueprints from natural language
Integrates with deterministic layout engine for structured output
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from services.deterministic_layout_engine import DeterministicLayoutEngine

class AIBlueprintGenerator:
    """
    AI-powered blueprint generation using Granite LLM
    Generates labeled architectural blueprints with measurements
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
        self.layout_engine = DeterministicLayoutEngine()
    
    def generate_blueprint(self, prompt: str) -> dict:
        """
        Generate architectural blueprint from natural language prompt
        
        Args:
            prompt: Natural language description (e.g., "30x40 ft plot, G+1, 2BHK")
            
        Returns:
            dict: {
                'layout': structured layout JSON,
                'blueprint_image': base64 encoded PNG with labels,
                'prompt': original prompt,
                'metadata': extracted parameters
            }
        """
        
        try:
            # Step 1: Parse input using deterministic engine
            params = self.layout_engine.parse_input(prompt)
            
            if 'error' in params:
                return {'error': params['error']}
            
            # Step 2: Generate layout structure
            layout = self.layout_engine.generate_layout(params)
            
            if 'error' in layout:
                return {'error': layout['error']}
            
            # Step 3: Enhance with Granite LLM reasoning
            enhanced_metadata = self._enhance_with_granite(prompt, layout)
            
            # Step 4: Generate blueprint image with labels
            blueprint_image = self._generate_blueprint_image(layout, enhanced_metadata)
            
            return {
                'layout': layout,
                'blueprint_image': blueprint_image,
                'prompt': prompt,
                'metadata': {
                    **params,
                    **enhanced_metadata
                }
            }
            
        except Exception as e:
            return {'error': f'Blueprint generation failed: {str(e)}'}
    
    def _enhance_with_granite(self, prompt: str, layout: dict) -> dict:
        """
        Use Granite LLM to add architectural reasoning and recommendations
        """
        
        granite_prompt = f"""You are an architectural AI assistant. Analyze this construction project:

USER REQUEST: {prompt}

GENERATED LAYOUT:
- Configuration: {layout['configuration']}
- Plot: {layout['plot']['width_m']}m x {layout['plot']['length_m']}m
- Total Built-up Area: {layout['total_built_up_area']} sq meters
- Efficiency: {layout['efficiency_ratio']}

Provide brief recommendations in JSON format:
{{
    "ventilation_notes": "brief ventilation recommendation",
    "lighting_notes": "brief natural lighting recommendation",
    "structural_notes": "brief structural consideration",
    "cost_estimate_range": "estimated cost range in lakhs"
}}

Keep each note under 15 words. Return ONLY JSON."""

        try:
            payload = {
                "model": self.granite_model,
                "prompt": granite_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 300
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                granite_response = result.get('response', '')
                
                # Parse JSON response
                import re
                json_match = re.search(r'\{[^}]+\}', granite_response, re.DOTALL)
                if json_match:
                    enhanced = json.loads(json_match.group(0))
                    return enhanced
            
        except Exception as e:
            print(f"Granite enhancement error: {str(e)}")
        
        # Fallback recommendations
        return {
            'ventilation_notes': 'Ensure cross-ventilation in all rooms',
            'lighting_notes': 'Maximize natural light from north and east',
            'structural_notes': 'RCC frame structure recommended',
            'cost_estimate_range': '15-25 lakhs'
        }
    
    def _generate_blueprint_image(self, layout: dict, metadata: dict) -> str:
        """
        Generate blueprint image with room labels and measurements
        Returns base64 encoded PNG
        """
        
        # Image dimensions
        img_width = 1200
        img_height = 900
        padding = 100
        
        # Create white canvas
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            label_font = ImageFont.truetype("arial.ttf", 16)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw title
        title = f"{layout['configuration']} - {layout['plot']['width_m']}m x {layout['plot']['length_m']}m"
        draw.text((padding, 30), title, fill='black', font=title_font)
        
        # Calculate scale
        plot_width = layout['plot']['width_m']
        plot_length = layout['plot']['length_m']
        
        available_width = img_width - 2 * padding
        available_height = img_height - 2 * padding - 100
        
        scale_x = available_width / plot_width
        scale_y = available_height / plot_length
        scale = min(scale_x, scale_y)
        
        # Draw each floor
        floor_offset_y = 0
        for floor_idx, floor in enumerate(layout['floors']):
            floor_y_start = padding + 80 + floor_offset_y
            
            # Draw floor label
            floor_label = f"Floor {floor['floor_number']}"
            draw.text((padding, floor_y_start - 25), floor_label, fill='blue', font=label_font)
            
            # Draw plot boundary
            plot_rect = [
                padding,
                floor_y_start,
                padding + plot_width * scale,
                floor_y_start + plot_length * scale
            ]
            draw.rectangle(plot_rect, outline='black', width=3)
            
            # Draw rooms
            for room in floor['rooms']:
                x = padding + room['x'] * scale
                y = floor_y_start + room['y'] * scale
                w = room['width'] * scale
                h = room['length'] * scale
                
                # Room rectangle
                room_rect = [x, y, x + w, y + h]
                
                # Color code by room type
                if 'Living' in room['name']:
                    fill_color = (173, 216, 230, 100)  # Light blue
                    outline_color = 'blue'
                elif 'Bedroom' in room['name']:
                    fill_color = (255, 182, 193, 100)  # Light pink
                    outline_color = 'red'
                elif 'Kitchen' in room['name']:
                    fill_color = (144, 238, 144, 100)  # Light green
                    outline_color = 'green'
                elif 'Toilet' in room['name']:
                    fill_color = (221, 160, 221, 100)  # Light purple
                    outline_color = 'purple'
                elif 'Staircase' in room['name']:
                    fill_color = (255, 255, 224, 100)  # Light yellow
                    outline_color = 'orange'
                else:
                    fill_color = (211, 211, 211, 100)  # Light gray
                    outline_color = 'gray'
                
                draw.rectangle(room_rect, outline=outline_color, width=2)
                
                # Room label
                label_x = x + w / 2
                label_y = y + h / 2
                
                # Room name
                bbox = draw.textbbox((0, 0), room['name'], font=label_font)
                text_width = bbox[2] - bbox[0]
                draw.text((label_x - text_width/2, label_y - 20), room['name'], 
                         fill='black', font=label_font)
                
                # Room dimensions
                dim_text = f"{room['width']:.1f}m x {room['length']:.1f}m"
                bbox = draw.textbbox((0, 0), dim_text, font=small_font)
                text_width = bbox[2] - bbox[0]
                draw.text((label_x - text_width/2, label_y + 5), dim_text, 
                         fill='gray', font=small_font)
                
                # Room area
                area_text = f"{room['area']:.1f} m²"
                bbox = draw.textbbox((0, 0), area_text, font=small_font)
                text_width = bbox[2] - bbox[0]
                draw.text((label_x - text_width/2, label_y + 20), area_text, 
                         fill='gray', font=small_font)
            
            floor_offset_y += plot_length * scale + 60
        
        # Draw metadata box
        meta_y = img_height - 150
        draw.rectangle([padding, meta_y, img_width - padding, img_height - 30], 
                      outline='black', width=2)
        
        meta_text = [
            f"Total Built-up: {layout['total_built_up_area']} m²",
            f"Efficiency: {layout['efficiency_ratio']*100:.0f}%",
            f"Ventilation: {metadata.get('ventilation_notes', 'N/A')}",
            f"Lighting: {metadata.get('lighting_notes', 'N/A')}"
        ]
        
        for idx, text in enumerate(meta_text):
            draw.text((padding + 10, meta_y + 10 + idx * 25), text, 
                     fill='black', font=small_font)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
