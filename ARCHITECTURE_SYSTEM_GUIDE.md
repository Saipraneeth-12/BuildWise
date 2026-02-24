# BuildWise Architecture System Guide

## Overview
The Architecture module provides two powerful ways to create architectural designs:
1. **AI Blueprint Generation** - Natural language to detailed blueprints
2. **Manual Drawing System** - AutoCAD-like drawing tools

---

## AI Blueprint Generation

### How It Works
The AI Blueprint Generator uses:
- **Deterministic Layout Engine**: Rule-based geometric placement
- **IBM Granite LLM**: Natural language understanding and recommendations
- **Image Generation**: Labeled blueprint images with measurements

### Input Format
Natural language prompts like:
```
30x40 ft plot, G+1, 2BHK, internal staircase
```

### Supported Parameters
- **Plot Dimensions**: "30x40 ft" or "10x12 m"
- **Floors**: "G+1" (2 floors), "G+2" (3 floors), up to G+10
- **Configuration**: "1BHK", "2BHK", "3BHK"
- **Options**: "duplex", "internal staircase"

### Room Constraints (Minimum Dimensions)
- Living Room: 3.5m × 4.0m
- Bedroom: 3.0m × 3.0m
- Kitchen: 2.4m × 3.0m
- Toilet: 1.2m × 2.4m
- Staircase: 1.0m × 3.0m

### Configuration Room Counts
- **1BHK**: 1 Living, 1 Bedroom, 1 Kitchen, 1 Toilet
- **2BHK**: 1 Living, 2 Bedrooms, 1 Kitchen, 2 Toilets
- **3BHK**: 1 Living, 3 Bedrooms, 1 Kitchen, 2 Toilets

### Deterministic Placement Logic

#### Step 1: Staircase Core (if multi-floor)
- Placed first at bottom-left corner
- Dimensions: 1.5m × 3.0m
- Same coordinates across all floors
- In duplex: Inside living room

#### Step 2: Living Room
- Front side placement (y = 0)
- Accessible from entrance
- Centered if possible
- 40% of plot length

#### Step 3: Kitchen
- Adjacent to living room
- Shared wall mandatory
- 30% of plot width

#### Step 4: Bedrooms
- Rear side placement
- Distributed left to right
- Circulation access maintained

#### Step 5: Toilets
- Attached to bedrooms
- Share at least one wall
- Cannot float independently

### Output Structure
```json
{
  "layout": {
    "plot": {
      "width_m": 9.14,
      "length_m": 12.19
    },
    "configuration": "2BHK",
    "floors": [
      {
        "floor_number": 1,
        "rooms": [
          {
            "name": "Living Room",
            "x": 1.5,
            "y": 0,
            "width": 7.64,
            "length": 4.88,
            "area": 37.28
          }
        ],
        "built_up_area": 82.5
      }
    ],
    "total_built_up_area": 165.0,
    "efficiency_ratio": 0.76
  },
  "blueprint_image": "data:image/png;base64,...",
  "metadata": {
    "ventilation_notes": "Ensure cross-ventilation in all rooms",
    "lighting_notes": "Maximize natural light from north and east",
    "structural_notes": "RCC frame structure recommended",
    "cost_estimate_range": "15-25 lakhs"
  }
}
```

### Blueprint Image Features
- Room rectangles with color coding:
  - Living Room: Light blue
  - Bedrooms: Light pink
  - Kitchen: Light green
  - Toilets: Light purple
  - Staircase: Light yellow
- Room labels with names
- Dimensions (width × length)
- Area in m²
- Plot boundary
- Metadata box with recommendations

### Integration Points
The generated layout data is exposed for:
1. **Quantity Engine** - Material calculations
2. **Cost Planner** - Budget estimation
3. **Scheduling Engine** - Timeline planning

---

## Manual Drawing System

### Drawing Tools

#### 1. Rectangle Tool
- Draw walls and rooms
- Transparent fill, black outline
- Drag to move, corner handles to resize

#### 2. Circle Tool
- Circular features (columns, curves)
- Transparent fill, black outline
- Drag to move, handles to resize

#### 3. Line Tool
- Draw walls and boundaries
- Black stroke, 2px width
- Drag endpoints to adjust

#### 4. Text Tool
- Add room labels and annotations
- Double-click to edit
- Arial font, 16px default
- Drag to reposition

#### 5. Measurement Tool
- Click two points to measure distance
- Shows distance in meters (scaled)
- Red line with measurement label
- Non-selectable after placement

### Canvas Features
- **Size**: 1000px × 700px
- **Background**: White
- **Grid**: 0.5m alignment
- **Selection**: Click to select, drag to move
- **Multi-select**: Not enabled (single object at a time)

### Saving Drawings
Drawings are saved to Documents with:
- Canvas data (JSON)
- Image data (base64 PNG)
- Measurements array
- Annotations array
- Timestamp

---

## Documents Integration

### Blueprint Documents
Saved with:
- Type: "blueprint"
- Prompt used
- Layout JSON
- Blueprint image (base64)
- Metadata (recommendations)

