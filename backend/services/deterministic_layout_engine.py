"""
BuildWise Deterministic Residential Layout Engine
Rule-based 2D residential layout generation with geometric logic
CRITICAL: Side-by-side floor positioning, realistic room sizes, doors, windows
"""

import re
import json
from typing import Dict, List, Tuple, Optional

class DeterministicLayoutEngine:
    """
    Deterministic residential layout generator
    Uses pure geometric rules - no probabilistic generation
    Generates side-by-side multi-floor layouts with doors and windows
    """
    
    # Room realistic dimensions (in meters) - CORRECTED FOR REALISM
    ROOM_CONSTRAINTS = {
        'living': {'min_width': 3.5, 'min_length': 4.0, 'typical_width': 4.0, 'typical_length': 4.0},
        'bedroom': {'min_width': 3.0, 'min_length': 3.0, 'typical_width': 3.0, 'typical_length': 3.5},
        'kitchen': {'min_width': 2.4, 'min_length': 2.5, 'typical_width': 3.0, 'typical_length': 2.5},
        'toilet': {'min_width': 1.2, 'min_length': 2.4, 'typical_width': 1.2, 'typical_length': 2.4},
        'staircase': {'min_width': 1.0, 'min_length': 3.0, 'typical_width': 1.0, 'typical_length': 3.0}
    }
    
    # Configuration room counts
    CONFIGURATIONS = {
        '1BHK': {'living': 1, 'bedroom': 1, 'kitchen': 1, 'toilet': 1},
        '2BHK': {'living': 1, 'bedroom': 2, 'kitchen': 1, 'toilet': 2},
        '3BHK': {'living': 1, 'bedroom': 3, 'kitchen': 1, 'toilet': 2}
    }
    
    # Door widths (in meters)
    DOOR_WIDTHS = {
        'main': 1.0,
        'internal': 0.8,
        'toilet': 0.7
    }
    
    # Window widths (in meters)
    WINDOW_WIDTHS = {
        'standard': 1.2,
        'ventilator': 0.6
    }
    
    def __init__(self):
        self.grid_size = 0.1  # 0.1m grid alignment for precision
        self.floor_gap = 2.0  # 2 meters gap between floors in visualization
    
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
        CRITICAL: Floors positioned side-by-side, not stacked
        """
        # Validate parameters
        if 'error' in params:
            return params
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        floors = params['floors']
        configuration = params['configuration']
        duplex_mode = params.get('duplex_mode', False)
        staircase_type = params.get('staircase_type', 'internal')
        
        # Validate plot size
        validation_error = self._validate_plot_size(plot_width, plot_length, configuration)
        if validation_error:
            return {'error': validation_error}
        
        # Generate floor layouts with side-by-side positioning
        floor_layouts = []
        
        for floor_num in range(1, floors + 1):
            # Calculate floor origin (side-by-side positioning)
            floor_origin_x = (floor_num - 1) * (plot_width + self.floor_gap)
            
            if duplex_mode and floor_num == 2:
                # Upper floor in duplex: bedrooms only
                floor_layout = self._generate_duplex_upper_floor(
                    plot_width, plot_length, configuration
                )
            else:
                # Standard floor layout
                floor_layout = self._generate_standard_floor(
                    plot_width, plot_length, configuration, 
                    has_staircase=(floors > 1 and staircase_type == 'internal')
                )
            
            floor_layout['floor_number'] = floor_num
            floor_layout['origin_x'] = floor_origin_x
            floor_layout['origin_y'] = 0
            floor_layouts.append(floor_layout)
        
        # Calculate areas - CORRECTED METRICS
        plot_area = plot_width * plot_length
        total_built_up = sum(floor['built_up_area'] for floor in floor_layouts)
        ground_coverage = round(floor_layouts[0]['built_up_area'] / plot_area, 2) if floor_layouts else 0
        fsi = round(total_built_up / plot_area, 2)
        
        # Calculate total canvas width for visualization
        total_canvas_width = floors * plot_width + (floors - 1) * self.floor_gap
        
        return {
            'plot': {
                'width_m': round(plot_width, 2),
                'length_m': round(plot_length, 2),
                'area_m2': round(plot_area, 2)
            },
            'configuration': configuration,
            'floors': floor_layouts,
            'total_built_up_area': round(total_built_up, 2),
            'ground_coverage': ground_coverage,
            'fsi': fsi,
            'canvas_width': round(total_canvas_width, 2),
            'canvas_height': round(plot_length, 2)
        }
    
    def _generate_standard_floor(self, width: float, length: float, 
                                 config: str, has_staircase: bool) -> Dict:
        """
        Generate standard floor layout with REALISTIC room sizes
        CRITICAL: Rooms must not occupy 80% of plot width
        """
        rooms = []
        doors = []
        windows = []
        current_x = 0
        current_y = 0
        
        room_counts = self.CONFIGURATIONS[config]
        
        # Step 1: Place staircase if multi-floor (internal)
        if has_staircase:
            stair_width = self.ROOM_CONSTRAINTS['staircase']['typical_width']
            stair_length = self.ROOM_CONSTRAINTS['staircase']['typical_length']
            rooms.append({
                'name': 'Staircase',
                'x': 0,
                'y': 0,
                'width': stair_width,
                'length': stair_length,
                'area': round(stair_width * stair_length, 2)
            })
            current_x = stair_width
        
        # Step 2: Place living room (REALISTIC SIZE - 4m x 4m)
        living_width = self.ROOM_CONSTRAINTS['living']['typical_width']
        living_length = self.ROOM_CONSTRAINTS['living']['typical_length']
        
        # Ensure living room fits
        if current_x + living_width > width:
            living_width = width - current_x
        
        rooms.append({
            'name': 'Living Room',
            'x': current_x,
            'y': 0,
            'width': self._round_to_grid(living_width),
            'length': self._round_to_grid(living_length),
            'area': round(living_width * living_length, 2)
        })
        
        # Main door for living room
        doors.append({
            'type': 'main',
            'width': self.DOOR_WIDTHS['main'],
            'x': current_x + living_width / 2,
            'y': 0,
            'connects': ['Living Room', 'Outside']
        })
        
        # Windows for living room (2 windows)
        windows.append({
            'width': self.WINDOW_WIDTHS['standard'],
            'x': current_x + 0.5,
            'y': 0,
            'room': 'Living Room'
        })
        windows.append({
            'width': self.WINDOW_WIDTHS['standard'],
            'x': current_x + living_width - 1.5,
            'y': 0,
            'room': 'Living Room'
        })
        
        # Step 3: Place kitchen (REALISTIC SIZE - 3m x 2.5m)
        kitchen_width = self.ROOM_CONSTRAINTS['kitchen']['typical_width']
        kitchen_length = self.ROOM_CONSTRAINTS['kitchen']['typical_length']
        kitchen_y = living_length
        
        rooms.append({
            'name': 'Kitchen',
            'x': 0,
            'y': kitchen_y,
            'width': self._round_to_grid(kitchen_width),
            'length': self._round_to_grid(kitchen_length),
            'area': round(kitchen_width * kitchen_length, 2)
        })
        
        # Kitchen door
        doors.append({
            'type': 'internal',
            'width': self.DOOR_WIDTHS['internal'],
            'x': kitchen_width / 2,
            'y': kitchen_y,
            'connects': ['Kitchen', 'Living Room']
        })
        
        # Kitchen window
        windows.append({
            'width': self.WINDOW_WIDTHS['standard'],
            'x': 0,
            'y': kitchen_y + kitchen_length / 2,
            'room': 'Kitchen'
        })
        
        # Step 4: Place bedrooms (REALISTIC SIZE - 3m x 3.5m each)
        bedroom_count = room_counts['bedroom']
        bedroom_start_y = living_length + kitchen_length
        bedroom_width = self.ROOM_CONSTRAINTS['bedroom']['typical_width']
        bedroom_length = self.ROOM_CONSTRAINTS['bedroom']['typical_length']
        
        # Ensure bedrooms fit in remaining space
        remaining_length = length - bedroom_start_y
        if bedroom_length > remaining_length:
            bedroom_length = remaining_length
        
        for i in range(bedroom_count):
            bedroom_x = i * bedroom_width
            
            # Ensure bedroom fits in width
            if bedroom_x + bedroom_width > width:
                bedroom_width = width - bedroom_x
            
            rooms.append({
                'name': f'Bedroom {i+1}',
                'x': bedroom_x,
                'y': bedroom_start_y,
                'width': self._round_to_grid(bedroom_width),
                'length': self._round_to_grid(bedroom_length),
                'area': round(bedroom_width * bedroom_length, 2)
            })
            
            # Bedroom door
            doors.append({
                'type': 'internal',
                'width': self.DOOR_WIDTHS['internal'],
                'x': bedroom_x + bedroom_width / 2,
                'y': bedroom_start_y,
                'connects': [f'Bedroom {i+1}', 'Corridor']
            })
            
            # Bedroom window
            windows.append({
                'width': self.WINDOW_WIDTHS['standard'],
                'x': bedroom_x + bedroom_width / 2,
                'y': length,
                'room': f'Bedroom {i+1}'
            })
        
        # Step 5: Place toilets (REALISTIC SIZE - 1.2m x 2.4m)
        toilet_count = room_counts['toilet']
        toilet_width = self.ROOM_CONSTRAINTS['toilet']['typical_width']
        toilet_length = self.ROOM_CONSTRAINTS['toilet']['typical_length']
        
        for i in range(toilet_count):
            # Attach to bedroom or place separately
            toilet_x = i * (width / toilet_count)
            toilet_y = bedroom_start_y + bedroom_length - toilet_length
            
            rooms.append({
                'name': f'Toilet {i+1}',
                'x': toilet_x,
                'y': toilet_y,
                'width': self._round_to_grid(toilet_width),
                'length': self._round_to_grid(toilet_length),
                'area': round(toilet_width * toilet_length, 2)
            })
            
            # Toilet door
            doors.append({
                'type': 'toilet',
                'width': self.DOOR_WIDTHS['toilet'],
                'x': toilet_x + toilet_width / 2,
                'y': toilet_y,
                'connects': [f'Toilet {i+1}', f'Bedroom {i+1}']
            })
            
            # Toilet ventilator
            windows.append({
                'width': self.WINDOW_WIDTHS['ventilator'],
                'x': toilet_x + toilet_width / 2,
                'y': toilet_y + toilet_length,
                'room': f'Toilet {i+1}',
                'type': 'ventilator'
            })
        
        # Calculate built-up area
        built_up_area = sum(room['area'] for room in rooms)
        
        return {
            'rooms': rooms,
            'doors': doors,
            'windows': windows,
            'built_up_area': round(built_up_area, 2)
        }
    
    def _generate_duplex_upper_floor(self, width: float, length: float, config: str) -> Dict:
        """
        Generate upper floor for duplex (bedrooms only)
        Staircase void removed from usable area
        """
        rooms = []
        doors = []
        windows = []
        room_counts = self.CONFIGURATIONS[config]
        
        # Staircase void (not counted in built-up)
        stair_width = self.ROOM_CONSTRAINTS['staircase']['typical_width']
        stair_length = self.ROOM_CONSTRAINTS['staircase']['typical_length']
        
        # Bedrooms distributed across remaining floor
        bedroom_count = room_counts['bedroom']
        bedroom_width = self.ROOM_CONSTRAINTS['bedroom']['typical_width']
        bedroom_length = self.ROOM_CONSTRAINTS['bedroom']['typical_length']
        
        for i in range(bedroom_count):
            bedroom_x = stair_width + i * bedroom_width
            
            rooms.append({
                'name': f'Bedroom {i+1}',
                'x': bedroom_x,
                'y': 0,
                'width': self._round_to_grid(bedroom_width),
                'length': self._round_to_grid(bedroom_length),
                'area': round(bedroom_width * bedroom_length, 2)
            })
            
            # Bedroom door
            doors.append({
                'type': 'internal',
                'width': self.DOOR_WIDTHS['internal'],
                'x': bedroom_x + bedroom_width / 2,
                'y': 0,
                'connects': [f'Bedroom {i+1}', 'Corridor']
            })
            
            # Bedroom window
            windows.append({
                'width': self.WINDOW_WIDTHS['standard'],
                'x': bedroom_x + bedroom_width / 2,
                'y': bedroom_length,
                'room': f'Bedroom {i+1}'
            })
        
        # Toilets
        toilet_count = room_counts['toilet']
        toilet_width = self.ROOM_CONSTRAINTS['toilet']['typical_width']
        toilet_length = self.ROOM_CONSTRAINTS['toilet']['typical_length']
        
        for i in range(toilet_count):
            toilet_x = stair_width + i * (width - stair_width) / toilet_count
            toilet_y = bedroom_length
            
            rooms.append({
                'name': f'Toilet {i+1}',
                'x': toilet_x,
                'y': toilet_y,
                'width': self._round_to_grid(toilet_width),
                'length': self._round_to_grid(toilet_length),
                'area': round(toilet_width * toilet_length, 2)
            })
            
            # Toilet door
            doors.append({
                'type': 'toilet',
                'width': self.DOOR_WIDTHS['toilet'],
                'x': toilet_x + toilet_width / 2,
                'y': toilet_y,
                'connects': [f'Toilet {i+1}', f'Bedroom {i+1}']
            })
            
            # Toilet ventilator
            windows.append({
                'width': self.WINDOW_WIDTHS['ventilator'],
                'x': toilet_x + toilet_width / 2,
                'y': toilet_y + toilet_length,
                'room': f'Toilet {i+1}',
                'type': 'ventilator'
            })
        
        built_up_area = sum(room['area'] for room in rooms)
        
        return {
            'rooms': rooms,
            'doors': doors,
            'windows': windows,
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
            return f"Layout cannot be generated with given constraints. Plot dimensions insufficient for {config}. Minimum {required}m² required, got {plot_area:.1f}m²"
        
        if width < 6 or length < 8:
            return "Layout cannot be generated with given constraints. Minimum plot dimensions: 6m × 8m"
        
        return None
    
    def _round_to_grid(self, value: float) -> float:
        """Round to nearest grid size"""
        return round(value / self.grid_size) * self.grid_size
