# BuildWise Data Flow & Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUILDWISE MATERIAL PRICING SYSTEM             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CURRENT (Realistic Simulation):                                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Market Data Aggregator                                │    │
│  │  • Base Prices (2026 Indian Market Rates)             │    │
│  │  • Location Factors (Metro +10%)                      │    │
│  │  • Seasonal Factors (Construction/Monsoon)            │    │
│  │  • Daily Variations (-3% to +5%)                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  FUTURE (Real Web Scraping):                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  SteelGuru   │  │ GoodReturns  │  │  IndiaMART   │         │
│  │  (Steel)     │  │  (Cement)    │  │  (All)       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Metal World  │  │ Construction │  │  Govt PWD    │         │
│  │  (Steel)     │  │   World      │  │  (Official)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPING & PROCESSING LAYER                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MaterialPriceScraper (material_price_scraper.py)               │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. fetch_all_prices()                                 │    │
│  │     • Iterate through all materials                    │    │
│  │     • Iterate through all locations (30+ cities)       │    │
│  │     • Apply intelligent variations                     │    │
│  │                                                         │    │
│  │  2. _fetch_price_with_variation()                      │    │
│  │     • Base Price × Location Factor                     │    │
│  │     • × Daily Variation                                │    │
│  │     • × Seasonal Factor                                │    │
│  │     • = Final Price                                    │    │
│  │                                                         │    │
│  │  3. Calculate Trends                                   │    │
│  │     • Compare with yesterday's price                   │    │
│  │     • Determine: up / down / same                      │    │
│  │     • Calculate change percentage                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Price Scheduler (price_scheduler.py)                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  • Runs every 6 hours                                  │    │
│  │  • Triggers fetch_all_prices()                         │    │
│  │  • Stores results in MongoDB                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MongoDB Collection: material_prices                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Document Structure:                                   │    │
│  │  {                                                     │    │
│  │    "_id": ObjectId,                                   │    │
│  │    "material": "Cement",                              │    │
│  │    "type": "OPC 53",                                  │    │
│  │    "price": 412.50,                                   │    │
│  │    "unit": "bag",                                     │    │
│  │    "location": "Mumbai",                              │    │
│  │    "state": "Maharashtra",                            │    │
│  │    "source": "Market Data Aggregator",                │    │
│  │    "trend": "up",                                     │    │
│  │    "scraped_at": "2026-02-24T10:30:00Z"              │    │
│  │  }                                                     │    │
│  │                                                         │    │
│  │  Indexes:                                              │    │
│  │  • material + type + location + scraped_at            │    │
│  │  • scraped_at (for time-based queries)                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Total Records: ~900 per refresh cycle                          │
│  • 5 materials × 30+ types × 30+ cities                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Routes (material_prices.py)                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  GET /api/materials/live                               │    │
│  │  • Filter by material, type, state, location          │    │
│  │  • Returns current day's prices                        │    │
│  │                                                         │    │
│  │  GET /api/materials/history                            │    │
│  │  • Query params: material, type, location, days       │    │
│  │  • Returns historical data for charts                  │    │
│  │                                                         │    │
│  │  POST /api/materials/refresh                           │    │
│  │  • Manually trigger price refresh                      │    │
│  │  • Admin only                                          │    │
│  │                                                         │    │
│  │  GET /api/materials/trends                             │    │
│  │  • Aggregated trends for all materials                │    │
│  │  • Compare today vs yesterday                          │    │
│  │                                                         │    │
│  │  GET /api/materials/filters                            │    │
│  │  • Available states, cities, materials, types         │    │
│  │                                                         │    │
│  │  GET /api/materials/summary                            │    │
│  │  • Dashboard summary cards                             │    │
│  │  • Average prices with trends                          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Material Prices Dashboard (MaterialPrices.jsx)                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  1. Summary Cards                                      │    │
│  │     • Cement Average: ₹385/bag ↑ 2.3%                │    │
│  │     • Steel Average: ₹61,500/ton ↓ 1.2%              │    │
│  │     • Sand Average: ₹43/cft → 0%                     │    │
│  │     • Aggregates Average: ₹48/cft ↑ 0.8%             │    │
│  │                                                         │    │
│  │  2. Price Comparison Table                             │    │
│  │     • Filter by: Material, Type, State, Location      │    │
│  │     • Sortable columns                                 │    │
│  │     • Trend indicators (↑↓→)                          │    │
│  │                                                         │    │
│  │  3. Price Trends Chart                                 │    │
│  │     • Line chart showing 30-day history               │    │
│  │     • Select material, type, location                 │    │
│  │     • Interactive tooltips                             │    │
│  │                                                         │    │
│  │  4. Location Comparison                                │    │
│  │     • Compare prices across cities                     │    │
│  │     • Bar chart visualization                          │    │
│  │     • Identify cheapest/expensive locations           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Generation Process

```
Step 1: Base Price Selection
┌─────────────────────────────────────┐
│  Material: Cement                   │
│  Type: OPC 53                       │
│  Base Price: ₹400/bag               │
└─────────────────────────────────────┘
              ↓
Step 2: Location Factor
┌─────────────────────────────────────┐
│  Location: Mumbai (Metro City)     │
│  Factor: 1.10 (10% higher)         │
│  Price: ₹400 × 1.10 = ₹440         │
└─────────────────────────────────────┘
              ↓
Step 3: Daily Variation
┌─────────────────────────────────────┐
│  Random Factor: 0.97 to 1.05       │
│  Today's Factor: 1.02              │
│  Price: ₹440 × 1.02 = ₹448.80     │
└─────────────────────────────────────┘
              ↓
Step 4: Seasonal Factor
┌─────────────────────────────────────┐
│  Month: February (Construction)    │
│  Factor: 1.05 (5% higher demand)   │
│  Price: ₹448.80 × 1.05 = ₹471.24  │
└─────────────────────────────────────┘
              ↓
Step 5: Final Price
┌─────────────────────────────────────┐
│  Final Price: ₹471.24/bag          │
│  Rounded: ₹471/bag                 │
│  Trend: Compare with yesterday     │
└─────────────────────────────────────┘
```

