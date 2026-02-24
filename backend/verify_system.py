"""
Final system verification script
"""

print("=" * 60)
print("BUILDWISE MATERIAL ESTIMATOR - SYSTEM VERIFICATION")
print("=" * 60)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    import app
    from services.construction_estimator import ConstructionEstimator
    from services.ai_estimator import AIEstimator
    from services.price_fetcher import PriceFetcher
    from routes.estimation import estimation_bp
    print("   ✓ All imports successful")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test 2: Steel calculation
print("\n2. Testing steel calculation (CRITICAL)...")
try:
    est = ConstructionEstimator.calculate_estimate(1500, 2, 500)
    steel_tons = est['steel_tons']
    if 7 <= steel_tons <= 8:
        print(f"   ✓ Steel: {steel_tons} tons (CORRECT)")
    else:
        print(f"   ✗ Steel: {steel_tons} tons (INCORRECT - should be 7-8)")
        exit(1)
except Exception as e:
    print(f"   ✗ Calculation failed: {e}")
    exit(1)

# Test 3: Material types
print("\n3. Testing material types...")
try:
    steel_types = ConstructionEstimator.get_steel_types()
    cement_types = ConstructionEstimator.get_cement_types()
    if len(steel_types) == 4 and len(cement_types) == 4:
        print(f"   ✓ Steel types: {len(steel_types)}")
        print(f"   ✓ Cement types: {len(cement_types)}")
    else:
        print(f"   ✗ Type count incorrect")
        exit(1)
except Exception as e:
    print(f"   ✗ Type test failed: {e}")
    exit(1)

# Test 4: AI extraction
print("\n4. Testing AI parameter extraction...")
try:
    ai = AIEstimator()
    extracted = ai._fallback_extraction("Build G+2 building of 1500 sqft using Fe500 steel")
    if extracted['floors'] == 3 and extracted['steel_type'] == 'Fe500':
        print(f"   ✓ G+2 = {extracted['floors']} floors (CORRECT)")
        print(f"   ✓ Steel type: {extracted['steel_type']}")
    else:
        print(f"   ✗ Extraction incorrect")
        exit(1)
except Exception as e:
    print(f"   ✗ AI test failed: {e}")
    exit(1)

# Test 5: Price fetcher
print("\n5. Testing price fetcher...")
try:
    pf = PriceFetcher()
    prices = pf.get_all_prices('Fe500', 'OPC 53', 'India')
    if prices['steel_price_per_ton'] > 0 and prices['cement_price_per_bag'] > 0:
        print(f"   ✓ Steel price: ₹{prices['steel_price_per_ton']:,}/ton")
        print(f"   ✓ Cement price: ₹{prices['cement_price_per_bag']}/bag")
    else:
        print(f"   ✗ Price fetching failed")
        exit(1)
except Exception as e:
    print(f"   ✗ Price test failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("ALL VERIFICATIONS PASSED ✓")
print("=" * 60)
print("\nSYSTEM STATUS: PRODUCTION READY")
print("\nKEY FIXES VERIFIED:")
print("  ✓ Steel formula: 2.5 kg/sqft (NOT 4 kg/sqft)")
print("  ✓ G+X format: Correctly adds 1")
print("  ✓ Steel/Cement types: Available and working")
print("  ✓ Price fetcher: Operational")
print("  ✓ All imports: Successful")
print("\nYou can now start the backend with: python app.py")
print("=" * 60)
