"""
Test historical data generation
Verifies realistic price trends over 90 days
"""

from services.material_price_scraper import MaterialPriceScraper
from datetime import datetime, timedelta

scraper = MaterialPriceScraper()

print("=" * 70)
print("HISTORICAL DATA GENERATION TEST")
print("=" * 70)

# Generate 90 days of historical data for one material/location
print("\nGenerating 90 days of historical data...")
historical_data = scraper.generate_historical_data(days=90)

# Filter for Cement OPC 53 in Mumbai
cement_mumbai = [
    record for record in historical_data
    if record['material'] == 'Cement'
    and record['type'] == 'OPC 53'
    and record['location'] == 'Mumbai'
]

print(f"Total records generated: {len(historical_data)}")
print(f"Cement OPC 53 Mumbai records: {len(cement_mumbai)}")

# Sort by date
cement_mumbai.sort(key=lambda x: x['scraped_at'])

print("\n" + "=" * 70)
print("PRICE TREND ANALYSIS - Cement OPC 53 in Mumbai")
print("=" * 70)

# Show first 10 days
print("\nFirst 10 days (90 days ago):")
for i, record in enumerate(cement_mumbai[:10]):
    date_str = record['scraped_at'].strftime('%Y-%m-%d')
    print(f"  {date_str}: ₹{record['price']:.2f}/bag")

# Show last 10 days
print("\nLast 10 days (recent):")
for i, record in enumerate(cement_mumbai[-10:]):
    date_str = record['scraped_at'].strftime('%Y-%m-%d')
    print(f"  {date_str}: ₹{record['price']:.2f}/bag")

# Calculate statistics
prices = [r['price'] for r in cement_mumbai]
min_price = min(prices)
max_price = max(prices)
avg_price = sum(prices) / len(prices)
first_price = prices[0]
last_price = prices[-1]
price_change = ((last_price - first_price) / first_price) * 100

print("\n" + "=" * 70)
print("STATISTICS")
print("=" * 70)
print(f"Minimum Price: ₹{min_price:.2f}/bag")
print(f"Maximum Price: ₹{max_price:.2f}/bag")
print(f"Average Price: ₹{avg_price:.2f}/bag")
print(f"First Day Price (90 days ago): ₹{first_price:.2f}/bag")
print(f"Last Day Price (today): ₹{last_price:.2f}/bag")
print(f"Total Change: {price_change:+.2f}%")
print(f"Price Range: ₹{max_price - min_price:.2f}")

# Verify realistic behavior
print("\n" + "=" * 70)
print("REALISM CHECKS")
print("=" * 70)

checks = []

# Check 1: Prices should be within reasonable range (±30% of base)
base_price = 400
reasonable_min = base_price * 0.7
reasonable_max = base_price * 1.3
within_range = all(reasonable_min <= p <= reasonable_max for p in prices)
checks.append(("Prices within ±30% of base", within_range))

# Check 2: Prices should show gradual increase over time (not sudden jumps)
max_daily_change = max(abs(prices[i] - prices[i-1]) for i in range(1, len(prices)))
gradual_change = max_daily_change < base_price * 0.1  # Less than 10% daily change
checks.append(("Gradual price changes (<10% daily)", gradual_change))

# Check 3: Should have 90 data points
correct_count = len(cement_mumbai) == 90
checks.append(("Correct number of days (90)", correct_count))

# Check 4: Dates should be sequential
dates = [r['scraped_at'] for r in cement_mumbai]
sequential = all((dates[i] - dates[i-1]).days == 1 for i in range(1, len(dates)))
checks.append(("Sequential daily dates", sequential))

# Check 5: Prices should generally increase over time (trend factor)
overall_increase = last_price > first_price
checks.append(("Overall upward trend", overall_increase))

for check_name, passed in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {check_name}")

all_passed = all(passed for _, passed in checks)

print("\n" + "=" * 70)
if all_passed:
    print("✓ ALL CHECKS PASSED - Historical data is realistic!")
else:
    print("✗ SOME CHECKS FAILED - Review data generation logic")
print("=" * 70)

# Test different materials
print("\n" + "=" * 70)
print("MULTI-MATERIAL TEST")
print("=" * 70)

materials_to_test = [
    ('Steel', 'TMT Fe 500', 'Mumbai'),
    ('Sand', 'River Sand', 'Delhi'),
    ('Aggregates', '20mm', 'Bangalore')
]

for material, mat_type, location in materials_to_test:
    filtered = [
        r for r in historical_data
        if r['material'] == material
        and r['type'] == mat_type
        and r['location'] == location
    ]
    
    if filtered:
        filtered.sort(key=lambda x: x['scraped_at'])
        first = filtered[0]['price']
        last = filtered[-1]['price']
        change = ((last - first) / first) * 100
        
        print(f"\n{material} ({mat_type}) in {location}:")
        print(f"  90 days ago: ₹{first:.2f}")
        print(f"  Today: ₹{last:.2f}")
        print(f"  Change: {change:+.2f}%")
        print(f"  Data points: {len(filtered)}")

print("\n" + "=" * 70)
print("HISTORICAL DATA GENERATION TEST COMPLETE")
print("=" * 70)
