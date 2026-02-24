"""
Test timeline and worker calculations
Verify realistic values with NO DECIMALS for workers
"""

from services.construction_estimator import ConstructionEstimator

print("=" * 70)
print("TIMELINE AND WORKER CALCULATION TEST")
print("=" * 70)

# Test Case 1: 1500 sqft × 2 floors (G+1)
print("\nTest Case 1: 1500 sqft × 2 floors (G+1)")
print("-" * 70)

area_per_floor = 1500
floors = 2
total_sqft = area_per_floor * floors

estimate = ConstructionEstimator.calculate_estimate(
    area_sqft=area_per_floor,
    floors=floors,
    wage_per_day=500
)

print(f"Input: {area_per_floor} sqft × {floors} floors = {total_sqft} sqft")
print(f"\nTimeline:")
print(f"  Days: {estimate['timeline_days']} (expected: 65-75 days)")
print(f"  Weeks: {estimate['timeline_weeks']}")
print(f"  Months: {estimate['timeline_months']} (expected: 2-2.5 months)")

print(f"\nWorkers (ALL INTEGERS):")
print(f"  Total: {estimate['total_workers']} (expected: 6-8)")
print(f"  Masons: {estimate['masons']} (40%)")
print(f"  Helpers: {estimate['helpers']} (40%)")
print(f"  Carpenters: {estimate['carpenters']} (20%)")
print(f"  Supervisors: {estimate['supervisors']}")

# Validation checks
checks = []

# Check 1: Timeline realistic (65-75 days for 3000 sqft)
timeline_ok = 65 <= estimate['timeline_days'] <= 75
checks.append(("Timeline realistic", timeline_ok, f"{estimate['timeline_days']} days"))

# Check 2: Timeline is integer
timeline_int = isinstance(estimate['timeline_days'], int)
checks.append(("Timeline is integer", timeline_int, f"Type: {type(estimate['timeline_days']).__name__}"))

# Check 3: Workers realistic (6-8 for 3000 sqft)
workers_ok = 6 <= estimate['total_workers'] <= 8
checks.append(("Workers realistic", workers_ok, f"{estimate['total_workers']} workers"))

# Check 4: All worker counts are integers
all_int = all(isinstance(estimate[key], int) for key in ['total_workers', 'masons', 'helpers', 'carpenters', 'supervisors'])
checks.append(("All workers are integers", all_int, "No decimals"))

# Check 5: Worker distribution adds up reasonably
worker_sum = estimate['masons'] + estimate['helpers'] + estimate['carpenters']
distribution_ok = worker_sum >= estimate['total_workers']  # Can be slightly more due to ceiling
checks.append(("Worker distribution valid", distribution_ok, f"Sum: {worker_sum}"))

print(f"\nValidation Checks:")
for check_name, passed, details in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {check_name} - {details}")

# Test Case 2: 2000 sqft × 3 floors (G+2)
print(f"\n" + "=" * 70)
print("Test Case 2: 2000 sqft × 3 floors (G+2)")
print("-" * 70)

estimate2 = ConstructionEstimator.calculate_estimate(
    area_sqft=2000,
    floors=3,
    wage_per_day=500
)

total2 = 2000 * 3
print(f"Input: 2000 sqft × 3 floors = {total2} sqft")
print(f"\nTimeline: {estimate2['timeline_days']} days ({estimate2['timeline_months']} months)")
print(f"Workers: {estimate2['total_workers']} total")
print(f"  Masons: {estimate2['masons']}")
print(f"  Helpers: {estimate2['helpers']}")
print(f"  Carpenters: {estimate2['carpenters']}")

# Test Case 3: 1000 sqft × 2 floors (Small G+1)
print(f"\n" + "=" * 70)
print("Test Case 3: 1000 sqft × 2 floors (Small G+1)")
print("-" * 70)

estimate3 = ConstructionEstimator.calculate_estimate(
    area_sqft=1000,
    floors=2,
    wage_per_day=500
)

total3 = 1000 * 2
print(f"Input: 1000 sqft × 2 floors = {total3} sqft")
print(f"\nTimeline: {estimate3['timeline_days']} days ({estimate3['timeline_months']} months)")
print(f"Workers: {estimate3['total_workers']} total")
print(f"  Masons: {estimate3['masons']}")
print(f"  Helpers: {estimate3['helpers']}")
print(f"  Carpenters: {estimate3['carpenters']}")

# Summary
print(f"\n" + "=" * 70)
all_passed = all(passed for _, passed, _ in checks)
if all_passed:
    print("✓ ALL TESTS PASSED")
    print("Timeline and workers are realistic with NO DECIMALS")
else:
    print("✗ SOME TESTS FAILED")
print("=" * 70)
