# 🚀 Quick Start Guide - Architecture System

## ✅ Issue Fixed

The Pillow module was not installed in the virtual environment. This has been fixed.

---

## 🏃 Start the System

### Step 1: Start Ollama (Terminal 1)
```bash
ollama serve
```

If Granite model not pulled:
```bash
ollama pull granite3.3:2b
```

### Step 2: Start Backend (Terminal 2)
```bash
cd backend
.\venv\Scripts\python.exe app.py
```

Expected output:
```
* Running on http://127.0.0.1:5000
* Running on http://192.168.0.106:5000
```

### Step 3: Start Frontend (Terminal 3)
```bash
cd frontend
npm run dev
```

Expected output:
```
Local: http://localhost:3000
```

---

## ✅ Backend is Now Running

The backend server is currently running on:
- http://localhost:5000
- http://192.168.0.106:5000

---

## 🧪 Test the Architecture System

### Option 1: Use the Web Interface
1. Open http://localhost:3000 in your browser
2. Login to the application
3. Navigate to "Architecture" page
4. Click "AI Generate Blueprint"
5. Enter: `30x40 ft plot, G+1, 2BHK`
6. Click "Generate Blueprint"
7. Wait 10-15 seconds
8. View the generated blueprint!

### Option 2: Run the Test Script
```bash
python test_architecture.py
```

Expected output:
```
✓ Parsed parameters: 9.00m × 12.00m, 2 floors, 2BHK
✓ Generated layout: 184.32 m², 171% efficiency
✓ Blueprint generated successfully!
```

---

## 🔧 Troubleshooting

### If Backend Fails to Start

#### Check Virtual Environment
```bash
cd backend
.\venv\Scripts\python.exe -c "from PIL import Image; print('OK')"
```

If error, reinstall:
```bash
.\venv\Scripts\python.exe -m pip install Pillow
```

#### Check All Dependencies
```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### If Ollama Not Running

#### Start Ollama
```bash
ollama serve
```

#### Check if Running
```bash
curl http://localhost:11434/api/tags
```

#### Pull Granite Model
```bash
ollama pull granite3.3:2b
```

### If Frontend Fails

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Clear Cache
```bash
npm run dev -- --force
```

---

## 📊 System Status

### ✅ Completed
- [x] Backend dependencies installed (Pillow, requests)
- [x] Backend server running on port 5000
- [x] All routes registered
- [x] Architecture endpoints ready
- [x] Test script passing

### 🔄 Next Steps
1. Start frontend server
2. Test AI blueprint generation
3. Test manual drawing system
4. Verify documents integration

---

## 🎯 Quick Test Commands

### Test Layout Engine
```bash
python -c "from backend.services.deterministic_layout_engine import DeterministicLayoutEngine; engine = DeterministicLayoutEngine(); params = engine.parse_input('30x40 ft plot, G+1, 2BHK'); layout = engine.generate_layout(params); print(f'Built-up: {layout[\"total_built_up_area\"]} m²')"
```

### Test API Endpoint
```bash
curl -X POST http://localhost:5000/api/architecture/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "30x40 ft plot, G+1, 2BHK"}'
```

---

## 📝 Important Notes

### Virtual Environment
Always use the virtual environment Python:
```bash
# Windows
.\venv\Scripts\python.exe

# Not this (global Python)
python
```

### Dependencies Location
Dependencies are installed in:
```
backend/venv/Lib/site-packages/
```

### Port Configuration
- Backend: 5000
- Frontend: 3000
- Ollama: 11434

---

## 🎉 Success Indicators

### Backend Started Successfully
```
✓ * Running on http://127.0.0.1:5000
✓ No import errors
✓ All blueprints registered
```

### Frontend Started Successfully
```
✓ Local: http://localhost:3000
✓ No compilation errors
✓ Ready in X ms
```

### Ollama Running
```
✓ curl http://localhost:11434/api/tags returns JSON
✓ granite3.3:2b model listed
```

---

## 🔗 Quick Links

- Backend: http://localhost:5000
- Frontend: http://localhost:3000
- Architecture Page: http://localhost:3000/architecture
- Documents Page: http://localhost:3000/documents
- API Health: http://localhost:5000/api/health

---

## 📞 Need Help?

### Check Logs
- Backend: Terminal 2 output
- Frontend: Terminal 3 output
- Browser: F12 → Console

### Common Issues
1. **Port already in use**: Kill process on port 5000/3000
2. **Module not found**: Reinstall dependencies in venv
3. **Ollama timeout**: Check if Ollama is running
4. **CORS error**: Check backend CORS configuration

---

## ✅ Current Status

**Backend**: ✅ Running on port 5000
**Dependencies**: ✅ Pillow and requests installed
**Routes**: ✅ Architecture routes registered
**Ready**: ✅ System ready for testing

---

**Next**: Start the frontend and test the Architecture module!
