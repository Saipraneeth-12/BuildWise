# AI Scrum Master - Example Prompts & Outputs

## How User Descriptions Are Processed

### ✅ YES - Your Description IS Considered!

When you enter a description like **"RCC residential apartment of 1000 sqft"**, the AI Scrum Master:

1. **Receives your full description** in the Granite LLM prompt
2. **Analyzes the details** (building type, area, special requirements)
3. **Adjusts recommendations** based on your specific project
4. **Displays your description** in the generated schedule

## Example Inputs & What AI Considers

### Example 1: Basic Description
**Input:**
```
Prompt: "RCC residential apartment of 1000 sqft"
Floors: G+2
Season: Monsoon
```

**What Granite LLM Sees:**
```
USER REQUEST: RCC residential apartment of 1000 sqft

IMPORTANT: Analyze the user's description carefully. Consider:
- Building area/size: 1000 sqft (mentioned)
- Building type: Residential apartment
- Special requirements: None mentioned
- Construction method: RCC (standard)

Adjust your schedule recommendations based on these details.
Larger areas may need more time for finishing work.
```

**What AI Considers:**
- ✅ Building type: Residential apartment
- ✅ Area: 1000 sqft (smaller apartment)
- ✅ Construction: RCC method
- ✅ Floors: G+2 (3 floors)
- ✅ Season: Monsoon (+35% duration)

**Schedule Adjustments:**
- Finishing work: Standard duration (1000 sqft is moderate)
- Plastering: ~6-8 weeks for 3 floors
- Flooring: ~4-6 weeks
- MEP work: Standard complexity

---

### Example 2: Detailed Description
**Input:**
```
Prompt: "Luxury RCC residential villa of 3500 sqft with basement parking, 
         modern amenities, and premium finishes"
Floors: G+2
Season: Summer
```

**What Granite LLM Sees:**
```
USER REQUEST: Luxury RCC residential villa of 3500 sqft with basement 
              parking, modern amenities, and premium finishes

IMPORTANT: Analyze the user's description carefully. Consider:
- Building area/size: 3500 sqft (large villa)
- Building type: Luxury residential villa
- Special requirements: Basement parking, modern amenities, premium finishes
- Construction method: RCC (standard)
```

**What AI Considers:**
- ✅ Building type: Luxury villa (higher quality standards)
- ✅ Area: 3500 sqft (large, needs more time)
- ✅ Special features: Basement parking (extra excavation)
- ✅ Amenities: Modern (complex MEP work)
- ✅ Finishes: Premium (extended finishing time)

**Schedule Adjustments:**
- Basement excavation: +2-3 weeks
- Finishing work: +30-40% time (premium quality)
- MEP work: +20-30% time (modern amenities)
- Inspection: More rigorous (luxury standards)

---

### Example 3: Commercial Building
**Input:**
```
Prompt: "Commercial office building 5000 sqft with open floor plan 
         and fast-track construction"
Floors: G+3
Season: Winter
```

**What AI Considers:**
- ✅ Building type: Commercial office
- ✅ Area: 5000 sqft (large commercial space)
- ✅ Layout: Open floor plan (less partition work)
- ✅ Method: Fast-track (parallel activities)
- ✅ Season: Winter (+15% duration)

**Schedule Adjustments:**
- Brickwork: Reduced (open floor plan)
- Parallel activities: Structure + MEP planning
- Finishing: Commercial grade (faster than residential)
- Fast-track: Overlapping phases where possible

---

### Example 4: Small Apartment
**Input:**
```
Prompt: "Small RCC apartment 600 sqft, single bedroom"
Floors: G+1
Season: Summer
```

**What AI Considers:**
- ✅ Area: 600 sqft (small, faster completion)
- ✅ Type: Single bedroom (simple layout)
- ✅ Floors: G+1 (only 2 floors)
- ✅ Season: Summer (normal duration)

**Schedule Adjustments:**
- Finishing work: -20% time (smaller area)
- Plastering: ~4-5 weeks (2 floors only)
- Flooring: ~2-3 weeks
- Overall: Faster completion

---

### Example 5: Multi-story Complex
**Input:**
```
Prompt: "Large residential complex 10000 sqft with multiple units, 
         common areas, and landscaping"
Floors: G+4
Season: Monsoon
```

**What AI Considers:**
- ✅ Area: 10000 sqft (very large)
- ✅ Type: Multi-unit complex
- ✅ Features: Common areas, landscaping
- ✅ Floors: G+4 (5 floors, tallest)
- ✅ Season: Monsoon (+35% duration)

**Schedule Adjustments:**
- Structure: 5 floors (longest phase)
- Finishing: +50% time (large area + multiple units)
- Common areas: Additional phase
- Landscaping: Final phase added
- Overall: Longest completion time

