# Construction Estimator - Complete Guide

## Overview

The Construction Estimator is a comprehensive system that calculates workers, timeline, materials, and costs for construction projects using engineering formulas. It supports both **Manual** (form-based) and **AI** (prompt-based) estimation modes.

---

## Features

### 1. Manual Estimator
- Form-based input
- Direct parameter entry
- Instant calculations
- Precise control

### 2. AI Estimator
- Natural language prompts
- IBM Granite LLM extraction
- Automatic parameter detection
- User-friendly interface

### 3. Comprehensive Output
- **Workers & Labor**: Masons, helpers, carpenters, supervisors
- **Timeline**: Days, weeks, months
- **Cost Breakdown**: Labour cost, material cost, total cost
- **Materials Required**: Cement, steel, bricks, sand, aggregate

---

## Engineering Formulas

### Area Conversion
```
total_sqft = area_sqyards × floors × 9
```

### Timeline Calculation
```
productivity_rate = 250 sqft/day
timeline_days = total_sqft ÷ productivity_rate
timeline_weeks = timeline_days ÷ 7
timeline_months = timeline_days ÷ 30
```

### Worker Calculation
```
masons = total_sqft ÷ 1500
helpers = masons (1:1 ratio)
carpenters = total_sqft ÷ 3000
supervisors = 1
total_workers = masons + helpers + carpenters + supervisors
```

### Material Calculation
```
steel_kg = total_sqft × 4
steel_tons = steel_kg ÷ 1000
cement_bags = total_sqft × 0.4
bricks = total_sqft × 50
sand_cft = total_sqft × 0.8
aggregate_cft = total_sqft × 1.2
```

### Cost Calculation
```
material_cost = area_sqyards × floors × cost_per_sqyard
labour_cost = total_workers × wage_per_day × timeline_days
total_cost = labour_cost + material_cost
```

---

## Manual Estimator Usage

### Input Parameters

1. **Built-up Area (sq yards)**
   - Example: 1000
   - Unit: Square yards

2. **Number of Floors**
   - G+1 = 2 floors
   - G+2 = 3 floors
   - G+3 = 4 floors
   - Example: 3 (for G+2)

3. **Daily Wage per Worker (₹)**
   - Example: 500
   - Unit: Rupees per day

4. **Cost per Sq Yard (₹)**
   - Material cost
   - Example: 1500
   - Unit: Rupees per square yard

### Steps

1. Click "Manual" mode
2. Fill in all four parameters
3. Click "Calculate Estimate"
4. View comprehensive results

---

## AI Estimator Usage

### Natural Language Prompts

The AI Estimator uses IBM Granite LLM to extract parameters from natural language.

### Example Prompts

**Example 1: Complete Specification**
```
Build G+2 residential building of 1000 sq yards with wage 500 and cost 1500 per sq yard
```

**Example 2: Detailed Description**
```
I need to construct a 3-floor building (G+2) with 1000 square yards area. 
Daily worker wage is 500 rupees and material cost is 1500 per square yard.
```

**Example 3: Casual Description**
```
Planning a G+2 house, around 1000 sq yards. Workers get 500/day, 
materials cost about 1500 per sq yard.
```

**Example 4: Minimal**
```
1000 sq yards, G+2, wage 500, cost 1500
```

### What AI Extracts

- **Area**: Square yards (1000)
- **Floors**: Number of floors (3 for G+2)
- **Wage**: Daily wage (500)
- **Cost per sq yard**: Material cost (1500)

### Steps

1. Click "AI Estimator" mode
2. Enter natural language prompt
3. Click "AI Generate Estimate"
4. AI extracts parameters (shown in green box)
5. View comprehensive results

---

## Output Sections

### 1. Project Summary (Top Right Card)

**Timeline**
- Total months
- Total days
- Total weeks

**Total Workers**
- Count of all workers
- Breakdown by type

**Total Cost**
- Complete project cost
- Labour + Material split

### 2. Workers & Labor

**Chart**: Bar chart showing worker distribution

**Details**:
- Masons: Skilled workers for masonry
- Helpers: Assistant workers (1:1 with masons)
- Carpenters: Formwork and carpentry
- Supervisors: Site supervision

**Formula**: Based on total square footage

### 3. Timeline

**Three Views**:
- Days: Total working days
- Weeks: Total weeks
- Months: Total months

**Calculation**: Based on 250 sqft/day productivity

### 4. Cost Breakdown

**Pie Chart**: Labour vs Material cost

**Labour Cost**:
- Formula: workers × wage × days
- Breakdown shown

**Material Cost**:
- Formula: area × floors × cost_per_sqyard
- Breakdown shown

**Total Cost**: Sum of both

### 5. Materials Required

**Bar Chart**: Material quantities

**Materials**:
- Cement (bags)
- Steel (tons and kg)
- Bricks (units)
- Sand (cubic feet)
- Aggregate (cubic feet)

**Formulas**: Industry-standard ratios per sqft

---

## Backend Architecture

### Files Created

1. **`backend/services/construction_estimator.py`**
   - Main calculation engine
   - Engineering formulas
   - Input validation

2. **`backend/services/ai_estimator.py`**
   - Granite LLM integration
   - Parameter extraction
   - Fallback regex extraction

3. **`backend/routes/estimation.py`**
   - `/estimate` - Manual endpoint
   - `/ai-estimate` - AI endpoint
   - `/estimate/test` - Test endpoint

### API Endpoints

#### POST /api/estimate (Manual)

**Request**:
```json
{
  "area": 1000,
  "floors": 3,
  "wage": 500,
  "cost_per_sqyard": 1500
}
```