### Manual Drawing Documents
Saved with:
- Type: "manual_drawing"
- Canvas data (JSON)
- Image data (base64)
- Measurements
- Annotations

### Document Categories
Documents page shows three sections:
1. **AI Generated Blueprints** (purple theme)
2. **Manual Drawings** (green theme)
3. **Regular Documents** (blue theme)

---

## API Endpoints

### POST /api/architecture/generate
Generate AI blueprint from prompt
```json
{
  "prompt": "30x40 ft plot, G+1, 2BHK"
}
```

### GET /api/architecture/blueprints
Get all blueprints for current user

### DELETE /api/architecture/blueprints/:id
Delete a blueprint

### POST /api/architecture/save-drawing
Save manual drawing to documents
```json
{
  "name": "Floor Plan",
  "canvas_data": "...",
  "image_data": "data:image/png;base64,...",
  "measurements": [],
  "annotations": []
}
```

### POST /api/architecture/save-blueprint-to-docs
Save AI blueprint to documents
```json
{
  "name": "2BHK Blueprint",
  "prompt": "...",
  "blueprint_image": "...",
  "layout": {},
  "metadata": {}
}
```

---

## Usage Examples

### Example 1: Simple 2BHK
```
Prompt: "30x40 ft plot, G+1, 2BHK"
Output: 2-floor building with living, 2 bedrooms, kitchen, 2 toilets
```

### Example 2: Duplex 3BHK
```
Prompt: "40x50 ft plot, G+1, 3BHK, duplex, internal staircase"
Output: Duplex with living on ground floor, bedrooms on upper floor
```

### Example 3: Single Floor 1BHK
```
Prompt: "25x30 ft plot, 1BHK"
Output: Single floor with living, 1 bedroom, kitchen, 1 toilet
```

---

## Technical Stack

### Backend
- **Flask**: Web framework
- **Pillow**: Image generation
- **Requests**: Ollama API calls
- **MongoDB**: Data storage

### Frontend
- **React**: UI framework
- **Fabric.js**: Canvas manipulation
- **Lucide React**: Icons
- **React Hot Toast**: Notifications

### AI Model
- **IBM Granite 3.3:2b**: Via Ollama
- **Temperature**: 0.1-0.3 (deterministic)
- **Purpose**: Parameter extraction and recommendations

---

## Validation Rules

### Plot Size Validation
- 1BHK: Minimum 40 m²
- 2BHK: Minimum 60 m²
- 3BHK: Minimum 80 m²

### Adjacency Validation
- Kitchen must be adjacent to living
- At least one toilet adjacent to bedroom
- Staircase connected to circulation path
- No isolated rooms

### Grid Alignment
- All coordinates rounded to 0.5m grid
- Ensures clean geometric layouts

---

## Error Handling

### Common Errors
1. **Plot too small**: "Plot dimensions insufficient for 2BHK. Minimum 60m² required"
2. **Invalid format**: "Plot dimensions not found. Format: '30x40 ft' or '10x12 m'"
3. **Ollama not running**: Falls back to default recommendations

### Fallback Behavior
- If Granite LLM fails: Uses regex extraction
- If image generation fails: Returns error message
- If validation fails: Returns structured error JSON

---

## Performance

### Generation Time
- Layout calculation: < 1 second
- Granite LLM call: 5-10 seconds
- Image generation: 1-2 seconds
- **Total**: ~10-15 seconds

### Image Size
- Resolution: 1200px × 900px
- Format: PNG
- Base64 encoded
- Typical size: 200-500 KB

---

## Future Enhancements

### Planned Features
1. 3D visualization
2. Virtual walkthrough
3. Furniture placement
4. Lighting simulation
5. Cost estimation per room
6. Material quantity per room
7. Export to DXF/DWG
8. Import existing blueprints
9. Collaborative editing
10. Version history

---

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama
ollama serve

# Pull Granite model
ollama pull granite3.3:2b
```

### Image Generation Fails
- Check Pillow installation: `pip install Pillow==10.2.0`
- Check font availability (falls back to default if Arial not found)

### Canvas Not Loading
- Check Fabric.js import in package.json
- Clear browser cache
- Check console for errors

---

## Best Practices

### For AI Generation
1. Be specific with dimensions
2. Include floor count (G+1, G+2)
3. Specify configuration (1BHK, 2BHK, 3BHK)
4. Mention special requirements (duplex, staircase)

### For Manual Drawing
1. Start with outer boundary
2. Add walls using rectangles/lines
3. Label rooms with text tool
4. Add measurements for key dimensions
5. Save frequently to documents

### For Integration
1. Use layout data for quantity estimation
2. Pass built-up area to cost planner
3. Use floor count for scheduling
4. Export blueprints before construction

---

## Support

For issues or questions:
1. Check error messages in console
2. Verify Ollama is running
3. Check MongoDB connection
4. Review API endpoint responses
5. Check browser compatibility (Chrome/Firefox recommended)
