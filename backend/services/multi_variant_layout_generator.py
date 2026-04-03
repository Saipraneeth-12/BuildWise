"""
Multi-Variant Layout Generator
Generates 3-4 different architectural layout options for the same requirements
User can select the best option that suits their needs
"""

from typing import Dict, List
from services.professional_architect_ai import ProfessionalArchitectAI

class MultiVariantLayoutGenerator:
    """
    Generates multiple layout variants for the same requirements
    Each variant has different room arrangements and spatial organization
    """
    
    def __init__(self):
        self.architect_ai = ProfessionalArchitectAI()
    
    def generate_variants(self, user_input: str, num_variants: int = 3) -> List[Dict]:
        """
        Generate multiple layout variants
        
        Args:
            user_input: User requirements (any format)
            num_variants: Number of variants to generate (default: 3)
            
        Returns:
            List of layout variants with different arrangements
        """
        
        # Extract base parameters
        base_params = self.architect_ai.extract_parameters(user_input)
        
        # Generate variants with different layout strategies
        variants = []
        
        # Variant 1: Linear Layout (All bedrooms in a row)
        variant1 = self._generate_linear_layout(base_params)
        variant1['variant_name'] = 'Linear Layout'
        variant1['variant_description'] = 'All bedrooms arranged in a row, living room and kitchen on opposite side'
        variant1['best_for'] = 'Narrow plots, maximum privacy between bedrooms'
        variants.append(variant1)
        
        # Variant 2: L-Shaped Layout (Bedrooms on two sides)
        variant2 = self._generate_l_shaped_layout(base_params)
        variant2['variant_name'] = 'L-Shaped Layout'
        variant2['variant_description'] = 'Bedrooms on two adjacent sides, living room in corner'
        variant2['best_for'] = 'Square plots, better ventilation, corner living room'
        variants.append(variant2)
        
        # Variant 3: Central Living Layout (Living room in center)
        variant3 = self._generate_central_living_layout(base_params)
        variant3['variant_name'] = 'Central Living Layout'
        variant3['variant_description'] = 'Living room in center, bedrooms and kitchen around it'
        variant3['best_for'] = 'Large plots, family gathering focus, easy access to all rooms'
        variants.append(variant3)
        
        # Variant 4: Split Layout (Bedrooms on opposite sides) - if requested
        if num_variants >= 4:
            variant4 = self._generate_split_layout(base_params)
            variant4['variant_name'] = 'Split Layout'
            variant4['variant_description'] = 'Bedrooms on opposite sides, living and kitchen in middle'
            variant4['best_for'] = 'Privacy between master and other bedrooms, guest separation'
            variants.append(variant4)
        
        return variants[:num_variants]
    
    def _generate_linear_layout(self, params: Dict) -> Dict:
        """
        Variant 1: Linear Layout
        All bedrooms in a row, living room and kitchen on opposite side
        
        Layout:
        ┌─────────────────────────────┐
        │  Living Room    │  Kitchen  │
        ├─────────────────────────────┤
        │ Bed1 │ Bed2 │ Bed3 │ Passage│
        │ Bath │ Bath │ Bath │        │
        └─────────────────────────────┘
        """
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        setback = params['setback']
        bedrooms = params['bedrooms']
        
        usable_width = plot_width - (2 * setback)
        usable_length = plot_length - (2 * setback)
        
        rooms = []
        
        # Front: Living room (60% width) + Kitchen (40% width)
        living_width = usable_width * 0.6
        living_length = usable_length * 0.4
        
        rooms.append({
            'name': 'Living Room',
            'dimensions': f'{living_width:.1f}ft × {living_length:.1f}ft',
            'area': round(living_width * living_length, 1),
            'location': 'front left (60% width)',
            'notes': 'Main entrance, large windows for natural light'
        })
        
        kitchen_width = usable_width * 0.4
        kitchen_length = usable_length * 0.4
        
        rooms.append({
            'name': 'Kitchen',
            'dimensions': f'{kitchen_width:.1f}ft × {kitchen_length:.1f}ft',
            'area': round(kitchen_width * kitchen_length, 1),
            'location': 'front right (40% width)',
            'notes': 'Adjacent to living, service entrance possible'
        })
        
        # Rear: Bedrooms in a row
        bedroom_width = usable_width / bedrooms
        bedroom_length = usable_length * 0.5
        
        for i in range(bedrooms):
            bed_name = 'Master Bedroom' if i == 0 else f'Bedroom {i+1}'
            rooms.append({
                'name': bed_name,
                'dimensions': f'{bedroom_width:.1f}ft × {bedroom_length:.1f}ft',
                'area': round(bedroom_width * bedroom_length, 1),
                'location': f'rear {"left" if i == 0 else "center" if i == 1 else "right"}',
                'notes': 'Attached bathroom, good privacy'
            })
            
            # Bathroom
            bath_width = bedroom_width * 0.4
            bath_length = bedroom_length * 0.3
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
                'area': round(bath_width * bath_length, 1),
                'location': f'attached to {bed_name}',
                'notes': 'Vertically stacked for plumbing'
            })
        
        # Passage
        passage_width = usable_width * 0.1
        passage_length = usable_length * 0.5
        rooms.append({
            'name': 'Passage/Corridor',
            'dimensions': f'{passage_width:.1f}ft × {passage_length:.1f}ft',
            'area': round(passage_width * passage_length, 1),
            'location': 'connecting all rooms',
            'notes': '3ft minimum width for circulation'
        })
        
        total_area = sum(room['area'] for room in rooms)
        
        return {
            'layout_type': 'linear',
            'rooms': rooms,
            'total_area': round(total_area, 1),
            'efficiency': round((total_area / (usable_width * usable_length)) * 100, 1),
            'pros': [
                'Maximum privacy between bedrooms',
                'Simple construction',
                'Clear zoning (public vs private)',
                'Easy furniture placement'
            ],
            'cons': [
                'Requires wider plot',
                'Less flexible for future changes',
                'Longer corridor needed'
            ]
        }
    
    def _generate_l_shaped_layout(self, params: Dict) -> Dict:
        """
        Variant 2: L-Shaped Layout
        Bedrooms on two adjacent sides, living room in corner
        
        Layout:
        ┌─────────────────┐
        │ Bed1  │ Bed2    │
        │ Bath  │ Bath    │
        ├───────┼─────────┤
        │ Living│ Kitchen │
        │ Room  │         │
        ├───────┴─────────┤
        │ Bed3  │ Passage │
        │ Bath  │         │
        └─────────────────┘
        """
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        setback = params['setback']
        bedrooms = params['bedrooms']
        
        usable_width = plot_width - (2 * setback)
        usable_length = plot_length - (2 * setback)
        
        rooms = []
        
        # Corner: Living room
        living_width = usable_width * 0.5
        living_length = usable_length * 0.4
        
        rooms.append({
            'name': 'Living Room',
            'dimensions': f'{living_width:.1f}ft × {living_length:.1f}ft',
            'area': round(living_width * living_length, 1),
            'location': 'corner (center-left)',
            'notes': 'Corner position, windows on two sides, excellent ventilation'
        })
        
        # Adjacent to living: Kitchen
        kitchen_width = usable_width * 0.5
        kitchen_length = usable_length * 0.4
        
        rooms.append({
            'name': 'Kitchen',
            'dimensions': f'{kitchen_width:.1f}ft × {kitchen_length:.1f}ft',
            'area': round(kitchen_width * kitchen_length, 1),
            'location': 'adjacent to living (right)',
            'notes': 'Open to living room, modern layout'
        })
        
        # Top side: 2 bedrooms
        for i in range(min(2, bedrooms)):
            bed_width = usable_width * 0.5
            bed_length = usable_length * 0.3
            
            bed_name = 'Master Bedroom' if i == 0 else f'Bedroom {i+1}'
            rooms.append({
                'name': bed_name,
                'dimensions': f'{bed_width:.1f}ft × {bed_length:.1f}ft',
                'area': round(bed_width * bed_length, 1),
                'location': f'top {"left" if i == 0 else "right"}',
                'notes': 'Good natural light, cross-ventilation'
            })
            
            # Bathroom
            bath_width = bed_width * 0.35
            bath_length = bed_length * 0.4
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
                'area': round(bath_width * bath_length, 1),
                'location': f'attached to {bed_name}',
                'notes': 'Attached bathroom'
            })
        
        # Bottom side: Remaining bedroom(s)
        if bedrooms > 2:
            bed_width = usable_width * 0.5
            bed_length = usable_length * 0.3
            
            rooms.append({
                'name': f'Bedroom 3',
                'dimensions': f'{bed_width:.1f}ft × {bed_length:.1f}ft',
                'area': round(bed_width * bed_length, 1),
                'location': 'bottom left',
                'notes': 'Separate from other bedrooms, guest room option'
            })
            
            # Bathroom
            bath_width = bed_width * 0.35
            bath_length = bed_length * 0.4
            rooms.append({
                'name': 'Bathroom 3',
                'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
                'area': round(bath_width * bath_length, 1),
                'location': 'attached to Bedroom 3',
                'notes': 'Attached bathroom'
            })
        
        total_area = sum(room['area'] for room in rooms)
        
        return {
            'layout_type': 'l_shaped',
            'rooms': rooms,
            'total_area': round(total_area, 1),
            'efficiency': round((total_area / (usable_width * usable_length)) * 100, 1),
            'pros': [
                'Excellent cross-ventilation',
                'Corner living room with windows on two sides',
                'Flexible room arrangement',
                'Good for square plots'
            ],
            'cons': [
                'Slightly complex construction',
                'More corners to finish',
                'May need more columns'
            ]
        }
    
    def _generate_central_living_layout(self, params: Dict) -> Dict:
        """
        Variant 3: Central Living Layout
        Living room in center, bedrooms and kitchen around it
        
        Layout:
        ┌─────────────────────────┐
        │ Bed1  │  Living  │ Bed2 │
        │ Bath  │   Room   │ Bath │
        ├───────┼──────────┼──────┤
        │Kitchen│  Passage │ Bed3 │
        │       │          │ Bath │
        └─────────────────────────┘
        """
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        setback = params['setback']
        bedrooms = params['bedrooms']
        
        usable_width = plot_width - (2 * setback)
        usable_length = plot_length - (2 * setback)
        
        rooms = []
        
        # Center: Living room (largest space)
        living_width = usable_width * 0.5
        living_length = usable_length * 0.5
        
        rooms.append({
            'name': 'Living Room',
            'dimensions': f'{living_width:.1f}ft × {living_length:.1f}ft',
            'area': round(living_width * living_length, 1),
            'location': 'center (heart of home)',
            'notes': 'Central hub, easy access to all rooms, family gathering space'
        })
        
        # Around living: Bedrooms
        bed_width = usable_width * 0.25
        bed_length = usable_length * 0.5
        
        for i in range(bedrooms):
            bed_name = 'Master Bedroom' if i == 0 else f'Bedroom {i+1}'
            location = 'left of living' if i == 0 else 'right of living' if i == 1 else 'bottom right'
            
            rooms.append({
                'name': bed_name,
                'dimensions': f'{bed_width:.1f}ft × {bed_length:.1f}ft',
                'area': round(bed_width * bed_length, 1),
                'location': location,
                'notes': 'Easy access from living room, good privacy'
            })
            
            # Bathroom
            bath_width = bed_width * 0.4
            bath_length = bed_length * 0.3
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
                'area': round(bath_width * bath_length, 1),
                'location': f'attached to {bed_name}',
                'notes': 'Attached bathroom'
            })
        
        # Kitchen
        kitchen_width = usable_width * 0.25
        kitchen_length = usable_length * 0.5
        
        rooms.append({
            'name': 'Kitchen',
            'dimensions': f'{kitchen_width:.1f}ft × {kitchen_length:.1f}ft',
            'area': round(kitchen_width * kitchen_length, 1),
            'location': 'bottom left (near living)',
            'notes': 'Open to living room, modern open-plan concept'
        })
        
        total_area = sum(room['area'] for room in rooms)
        
        return {
            'layout_type': 'central_living',
            'rooms': rooms,
            'total_area': round(total_area, 1),
            'efficiency': round((total_area / (usable_width * usable_length)) * 100, 1),
            'pros': [
                'Family-centric design',
                'Easy access to all rooms from living',
                'Great for entertaining guests',
                'Modern open-plan feel',
                'Excellent for large families'
            ],
            'cons': [
                'Less privacy for bedrooms',
                'Noise from living room may reach bedrooms',
                'Requires larger plot'
            ]
        }
    
    def _generate_split_layout(self, params: Dict) -> Dict:
        """
        Variant 4: Split Layout
        Bedrooms on opposite sides, living and kitchen in middle
        
        Layout:
        ┌─────────────────────────┐
        │ Bed1  │  Living  │ Bed2 │
        │ Bath  │   Room   │ Bath │
        ├───────┼──────────┼──────┤
        │Passage│ Kitchen  │ Bed3 │
        │       │          │ Bath │
        └─────────────────────────┘
        """
        
        plot_width = params['plot_width']
        plot_length = params['plot_length']
        setback = params['setback']
        bedrooms = params['bedrooms']
        
        usable_width = plot_width - (2 * setback)
        usable_length = plot_length - (2 * setback)
        
        rooms = []
        
        # Center top: Living room
        living_width = usable_width * 0.5
        living_length = usable_length * 0.5
        
        rooms.append({
            'name': 'Living Room',
            'dimensions': f'{living_width:.1f}ft × {living_length:.1f}ft',
            'area': round(living_width * living_length, 1),
            'location': 'center top',
            'notes': 'Separates master bedroom from other bedrooms'
        })
        
        # Center bottom: Kitchen
        kitchen_width = usable_width * 0.5
        kitchen_length = usable_length * 0.5
        
        rooms.append({
            'name': 'Kitchen',
            'dimensions': f'{kitchen_width:.1f}ft × {kitchen_length:.1f}ft',
            'area': round(kitchen_width * kitchen_length, 1),
            'location': 'center bottom',
            'notes': 'Central location, easy access'
        })
        
        # Left side: Master bedroom
        bed_width = usable_width * 0.25
        bed_length = usable_length * 0.5
        
        rooms.append({
            'name': 'Master Bedroom',
            'dimensions': f'{bed_width:.1f}ft × {bed_length:.1f}ft',
            'area': round(bed_width * bed_length, 1),
            'location': 'left side (top)',
            'notes': 'Maximum privacy, separate from other bedrooms'
        })
        
        bath_width = bed_width * 0.4
        bath_length = bed_length * 0.3
        rooms.append({
            'name': 'Master Bathroom',
            'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
            'area': round(bath_width * bath_length, 1),
            'location': 'attached to Master Bedroom',
            'notes': 'Attached bathroom'
        })
        
        # Right side: Other bedrooms
        for i in range(1, bedrooms):
            rooms.append({
                'name': f'Bedroom {i+1}',
                'dimensions': f'{bed_width:.1f}ft × {bed_length:.1f}ft',
                'area': round(bed_width * bed_length, 1),
                'location': f'right side ({"top" if i == 1 else "bottom"})',
                'notes': 'Separate wing from master bedroom'
            })
            
            rooms.append({
                'name': f'Bathroom {i+1}',
                'dimensions': f'{bath_width:.1f}ft × {bath_length:.1f}ft',
                'area': round(bath_width * bath_length, 1),
                'location': f'attached to Bedroom {i+1}',
                'notes': 'Attached bathroom'
            })
        
        total_area = sum(room['area'] for room in rooms)
        
        return {
            'layout_type': 'split',
            'rooms': rooms,
            'total_area': round(total_area, 1),
            'efficiency': round((total_area / (usable_width * usable_length)) * 100, 1),
            'pros': [
                'Maximum privacy for master bedroom',
                'Separate guest wing possible',
                'Good for joint families',
                'Clear separation of spaces'
            ],
            'cons': [
                'Longer distances between rooms',
                'More corridor space needed',
                'May feel disconnected'
            ]
        }