**Response**:
```json
{
  "success": true,
  "estimate": {
    "timeline_days": 108,
    "timeline_weeks": 15.43,
    "timeline_months": 3.6,
    "masons": 18,
    "helpers": 18,
    "carpenters": 9,
    "supervisors": 1,
    "total_workers": 46,
    "steel_kg": 108000,
    "steel_tons": 108,
    "cement_bags": 10800,
    "bricks": 1350000,
    "sand_cft": 21600,
    "aggregate_cft": 32400,
    "labour_cost": 2484000,
    "material_cost": 4500000,
    "total_cost": 6984000
  },
  "mode": "manual"
}
```

#### POST /api/ai-estimate (AI)

**Request**:
```json
{
  "prompt": "Build G+2 residential building of 1000 sq yards with wage 500 and cost 1500 per sq yard"
}
```

**Response**:
```json
{
  "success": true,
  "estimate": { ... },
  "extracted_parameters": {
    "area": 1000,
    "floors": 3,
    "wage": 500,
    "cost_per_sqyard": 1500
  },
  "original_prompt": "Build G+2...",
  "mode": "ai"
}
```

---

## AI Extraction Logic

### Granite LLM Prompt

```
You are a construction parameter extraction AI. Extract ONLY the following numerical values:

USER PROMPT: {user_prompt}

Extract:
1. area: Built-up area in square yards
2. floors: Number of floors (G+1 = 2, G+2 = 3)
3. wage: Daily wage per worker
4. cost_per_sqyard: Material cost per square yard

Return JSON:
{"area": <number>, "floors": <number>, "wage": <number>, "cost_per_sqyard": <number>}
```

### Fallback Extraction

If Granite fails, regex patterns extract:
- Area: `1000 sq yards`, `area 1000`
- Floors: `G+2`, `3 floors`
- Wage: `wage 500`, `500 per day`
- Cost: `cost 1500`, `1500 per sq yard`

---

## Example Calculations

### Example: G+2 Building, 1000 sq yards

**Input**:
- Area: 1000 sq yards
- Floors: 3 (G+2)
- Wage: ₹500/day
- Cost: ₹1500/sq yard

**Calculations**:

1. **Total Area**:
   ```
   1000 × 3 × 9 = 27,000 sqft
   ```

2. **Timeline**:
   ```
   27,000 ÷ 250 = 108 days
   108 ÷ 7 = 15.43 weeks
   108 ÷ 30 = 3.6 months
   ```

3. **Workers**:
   ```
   Masons: 27,000 ÷ 1500 = 18
   Helpers: 18
   Carpenters: 27,000 ÷ 3000 = 9
   Supervisors: 1
   Total: 46 workers
   ```

4. **Materials**:
   ```
   Steel: 27,000 × 4 = 108,000 kg = 108 tons
   Cement: 27,000 × 0.4 = 10,800 bags
   Bricks: 27,000 × 50 = 1,350,000 units
   Sand: 27,000 × 0.8 = 21,600 cft
   Aggregate: 27,000 × 1.2 = 32,400 cft
   ```

5. **Costs**:
   ```
   Material: 1000 × 3 × 1500 = ₹45,00,000
   Labour: 46 × 500 × 108 = ₹24,84,000
   Total: ₹69,84,000
   ```

---

## Setup Instructions

### Prerequisites

1. **Ollama** installed
2. **Granite model** downloaded
3. **Backend** running
4. **Frontend** running

### Install Ollama

```bash
# Visit https://ollama.ai
# Or use package manager
brew install ollama  # macOS
```

### Install Granite Model

```bash
ollama pull granite3.3:2b
```

### Start Ollama

```bash
ollama serve
```

### Start Backend

```bash
cd backend
python app.py
```

### Start Frontend

```bash
cd frontend
npm run dev
```

---

## Testing

### Test Manual Estimator

1. Navigate to Material Estimator page
2. Click "Manual" mode
3. Enter:
   - Area: 1000
   - Floors: 3
   - Wage: 500
   - Cost: 1500
4. Click "Calculate Estimate"
5. Verify all sections display

### Test AI Estimator

1. Click "AI Estimator" mode
2. Enter prompt: "Build G+2 residential building of 1000 sq yards with wage 500 and cost 1500 per sq yard"
3. Click "AI Generate Estimate"
4. Verify extracted parameters show in green box
5. Verify all sections display

### Test API Directly

```bash
# Test manual endpoint
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"area":1000,"floors":3,"wage":500,"cost_per_sqyard":1500}'

# Test AI endpoint
curl -X POST http://localhost:5000/api/ai-estimate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt":"Build G+2 building of 1000 sq yards with wage 500 and cost 1500"}'
```

---

## Troubleshooting

### Granite Not Responding

**Check**:
```bash
ps aux | grep ollama
ollama list
```

**Fix**:
```bash
ollama serve
ollama pull granite3.3:2b
```

### AI Extraction Fails

- System falls back to regex extraction
- Check extracted parameters in green box
- Verify prompt includes all values

### Calculations Seem Wrong

- Verify input parameters
- Check formulas in this guide
- All formulas are industry-standard

---

## Summary

The Construction Estimator provides:

✅ **Two Modes**: Manual and AI
✅ **Engineering Formulas**: Industry-standard calculations
✅ **Comprehensive Output**: Workers, timeline, materials, costs
✅ **AI Integration**: Granite LLM for natural language
✅ **Visual Charts**: Bar charts, pie charts
✅ **Detailed Breakdown**: Every calculation explained

**Ready for production use!** 🏗️✨
