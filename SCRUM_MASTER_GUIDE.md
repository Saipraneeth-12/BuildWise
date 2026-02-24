# BuildWise AI Scrum Master Guide

## Overview

The BuildWise AI Scrum Master is an intelligent construction scheduling system that generates realistic, season-aware construction schedules using IBM Granite LLM (granite3.3:2b). It follows proper RCC (Reinforced Cement Concrete) construction methodology and provides interactive schedule management.

## Features

### 1. Realistic Construction Scheduling
- Follows standard RCC construction sequence
- Multi-floor support (G, G+1, G+2, G+3, G+4)
- Season-aware duration adjustments
- Proper task dependencies
- Detailed checklists per phase

### 2. Season Adjustments
- **Summer**: Normal duration (1.0x multiplier)
- **Monsoon**: +35% duration increase (1.35x multiplier)
  - Extended curing times
  - Rain delay considerations
  - Excavation challenges
- **Winter**: +15% duration increase (1.15x multiplier)
  - Cold weather impact
  - Shorter working hours
  - Extended concrete setting time

### 3. Construction Phases

#### Phase 1: Pre-construction (2 weeks)
- Site clearing
- Layout marking
- Soil testing

#### Phase 2: Foundation (4 weeks)
- Excavation
- PCC (Plain Cement Concrete)
- Footing reinforcement
- Footing concrete casting

#### Phase 3: Structure (6 weeks per floor)
- Column casting
- Beam casting
- Slab casting
- Curing (28 days normal, adjusted for season)

#### Phase 4: Brickwork (8 weeks)
- Brickwork all floors
- Internal wall construction

#### Phase 5: Finishing (8 weeks)
- Plastering
- Flooring
- Electrical installation
- Plumbing installation

#### Phase 6: Final (4 weeks)
- Painting
- Fixture installation
- Final inspection

### 4. Interactive Features

#### Delay Handling
- Report delays for any task
- Automatic recalculation of dependent tasks
- Updated completion dates
- Visual delay indicators

#### Checklist Tracking
- Task-specific checklists
- Toggle completion status
- Automatic sprint status updates
- "Ready for next" status when all items complete

#### Sprint Status
- **Pending**: Not started
- **Delayed**: Behind schedule
- **Ready for next**: All checklists complete

## Setup Instructions

### Prerequisites

1. **Install Ollama**
   ```bash
   # Visit https://ollama.ai and download for your OS
   # Or use package manager:
   # macOS: brew install ollama
   # Linux: curl https://ollama.ai/install.sh | sh
   ```

2. **Install Granite Model**
   ```bash
   ollama pull granite3.3:2b
   ```

3. **Start Ollama Server**
   ```bash
   ollama serve
   ```
   The server will run on `http://localhost:11434`

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection string
   ```

3. **Start Backend**
   ```bash
   python app.py
   ```
   Backend runs on `http://localhost:5000`

### Frontend Setup

1. **Install Node Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:5000/api)
   ```

3. **Start Frontend**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:3000`

## Testing

Run the test suite to verify everything is working:

```bash
python test_scrum_master.py
```

This will test:
- Granite LLM connection
- Schedule generation
- Delay handling
- Checklist updates

## Usage Guide

### Generating a Schedule

1. Navigate to **Progress Tracker** page
2. Click **AI Scrum Master** button
3. Fill in the form:
   - **Project Description**: Describe your construction project
   - **Building Type**: Select floors (G, G+1, G+2, G+3, G+4)
   - **Season**: Select season (Summer, Monsoon, Winter)
4. Click **Generate Schedule**
5. Wait for AI to generate the schedule (10-30 seconds)

### Example Prompts

**Good prompts:**
- "RCC residential building with standard construction"
- "Commercial building with fast-track construction"
- "Multi-story apartment complex with basement parking"
- "Villa construction with modern amenities"

**What the AI considers:**
- Building type (residential, commercial, etc.)
- Construction methodology (RCC, fast-track, etc.)
- Special requirements mentioned in prompt

### Viewing the Schedule

The generated schedule shows:
- **Project Summary**: Duration, floor count, season impact
- **Sprint Cards**: Each phase with:
  - Sprint number and week range
  - Phase name and duration
  - Task list
  - Checklist items (interactive)
  - Dependencies
  - Risks
  - Status indicator

### Reporting Delays

1. Click **Report Delay** button
2. Select the delayed task from dropdown
3. Enter delay in days
4. Click **Report Delay**
5. AI automatically:
   - Marks task as delayed
   - Shifts all dependent tasks
   - Recalculates completion date
   - Updates project summary

### Managing Checklists

1. Find the sprint/phase in the schedule
2. Click checkboxes next to checklist items
3. Status updates automatically:
   - Checked items show as complete (strikethrough)
   - When all items complete, sprint status → "Ready for next"
