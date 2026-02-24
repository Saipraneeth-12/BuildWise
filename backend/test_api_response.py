"""
Test API response format for history endpoint
"""

from services.material_price_scraper import MaterialPriceScraper
from datetime import datetime

scraper = MaterialPriceScraper()

# Generate 90 days of data
print("Generating 90 days of historical data...")
data = scraper.generate_historical_data(days=90)

# Filter for Cement OPC 53 in Mumbai
cement_mumbai = [
    r for r in data 
    if r['material'] == 'Cement' 
    and r['type'] == 'OPC 53' 
    and r['location'] == 'Mumbai'
]

# Sort by date
cement_mumbai.sort(key=lambda x: x['scraped_at'])

print(f"\nTotal records: {len(cement_mumbai)}")
print(f"First date: {cement_mumbai[0]['scraped_at']}")
print(f"Last date: {cement_mumbai[-1]['scraped_at']}")
print(f"Date range: {(cement_mumbai[-1]['scraped_at'] - cement_mumbai[0]['scraped_at']).days} days")

# Show how dates are formatted for API response
print("\nAPI Response Format (first 5 records):")
for record in cement_mumbai[:5]:
    date_str = record['scraped_at'].strftime('%Y-%m-%d')
    print(f"  {date_str}: ₹{record['price']:.2f}")

print("\nAPI Response Format (last 5 records):")
for record in cement_mumbai[-5:]:
    date_str = record['scraped_at'].strftime('%Y-%m-%d')
    print(f"  {date_str}: ₹{record['price']:.2f}")

# Check for duplicate dates
dates = [r['scraped_at'].strftime('%Y-%m-%d') for r in cement_mumbai]
unique_dates = set(dates)
print(f"\nUnique dates: {len(unique_dates)}")
print(f"Total records: {len(dates)}")
print(f"Duplicates: {len(dates) - len(unique_dates)}")

if len(unique_dates) == len(dates):
    print("✓ All dates are unique")
else:
    print("✗ Some dates are duplicated")
