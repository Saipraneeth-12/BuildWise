class CostPlanner:
    @staticmethod
    def calculate(materials, prices):
        material_cost = sum(materials.get(m, 0) * prices.get(m, 0) for m in materials)
        labour_cost = material_cost * 0.3
        equipment_cost = material_cost * 0.15
        contingency = (material_cost + labour_cost + equipment_cost) * 0.1
        
        return {
            'material_cost': round(material_cost, 2),
            'labour_cost': round(labour_cost, 2),
            'equipment_cost': round(equipment_cost, 2),
            'contingency': round(contingency, 2),
            'total': round(material_cost + labour_cost + equipment_cost + contingency, 2)
        }