4. Changes save immediately to database

## Architecture

### Backend Components

**`backend/services/advanced_scrum_master.py`**
- Main AI Scrum Master logic
- Granite LLM integration
- Schedule generation algorithms
- Delay handling
- Checklist management

**`backend/routes/scrum.py`**
- API endpoints for Scrum operations
- Database operations
- Authentication

### Frontend Components

**`frontend/src/pages/Progress.jsx`**
- Main Progress Tracker UI
- Scrum schedule display
- Interactive modals
- Checklist toggles
- Delay reporting

**`frontend/src/services/api.js`**
- API client methods
- Scrum endpoints

### Database Schema

**Collection: `scrum_schedules`**
```javascript
{
  _id: ObjectId,
  user_id: String,
  prompt: String,
  floors: String,
  season: String,
  schedule: {
    project_summary: {
      project_type: String,
      building_height: String,
      floor_count: Number,
      season: String,
      sprint_duration: String,
      adjusted_slab_cycle: String,
      season_impact: String,
      total_weeks: Number,
      total_months: Number,
      estimated_completion: String
    },
    sprints: [{
      sprint: String,
      weeks: String,
      phase: String,
      tasks: [String],
      duration: String,
      checklist: [String],
      checklist_status: {
        [item]: Boolean
      },
      dependencies: [String],
      risks: [String],
      status: String  // 'pending', 'delayed', 'ready_for_next'
    }],
    granite_response: String,
    checklist_summary: Object,
    dependencies: String,
    risks: Object,
    next_actions: [String]
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

## API Endpoints

### Generate Schedule
```
POST /api/scrum/generate
Authorization: Bearer <token>

Request:
{
  "prompt": "RCC residential building",
  "floors": "G+2",
  "season": "monsoon"
}

Response:
{
  "message": "Realistic Scrum schedule generated successfully",
  "schedule": { ... }
}
```

### Report Delay
```
POST /api/scrum/delay
Authorization: Bearer <token>

Request:
{
  "schedule_id": "...",
  "task_name": "Foundation - Excavation",
  "delay_days": 7
}

Response:
{
  "message": "Delay handled successfully",
  "schedule": { ... }
}
```

### Update Checklist
```
POST /api/scrum/checklist
Authorization: Bearer <token>

Request:
{
  "schedule_id": "...",
  "task_name": "Pre-construction",
  "checklist_item": "Site cleared",
  "completed": true
}

Response:
{
  "message": "Checklist updated successfully",
  "schedule": { ... }
}
```

### Get Schedules
```
GET /api/scrum/schedules
Authorization: Bearer <token>

Response:
{
  "schedules": [...]
}
```

## Troubleshooting

### Granite LLM Not Accessible

**Error**: "Cannot connect to Ollama at http://localhost:11434"

**Solutions**:
1. Check if Ollama is running: `ps aux | grep ollama`
2. Start Ollama: `ollama serve`
3. Verify model is installed: `ollama list`
4. Pull model if missing: `ollama pull granite3.3:2b`

### Schedule Not Displaying

**Check**:
1. Open browser console (F12)
2. Look for API errors
3. Verify backend is running on port 5000
4. Check MongoDB connection
5. Verify JWT token is valid

**Common fixes**:
- Refresh the page
- Re-login
- Clear browser cache
- Restart backend server

### Slow Schedule Generation

**Normal**: 10-30 seconds for first generation
**Slow**: >60 seconds

**Causes**:
- Granite model loading for first time
- System resources (CPU/RAM)
- Ollama not optimized

**Solutions**:
- Wait for first generation (model loads)
- Subsequent generations will be faster
- Increase system resources
- Use smaller model if needed

### Checklist Not Updating

**Check**:
1. Browser console for errors
2. Network tab for API calls
3. Backend logs for errors

**Common fixes**:
- Verify schedule_id is correct
- Check authentication token
- Restart backend if needed

## Performance Tips

1. **First Generation**: Takes longer (model loading)
2. **Subsequent Generations**: Much faster (model cached)
3. **Concurrent Users**: Ollama handles multiple requests
4. **Resource Usage**: Granite 2B model is lightweight

## Future Enhancements

- [ ] Blueprint image analysis with Vision LLM
- [ ] Gantt chart visualization
- [ ] Export to PDF/Excel
- [ ] Resource allocation planning
- [ ] Cost estimation integration
- [ ] Weather API integration
- [ ] Mobile app support
- [ ] Multi-language support

## Support

For issues or questions:
1. Check this guide first
2. Run test suite: `python test_scrum_master.py`
3. Check backend logs
4. Check browser console
5. Verify all services are running

## Credits

- **AI Model**: IBM Granite 3.3 (2B parameters)
- **LLM Runtime**: Ollama
- **Construction Methodology**: Standard RCC practices
- **Season Data**: Industry-standard adjustments
