"""
BuildWise Senior Architect + Structural Engineer + Quantity Estimator System
25+ years real residential design experience
Handles ANY input format with percentage-based space allocation
"""

import re
import json
from typing import Dict, List, Tuple, Optional

class SeniorArchitectSystem:
    """
    Professional residential architecture generator with:
    - Universal input handling
    - Percentage-based space allocation
    - Structural integration
    - Quantity estimation
    - Tool-ready output
    """
    
    # Professional space allocation percentages (when dimensions not provided)
    SPACE_ALLOCATION = {
        'living_dining': {'min': 18, 'max': 25, 'typical': 22},
        'kitchen': {'min': 8, 'max': 12, 'typical': 10},
        'master_bedroom': {'min': 12, 'max': 15, 'typical': 13},
        'other_bedroom': {'min': 10, 'max': 12, 'typical': 11},
        'bathrooms_total': {'min': 8, 'max': 12, 'typical': 10},
        'staircase_internal': {'min': 6, 'max': 8, 'typical': 7},
        'staircase_external': {'min': 4, 'max': 6, 'typical': 5},
        'pooja': {'min': 1, 'max': 3, 'typical': 2},
        'circulation': {'min': 8, 'max': 12, 'typical': 10},
        'balcony': {'min': 3, 'max': 5, 'typical': 4},
        'utility': {'min': 2, 'max': 4, 'typical': 3},
        'parking_single': {'min': 10, 'max': 15, 'typical': 12}
    }
    
    # Ground coverage assumptions
    GROUND_COVERAGE = {
        'urban': {'min': 60, 'max': 70, 'typical': 65},
        'semi_urban': {'min': 65, 'max': 75, 'typical': 70},
        'premium_villa': {'min': 50, 'max': 60, 'typical': 55}
    }
    
    # Structural parameters
    STRUCTURAL_PARAMS = {
        'column_spacing_min': 3.0,  # meters
        'column_spacing_max': 4.5,
        'slab_thickness_min': 125,  # mm
        'slab_thickness_max': 150,
        'beam_depth_ratio': 20,  # span/20
        'column_min_size': 230,  # mm
        'concrete_grade': 'M20',
        'steel_grade': 'Fe500',
        'max_beam_span': 5.5  # meters
    }
    
    # Quantity estimation factors
    QUANTITY_FACTORS = {
        'concrete_per_sqm': {'min': 0.25, 'max': 0.35, 'typical': 0.30},  # m³/m²
        'steel_per_sqm': {'min': 30, 'max': 45, 'typical': 38},  # kg/m²
        'shuttering_per_sqm': {'min': 1.5, 'max': 2.5, 'typical': 2.0},  # m²/m²
        'excavation_depth': 1.5,  # meters
        'brickwork_per_sqm': 55  # bricks per sqm (9" wall)
    }
    
    def __init__(self):
        self.assumptions = []
        self.user_dimensions = {}
    
    def extract_parameters(self, user_input: str) -> Dict:
        """
        SECTION 1: Universal input handling
        Extract and normalize from ANY format
        """
        input_lower = user_input.lower()
        params = {}
        
        # Extract plot dimensions
        plot_patterns = [
            r'(\d+\.?\d*)\s*(?:ft|feet|foot)?\s*[x×]\s*(\d+\.?\d*)\s*(ft|feet|foot|m|meter|metre)',
            r'plot[:\s]+(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)\s*(ft|feet|foot|m|meter|metre)?',
            r'length[:\s]+(\d+\.?\d*).*width[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s+by\s+(\d+\.?\d*)\s*(ft|feet|m)'
        ]
        
        plot_size = None
        unit = 'ft'
        for pattern in plot_patterns:
            match = re.search(pattern, input_lower)
            if match:
                length = float(match.group(1))
                width = float(match.group(2))
                unit = 'ft'  # default
                if len(match.groups()) >= 3 and match.group(3):
                    unit = match.group(3)
                plot_size = (length, width, unit)
                break
        
        if not plot_size:
            # Default assumption
            plot_size = (40, 50, 'ft')
            self.assumptions.append(f"Plot size assumed as {plot_size[0]}ft × {plot_size[1]}ft (standard residential)")
        
        params['plot_length'] = plot_size[0]
        params['plot_width'] = plot_size[1]
        params['plot_unit'] = unit if unit in ['m', 'meter', 'metre'] else 'ft'
        
        # Convert to feet if in meters
        if params['plot_unit'] in ['m', 'meter', 'metre']:
            params['plot_length'] = params['plot_length'] * 3.28084
            params['plot_width'] = params['plot_width'] * 3.28084
            params['plot_unit'] = 'ft'
        
        # Calculate plot area
        params['plot_area_sqft'] = params['plot_length'] * params['plot_width']
        
        # Extract facing direction
        facing_patterns = ['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
        params['facing'] = next((f for f in facing_patterns if f in input_lower), 'east')
        
        # Extract road side
        if 'road' in input_lower:
            for direction in facing_patterns:
                if direction in input_lower and 'road' in input_lower:
                    params['road_side'] = direction
                    break
        if 'road_side' not in params:
            params['road_side'] = params['facing']
        
        # Extract setbacks
        setback_match = re.search(r'setback[:\s]+(\d+)', input_lower)
        params['setback'] = int(setback_match.group(1)) if setback_match else 5
        if not setback_match:
            self.assumptions.append(f"Setback assumed as {params['setback']} feet on all sides")
        
        # Extract number of floors
        floor_patterns = [
            r'g\+(\d+)',
            r'(\d+)\s*floor',
            r'(\d+)\s*storey'
        ]
        
        floors = 1
        for pattern in floor_patterns:
            match = re.search(pattern, input_lower)
            if match:
                if 'g+' in input_lower:
                    floors = int(match.group(1)) + 1
                else:
                    floors = int(match.group(1))
                break
        params['floors'] = floors
        
        # Extract BHK configuration
        bhk_match = re.search(r'(\d+)\s*bhk', input_lower)
        params['bhk'] = int(bhk_match.group(1)) if bhk_match else 2
        
        # Extract special requirements
        params['parking'] = any(word in input_lower for word in ['parking', 'car', 'garage'])
        params['balcony'] = any(word in input_lower for word in ['balcony', 'balconies'])
        params['pooja'] = any(word in input_lower for word in ['pooja', 'puja', 'prayer'])
        params['lift'] = any(word in input_lower for word in ['lift', 'elevator'])
        params['duplex'] = 'duplex' in input_lower
        
        # Extract staircase type
        if 'internal' in input_lower and 'stair' in input_lower:
            params['staircase_type'] = 'internal'
        elif 'external' in input_lower and 'stair' in input_lower:
            params['staircase_type'] = 'external'
        else:
            params['staircase_type'] = 'internal' if floors > 1 else 'none'
        
        # Extract budget category
        if any(word in input_lower for word in ['premium', 'luxury', 'high end']):
            params['budget_category'] = 'premium'
        elif any(word in input_lower for word in ['compact', 'budget', 'economical']):
            params['budget_category'] = 'compact'
        else:
            params['budget_category'] = 'standard'
        
        # Extract built-up area if mentioned
        builtup_match = re.search(r'built[- ]?up[:\s]+(\d+)', input_lower)
        if builtup_match:
            params['target_builtup'] = int(builtup_match.group(1))
        
        # Extract soil SBC if mentioned
        sbc_match = re.search(r'sbc[:\s]+(\d+)', input_lower)
        params['soil_sbc'] = int(sbc_match.group(1)) if sbc_match else 150  # kN/m²
        if not sbc_match:
            self.assumptions.append(f"Soil SBC assumed as {params['soil_sbc']} kN/m²")
        
        # Extract seismic zone
        zone_match = re.search(r'zone[:\s]+(ii|iii|iv|v)', input_lower)
        params['seismic_zone'] = zone_match.group(1).upper() if zone_match else 'III'
        if not zone_match:
            self.assumptions.append(f"Seismic zone assumed as Zone {params['seismic_zone']} (moderate)")
        
        # Extract user-provided room dimensions
        self._extract_user_dimensions(user_input, params)
        
        return params
    
    def _extract_user_dimensions(self, user_input: str, params: Dict):
        """Extract any user-specified room dimensions"""
        # Look for patterns like "master bedroom 12x14" or "living room: 14x16 ft"
        room_patterns = [
            r'(master bedroom|bedroom|living|kitchen|dining)[:\s]+(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)',
            r'(master bedroom|bedroom|living|kitchen|dining)\s+(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)'
        ]
        
        for pattern in room_patterns:
            matches = re.finditer(pattern, user_input.lower())
            for match in matches:
                room_name = match.group(1).strip()
                dim1 = float(match.group(2))
                dim2 = float(match.group(3))
                self.user_dimensions[room_name] = (dim1, dim2)
                print(f"User dimension detected: {room_name} = {dim1} × {dim2} ft")
    
    def calculate_builtup_area(self, params: Dict) -> float:
        """
        SECTION 4: Built-up area calculation
        """
        if 'target_builtup' in params:
            return params['target_builtup']
        
        # Calculate based on ground coverage
        plot_area = params['plot_area_sqft']
        budget = params['budget_category']
        
        if budget == 'premium':
            coverage_pct = self.GROUND_COVERAGE['premium_villa']['typical']
        elif budget == 'compact':
            coverage_pct = self.GROUND_COVERAGE['urban']['max']
        else:
            coverage_pct = self.GROUND_COVERAGE['semi_urban']['typical']
        
        ground_floor_area = plot_area * (coverage_pct / 100)
        
        # Account for setbacks
        setback = params['setback']
        usable_length = params['plot_length'] - (2 * setback)
        usable_width = params['plot_width'] - (2 * setback)
        usable_area = usable_length * usable_width
        
        ground_floor_area = min(ground_floor_area, usable_area)
        
        # Total built-up for all floors
        total_builtup = ground_floor_area * params['floors']
        
        self.assumptions.append(f"Built-up area calculated as {total_builtup:.0f} sqft ({coverage_pct}% ground coverage × {params['floors']} floors)")
        
        return total_builtup

    
    def allocate_spaces_by_percentage(self, params: Dict, total_builtup: float) -> Dict:
        """
        SECTION 3: Percentage-based space allocation
        Only used when user dimensions NOT provided
        """
        allocation = {}
        bhk = params['bhk']
        floors = params['floors']
        has_staircase = params['staircase_type'] != 'none'
        
        # Living + Dining
        if 'living' not in self.user_dimensions:
            living_pct = self.SPACE_ALLOCATION['living_dining']['typical']
            allocation['living_dining'] = total_builtup * (living_pct / 100)
        
        # Kitchen
        if 'kitchen' not in self.user_dimensions:
            kitchen_pct = self.SPACE_ALLOCATION['kitchen']['typical']
            allocation['kitchen'] = total_builtup * (kitchen_pct / 100)
        
        # Master Bedroom
        if 'master bedroom' not in self.user_dimensions:
            master_pct = self.SPACE_ALLOCATION['master_bedroom']['typical']
            allocation['master_bedroom'] = total_builtup * (master_pct / 100)
        
        # Other Bedrooms
        other_bedrooms = bhk - 1
        if 'bedroom' not in self.user_dimensions:
            bedroom_pct = self.SPACE_ALLOCATION['other_bedroom']['typical']
            allocation['other_bedrooms'] = total_builtup * (bedroom_pct / 100) * other_bedrooms
        
        # Bathrooms
        bathroom_pct = self.SPACE_ALLOCATION['bathrooms_total']['typical']
        allocation['bathrooms'] = total_builtup * (bathroom_pct / 100)
        
        # Staircase
        if has_staircase:
            if params['staircase_type'] == 'internal':
                stair_pct = self.SPACE_ALLOCATION['staircase_internal']['typical']
            else:
                stair_pct = self.SPACE_ALLOCATION['staircase_external']['typical']
            allocation['staircase'] = total_builtup * (stair_pct / 100)
        
        # Pooja
        if params['pooja']:
            pooja_pct = self.SPACE_ALLOCATION['pooja']['typical']
            allocation['pooja'] = total_builtup * (pooja_pct / 100)
        
        # Circulation
        circulation_pct = self.SPACE_ALLOCATION['circulation']['typical']
        allocation['circulation'] = total_builtup * (circulation_pct / 100)
        
        # Balcony
        if params['balcony']:
            balcony_pct = self.SPACE_ALLOCATION['balcony']['typical']
            allocation['balcony'] = total_builtup * (balcony_pct / 100)
        
        # Parking
        if params['parking']:
            parking_pct = self.SPACE_ALLOCATION['parking_single']['typical']
            allocation['parking'] = total_builtup * (parking_pct / 100)
        
        return allocation
    
    def generate_floor_layout(self, params: Dict, allocation: Dict, floor_num: int) -> Dict:
        """
        SECTION 5: Architectural design with rules
        Generate realistic, buildable floor layout
        """
        floor = {
            'floor_number': floor_num,
            'rooms': [],
            'built_up_area': 0
        }
        
        usable_length = params['plot_length'] - (2 * params['setback'])
        usable_width = params['plot_width'] - (2 * params['setback'])
        
        current_x = 0
        current_y = 0
        
        # Ground floor layout
        if floor_num == 1:
            # Parking (if required)
            if params['parking'] and 'parking' in allocation:
                parking_area = allocation['parking']
                parking_width = 10  # ft
                parking_length = parking_area / parking_width
                floor['rooms'].append({
                    'name': 'Parking',
                    'width': parking_width,
                    'length': parking_length,
                    'area': parking_area,
                    'position': 'front',
                    'coordinates': {'x1': current_x, 'y1': current_y, 
                                  'x2': current_x + parking_width, 'y2': current_y + parking_length}
                })
                current_y += parking_length
            
            # Living + Dining
            if 'living' in self.user_dimensions:
                living_width, living_length = self.user_dimensions['living']
                living_area = living_width * living_length
            elif 'living_dining' in allocation:
                living_area = allocation['living_dining']
                living_width = min(usable_width * 0.6, 16)
                living_length = living_area / living_width
            else:
                living_width = 14
                living_length = 16
                living_area = living_width * living_length
            
            floor['rooms'].append({
                'name': 'Living + Dining',
                'width': round(living_width, 1),
                'length': round(living_length, 1),
                'area': round(living_area, 1),
                'position': 'front center',
                'coordinates': {'x1': current_x, 'y1': current_y,
                              'x2': current_x + living_width, 'y2': current_y + living_length},
                'user_specified': 'living' in self.user_dimensions
            })
            current_y += living_length
            
            # Kitchen
            if 'kitchen' in self.user_dimensions:
                kitchen_width, kitchen_length = self.user_dimensions['kitchen']
                kitchen_area = kitchen_width * kitchen_length
            elif 'kitchen' in allocation:
                kitchen_area = allocation['kitchen']
                kitchen_width = 10
                kitchen_length = kitchen_area / kitchen_width
            else:
                kitchen_width = 10
                kitchen_length = 12
                kitchen_area = kitchen_width * kitchen_length
            
            floor['rooms'].append({
                'name': 'Kitchen',
                'width': round(kitchen_width, 1),
                'length': round(kitchen_length, 1),
                'area': round(kitchen_area, 1),
                'position': 'rear left',
                'coordinates': {'x1': 0, 'y1': current_y,
                              'x2': kitchen_width, 'y2': current_y + kitchen_length},
                'user_specified': 'kitchen' in self.user_dimensions
            })
            
            # Pooja Room
            if params['pooja']:
                if 'pooja' in allocation:
                    pooja_area = allocation['pooja']
                    pooja_width = 5
                    pooja_length = pooja_area / pooja_width
                else:
                    pooja_width = 5
                    pooja_length = 6
                    pooja_area = pooja_width * pooja_length
                
                floor['rooms'].append({
                    'name': 'Pooja Room',
                    'width': round(pooja_width, 1),
                    'length': round(pooja_length, 1),
                    'area': round(pooja_area, 1),
                    'position': 'near entrance (east/northeast preferred)',
                    'coordinates': {'x1': kitchen_width, 'y1': current_y,
                                  'x2': kitchen_width + pooja_width, 'y2': current_y + pooja_length}
                })
        
        # Bedrooms (distributed across floors for duplex)
        bhk = params['bhk']
        bedrooms_this_floor = bhk if floor_num == 1 and params['floors'] == 1 else (1 if floor_num == 1 else bhk - 1)
        
        for i in range(bedrooms_this_floor):
            is_master = (i == 0 and floor_num == (2 if params['duplex'] else 1))
            
            if is_master and 'master bedroom' in self.user_dimensions:
                bed_width, bed_length = self.user_dimensions['master bedroom']
                bed_area = bed_width * bed_length
            elif not is_master and 'bedroom' in self.user_dimensions:
                bed_width, bed_length = self.user_dimensions['bedroom']
                bed_area = bed_width * bed_length
            elif is_master and 'master_bedroom' in allocation:
                bed_area = allocation['master_bedroom']
                bed_width = 12
                bed_length = bed_area / bed_width
            elif 'other_bedrooms' in allocation:
                bed_area = allocation['other_bedrooms'] / (bhk - 1)
                bed_width = 11
                bed_length = bed_area / bed_width
            else:
                bed_width = 12 if is_master else 11
                bed_length = 14 if is_master else 12
                bed_area = bed_width * bed_length
            
            floor['rooms'].append({
                'name': 'Master Bedroom' if is_master else f'Bedroom {i+1}',
                'width': round(bed_width, 1),
                'length': round(bed_length, 1),
                'area': round(bed_area, 1),
                'position': f'rear {"left" if i == 0 else "right" if i == 1 else "center"}',
                'coordinates': {'x1': i * bed_width, 'y1': current_y,
                              'x2': (i + 1) * bed_width, 'y2': current_y + bed_length},
                'user_specified': ('master bedroom' in self.user_dimensions if is_master else 'bedroom' in self.user_dimensions)
            })
        
        # Bathrooms
        num_bathrooms = bhk
        if 'bathrooms' in allocation:
            total_bath_area = allocation['bathrooms']
            bath_area = total_bath_area / num_bathrooms
            bath_width = 5
            bath_length = bath_area / bath_width
        else:
            bath_width = 5
            bath_length = 8
            bath_area = bath_width * bath_length
        
        for i in range(num_bathrooms):
            floor['rooms'].append({
                'name': f'Bathroom {i+1}',
                'width': round(bath_width, 1),
                'length': round(bath_length, 1),
                'area': round(bath_area, 1),
                'position': f'attached to {"Master Bedroom" if i == 0 else f"Bedroom {i+1}"}',
                'coordinates': {'x1': i * 10, 'y1': current_y + 12,
                              'x2': i * 10 + bath_width, 'y2': current_y + 12 + bath_length}
            })
        
        # Staircase
        if params['staircase_type'] != 'none':
            if 'staircase' in allocation:
                stair_area = allocation['staircase']
                stair_width = 3.5
                stair_length = stair_area / stair_width
            else:
                stair_width = 3.5
                stair_length = 12
                stair_area = stair_width * stair_length
            
            floor['rooms'].append({
                'name': 'Staircase',
                'width': round(stair_width, 1),
                'length': round(stair_length, 1),
                'area': round(stair_area, 1),
                'position': 'rear right corner',
                'coordinates': {'x1': usable_width - stair_width, 'y1': 0,
                              'x2': usable_width, 'y2': stair_length},
                'type': params['staircase_type']
            })
        
        # Calculate total built-up for this floor
        floor['built_up_area'] = sum(room['area'] for room in floor['rooms'])
        
        return floor
    
    def generate_structural_grid(self, params: Dict) -> Dict:
        """
        SECTION 6: Structural integration
        """
        usable_length = params['plot_length'] - (2 * params['setback'])
        usable_width = params['plot_width'] - (2 * params['setback'])
        
        # Convert to meters for structural calculations
        length_m = usable_length * 0.3048
        width_m = usable_width * 0.3048
        
        # Calculate optimal column spacing (3-4.5m)
        ideal_spacing = 4.0  # meters
        
        cols_length = max(3, int(length_m / ideal_spacing) + 1)
        cols_width = max(3, int(width_m / ideal_spacing) + 1)
        
        actual_spacing_length = length_m / (cols_length - 1)
        actual_spacing_width = width_m / (cols_width - 1)
        
        total_columns = cols_length * cols_width
        
        # Column size based on floors
        if params['floors'] == 1:
            column_size = '230mm × 230mm (9" × 9")'
        elif params['floors'] == 2:
            column_size = '230mm × 300mm (9" × 12")'
        elif params['floors'] == 3:
            column_size = '300mm × 300mm (12" × 12")'
        else:
            column_size = '300mm × 380mm (12" × 15")'
        
        # Beam depth calculation
        max_span = max(actual_spacing_length, actual_spacing_width)
        beam_depth = max_span / self.STRUCTURAL_PARAMS['beam_depth_ratio']
        beam_depth_mm = int(beam_depth * 1000)
        beam_width_mm = int(beam_depth_mm * 0.5)  # Width = 0.5 × Depth
        
        # Slab thickness
        slab_thickness = self.STRUCTURAL_PARAMS['slab_thickness_min'] if params['floors'] <= 2 else self.STRUCTURAL_PARAMS['slab_thickness_max']
        
        return {
            'grid_pattern': f'{cols_length} × {cols_width}',
            'spacing_length_m': round(actual_spacing_length, 2),
            'spacing_width_m': round(actual_spacing_width, 2),
            'total_columns': total_columns,
            'column_size': column_size,
            'beam_size': f'{beam_width_mm}mm × {beam_depth_mm}mm',
            'slab_thickness_mm': slab_thickness,
            'concrete_grade': self.STRUCTURAL_PARAMS['concrete_grade'],
            'steel_grade': self.STRUCTURAL_PARAMS['steel_grade'],
            'max_span_m': round(max_span, 2),
            'span_check': '✓ Safe' if max_span <= self.STRUCTURAL_PARAMS['max_beam_span'] else '⚠️ Exceeds 5.5m',
            'notes': 'Columns aligned vertically from foundation to top floor'
        }
    
    def recommend_foundation(self, params: Dict, structural_grid: Dict) -> Dict:
        """
        SECTION 7: Foundation selection
        """
        sbc = params['soil_sbc']  # kN/m²
        floors = params['floors']
        
        if sbc >= 200:
            foundation_type = 'Isolated Footing'
            depth = '1.0-1.5m'
        elif sbc >= 150:
            foundation_type = 'Isolated Footing' if floors <= 2 else 'Combined Footing'
            depth = '1.2-1.8m'
        elif sbc >= 100:
            foundation_type = 'Combined Footing' if floors <= 3 else 'Raft Foundation'
            depth = '1.5-2.0m'
        else:
            foundation_type = 'Raft Foundation' if floors <= 4 else 'Pile Foundation'
            depth = '2.0-3.0m' if foundation_type == 'Raft Foundation' else '5.0-15.0m'
        
        return {
            'type': foundation_type,
            'depth': depth,
            'soil_sbc': f'{sbc} kN/m²',
            'bearing_pressure': 'Within safe limits' if sbc >= 150 else 'Requires soil improvement',
            'plinth_height': '0.45-0.60m (1.5-2.0 ft) above ground level',
            'notes': 'Soil test mandatory before final design'
        }
    
    def estimate_quantities(self, params: Dict, total_builtup: float) -> Dict:
        """
        SECTION 8: Quantity estimation (early stage)
        """
        builtup_sqm = total_builtup * 0.092903  # sqft to sqm
        
        # Concrete
        concrete_factor = self.QUANTITY_FACTORS['concrete_per_sqm']['typical']
        concrete_m3 = builtup_sqm * concrete_factor
        
        # Steel
        steel_factor = self.QUANTITY_FACTORS['steel_per_sqm']['typical']
        steel_kg = builtup_sqm * steel_factor
        steel_tons = steel_kg / 1000
        
        # Shuttering
        shuttering_factor = self.QUANTITY_FACTORS['shuttering_per_sqm']['typical']
        shuttering_sqm = builtup_sqm * shuttering_factor
        
        # Excavation
        plot_area_sqm = params['plot_area_sqft'] * 0.092903
        excavation_depth = self.QUANTITY_FACTORS['excavation_depth']
        excavation_m3 = plot_area_sqm * excavation_depth * 0.3  # 30% of plot area
        
        # Brickwork
        wall_area_sqm = builtup_sqm * 2.5  # Approximate wall area
        bricks = wall_area_sqm * self.QUANTITY_FACTORS['brickwork_per_sqm']
        
        return {
            'concrete_m3': round(concrete_m3, 2),
            'concrete_bags_cement': int(concrete_m3 * 7),  # 7 bags per m³
            'steel_kg': round(steel_kg, 0),
            'steel_tons': round(steel_tons, 2),
            'shuttering_sqm': round(shuttering_sqm, 2),
            'excavation_m3': round(excavation_m3, 2),
            'bricks': int(bricks),
            'sand_cft': int(builtup_sqm * 1.8 * 10.764),  # cft
            'aggregate_cft': int(builtup_sqm * 2.7 * 10.764),  # cft
            'note': 'Preliminary conceptual estimate - detailed BOQ required'
        }
    
    def check_compliance(self, params: Dict, floors: List[Dict]) -> List[str]:
        """
        SECTION 10: Compliance & feasibility check
        """
        checks = []
        
        # Check room sizes
        for floor in floors:
            for room in floor['rooms']:
                if 'Bedroom' in room['name']:
                    if room['area'] < 100:
                        checks.append(f"⚠️ {room['name']} ({room['area']} sqft) below recommended 100 sqft")
                    else:
                        checks.append(f"✓ {room['name']} ({room['area']} sqft) meets standards")
                
                if 'Living' in room['name']:
                    if room['area'] < 150:
                        checks.append(f"⚠️ {room['name']} ({room['area']} sqft) below recommended 150 sqft")
                    else:
                        checks.append(f"✓ {room['name']} ({room['area']} sqft) meets standards")
                
                if 'Kitchen' in room['name']:
                    if room['area'] < 80:
                        checks.append(f"⚠️ {room['name']} ({room['area']} sqft) below recommended 80 sqft")
                    else:
                        checks.append(f"✓ {room['name']} ({room['area']} sqft) meets standards")
        
        # Check aspect ratios
        for floor in floors:
            for room in floor['rooms']:
                if room['width'] > 0 and room['length'] > 0:
                    ratio = max(room['width'], room['length']) / min(room['width'], room['length'])
                    if ratio > 2.0:
                        checks.append(f"⚠️ {room['name']} aspect ratio {ratio:.1f}:1 exceeds recommended 2:1")
        
        # Check circulation
        total_builtup = sum(floor['built_up_area'] for floor in floors)
        circulation_area = sum(room['area'] for floor in floors for room in floor['rooms'] if 'circulation' in room['name'].lower())
        circulation_pct = (circulation_area / total_builtup) * 100 if total_builtup > 0 else 0
        
        if circulation_pct > 15:
            checks.append(f"⚠️ Circulation {circulation_pct:.1f}% exceeds recommended 15%")
        elif circulation_pct < 8:
            checks.append(f"⚠️ Circulation {circulation_pct:.1f}% below recommended 8%")
        else:
            checks.append(f"✓ Circulation {circulation_pct:.1f}% within optimal range")
        
        return checks
    
    def generate_complete_solution(self, user_input: str) -> Dict:
        """
        Main method: Generate complete architectural solution
        """
        # Section 1: Extract parameters
        params = self.extract_parameters(user_input)
        
        # Section 4: Calculate built-up area
        total_builtup = self.calculate_builtup_area(params)
        
        # Section 3: Allocate spaces by percentage
        allocation = self.allocate_spaces_by_percentage(params, total_builtup)
        
        # Section 5: Generate floor layouts
        floors = []
        for floor_num in range(1, params['floors'] + 1):
            floor = self.generate_floor_layout(params, allocation, floor_num)
            floors.append(floor)
        
        # Section 6: Structural grid
        structural_grid = self.generate_structural_grid(params)
        
        # Section 7: Foundation recommendation
        foundation = self.recommend_foundation(params, structural_grid)
        
        # Section 8: Quantity estimation
        quantities = self.estimate_quantities(params, total_builtup)
        
        # Section 10: Compliance check
        compliance = self.check_compliance(params, floors)
        
        # Compile complete solution
        solution = {
            '1_extracted_parameters': params,
            '2_assumptions': self.assumptions,
            '3_builtup_area_calculation': {
                'total_builtup_sqft': round(total_builtup, 0),
                'ground_floor_sqft': round(total_builtup / params['floors'], 0),
                'floors': params['floors']
            },
            '4_percentage_allocation': allocation,
            '5_floor_layouts': floors,
            '6_structural_grid': structural_grid,
            '7_foundation': foundation,
            '8_quantity_estimate': quantities,
            '9_services_stacking': {
                'bathrooms': 'Vertically stacked for plumbing efficiency',
                'kitchen': 'Separate stack for kitchen drainage',
                'water_tank': 'Terrace level, above bathroom stack',
                'electrical': 'Vertical risers in service shaft'
            },
            '10_compliance_check': compliance,
            '11_optimization_suggestions': self._generate_suggestions(params, floors, structural_grid)
        }
        
        return solution
    
    def _generate_suggestions(self, params: Dict, floors: List[Dict], structural_grid: Dict) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        suggestions.append("Conduct detailed soil investigation before finalizing foundation")
        suggestions.append("Obtain structural design from licensed engineer")
        suggestions.append("Ensure proper curing of concrete (minimum 7 days)")
        suggestions.append("Provide cross-ventilation in all habitable rooms")
        suggestions.append("Use earthquake-resistant design as per IS 1893")
        suggestions.append("Maintain 25mm concrete cover for durability")
        suggestions.append("Install rainwater harvesting system")
        suggestions.append("Consider solar panels for energy efficiency")
        
        return suggestions
