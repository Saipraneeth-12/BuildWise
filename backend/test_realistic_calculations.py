"""
Test REALISTIC calculation formulas
Verify outputs match civil engineering standards
"""

from services.construction_estimator import ConstructionEstimator

print("=" * 70)
print("REALISTIC CALCULATION VERIFICATION TEST")
print("=" * 70)

# Test Case: 1500 sqft per floor, 3 floors (G+2)
area_per_floor = 1500
floors = 3
wage = 500

print(f"\nInput:")
print(f"  Area per floor: {area_per_floor} sqft")
print(f"  Number of floors: {floors}")
print(f"  Daily wage: ₹{wage}")

# Calculate estimate
estimate = ConstructionEstimator.calculate_estimate(
    area_sqft=area_per_floor,
    floors=floors,
    wage_per_day=wage,
    steel_type='Fe500',
    cement_type='OPC 53'
)

print(f"\n" + "=" * 70)
print("CALCULATED OUTPUTS")
print("=" * 70)

print(f"\nTotal Area:")
print(f"  {estimate['total_sqft']} sqft")

print(f"\nSteel:")
print(f"  {estimate['steel_tons']} tons ({estimate['steel_kg']} kg)")
print(f"  Formula: {estimate['total_sqft']} sqft × 3.0 kg/sqft = {estimate['steel_kg']} kg")

print(f"\nCement:")
print(f"  {estimate['cement_bags']} bags")
print(f"  Formula: {estimate['total_sqft']} sqft × 0.33 bags/sqft = {estimate['cement_bags']} bags")

print(f"\nSand:")
print(f"  {estimate['sand_cft']} cft")
print(f"  Formula: {estimate['total_sqft']} sqft × 1.8 cft/sqft = {estimate['sand_cft']} cft")

print(f"\nAggregate:")
print(f"  {estimate['aggregate_cft']} cft")
print(f"  Formula: {estimate['total_sqft']} sqft × 2.7 cft/sqft = {estimate['aggregate_cft']} cft")

print(f"\nBricks:")
print(f"  {estimate['bricks']} units")
print(f"  Formula: {estimate['total_sqft']} sqft × 55 bricks/sqft = {estimate['bricks']} bricks")

print(f"\nWorkers:")
print(f"  {estimate['workers']} workers")
print(f"  Formula: CEILING({estimate['total_sqft']} / (120 × project_duration))")

print(f"\nTimeline:")
print(f"  {estimate['timeline_days']} days ({estimate['timeline_months']} months)")
print(f"  Formula: {estimate['total_sqft']} sqft ÷ 75 sqft/day = {estimate['timeline_days']} days")

print(f"\nCosts:")
print(f"  Steel: ₹{estimate['steel_cost']:,.2f}")
print(f"  Cement: ₹{estimate['cement_cost']:,.2f}")
print(f"  Labour: ₹{estimate['labour_cost']:,.2f}")
print(f"  Material: ₹{estimate['material_cost']:,.2f}")
print(f"  Total: ₹{estimate['total_cost']:,.2f}")

print(f"\n" + "=" * 70)
print("VALIDATION CHECKS")
print("=" * 70)

# Expected ranges for 1500 sqft × 3 floors = 4500 sqft
checks = []

# Check 1: Total area
expected_total = area_per_floor * floors
actual_total = estimate['total_sqft']
checks.append(("Total area calculation", expected_total == actual_total, f"{actual_total} sqft"))

# Check 2: Steel (should be ~13.5 tons for 4500 sqft)
expected_steel = 4500 * 3.0 / 1000  # 13.5 tons
actual_steel = estimate['steel_tons']
steel_ok = 12 <= actual_steel <= 15
checks.append(("Steel requirement", steel_ok, f"{actual_steel} tons (expected ~13.5)"))

# Check 3: Cement (should be ~1485 bags for 4500 sqft)
expected_cement = 4500 * 0.33  # 1485 bags
actual_cement = estimate['cement_bags']
cement_ok = 1400 <= actual_cement <= 1600
checks.append(("Cement requirement", cement_ok, f"{actual_cement} bags (expected ~1485)"))

# Check 4: Timeline (should be ~60 days for 4500 sqft)
expected_timeline = 4500 / 75  # 60 days
actual_timeline = estimate['timeline_days']
timeline_ok = 50 <= actual_timeline <= 70
checks.append(("Timeline", timeline_ok, f"{actual_timeline} days (expected ~60)"))

# Check 5: Workers (should be 6-10 for 4500 sqft)
actual_workers = estimate['workers']
workers_ok = 6 <= actual_workers <= 10
checks.append(("Workers", workers_ok, f"{actual_workers} workers (expected 6-10)"))

# Check 6: No unrealistic values
no_huge_steel = estimate['steel_tons'] < 50
no_huge_cement = estimate['cement_bags'] < 5000
no_tiny_timeline = estimate['timeline_days'] > 10
checks.append(("No unrealistic values", no_huge_steel and no_huge_cement and no_tiny_timeline, "All values realistic"))

for check_name, passed, details in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {check_name} - {details}")

all_passed = all(passed for _, passed, _ in checks)

print(f"\n" + "=" * 70)
if all_passed:
    print("✓ ALL VALIDATION CHECKS PASSED")
    print("Calculations match realistic civil engineering standards!")
else:
    print("✗ SOME CHECKS FAILED")
    print("Review calculation formulas")
print("=" * 70)

# Additional test cases
print(f"\n" + "=" * 70)
print("ADDITIONAL TEST CASES")
print("=" * 70)

test_cases = [
    (1000, 2, "Small G+1 building"),
    (2000, 4, "Medium G+3 building"),
    (3000, 5, "Large G+4 building"),
]

for area, floors_test, description in test_cases:
    est = ConstructionEstimator.calculate_estimate(area, floors_test, 500)
    total = area * floors_test
    print(f"\n{description} ({area} sqft × {floors_test} floors = {total} sqft):")
    print(f"  Steel: {est['steel_tons']} tons")
    print(f"  Cement: {est['cement_bags']} bags")
    print(f"  Timeline: {est['timeline_days']} days")
    print(f"  Workers: {est['workers']}")
    print(f"  Total Cost: ₹{est['total_cost']:,.2f}")

print(f"\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