---

## How It Works in the Schedule

### Project Summary Display

When you generate a schedule, you'll see:

```
AI Scrum Master Schedule
📋 RCC residential apartment of 1000 sqft
RCC Residential Building • Monsoon season

[Total Duration] [Total Weeks] [Floor Count] [Season Impact]
```

Your description is displayed prominently at the top!

### Granite LLM Response

The AI's reasoning includes your description:

```
Based on the user's request for an RCC residential apartment of 1000 sqft,
I recommend the following schedule:

- Area: 1000 sqft is moderate size, standard finishing duration
- Type: Residential apartment requires standard quality finishes
- Construction: RCC method with proper curing cycles
- Monsoon season: Extended curing and rain protection needed

Sprint Plan:
...
```

---

## What Details Matter Most?

### High Impact Details (AI adjusts significantly)

1. **Building Area/Size**
   - Small (< 1000 sqft): -10-20% finishing time
   - Medium (1000-2500 sqft): Standard time
   - Large (> 2500 sqft): +20-40% finishing time

2. **Building Type**
   - Residential: Standard quality
   - Commercial: Different finishing standards
   - Luxury/Premium: +30-50% finishing time
   - Industrial: Different requirements

3. **Special Features**
   - Basement: +2-4 weeks excavation
   - Parking: Additional structural work
   - Amenities: +20-30% MEP time
   - Premium finishes: +30-40% finishing time

4. **Construction Method**
   - Standard RCC: Normal timeline
   - Fast-track: Parallel activities
   - Prefab: Reduced on-site time

### Medium Impact Details

5. **Layout Complexity**
   - Open floor plan: Less partition work
   - Multiple rooms: Standard work
   - Complex layout: +10-20% time

6. **Quality Level**
   - Standard: Normal timeline
   - Premium: +20-30% time
   - Luxury: +40-50% time

### Low Impact Details (AI notes but doesn't adjust much)

7. **Aesthetic Preferences**
   - Modern, traditional, contemporary
   - Noted in recommendations
   - Minimal timeline impact

8. **Future Plans**
   - Expansion possibilities
   - Noted for planning
   - No immediate timeline impact

---

## Best Practices for Descriptions

### ✅ Good Descriptions (AI can work with these)

1. **"RCC residential apartment of 1000 sqft"**
   - Clear type, area, method

2. **"Commercial building 3000 sqft with open floor plan"**
   - Type, area, layout specified

3. **"Luxury villa 4000 sqft with basement and premium finishes"**
   - Type, area, special features, quality level

4. **"Small residential house 800 sqft, 2 bedrooms, standard construction"**
   - Size, type, layout, quality level

5. **"Multi-story apartment complex 8000 sqft with modern amenities"**
   - Scale, type, features

### ⚠️ Vague Descriptions (AI uses defaults)

1. **"Build a house"**
   - Missing: area, type, features
   - AI assumes: Standard residential, medium size

2. **"Construction project"**
   - Missing: everything
   - AI assumes: Standard RCC residential

3. **"Big building"**
   - Missing: specific size, type
   - AI assumes: Large residential

### 💡 Pro Tips

**Include these for best results:**
1. Building type (residential, commercial, villa, apartment)
2. Area in sqft (e.g., 1000 sqft, 2500 sqft)
3. Special features (basement, parking, amenities)
4. Quality level (standard, premium, luxury)
5. Any time constraints (fast-track, standard)

**Example Perfect Description:**
```
"Luxury RCC residential villa of 3500 sqft with basement parking, 
4 bedrooms, modern amenities, premium finishes, and landscaping. 
Standard construction timeline acceptable."
```

This gives AI maximum context to generate the most accurate schedule!

---

## Summary

### ✅ Your Description IS Used!

1. **Granite LLM receives** your full description
2. **AI analyzes** area, type, features, quality
3. **Schedule adjusts** based on your specifics
4. **Display shows** your description prominently
5. **Recommendations** tailored to your project

### 📊 Impact Levels

- **Area size**: High impact on finishing duration
- **Building type**: Medium-high impact on standards
- **Special features**: High impact on specific phases
- **Quality level**: High impact on finishing time
- **Season**: High impact on overall duration (already selected)
- **Floor count**: High impact on structure phase (already selected)

### 🎯 Result

When you enter **"RCC residential apartment of 1000 sqft"**, the AI:
- Knows it's a residential apartment (not commercial)
- Knows it's 1000 sqft (moderate size)
- Knows it's RCC construction (standard method)
- Adjusts finishing work accordingly
- Generates realistic schedule for YOUR specific project

**Your description matters and IS considered!** 🎉
