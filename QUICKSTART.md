# BuildWise AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Ollama & Granite LLM (2 minutes)

**Windows:**
```powershell
# Download and install from https://ollama.ai
# Then run:
ollama pull granite3.3:2b
ollama serve
```

**macOS:**
```bash
brew install ollama
ollama pull granite3.3:2b
ollama serve
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama pull granite3.3:2b
ollama serve
```

### Step 2: Start Backend (1 minute)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend will run on `http://localhost:5000`

### Step 3: Start Frontend (1 minute)

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

### Step 4: Test AI Scrum Master (1 minute)

1. Open browser: `http://localhost:3000`
2. Sign up / Login
3. Navigate to **Progress Tracker**
4. Click **AI Scrum Master** button
5. Fill in:
   - Prompt: "RCC residential building"
   - Floors: "G+2"
   - Season: "Monsoon"
6. Click **Generate Schedule**
7. Wait 10-30 seconds
8. See your realistic construction schedule!

## ✅ Verify Everything Works

Run the test suite:
```bash
python test_scrum_master.py
```

Expected output:
```
✓ Granite LLM is accessible!
✓ Schedule generated successfully!
✓ Delay handling works!
✓ Checklist update works!
```

## 🎯 Key Features to Try

### 1. Generate Schedule
- Try different floor counts (G, G+1, G+2, G+3, G+4)
- Try different seasons (Summer, Monsoon, Winter)
- See how duration changes with season

### 2. Report Delay
- Click "Report Delay" button
- Select a task
- Enter delay days
- Watch AI recalculate everything

### 3. Track Checklist
- Click checkboxes in sprint cards
- See status change to "Ready for next"
- All changes save automatically

### 4. View AI Response
- Expand "View AI Granite LLM Response"
- See the raw AI reasoning
- Understand how schedule was generated

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Check if running
ps aux | grep ollama

# Start it
ollama serve
```

### Backend Not Starting
```bash
# Check MongoDB connection in backend/.env
MONGODB_URI=mongodb://localhost:27017/buildwise

# Or use MongoDB Atlas (cloud)
```

### Frontend Not Loading
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Should return: {"status":"healthy"}
```

## 📚 Next Steps

- Read full guide: `SCRUM_MASTER_GUIDE.md`
- Explore other features:
  - Material Estimator
  - Cost Planner
  - Finance Tracker
  - Architecture Generator
  - Reports & Analytics

## 🎉 You're Ready!

The AI Scrum Master is now fully functional and ready to generate realistic construction schedules with:
- ✅ Proper RCC construction sequence
- ✅ Season-aware duration adjustments
- ✅ Multi-floor support (up to G+4)
- ✅ Interactive delay handling
- ✅ Checklist tracking
- ✅ Dependency management
- ✅ Risk assessment
- ✅ Granite LLM reasoning

Happy building! 🏗️
