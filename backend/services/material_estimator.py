class MaterialEstimator:
    @staticmethod
    def estimate(built_up_area, floors, structure_type):
        # Basic estimation formulas (simplified)
        multiplier = 1.0
        if structure_type == 'RCC':
            multiplier = 1.2
        elif structure_type == 'Steel':
            multiplier = 1.5
        
        total_area = built_up_area * floors * multiplier
        
        return {
            'cement': round(total_area * 0.4, 2),  # bags
            'steel': round(total_area * 4, 2),  # kg
            'bricks': round(total_area * 50, 2),  # units
            'sand': round(total_area * 0.8, 2),  # cubic feet
            'aggregate': round(total_area * 1.2, 2)  # cubic feet
        }
