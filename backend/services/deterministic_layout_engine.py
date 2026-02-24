"""
BuildWise Deterministic Residential Layout Engine
Rule-based 2D residential layout generation with geometric logic
"""

import re
import json
from typing import Dict, List, Tuple, Optional

class DeterministicLayoutEngine:
    """
    Deterministic residential layout generator
    Uses pure geometric rules - no probabilistic generation
    """
    
    # Room minimum dimensions (in meters)
    ROOM_CONSTRAINTS = {
        'living': {'min_width': 3.5, 'min_length': 4.0},
        'bedroom': {'min_width': 3.0, 'min_length': 3.0},
        'kitchen': {'min_width': 2.4, 'min_length': 3.0},
        'toilet': {'min_width': 1.2, 'min_length': 2.4},
        'staircase': {'min_width': 1.0, 'min_length': 3.0}
    }
    
    # Configuration room counts
    CONFIGURATIONS = {
        '1BHK': {'living': 1, 'bedroom': 1, 'kitchen': 1, 'toilet': 1},
        '2BHK': {'living': 1, 'bedroom': 2, 'kitchen': 1, 'toilet': 2},
        '3BHK': {'living': 1, 'bedroom': 3, 'kitchen': 1, 'toilet': 2}
    }
    
    def __init__(self):
        self.grid_size = 0.5  # 0.5m grid alignment
    
    def parse_input(self, prompt: str) -> Dict:
        """
        Extract parameters from natural language prompt
        Example: "30x40 ft plot, G+1, 2BHK, internal staircase, duplex"
        """
        prompt_lower = prompt.lower()
        
        # Extract plot dimensions
        plot_match = re.search(r'(\d+)\s*[x×]\s*(\d+)\s*(ft|feet|m|meter)', prompt_lower)
        if not plot_match:
            return {'error': 'Plot dimensions not found. Format: "30x40 ft" or "10x12 m"'}
        
        width = float(plot_match.group(1))
        length = float(plot_match.group(2))
        unit = plot_match.group(3)
        
        # Convert to meters if needed
        if unit in ['ft', 'feet']:
            width = width * 0.3048
            length = length * 0.3048
        
        # Round to grid
        width = self._round_to_grid(width)
        length = self._round_to_grid(length)
        
        # Extract floors
        floors = 1
        floor_match = re.search(r'g\+(\d+)', prompt_lower)
        if floor_match:
            floors = int(floor_match.group(1)) + 1
        elif re.search(r'(\d+)\s*floor', prompt_lower):
            floor_match = re.search(r'(\d+)\s*floor', prompt_lower)
            floors = int(floor_match.group(1))
        
        # Extract configuration
        configuration = '2BHK'  # default
        if '1bhk' in prompt_lower or '1 bhk' in prompt_lower:
            configuration = '1BHK'
        elif '3bhk' in prompt_lower or '3 bhk' in prompt_lower:
            configuration = '3BHK'
        elif '2bhk' in prompt_lower or '2 bhk' in prompt_lower:
            configuration = '2BHK'
        
        # Extract staircase type
        staircase_type = 'internal' if 'internal' in prompt_lower else 'external'
        
        # Extract duplex mode
        duplex_mode = 'duplex' in prompt_lower
        
        return {
            'plot_width': width,
            'plot_length': length,
            'unit': 'meters',
            'floors': floors,
            'configuration': configuration,
            'staircase_type': staircase_type,
            'duplex_mode': duplex_mode
        }
    
    def generate_layout(self, params: Dict) -> Dict:
        """
        Generate deterministic layout based on parameters
        """
        # Validate parameters
        if 'error' in params:
            return params
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        floors = params['floors']
        configuration = params['configuration']
        duplex_mode = params.get('duplex_mode', False)
        
        # Validate plot size
        validation_error = self._validate_plot_size(plot_width, plot_length, configuration)
        if validation_error:
            return {'error': validation_error}
        
        # Generate floor layouts
        floor_layouts = []
        
        for floor_num in range(1, floors + 1):
            if duplex_mode and floor_num == 2:
                # Upper floor in duplex: bedrooms only
                floor_layout = self._generate_duplex_upper_floor(
                    plot_width, plot_length, configuration
                )
            else:
                # Standard floor layout
                floor_layout = self._generate_standard_floor(
                    plot_width, plot_length, configuration, 
                    has_staircase=(floors > 1)
                )
            
            floor_layout['floor_number'] = floor_num
            floor_layouts.append(floor_layout)
        
        # Calculate areas
        total_built_up = sum(floor['built_up_area'] for floor in floor_layouts)
        plot_area = plot_width * plot_length
        efficiency_ratio = round(total_built_up / plot_area, 2)
        
        return {
            'plot': {
                'width_m': round(plot_width, 2),
                'length_m': round(plot_length, 2)
            },
            'configuration': configuration,
            'floors': floor_layouts,
            'total_built_up_area': round(total_built_up, 2),
            'efficiency_ratio': efficiency_ratio
        }
    
    def _generate_standard_floor(self, width: float, length: float, 
                                 config: str, has_staircase: bool) -> Dict:
        """Generate standard floor layout"""
        rooms = []
        current_x = 0
        current_y = 0
        
        room_counts = self.CONFIGURATIONS[config]
        
        # Step 1: Place staircase if multi-floor
        if has_staircase:
            stair_width = 1.5
            stair_length = 3.0
            rooms.append({
                'name': 'Staircase',
                'x': 0,
                'y': 0,
                'width': stair_width,
                'length': stair_length,
                'area': round(stair_width * stair_length, 2)
            })
            current_x = stair_width
        
        # Step 2: Place living room (front side)
        living_width = width - current_x
        living_length = length * 0.4  # 40% of plot length
        living_width = max(living_width, self.ROOM_CONSTRAINTS['living']['min_width'])
        living_length = max(living_length, self.ROOM_CONSTRAINTS['living']['min_length'])
        
        rooms.append({
            'name': 'Living Room',
            'x': current_x,
            'y': 0,
            'width': self._round_to_grid(living_width),
            'length': self._round_to_grid(living_length),
            'area': round(living_width * living_length, 2)
        })
        
        # Step 3: Place kitchen (adjacent to living)
        kitchen_width = width * 0.3
        kitchen_length = length * 0.25
        kitchen_width = max(kitchen_width, self.ROOM_CONSTRAINTS['kitchen']['min_width'])
        kitchen_length = max(kitchen_length, self.ROOM_CONSTRAINTS['kitchen']['min_length'])
        
        rooms.append({
            'name': 'Kitchen',
            'x': 0,
            'y': living_length,
            'width': self._round_to_grid(kitchen_width),
            'length': self._round_to_grid(kitchen_length),
            'area': round(kitchen_width * kitchen_length, 2)
        })
        
        # Step 4: Place bedrooms (rear side)
        bedroom_count = room_counts['bedroom']
        bedroom_start_y = living_length + kitchen_length
        bedroom_width = width / bedroom_count
        bedroom_length = length - bedroom_start_y
        
        bedroom_width = max(bedroom_width, self.ROOM_CONSTRAINTS['bedroom']['min_width'])
        bedroom_length = max(bedroom_length, self.ROOM_CONSTRAINTS['bedroom']['min_length'])
        
        for i in range(bedroom_count):
            rooms.append({
                'name': f'Bedroom {i+1}',
                'x': i * bedroom_width,
                'y': bedroom_start_y,
                'width': self._round_to_grid(bedroom_width),
                'length': self._round_to_grid(bedroom_length),
                'area': round(bedroom_width * bedroom_length, 2)
            })
        
        # Step 5: Place toilets (attached to bedrooms)
        toilet_count = room_counts['toilet']
        toilet_width = self.ROOM_CONSTRAINTS['toilet']['min_width']
        toilet_length = self.ROOM_CONSTRAINTS['toilet']['min_length']
        
        for i in range(toilet_count):
            # Attach to bedroom
            bedroom_x = rooms[-(bedroom_count - i)]['x']
            rooms.append({
                'name': f'Toilet {i+1}',
                'x': bedroom_x,
                'y': bedroom_start_y + bedroom_length - toilet_length,
                'width': self._round_to_grid(toilet_width),
                'length': self._round_to_grid(toilet_length),
                'area': round(toilet_width * toilet_length, 2)
            })
        
        # Calculate built-up area
        built_up_area = sum(room['area'] for room in rooms)
        
        return {
            'rooms': rooms,
            'built_up_area': round(built_up_area, 2)
        }
    
    def _generate_duplex_upper_floor(self, width: float, length: float, config: str) -> Dict:
        """Generate upper floor for duplex (bedrooms only)"""
        rooms = []
        room_counts = self.CONFIGURATIONS[config]
        
        # Bedrooms distributed across floor
        bedroom_count = room_counts['bedroom']
        bedroom_width = width / bedroom_count
        bedroom_length = length * 0.6
        
        for i in range(bedroom_count):
            rooms.append({
                'name': f'Bedroom {i+1}',
                'x': i * bedroom_width,
                'y': 0,
                'width': self._round_to_grid(bedroom_width),
                'length': self._round_to_grid(bedroom_length),
                'area': round(bedroom_width * bedroom_length, 2)
            })
        
        # Toilets
        toilet_count = room_counts['toilet']
        for i in range(toilet_count):
            toilet_width = self.ROOM_CONSTRAINTS['toilet']['min_width']
            toilet_length = self.ROOM_CONSTRAINTS['toilet']['min_length']
            rooms.append({
                'name': f'Toilet {i+1}',
                'x': i * (width / toilet_count),
                'y': bedroom_length,
                'width': self._round_to_grid(toilet_width),
                'length': self._round_to_grid(toilet_length),
                'area': round(toilet_width * toilet_length, 2)
            })
        
        built_up_area = sum(room['area'] for room in rooms)
        
        return {
            'rooms': rooms,
            'built_up_area': round(built_up_area, 2)
        }
    
    def _validate_plot_size(self, width: float, length: float, config: str) -> Optional[str]:
        """Validate if plot can accommodate configuration"""
        min_area_required = {
            '1BHK': 40,  # sq meters
            '2BHK': 60,
            '3BHK': 80
        }
        
        plot_area = width * length
        required = min_area_required.get(config, 60)
        
        if plot_area < required:
            return f"Plot dimensions insufficient for {config}. Minimum {required}m² required, got {plot_area:.1f}m²"
        
        return None
    
    def _round_to_grid(self, value: float) -> float:
        """Round to nearest grid size"""
        return round(value / self.grid_size) * self.grid_size
