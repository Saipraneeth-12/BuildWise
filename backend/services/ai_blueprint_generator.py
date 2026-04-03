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
from services.professional_architect_ai import ProfessionalArchitectAI
from services.multi_variant_layout_generator import MultiVariantLayoutGenerator

class AIBlueprintGenerator:
    """
    AI-powered blueprint generation using Granite LLM
    Generates labeled architectural blueprints with measurements
    Now includes Professional Architect AI for intelligent input extraction
    Supports multi-variant generation (3-4 layout options)
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
        self.layout_engine = DeterministicLayoutEngine()
        self.professional_ai = ProfessionalArchitectAI()
        self.variant_generator = MultiVariantLayoutGenerator()
    
    def generate_blueprint(self, prompt: str, use_professional_ai: bool = False, generate_variants: bool = False, num_variants: int = 3) -> dict:
        """
        Generate architectural blueprint from natural language prompt
        
        Args:
            prompt: Natural language description (any format)
            use_professional_ai: Use professional architect AI for intelligent extraction
            generate_variants: Generate multiple layout variants for user selection
            num_variants: Number of variants to generate (3-4)
            
        Returns:
            dict: {
                'layout': structured layout JSON,
                'blueprint_image': base64 encoded PNG with labels,
                'prompt': original prompt,
                'metadata': extracted parameters,
                'professional_analysis': (if use_professional_ai=True) 10-section analysis,
                'variants': (if generate_variants=True) list of layout variants
            }
        """
        
        try:
            if generate_variants:
                # Generate multiple layout variants
                variants = self.variant_generator.generate_variants(prompt, num_variants)
                
                # Generate blueprint for first variant (default selection)
                default_variant = variants[0]
                
                # Convert variant to deterministic engine format
                params = self._variant_to_params(prompt, default_variant)
                layout = self.layout_engine.generate_layout(params)
                
                if 'error' in layout:
                    return {'error': layout['error']}
                
                # Enhance with Granite
                enhanced_metadata = self._enhance_with_granite(prompt, layout)
                
                # Generate blueprint image
                blueprint_image = self._generate_blueprint_image(layout, enhanced_metadata)
                
                return {
                    'layout': layout,
                    'blueprint_image': blueprint_image,
                    'prompt': prompt,
                    'metadata': enhanced_metadata,
                    'variants': variants,
                    'selected_variant': 0  # Default to first variant
                }
            
            elif use_professional_ai:
                # Use Professional Architect AI for intelligent extraction
                professional_analysis = self.professional_ai.generate_professional_layout(prompt)
                
                # Extract parameters for deterministic engine
                extracted_params = professional_analysis['1_extracted_parameters']
                
                # Convert to deterministic engine format
                params = {
                    'plot_width': extracted_params['plot_width'] * 0.3048,  # Convert ft to m
                    'plot_length': extracted_params['plot_length'] * 0.3048,
                    'unit': 'meters',
                    'floors': extracted_params['floors'],
                    'configuration': f"{extracted_params['bedrooms']}BHK",
                    'staircase_type': extracted_params['staircase_type'],
                    'duplex_mode': extracted_params.get('duplex', False)
                }
                
                # Generate layout using deterministic engine
                layout = self.layout_engine.generate_layout(params)
                
                if 'error' in layout:
                    return {'error': layout['error']}
                
                # Use professional analysis for metadata
                enhanced_metadata = {
                    'configuration': f"{extracted_params['bedrooms']}BHK",
                    'plot_width': extracted_params['plot_width'],
                    'plot_length': extracted_params['plot_length'],
                    'floors': extracted_params['floors'],
                    'ventilation_notes': professional_analysis['7_ventilation_strategy']['strategy'],
                    'lighting_notes': f"Primary openings: {professional_analysis['7_ventilation_strategy']['primary_openings']}",
                    'structural_notes': professional_analysis['4_structural_grid']['notes'],
                    'cost_estimate_range': next((r for r in professional_analysis['10_recommendations'] if 'cost' in r.lower()), 'Contact for estimate')
                }
                
                # Generate blueprint image
                blueprint_image = self._generate_blueprint_image(layout, enhanced_metadata)
                
                return {
                    'layout': layout,
                    'blueprint_image': blueprint_image,
                    'prompt': prompt,
                    'metadata': enhanced_metadata,
                    'professional_analysis': professional_analysis
                }
            
            else:
                # Original deterministic approach
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
    
    def _variant_to_params(self, prompt: str, variant: dict) -> dict:
        """Convert variant layout to deterministic engine parameters"""
        # Extract parameters from prompt
        params = self.layout_engine.parse_input(prompt)
        
        # Add variant-specific information
        params['variant_type'] = variant['layout_type']
        params['variant_name'] = variant['variant_name']
        
        return params
    
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
- Ground Coverage: {layout.get('ground_coverage', 0)*100:.0f}%
- FSI: {layout.get('fsi', 0)}

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
        Generate blueprint image with room labels, doors, windows, and measurements
        CRITICAL: Side-by-side floor positioning, proper scaling, no overlap
        Returns base64 encoded PNG
        """
        
        # Image dimensions - wider for side-by-side floors
        canvas_width = layout.get('canvas_width', layout['plot']['width_m'])
        canvas_height = layout.get('canvas_height', layout['plot']['length_m'])
        
        # Calculate scale to fit image
        img_width = 1600
        img_height = 1000
        padding = 100
        bottom_padding = 200  # Extra padding for metadata (UI safety)
        
        available_width = img_width - 2 * padding
        available_height = img_height - padding - bottom_padding
        
        scale_x = available_width / canvas_width
        scale_y = available_height / canvas_height
        scale = min(scale_x, scale_y)
        
        # Create white canvas
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            label_font = ImageFont.truetype("arial.ttf", 14)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw title
        title = "Deterministic Residential Layout Generator"
        subtitle = f"{layout['configuration']} - {layout['plot']['width_m']}m × {layout['plot']['length_m']}m"
        draw.text((padding, 20), title, fill='black', font=title_font)
        draw.text((padding, 45), subtitle, fill='gray', font=small_font)
        
        # Draw each floor side-by-side
        plot_width = layout['plot']['width_m']
        plot_length = layout['plot']['length_m']
        
        for floor_idx, floor in enumerate(layout['floors']):
            floor_origin_x = floor.get('origin_x', 0)
            floor_x_start = padding + floor_origin_x * scale
            floor_y_start = padding + 70
            
            # Draw floor label
            floor_label = f"Floor {floor['floor_number']}"
            draw.text((floor_x_start, floor_y_start - 25), floor_label, fill='blue', font=label_font)
            
            # Draw plot boundary
            plot_rect = [
                floor_x_start,
                floor_y_start,
                floor_x_start + plot_width * scale,
                floor_y_start + plot_length * scale
            ]
            draw.rectangle(plot_rect, outline='black', width=3)
            
            # Draw rooms
            for room in floor['rooms']:
                x = floor_x_start + room['x'] * scale
                y = floor_y_start + room['y'] * scale
                w = room['width'] * scale
                h = room['length'] * scale
                
                # Room rectangle
                room_rect = [x, y, x + w, y + h]
                
                # Color code by room type
                if 'Living' in room['name']:
                    outline_color = 'blue'
                elif 'Bedroom' in room['name']:
                    outline_color = 'red'
                elif 'Kitchen' in room['name']:
                    outline_color = 'green'
                elif 'Toilet' in room['name']:
                    outline_color = 'purple'
                elif 'Staircase' in room['name']:
                    outline_color = 'orange'
                else:
                    outline_color = 'gray'
                
                draw.rectangle(room_rect, outline=outline_color, width=2)
                
                # Room label (centered, no overflow)
                label_x = x + w / 2
                label_y = y + h / 2
                
                # Room name
                name_text = room['name']
                bbox = draw.textbbox((0, 0), name_text, font=label_font)
                text_width = bbox[2] - bbox[0]
                
                # Only draw if text fits
                if text_width < w - 10:
                    draw.text((label_x - text_width/2, label_y - 20), name_text, 
                             fill='black', font=label_font)
                
                # Room dimensions
                dim_text = f"{room['width']:.1f}m × {room['length']:.1f}m"
                bbox = draw.textbbox((0, 0), dim_text, font=small_font)
                text_width = bbox[2] - bbox[0]
                
                if text_width < w - 10:
                    draw.text((label_x - text_width/2, label_y), dim_text, 
                             fill='gray', font=small_font)
                
                # Room area
                area_text = f"{room['area']:.1f} m²"
                bbox = draw.textbbox((0, 0), area_text, font=small_font)
                text_width = bbox[2] - bbox[0]
                
                if text_width < w - 10:
                    draw.text((label_x - text_width/2, label_y + 15), area_text, 
                             fill='gray', font=small_font)
            
            # Draw doors
            for door in floor.get('doors', []):
                door_x = floor_x_start + door['x'] * scale
                door_y = floor_y_start + door['y'] * scale
                door_width = door['width'] * scale
                
                # Draw door gap (red line)
                draw.line([door_x - door_width/2, door_y, door_x + door_width/2, door_y], 
                         fill='red', width=3)
                
                # Draw door swing arc (quarter circle)
                arc_radius = door_width / 2
                arc_bbox = [door_x - arc_radius, door_y, door_x + arc_radius, door_y + arc_radius]
                draw.arc(arc_bbox, start=0, end=90, fill='red', width=1)
            
            # Draw windows
            for window in floor.get('windows', []):
                win_x = floor_x_start + window['x'] * scale
                win_y = floor_y_start + window['y'] * scale
                win_width = window['width'] * scale
                
                # Draw window (double line)
                draw.line([win_x - win_width/2, win_y, win_x + win_width/2, win_y], 
                         fill='blue', width=2)
                draw.line([win_x - win_width/2, win_y + 3, win_x + win_width/2, win_y + 3], 
                         fill='blue', width=2)
        
        # Draw metadata box (bottom, with safety padding)
        meta_y = img_height - bottom_padding + 20
        draw.rectangle([padding, meta_y, img_width - padding, img_height - 30], 
                      outline='black', width=2)
        
        # Plot details
        draw.text((padding + 10, meta_y + 10), "Plot Details:", fill='black', font=label_font)
        
        meta_text = [
            f"Plot Area: {layout['plot'].get('area_m2', layout['plot']['width_m'] * layout['plot']['length_m']):.1f} m²",
            f"Floor 1 Built-up: {layout['floors'][0]['built_up_area']} m²",
        ]
        
        if len(layout['floors']) > 1:
            meta_text.append(f"Floor 2 Built-up: {layout['floors'][1]['built_up_area']} m²")
        
        meta_text.extend([
            f"Total Built-up: {layout['total_built_up_area']} m²",
            f"Ground Coverage: {layout.get('ground_coverage', 0)*100:.0f}%",
            f"FSI: {layout.get('fsi', 0)}"
        ])
        
        for idx, text in enumerate(meta_text):
            draw.text((padding + 10, meta_y + 30 + idx * 18), text, 
                     fill='black', font=small_font)
        
        # Recommendations (right side)
        draw.text((img_width // 2 + 50, meta_y + 10), "Recommendations:", fill='black', font=label_font)
        
        rec_text = [
            f"Ventilation: {metadata.get('ventilation_notes', 'N/A')[:40]}",
            f"Lighting: {metadata.get('lighting_notes', 'N/A')[:40]}",
            f"Structure: {metadata.get('structural_notes', 'N/A')[:40]}",
            f"Cost Range: {metadata.get('cost_estimate_range', 'N/A')}"
        ]
        
        for idx, text in enumerate(rec_text):
            draw.text((img_width // 2 + 50, meta_y + 30 + idx * 18), text, 
                     fill='black', font=small_font)
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
