"""
Construction Estimation Engine
Calculates workers, timeline, materials, and costs based on REALISTIC engineering formulas
Uses industry-standard civil engineering constants
"""

import math

class ConstructionEstimator:
    """
    Engineering-based construction estimation engine
    Uses REALISTIC industry-standard formulas for accurate calculations
    """
    
    # FIXED MATERIAL CONSTANTS (REALISTIC ENGINEERING VALUES)
    STEEL_KG_PER_SQFT = 3.0  # Realistic steel requirement
    CEMENT_BAGS_PER_SQFT = 0.33  # Realistic cement requirement
    SAND_CFT_PER_SQFT = 1.8  # Realistic sand requirement
    AGGREGATE_CFT_PER_SQFT = 2.7  # Realistic aggregate requirement
    BRICKS_PER_SQFT = 55  # Realistic brick requirement
    
    # WORKER AND TIMELINE CONSTANTS (REALISTIC RESIDENTIAL CONSTRUCTION)
    CONSTRUCTION_SPEED_SQFT_PER_DAY = 45  # Realistic residential construction speed
    WORKER_PRODUCTIVITY_SQFT_PER_DAY = 90  # One worker handles 90 sqft/day
    
    # Material pricing (fallback defaults if web scraping fails)
    STEEL_PRICES = {
        'Fe415': 58000,  # per ton
        'Fe500': 62000,
        'Fe550': 65000,
        'TMT Premium': 68000
    }
    
    CEMENT_PRICES = {
        'OPC 43': 350,  # per bag
        'OPC 53': 400,
        'PPC': 380,
        'PSC': 360
    }
    
    @staticmethod
    def calculate_estimate(area_sqft, floors, wage_per_day, steel_type='Fe500', cement_type='OPC 53', 
                          steel_price_per_ton=None, cement_price_per_bag=None):
        """
        Main calculation engine using REALISTIC engineering formulas
        
        Args:
            area_sqft: Built-up area in square feet PER FLOOR (frontend provides this)
            floors: Number of floors
            wage_per_day: Daily wage per worker
            steel_type: Type of steel (Fe415, Fe500, Fe550, TMT Premium)
            cement_type: Type of cement (OPC 43, OPC 53, PPC, PSC)
            steel_price_per_ton: Real-time steel price (optional)
            cement_price_per_bag: Real-time cement price (optional)
            
        Returns:
            dict: Complete estimation with timeline, workers, materials, costs
        """
        
        # CRITICAL: Total area calculation (area is PER FLOOR from frontend)
        total_sqft = area_sqft * floors
        
        # Timeline calculation using REALISTIC residential construction speed (45 sqft/day)
        timeline_days = math.ceil(total_sqft / ConstructionEstimator.CONSTRUCTION_SPEED_SQFT_PER_DAY)
        timeline_weeks = round(timeline_days / 7, 2)
        timeline_months = round(timeline_days / 30, 2)
        
        # Worker calculation using REALISTIC productivity (90 sqft/day per worker)
        # Formula: workers = total_sqft / (worker_productivity × timeline_days)
        # But this gives very small numbers, so use simpler realistic formula:
        # 1 worker per 400-500 sqft of total area
        workers_calculated = total_sqft / 450
        total_workers = max(4, math.ceil(workers_calculated))  # Min 4 workers, always integer
        
        # Worker role distribution (ALWAYS INTEGERS)
        # Masons: 40%, Helpers: 40%, Carpenters: 20%
        masons = math.ceil(total_workers * 0.4)
        helpers = math.ceil(total_workers * 0.4)
        carpenters = math.ceil(total_workers * 0.2)
        supervisors = max(1, math.ceil(total_workers * 0.05))  # At least 1 supervisor
        
        # REALISTIC Steel calculation: 3.0 kg per sqft
        steel_kg = total_sqft * ConstructionEstimator.STEEL_KG_PER_SQFT
        steel_tons = steel_kg / 1000
        
        # REALISTIC Cement calculation: 0.33 bags per sqft
        cement_bags = total_sqft * ConstructionEstimator.CEMENT_BAGS_PER_SQFT
        
        # REALISTIC Additional materials
        sand_cft = total_sqft * ConstructionEstimator.SAND_CFT_PER_SQFT
        aggregate_cft = total_sqft * ConstructionEstimator.AGGREGATE_CFT_PER_SQFT
        bricks = total_sqft * ConstructionEstimator.BRICKS_PER_SQFT
        
        # Get prices (use provided or fallback to defaults)
        if steel_price_per_ton is None:
            steel_price_per_ton = ConstructionEstimator.STEEL_PRICES.get(steel_type, 62000)
        
        if cement_price_per_bag is None:
            cement_price_per_bag = ConstructionEstimator.CEMENT_PRICES.get(cement_type, 400)
        
        # Cost calculations using real prices
        steel_cost = steel_tons * steel_price_per_ton
        cement_cost = cement_bags * cement_price_per_bag
        
        # Other material costs (estimated)
        bricks_cost = bricks * 8  # ₹8 per brick
        sand_cost = sand_cft * 50  # ₹50 per cft
        aggregate_cost = aggregate_cft * 60  # ₹60 per cft
        
        # Total material cost
        material_cost = steel_cost + cement_cost + bricks_cost + sand_cost + aggregate_cost
        
        # Labour cost calculation (using integer workers and integer timeline_days)
        labour_cost = total_workers * wage_per_day * timeline_days
        
        # Total cost calculation
        total_cost = labour_cost + material_cost
        
        return {
            # Timeline (integers for days)
            'timeline_days': timeline_days,
            'timeline_weeks': timeline_weeks,
            'timeline_months': timeline_months,
            
            # Workers (ALL INTEGERS - no decimals)
            'workers': total_workers,
            'masons': masons,
            'helpers': helpers,
            'carpenters': carpenters,
            'supervisors': supervisors,
            'total_workers': total_workers,
            
            # Steel (REALISTIC)
            'steel_type': steel_type,
            'steel_kg': round(steel_kg, 2),
            'steel_tons': round(steel_tons, 2),
            'steel_price_per_ton': steel_price_per_ton,
            'steel_cost': round(steel_cost, 2),
            
            # Cement (REALISTIC)
            'cement_type': cement_type,
            'cement_bags': round(cement_bags, 2),
            'cement_price_per_bag': cement_price_per_bag,
            'cement_cost': round(cement_cost, 2),
            
            # Other materials (REALISTIC)
            'bricks': round(bricks, 2),
            'bricks_cost': round(bricks_cost, 2),
            'sand_cft': round(sand_cft, 2),
            'sand_cost': round(sand_cost, 2),
            'aggregate_cft': round(aggregate_cft, 2),
            'aggregate_cost': round(aggregate_cost, 2),
            
            # Costs
            'labour_cost': round(labour_cost, 2),
            'material_cost': round(material_cost, 2),
            'total_cost': round(total_cost, 2),
            
            # Input parameters (for reference)
            'area_sqft': area_sqft,
            'floors': floors,
            'total_sqft': round(total_sqft, 2),
            'wage_per_day': wage_per_day
        }
    
    @staticmethod
    def validate_inputs(area, floors, wage):
        """Validate input parameters"""
        errors = []
        
        if area <= 0:
            errors.append("Area must be greater than 0")
        if floors <= 0:
            errors.append("Floors must be greater than 0")
        if wage <= 0:
            errors.append("Wage must be greater than 0")
            
        return errors
    
    @staticmethod
    def get_steel_types():
        """Get available steel types"""
        return list(ConstructionEstimator.STEEL_PRICES.keys())
    
    @staticmethod
    def get_cement_types():
        """Get available cement types"""
        return list(ConstructionEstimator.CEMENT_PRICES.keys())
