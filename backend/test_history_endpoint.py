"""
Test the history endpoint response
"""

from services.material_price_scraper import MaterialPriceScraper
from datetime import datetime, timedelta

scraper = MaterialPriceScraper()

# Simulate what the endpoint does
material = 'Cement'
material_type = 'OPC 53'
location = 'Mumbai'
days = 90

# Generate historical data
print(f"Generating {days} days of historical data...")
historical_data = scraper.generate_historical_data(days=days)

# Filter for requested material/type/location
filtered_data = [
    record for record in historical_data
    if record['material'] == material 
    and record['type'] == material_type 
    and record['location'] == location
]

print(f"Filtered records: {len(filtered_data)}")

# Sort by date
filtered_data.sort(key=lambda x: x['scraped_at'])

# Convert to chart-friendly format (what API returns)
chart_data = []
for record in filtered_data:
    chart_data.append({
        'date': record['scraped_at'].strftime('%Y-%m-%d'),
        'price': record['price'],
        'trend': record.get('trend', 'same')
    })

print(f"\nChart data records: {len(chart_data)}")
print(f"\nFirst 5 records:")
for item in chart_data[:5]:
    print(f"  {item['date']}: ₹{item['price']:.2f}")

print(f"\nLast 5 records:")
for item in chart_data[-5:]:
    print(f"  {item['date']}: ₹{item['price']:.2f}")

# Check date distribution
dates = [item['date'] for item in chart_data]
unique_dates = set(dates)

print(f"\nDate Analysis:")
print(f"  Total records: {len(dates)}")
print(f"  Unique dates: {len(unique_dates)}")
print(f"  First date: {dates[0]}")
print(f"  Last date: {dates[-1]}")

# Calculate actual date range
from datetime import datetime as dt
first_dt = dt.strptime(dates[0], '%Y-%m-%d')
last_dt = dt.strptime(dates[-1], '%Y-%m-%d')
date_range = (last_dt - first_dt).days

print(f"  Date range: {date_range} days")

if len(unique_dates) == len(dates) and date_range >= 89:
    print("\n✓ Data is correct - all dates unique and spans 90 days")
else:
    print("\n✗ Data has issues")
