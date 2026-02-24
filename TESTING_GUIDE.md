# Material Estimator Testing Guide

## Quick Start

### 1. Start Backend
```powershell
cd backend
python app.py
```
Backend will run on: http://localhost:5000

### 2. Start Frontend
```powershell
cd frontend
npm run dev
```
Frontend will run on: http://localhost:3000

---

## Test Cases

### Test Case 1: Manual Mode - Verify Correct Steel Calculation
**Purpose**: Verify the CRITICAL steel formula fix (2.5 kg/sqft, not 4 kg/sqft)

**Steps**:
1. Navigate to Material Estimator page
2. Select "Manual" mode
3. Enter:
   - Area: 1500 sqft
   - Floors: 2 (G+1)
   - Steel Type: Fe500
   - Cement Type: OPC 53
   - Wage: 500
   - Location: India
4. Click "Calculate Estimate"

**Expected Result**:
- Steel Required: 7.5 tons (NOT 70+ tons)
- Cement: 1200 bags
- Workers: 6
- Timeline: 0.5 months
- Total Cost: ~₹2,526,000

**Status**: ✓ PASS if steel is 7-8 tons

---

### Test Case 2: AI Mode - Parameter Extraction
**Purpose**: Verify AI extracts steel type, cement type, and G+X format

**Steps**:
1. Select "AI Estimator" mode
2. Enter prompt:
   ```
   Build G+2 residential building of 1500 sqft using Fe500 steel and OPC 53 cement with wage 500
   ```
3. Click "AI Generate Estimate"

**Expected Result**:
- AI Extracted Parameters shown:
  - Area: 1500 sqft
  - Floors: 3 (G+2 = 3 floors)
  - Steel Type: Fe500
  - Cement Type: OPC 53
  - Wage: ₹500/day
  - Location: India
- Estimation calculated correctly

**Status**: ✓ PASS if all parameters extracted correctly

---

### Test Case 3: Blueprint Mode - Image Upload
**Purpose**: Verify blueprint mode with steel/cement selection

**Steps**:
1. Select "Blueprint" mode
2. Upload one or more blueprint images
3. Select:
   - Steel Type: Fe550
   - Cement Type: PPC
   - Wage: 600
   - Location: Mumbai
4. Click "Estimate from Blueprint"

**Expected Result**:
- Extraction details shown with floor areas
- Steel type: Fe550 displayed
- Cement type: PPC displayed
- Estimation calculated with selected types
- Prices shown in results

**Status**: ✓ PASS if types are displayed and used

---

### Test Case 4: Steel Type Selection
**Purpose**: Verify different steel types affect pricing

**Steps**:
1. Manual mode, enter: 1500 sqft, 2 floors, wage 500
2. Test each steel type:
   - Fe415 (₹58,000/ton)
   - Fe500 (₹62,000/ton)
   - Fe550 (₹65,000/ton)
   - TMT Premium (₹68,000/ton)

**Expected Result**:
- Steel quantity stays same (7.5 tons)
- Steel cost changes based on type:
  - Fe415: ₹435,000
  - Fe500: ₹465,000
  - Fe550: ₹487,500
  - TMT Premium: ₹510,000

**Status**: ✓ PASS if costs change correctly

---

### Test Case 5: Cement Type Selection
**Purpose**: Verify different cement types affect pricing

**Steps**:
1. Manual mode, enter: 1500 sqft, 2 floors, wage 500, Fe500
2. Test each cement type:
   - OPC 43 (₹350/bag)
   - OPC 53 (₹400/bag)
   - PPC (₹380/bag)
   - PSC (₹360/bag)

**Expected Result**:
- Cement quantity stays same (1200 bags)
- Cement cost changes based on type:
  - OPC 43: ₹420,000
  - OPC 53: ₹480,000
  - PPC: ₹456,000
  - PSC: ₹432,000

**Status**: ✓ PASS if costs change correctly

---

### Test Case 6: G+X Format Handling
**Purpose**: Verify G+X format is correctly interpreted

**Test Data**:
| Input | Expected Floors |
|-------|----------------|
| G+0   | 1 floor        |
| G+1   | 2 floors       |
| G+2   | 3 floors       |
| G+3   | 4 floors       |
| G+10  | 11 floors      |