---

## Geographic Coverage Map

```
┌─────────────────────────────────────────────────────────────┐
│                    INDIA - COVERAGE MAP                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  NORTH                                                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │  • Delhi: New Delhi, Delhi                       │      │
│  │  • Punjab: Chandigarh, Ludhiana, Amritsar       │      │
│  │  • Rajasthan: Jaipur, Jodhpur, Udaipur          │      │
│  │  • Uttar Pradesh: Lucknow, Kanpur, Agra         │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  WEST                                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │  • Maharashtra: Mumbai, Pune, Nagpur             │      │
│  │  • Gujarat: Ahmedabad, Surat, Vadodara           │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  SOUTH                                                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │  • Karnataka: Bangalore, Mysore, Hubli           │      │
│  │  • Tamil Nadu: Chennai, Coimbatore, Madurai      │      │
│  │  • Telangana: Hyderabad, Warangal, Nizamabad    │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  EAST                                                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │  • West Bengal: Kolkata, Howrah, Durgapur       │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  Total: 10 States, 30+ Cities                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Material Categories & Types

```
┌─────────────────────────────────────────────────────────────┐
│                    MATERIAL HIERARCHY                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CEMENT (5 types)                                        │
│     ├── OPC 33 (₹320/bag)                                  │
│     ├── OPC 43 (₹350/bag)                                  │
│     ├── OPC 53 (₹400/bag)                                  │
│     ├── PPC (₹380/bag)                                     │
│     └── PSC (₹360/bag)                                     │
│                                                              │
│  2. STEEL (5 types)                                         │
│     ├── TMT Fe 415 (₹58,000/ton)                          │
│     ├── TMT Fe 500 (₹62,000/ton)                          │
│     ├── TMT Fe 550 (₹65,000/ton)                          │
│     ├── Structural Steel (₹70,000/ton)                    │
│     └── Binding Wire (₹65/kg)                             │
│                                                              │
│  3. SAND (4 types)                                          │
│     ├── River Sand (₹45/cft)                               │
│     ├── M Sand (₹40/cft)                                   │
│     ├── Plaster Sand (₹42/cft)                            │
│     └── Fill Sand (₹35/cft)                               │
│                                                              │
│  4. AGGREGATES (4 types)                                    │
│     ├── 10mm (₹50/cft)                                     │
│     ├── 20mm (₹48/cft)                                     │
│     ├── 40mm (₹45/cft)                                     │
│     └── Crusher Dust (₹30/cft)                            │
│                                                              │
│  5. BRICKS (4 types)                                        │
│     ├── Red Bricks (₹8/piece)                              │
│     ├── Fly Ash Bricks (₹6/piece)                         │
│     ├── AAC Blocks (₹55/piece)                            │
│     └── Concrete Blocks (₹45/piece)                       │
│                                                              │
│  6. OTHERS (6 types)                                        │
│     ├── Bitumen (₹45/kg)                                   │
│     ├── RMC M20 (₹5,500/m³)                               │
│     ├── Tiles (₹45/sqft)                                   │
│     ├── Paint (₹350/litre)                                 │
│     ├── Electrical Wire (₹2,500/coil)                     │
│     └── PVC Pipes (₹180/length)                           │
│                                                              │
│  Total: 6 Categories, 28 Material Types                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Update Frequency & Scheduling

```
┌─────────────────────────────────────────────────────────────┐
│                    UPDATE SCHEDULE                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Automated Updates (price_scheduler.py):                    │
│  ┌────────────────────────────────────────────────┐        │
│  │  Every 6 hours:                                │        │
│  │  • 00:00 (Midnight)                            │        │
│  │  • 06:00 (Morning)                             │        │
│  │  • 12:00 (Noon)                                │        │
│  │  • 18:00 (Evening)                             │        │
│  │                                                 │        │
│  │  Process:                                       │        │
│  │  1. Fetch all prices (900+ records)           │        │
│  │  2. Calculate trends                           │        │
│  │  3. Store in MongoDB                           │        │
│  │  4. Log completion                             │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
│  Manual Updates:                                             │
│  ┌────────────────────────────────────────────────┐        │
│  │  POST /api/materials/refresh                   │        │
│  │  • Triggered by admin                          │        │
│  │  • Immediate price refresh                     │        │
│  │  • Returns count of updated records            │        │
│  └────────────────────────────────────────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

**Current Data Source**: Market Data Aggregator (Realistic Simulation)
**Base Prices**: 2026 Indian Construction Material Rates
**Coverage**: 30+ Cities, 10 States, 28 Material Types
**Update Frequency**: Every 6 hours (automated)
**Total Records**: ~900 per refresh cycle
**Storage**: MongoDB (material_prices collection)
**API Endpoints**: 6 endpoints for data access
**Frontend**: Material Prices Dashboard with charts & filters

**Migration Path**: Framework ready for real web scraping from:
- SteelGuru, Metal World (steel prices)
- GoodReturns, Construction World (cement prices)
- IndiaMART, TradeIndia (all materials)
- Government PWD websites (official rates)
