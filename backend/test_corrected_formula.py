"""
Test script to verify CORRECTED steel calculation formula
"""

from services.construction_estimator import ConstructionEstimator

# Test with 1500 sqft, G+1 (2 floors)
# Should give 7.5 tons of steel (NOT 70+ tons)
estimate = ConstructionEstimator.calculate_estimate(
    area_sqft=1500,
    floors=2,  # G+1
    wage_per_day=500,
    steel_type='Fe500',
    cement_type='OPC 53'
)

print("=" * 60)
print("CORRECTED STEEL CALCULATION TEST")
print("=" * 60)
print(f"Input: 1500 sqft per floor, G+1 (2 floors)")
print(f"Total Area: {estimate['total_sqft']} sqft")
print()
print(f"Steel Required: {estimate['steel_tons']} tons ({estimate['steel_kg']} kg)")
print(f"Formula Used: 2.5 kg/sqft (CORRECTED from 4 kg/sqft)")
print()
print(f"Expected: 7-8 tons")
print(f"Result: {'✓ CORRECT' if 7 <= estimate['steel_tons'] <= 8 else '✗ INCORRECT'}")
print()
print(f"Cement: {estimate['cement_bags']} bags")
print(f"Workers: {estimate['workers']}")
print(f"Timeline: {estimate['timeline_days']} days ({estimate['timeline_months']} months)")
print()
print(f"Steel Cost: ₹{estimate['steel_cost']:,.2f} @ ₹{estimate['steel_price_per_ton']}/ton")
print(f"Cement Cost: ₹{estimate['cement_cost']:,.2f} @ ₹{estimate['cement_price_per_bag']}/bag")
print(f"Labour Cost: ₹{estimate['labour_cost']:,.2f}")
print(f"Total Cost: ₹{estimate['total_cost']:,.2f}")
print("=" * 60)
