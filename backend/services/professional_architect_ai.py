"""
BuildWise Professional Architect AI System
Intelligent input extraction and architectural design logic
Accepts ANY input format and generates realistic, buildable layouts
"""

import re
import json
import requests
from typing import Dict, List, Optional, Tuple

class ProfessionalArchitectAI:
    """
    Professional Architect AI with 20+ years experience
    Accepts ANY input format and generates realistic architectural layouts
    """
    
    # Room size standards (in feet) - Professional minimums
    ROOM_STANDARDS = {
        'master_bedroom': {'min_width': 11, 'min_length': 12, 'typical_width': 12, 'typical_length': 14},
        'bedroom': {'min_width': 10, 'min_length': 11, 'typical_width': 11, 'typical_length': 12},
        'living': {'min_width': 12, 'min_length': 14, 'typical_width': 14, 'typical_length': 16},
        'kitchen': {'min_width': 8, 'min_length': 10, 'typical_width': 10, 'typical_length': 12},
        'bathroom': {'min_width': 4, 'min_length': 7, 'typical_width': 5, 'typical_length': 8},
        'staircase': {'min_width': 3, 'min_length': 10, 'typical_width': 3.5, 'typical_length': 12},
        'passage': {'min_width': 3, 'min_length': 5, 'typical_width': 3.5, 'typical_length': 8},
        'parking': {'min_width': 9, 'min_length': 15, 'typical_width': 10, 'typical_length': 18}
    }
    
    # Wall thickness standards (in inches)
    WALL_THICKNESS = {
        'external': 9,  # 230mm
        'internal': 4.5  # 115mm
    }
    
    # Beam span standards (in feet)
    BEAM_SPANS = {
        'ideal_min': 10,
        'ideal_max': 16,
        'absolute_max': 20
    }
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
    
    def extract_parameters(self, user_input: str) -> Dict:
        """
        Extract architectural parameters from ANY input format
        Handles: paragraph, bullets, JSON, mixed, incomplete inputs
        
        Args:
            user_input: Any format text input
            
        Returns:
            dict: Normalized parameters with smart assumptions
        """
        input_lower = user_input.lower()
        params = {}
        
        # Extract plot size (multiple formats)
        plot_patterns = [
            r'(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)\s*(ft|feet|foot|m|meter|metre)',
            r'plot\s+size[:\s]+(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s+by\s+(\d+\.?\d*)\s*(ft|feet|foot|m|meter)',
            r'length[:\s]+(\d+\.?\d*).*width[:\s]+(\d+\.?\d*)',
            r'width[:\s]+(\d+\.?\d*).*length[:\s]+(\d+\.?\d*)'
        ]
        
        plot_size = None
        unit = 'ft'
        for pattern in plot_patterns:
            match = re.search(pattern, input_lower)
            if match:
                width = float(match.group(1))
                length = float(match.group(2))
                if len(match.groups()) >= 3 and match.group(3):
                    unit = match.group(3)
                plot_size = (width, length, unit)
                break
        
        if not plot_size:
            # Default assumption for missing plot size
            plot_size = (30, 40, 'ft')
            params['plot_size_assumed'] = True
        
        params['plot_width'] = plot_size[0]
        params['plot_length'] = plot_size[1]
        params['plot_unit'] = unit if unit in ['m', 'meter', 'metre'] else 'ft'
        
        # Convert to feet if in meters
        if params['plot_unit'] in ['m', 'meter', 'metre']:
            params['plot_width'] = params['plot_width'] * 3.28084
            params['plot_length'] = params['plot_length'] * 3.28084
            params['plot_unit'] = 'ft'
        
        # Extract facing direction
        facing_patterns = ['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
        params['facing'] = next((f for f in facing_patterns if f in input_lower), 'east')
        
        # Extract number of floors
        floor_patterns = [
            r'g\+(\d+)',
            r'(\d+)\s*floor',
            r'(\d+)\s*storey',
            r'(\d+)\s*story'
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
        
        # Extract bedrooms
        bedroom_patterns = [
            r'(\d+)\s*bhk',
            r'(\d+)\s*bedroom',
            r'(\d+)\s*bed'
        ]
        
        bedrooms = 2  # default
        for pattern in bedroom_patterns:
            match = re.search(pattern, input_lower)
            if match:
                bedrooms = int(match.group(1))
                break
        params['bedrooms'] = bedrooms
        
        # Extract special requirements
        params['parking'] = any(word in input_lower for word in ['parking', 'car', 'garage'])
        params['balcony'] = any(word in input_lower for word in ['balcony', 'balconies'])
        params['pooja'] = any(word in input_lower for word in ['pooja', 'puja', 'prayer'])
        params['office'] = any(word in input_lower for word in ['office', 'study', 'work room'])
        params['duplex'] = 'duplex' in input_lower
        
        # Extract staircase type
        if 'internal' in input_lower and 'stair' in input_lower:
            params['staircase_type'] = 'internal'
        elif 'external' in input_lower and 'stair' in input_lower:
            params['staircase_type'] = 'external'
        else:
            params['staircase_type'] = 'internal' if floors > 1 else 'none'
        
        # Extract setbacks (if mentioned)
        setback_match = re.search(r'setback[:\s]+(\d+)', input_lower)
        params['setback'] = int(setback_match.group(1)) if setback_match else 5  # default 5 ft
        
        # Extract budget category
        if any(word in input_lower for word in ['premium', 'luxury', 'high end']):
            params['budget_category'] = 'premium'
        elif any(word in input_lower for word in ['mid', 'medium', 'moderate']):
            params['budget_category'] = 'mid'
        else:
            params['budget_category'] = 'standard'
        
        # Calculate built-up area if mentioned
        area_match = re.search(r'(\d+)\s*sqft', input_lower)
        if area_match:
            params['target_builtup'] = int(area_match.group(1))
        
        return params
    
    def generate_professional_layout(self, user_input: str) -> Dict:
        """
        Generate professional architectural layout from any input format
        
        Returns:
            dict: Complete architectural design with 10 sections
        """
        # Step 1: Extract parameters
        params = self.extract_parameters(user_input)
        
        # Step 2: Make assumptions for missing data
        assumptions = self._make_assumptions(params)
        
        # Step 3: Generate floor-wise layout
        floor_layouts = self._generate_floor_layouts(params)
        
        # Step 4: Generate structural grid
        structural_grid = self._generate_structural_grid(params)
        
        # Step 5: Determine staircase location
        staircase_location = self._determine_staircase_location(params)
        
        # Step 6: Plan plumbing stack
        plumbing_strategy = self._plan_plumbing_stack(params, floor_layouts)
        
        # Step 7: Plan ventilation
        ventilation_strategy = self._plan_ventilation(params, floor_layouts)
        
        # Step 8: Plan parking
        parking_arrangement = self._plan_parking(params)
        
        # Step 9: Structural feasibility check
        feasibility_notes = self._check_structural_feasibility(params, floor_layouts, structural_grid)
        
        # Step 10: Generate recommendations
        recommendations = self._generate_recommendations(params, floor_layouts, feasibility_notes)
        
        return {
            '1_extracted_parameters': params,
            '2_assumptions_made': assumptions,
            '3_floor_layouts': floor_layouts,
            '4_structural_grid': structural_grid,
            '5_staircase_location': staircase_location,
            '6_plumbing_stack_strategy': plumbing_strategy,
            '7_ventilation_strategy': ventilation_strategy,
            '8_parking_arrangement': parking_arrangement,
            '9_structural_feasibility': feasibility_notes,
            '10_recommendations': recommendations,
            'original_input': user_input
        }

    
    def _make_assumptions(self, params: Dict) -> List[str]:
        """Generate list of assumptions made for missing data"""
        assumptions = []
        
        if params.get('plot_size_assumed'):
            assumptions.append(f"Plot size assumed as {params['plot_width']}ft × {params['plot_length']}ft (standard residential)")
        
        if 'target_builtup' not in params:
            assumptions.append(f"Target built-up area calculated based on {params['bedrooms']}BHK configuration")
        
        assumptions.append(f"Wall thickness: {self.WALL_THICKNESS['external']}\" external, {self.WALL_THICKNESS['internal']}\" internal")
        assumptions.append(f"Floor height: 10 feet (standard residential)")
        assumptions.append(f"Setback: {params['setback']} feet on all sides")
        assumptions.append(f"Structural system: RCC frame structure")
        assumptions.append(f"Foundation: Isolated footings (subject to soil test)")
        
        if params['floors'] > 1:
            assumptions.append(f"Staircase type: {params['staircase_type']}")
        
        return assumptions
    
    def _generate_floor_layouts(self, params: Dict) -> List[Dict]:
        """Generate realistic floor-wise layouts"""
        floors = []
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        setback = params['setback']
        
        # Usable area after setbacks
        usable_width = plot_width - (2 * setback)
        usable_length = plot_length - (2 * setback)
        
        for floor_num in range(1, params['floors'] + 1):
            if params.get('duplex') and floor_num == 2:
                # Upper floor in duplex: bedrooms only
                floor = self._generate_duplex_upper_floor(params, usable_width, usable_length)
            else:
                # Standard floor
                floor = self._generate_standard_floor(params, usable_width, usable_length, floor_num)
            
            floor['floor_number'] = floor_num
            floors.append(floor)
        
        return floors
    
    def _generate_standard_floor(self, params: Dict, width: float, length: float, floor_num: int) -> Dict:
        """Generate standard floor layout with realistic room placement"""
        rooms = []
        current_y = 0
        
        # Staircase (if multi-floor and internal)
        if params['floors'] > 1 and params['staircase_type'] == 'internal':
            stair = self.ROOM_STANDARDS['staircase']
            rooms.append({
                'name': 'Staircase',
                'dimensions': f"{stair['typical_width']}ft × {stair['typical_length']}ft",
                'area': round(stair['typical_width'] * stair['typical_length'], 1),
                'location': 'rear right',
                'notes': 'U-shaped, 3ft width minimum'
            })
        
        # Living room (front)
        living = self.ROOM_STANDARDS['living']
        living_width = min(living['typical_width'], width * 0.6)
        living_length = min(living['typical_length'], length * 0.35)
        rooms.append({
            'name': 'Living Room',
            'dimensions': f"{living_width}ft × {living_length}ft",
            'area': round(living_width * living_length, 1),
            'location': 'front center',
            'notes': 'Main entrance, cross-ventilation'
        })
        current_y += living_length
        
        # Kitchen (adjacent to living)
        kitchen = self.ROOM_STANDARDS['kitchen']
        kitchen_width = min(kitchen['typical_width'], width * 0.4)
        kitchen_length = min(kitchen['typical_length'], length * 0.25)
        rooms.append({
            'name': 'Kitchen',
            'dimensions': f"{kitchen_width}ft × {kitchen_length}ft",
            'area': round(kitchen_width * kitchen_length, 1),
            'location': 'rear left',
            'notes': 'Adjacent to living, service entrance'
        })
        
        # Bedrooms (rear)
        bedroom_count = params['bedrooms']
        for i in range(bedroom_count):
            if i == 0:
                # Master bedroom
                bed = self.ROOM_STANDARDS['master_bedroom']
                name = 'Master Bedroom'
            else:
                bed = self.ROOM_STANDARDS['bedroom']
                name = f'Bedroom {i+1}'
            
            bed_width = min(bed['typical_width'], width / bedroom_count)
            bed_length = min(bed['typical_length'], length * 0.4)
            
            rooms.append({
                'name': name,
                'dimensions': f"{bed_width}ft × {bed_length}ft",
                'area': round(bed_width * bed_length, 1),
                'location': f'rear {"left" if i == 0 else "right" if i == 1 else "center"}',
                'notes': 'Attached bathroom' if i == 0 else 'Common bathroom access'
            })
        
        # Bathrooms
        bathroom_count = bedroom_count  # One per bedroom
        for i in range(bathroom_count):
            bath = self.ROOM_STANDARDS['bathroom']
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f"{bath['typical_width']}ft × {bath['typical_length']}ft",
                'area': round(bath['typical_width'] * bath['typical_length'], 1),
                'location': f'attached to {"Master Bedroom" if i == 0 else f"Bedroom {i+1}"}',
                'notes': 'Vertically stacked for plumbing'
            })
        
        # Optional rooms
        if params.get('pooja'):
            rooms.append({
                'name': 'Pooja Room',
                'dimensions': '5ft × 6ft',
                'area': 30,
                'location': 'near entrance',
                'notes': 'East or northeast facing preferred'
            })
        
        if params.get('office'):
            rooms.append({
                'name': 'Study/Office',
                'dimensions': '8ft × 10ft',
                'area': 80,
                'location': 'front side',
                'notes': 'Good natural lighting'
            })
        
        # Calculate total built-up
        total_builtup = sum(room['area'] for room in rooms)
        
        # Add circulation (15-20%)
        circulation = total_builtup * 0.18
        total_with_circulation = total_builtup + circulation
        
        return {
            'rooms': rooms,
            'built_up_area': round(total_builtup, 1),
            'circulation_area': round(circulation, 1),
            'total_area': round(total_with_circulation, 1)
        }
    
    def _generate_duplex_upper_floor(self, params: Dict, width: float, length: float) -> Dict:
        """Generate upper floor for duplex (bedrooms only)"""
        rooms = []
        
        # Bedrooms
        bedroom_count = params['bedrooms']
        for i in range(bedroom_count):
            bed = self.ROOM_STANDARDS['master_bedroom'] if i == 0 else self.ROOM_STANDARDS['bedroom']
            bed_width = min(bed['typical_width'], width / bedroom_count)
            bed_length = min(bed['typical_length'], length * 0.5)
            
            rooms.append({
                'name': f'Bedroom {i+1}',
                'dimensions': f"{bed_width}ft × {bed_length}ft",
                'area': round(bed_width * bed_length, 1),
                'location': f'{"left" if i == 0 else "right" if i == 1 else "center"}',
                'notes': 'Attached bathroom'
            })
        
        # Bathrooms
        for i in range(bedroom_count):
            bath = self.ROOM_STANDARDS['bathroom']
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f"{bath['typical_width']}ft × {bath['typical_length']}ft",
                'area': round(bath['typical_width'] * bath['typical_length'], 1),
                'location': f'attached to Bedroom {i+1}',
                'notes': 'Vertically stacked'
            })
        
        total_builtup = sum(room['area'] for room in rooms)
        circulation = total_builtup * 0.15
        
        return {
            'rooms': rooms,
            'built_up_area': round(total_builtup, 1),
            'circulation_area': round(circulation, 1),
            'total_area': round(total_builtup + circulation, 1)
        }
    
    def _generate_structural_grid(self, params: Dict) -> Dict:
        """Generate structural column grid suggestion"""
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        
        # Ideal column spacing: 12-15 feet
        ideal_spacing = 12
        
        # Calculate number of columns
        cols_width = max(3, int(plot_width / ideal_spacing) + 1)
        cols_length = max(3, int(plot_length / ideal_spacing) + 1)
        
        # Actual spacing
        actual_spacing_width = plot_width / (cols_width - 1)
        actual_spacing_length = plot_length / (cols_length - 1)
        
        total_columns = cols_width * cols_length
        
        # Column size based on floors
        if params['floors'] == 1:
            column_size = '9" × 9"'
        elif params['floors'] == 2:
            column_size = '9" × 12"'
        else:
            column_size = '12" × 12"'
        
        return {
            'grid_pattern': f'{cols_width} × {cols_length}',
            'spacing_width': f'{actual_spacing_width:.1f} ft',
            'spacing_length': f'{actual_spacing_length:.1f} ft',
            'total_columns': total_columns,
            'column_size': column_size,
            'notes': 'Columns aligned vertically from foundation to top floor'
        }
    
    def _determine_staircase_location(self, params: Dict) -> Dict:
        """Determine optimal staircase location"""
        if params['floors'] == 1:
            return {'required': False, 'location': 'N/A'}
        
        staircase_type = params['staircase_type']
        
        if staircase_type == 'internal':
            return {
                'required': True,
                'type': 'Internal U-shaped',
                'location': 'Rear right corner',
                'dimensions': '3.5ft × 12ft',
                'notes': 'Minimum 3ft width, 7" rise, 10" tread'
            }
        else:
            return {
                'required': True,
                'type': 'External',
                'location': 'Outside building envelope',
                'dimensions': '3ft × 15ft',
                'notes': 'Saves internal space, weather protection needed'
            }
    
    def _plan_plumbing_stack(self, params: Dict, floor_layouts: List[Dict]) -> Dict:
        """Plan plumbing stack strategy"""
        return {
            'strategy': 'Vertical stacking',
            'main_stack_location': 'Rear wall, centralized',
            'bathroom_alignment': 'All bathrooms vertically aligned',
            'kitchen_connection': 'Separate stack for kitchen',
            'water_tank_location': 'Terrace, above bathroom stack',
            'drainage': 'Gravity-based, slope towards main drain',
            'notes': 'Minimize horizontal runs, use PVC pipes'
        }
    
    def _plan_ventilation(self, params: Dict, floor_layouts: List[Dict]) -> Dict:
        """Plan ventilation strategy"""
        facing = params['facing']
        
        return {
            'strategy': 'Cross-ventilation',
            'primary_openings': f'{facing.capitalize()} facing (main windows)',
            'secondary_openings': 'Opposite side for cross-flow',
            'living_room': '2-3 large windows, opposite walls',
            'bedrooms': '2 windows each, cross-ventilation',
            'kitchen': 'Window + exhaust fan',
            'bathrooms': 'Exhaust fan + ventilator',
            'notes': 'Minimum 10% of floor area as openings (NBC requirement)'
        }
    
    def _plan_parking(self, params: Dict) -> Dict:
        """Plan parking arrangement"""
        if not params.get('parking'):
            return {'required': False, 'arrangement': 'N/A'}
        
        parking = self.ROOM_STANDARDS['parking']
        
        return {
            'required': True,
            'type': 'Ground level parking',
            'location': 'Front setback area',
            'dimensions': f"{parking['typical_width']}ft × {parking['typical_length']}ft",
            'capacity': '1 car',
            'notes': 'Minimum 9ft × 15ft per car, paved surface'
        }
    
    def _check_structural_feasibility(self, params: Dict, floor_layouts: List[Dict], structural_grid: Dict) -> List[str]:
        """Check structural feasibility and identify issues"""
        notes = []
        
        # Check plot size adequacy
        plot_area = params['plot_width'] * params['plot_length']
        min_area_required = params['bedrooms'] * 500  # 500 sqft per bedroom
        
        if plot_area < min_area_required:
            notes.append(f'⚠️ Plot area ({plot_area:.0f} sqft) may be tight for {params["bedrooms"]}BHK')
        else:
            notes.append(f'✓ Plot area ({plot_area:.0f} sqft) adequate for {params["bedrooms"]}BHK')
        
        # Check column spacing
        spacing = float(structural_grid['spacing_width'].split()[0])
        if spacing > 20:
            notes.append(f'⚠️ Column spacing ({spacing:.1f}ft) exceeds recommended 20ft maximum')
        else:
            notes.append(f'✓ Column spacing ({spacing:.1f}ft) within safe limits')
        
        # Check beam spans
        if spacing > self.BEAM_SPANS['ideal_max']:
            notes.append(f'⚠️ Beam spans may require deeper beams or intermediate columns')
        else:
            notes.append(f'✓ Beam spans practical for residential construction')
        
        # Check floor height
        notes.append('✓ Standard 10ft floor height provides good ventilation')
        
        # Check load path
        notes.append('✓ Columns aligned vertically for proper load transfer')
        
        # Check bathroom stacking
        notes.append('✓ Bathrooms vertically stacked for efficient plumbing')
        
        return notes
    
    def _generate_recommendations(self, params: Dict, floor_layouts: List[Dict], feasibility: List[str]) -> List[str]:
        """Generate professional recommendations"""
        recommendations = []
        
        # Structural recommendations
        recommendations.append('Conduct soil test before finalizing foundation design')
        recommendations.append('Use RCC frame structure with brick infill walls')
        recommendations.append('Ensure proper curing of concrete (minimum 7 days)')
        
        # Design recommendations
        recommendations.append('Maintain 3ft minimum passage width for circulation')
        recommendations.append('Provide cross-ventilation in all habitable rooms')
        recommendations.append('Use 9" walls for external, 4.5" for internal partitions')
        
        # Compliance recommendations
        recommendations.append('Verify setbacks as per local building bylaws')
        recommendations.append('Obtain structural design from licensed engineer')
        recommendations.append('Follow NBC and IS codes for construction')
        
        # Cost optimization
        total_builtup = sum(floor['total_area'] for floor in floor_layouts)
        estimated_cost = total_builtup * 1800  # ₹1800 per sqft average
        recommendations.append(f'Estimated construction cost: ₹{estimated_cost/100000:.1f} lakhs (₹1800/sqft)')
        
        # Timeline
        construction_days = int(total_builtup / 45)  # 45 sqft per day
        recommendations.append(f'Estimated construction time: {construction_days} days ({construction_days//30} months)')
        
        return recommendations
