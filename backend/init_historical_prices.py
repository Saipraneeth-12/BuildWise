"""
Initialize historical price data in MongoDB
Run this once to populate the database with 90 days of historical data
"""

from utils.db import get_db
from services.material_price_scraper import MaterialPriceScraper
from datetime import datetime

print("=" * 70)
print("INITIALIZING HISTORICAL PRICE DATA")
print("=" * 70)

# Connect to database
db = get_db()

# Check if data already exists
existing_count = db.material_prices.count_documents({})
print(f"\nExisting records in database: {existing_count}")

if existing_count > 0:
    response = input("\nDatabase already has data. Clear and reinitialize? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        exit(0)
    
    # Clear existing data
    print("Clearing existing data...")
    db.material_prices.delete_many({})
    print("✓ Cleared")

# Generate historical data
print("\nGenerating 90 days of historical data...")
scraper = MaterialPriceScraper()
historical_data = scraper.generate_historical_data(days=90)

print(f"Generated {len(historical_data)} records")

# Insert in batches
batch_size = 1000
total_inserted = 0

print("\nInserting into database...")
for i in range(0, len(historical_data), batch_size):
    batch = historical_data[i:i+batch_size]
    db.material_prices.insert_many(batch)
    total_inserted += len(batch)
    progress = (total_inserted / len(historical_data)) * 100
    print(f"  Progress: {total_inserted}/{len(historical_data)} ({progress:.1f}%)")

print(f"\n✓ Successfully inserted {total_inserted} records")

# Verify data
print("\nVerifying data...")
cement_mumbai = list(db.material_prices.find({
    'material': 'Cement',
    'type': 'OPC 53',
    'location': 'Mumbai'
}).sort('scraped_at', 1))

if len(cement_mumbai) > 0:
    first_date = cement_mumbai[0]['scraped_at'].strftime('%Y-%m-%d')
    last_date = cement_mumbai[-1]['scraped_at'].strftime('%Y-%m-%d')
    print(f"  Cement OPC 53 Mumbai: {len(cement_mumbai)} records")
    print(f"  Date range: {first_date} to {last_date}")
    print(f"  First price: ₹{cement_mumbai[0]['price']:.2f}")
    print(f"  Last price: ₹{cement_mumbai[-1]['price']:.2f}")

# Create indexes for better performance
print("\nCreating indexes...")
db.material_prices.create_index([
    ('material', 1),
    ('type', 1),
    ('location', 1),
    ('scraped_at', 1)
])
db.material_prices.create_index([('scraped_at', 1)])
print("✓ Indexes created")

print("\n" + "=" * 70)
print("INITIALIZATION COMPLETE")
print("=" * 70)
print("\nYou can now:")
print("1. Start the backend: python app.py")
print("2. Open Material Prices page in frontend")
print("3. Select 'Last 90 days' to see the full price trend")
print("=" * 70)