**Steps**:
1. AI mode
2. Test each format:
   - "Build G+0 building of 1000 sqft"
   - "Build G+1 building of 1000 sqft"
   - "Build G+2 building of 1000 sqft"
   - etc.

**Expected Result**:
- AI correctly extracts floors = X + 1
- Calculations use correct floor count

**Status**: ✓ PASS if all formats interpreted correctly

---

### Test Case 7: Results Display
**Purpose**: Verify all information is displayed correctly

**Steps**:
1. Generate any estimate
2. Check results sections

**Expected Display**:
- Project Summary:
  - Timeline (days/weeks/months)
  - Total Workers
  - Total Cost
  
- Workers & Labor:
  - Masons, Helpers, Carpenters, Supervisors
  - Chart visualization
  
- Materials Required:
  - Steel (TYPE) - X tons (Y kg)
  - Steel Cost - ₹X @ ₹Y/ton
  - Cement (TYPE) - X bags
  - Cement Cost - ₹X @ ₹Y/bag
  - Bricks, Sand, Aggregate
  
- Cost Breakdown:
  - Labour Cost
  - Material Cost
  - Total Cost
  - Pie chart

**Status**: ✓ PASS if all sections display correctly

---

## Backend API Tests

### Test Endpoint 1: Manual Estimation
```bash
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "area": 1500,
    "floors": 2,
    "wage": 500,
    "steel_type": "Fe500",
    "cement_type": "OPC 53",
    "location": "India"
  }'
```

**Expected**: JSON with estimate object, steel_tons: 7.5

---

### Test Endpoint 2: AI Estimation
```bash
curl -X POST http://localhost:5000/api/ai-estimate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "Build G+2 building of 1500 sqft using Fe500 steel and OPC 53 cement"
  }'
```

**Expected**: JSON with estimate + extracted_parameters

---

### Test Endpoint 3: Material Prices
```bash
curl "http://localhost:5000/api/prices/materials?steel_type=Fe500&cement_type=OPC%2053&location=India" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: JSON with steel_price_per_ton and cement_price_per_bag

---

### Test Endpoint 4: Material Types
```bash
curl http://localhost:5000/api/materials/types
```

**Expected**: JSON with steel_types and cement_types arrays

---

## Automated Backend Tests

### Run All Tests
```powershell
cd backend

# Test 1: Corrected formula
python test_corrected_formula.py

# Test 2: AI extraction
python test_fallback_extraction.py

# Test 3: Complete system
python test_complete_system.py
```

**Expected**: All tests show ✓ CORRECT

---

## Common Issues & Solutions

### Issue 1: Frontend shows "Failed to calculate estimate"
**Solution**: Check backend is running on port 5000

### Issue 2: AI extraction times out
**Solution**: System uses fallback regex extraction automatically

### Issue 3: Steel calculation still shows 70+ tons
**Solution**: Restart backend to load updated code

### Issue 4: PIL import error
**Solution**: 
```powershell
cd backend
pip install Pillow
```

### Issue 5: Blueprint upload fails
**Solution**: Check pytesseract is installed and Tesseract OCR is available

---

## Verification Checklist

Before marking as complete, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Manual mode calculates correctly (7.5 tons for 1500 sqft G+1)
- [ ] AI mode extracts all parameters
- [ ] Blueprint mode accepts images
- [ ] Steel type dropdown works in all modes
- [ ] Cement type dropdown works in all modes
- [ ] G+X format interpreted correctly (G+2 = 3 floors)
- [ ] Results display steel/cement types
- [ ] Results display prices
- [ ] All three modes produce estimates
- [ ] No console errors in browser
- [ ] No errors in backend logs

---

## Performance Benchmarks

**Expected Response Times**:
- Manual estimation: < 100ms
- AI estimation (fallback): < 200ms
- Blueprint estimation: < 2s per image
- Price fetching: < 500ms

**Expected Accuracy**:
- Steel calculation: ±0.5 tons
- Cement calculation: ±10 bags
- Timeline: ±1 day
- Cost: ±5%

---

**Last Updated**: February 24, 2026
**System Version**: BuildWise v1.0
**Test Status**: ALL TESTS PASSING ✓
