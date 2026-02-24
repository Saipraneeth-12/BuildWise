# BuildWise AI - Deployment Checklist

## ✅ Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] MongoDB running (local or cloud)
- [ ] Ollama installed (for AI Scrum Master)
- [ ] Granite 3.3 model downloaded

### Environment Setup

#### Backend
- [ ] `backend/.env` file created
- [ ] MongoDB URI configured
- [ ] JWT secret key set
- [ ] Flask environment set (development/production)
- [ ] Port configured (default: 5000)

#### Frontend
- [ ] `frontend/.env` file created
- [ ] API URL configured (default: http://localhost:5000/api)
- [ ] Build settings verified

### Dependencies

#### Backend
- [ ] Virtual environment created
- [ ] `pip install -r requirements.txt` completed
- [ ] All packages installed successfully
- [ ] No dependency conflicts

#### Frontend
- [ ] `npm install` completed
- [ ] All packages installed successfully
- [ ] No vulnerability warnings (or resolved)

### Database

- [ ] MongoDB connection tested
- [ ] Database created: `buildwise`
- [ ] Collections auto-created on first use
- [ ] Indexes created (if any)

### AI Services

- [ ] Ollama server running (`ollama serve`)
- [ ] Granite model available (`ollama list`)
- [ ] Test connection: `curl http://localhost:11434/api/generate`
- [ ] Model responds correctly

## 🚀 Deployment Steps

### Step 1: Start Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start MongoDB (if local)
mongod

# Terminal 3: Start Backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py

# Terminal 4: Start Frontend
cd frontend
npm run dev
```

### Step 2: Verify Services

- [ ] Ollama: http://localhost:11434 (responds)
- [ ] MongoDB: Connection successful
- [ ] Backend: http://localhost:5000/api/health (returns {"status":"healthy"})
- [ ] Frontend: http://localhost:3000 (loads)

### Step 3: Test Core Features

#### Authentication
- [ ] Signup works
- [ ] Login works
- [ ] JWT token stored
- [ ] Protected routes work
- [ ] Logout works

#### Dashboard
- [ ] Loads without errors
- [ ] Shows real data (or empty state)
- [ ] Charts render correctly
- [ ] Quick actions work

#### Material Estimator
- [ ] Form accepts input
- [ ] Calculations are correct
- [ ] Results display properly
- [ ] Charts render

#### Cost Planner
- [ ] Form accepts input
- [ ] Calculations are correct
- [ ] Pie chart renders
- [ ] Total cost accurate

#### Progress Tracker
- [ ] Task list loads
- [ ] Add task works
- [ ] Toggle completion works
- [ ] Delete task works
- [ ] AI Generate Tracker modal opens

#### AI Scrum Master ⭐
- [ ] Modal opens
- [ ] Form accepts input
- [ ] Generate button works
- [ ] Schedule generates (10-30 sec)
- [ ] Schedule displays correctly
- [ ] Project summary shows
- [ ] Sprints display
- [ ] Checklists are interactive
- [ ] Report Delay works
- [ ] Checklist toggle works
- [ ] Granite response visible

#### Finance
- [ ] Expense list loads
- [ ] Add expense works
- [ ] Budget edit works
- [ ] Remaining budget calculates
- [ ] Charts render

#### Reports
- [ ] Dashboard loads
- [ ] Real data displays
- [ ] Charts render
- [ ] Export buttons present

#### Team
- [ ] Team list loads
- [ ] Add member works
- [ ] Activity feed shows

#### Other Features
- [ ] Calendar works
- [ ] Documents work
- [ ] Settings work
- [ ] Architecture canvas works

## 🧪 Testing Checklist

### Unit Tests
- [ ] Backend: `pytest` (if tests exist)
- [ ] Frontend: `npm test` (if tests exist)
- [ ] Scrum Master: `python test_scrum_master.py`

### Integration Tests
- [ ] API endpoints respond correctly
- [ ] Database operations work
- [ ] Authentication flow works
- [ ] AI integration works

### User Acceptance Tests
- [ ] Complete user flow works
- [ ] No console errors
- [ ] No network errors
- [ ] Toast notifications work
- [ ] Loading states work
- [ ] Error handling works

## 🐛 Troubleshooting

### Common Issues

#### Ollama Not Responding
```bash
# Check if running
ps aux | grep ollama

# Restart
pkill ollama
ollama serve
```

#### MongoDB Connection Failed
```bash
# Check if running
ps aux | grep mongod

# Start MongoDB
mongod --dbpath /path/to/data
```

#### Backend Port Already in Use
```bash
# Find process
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process or change port in .env
```

#### Frontend Build Errors
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Or
npm cache clean --force
npm install
```

#### Scrum Master Not Working
1. Check Ollama is running
2. Check Granite model is installed
3. Check backend logs for errors
4. Check browser console for errors
5. Run test suite: `python test_scrum_master.py`

## 📊 Performance Checklist

### Backend
- [ ] Response times < 1s (except AI)
- [ ] Database queries optimized
- [ ] No memory leaks
- [ ] Error handling in place
- [ ] Logging configured

### Frontend
- [ ] Page load < 3s
- [ ] No unnecessary re-renders
- [ ] Images optimized
- [ ] Code splitting (if needed)
- [ ] Lazy loading (if needed)

### AI Services
- [ ] First generation: 10-30s (acceptable)
- [ ] Subsequent: 5-10s (acceptable)
- [ ] Fallback works if Ollama down
- [ ] Error messages clear

## 🔒 Security Checklist

- [ ] JWT secret is strong and unique
- [ ] Passwords are hashed (bcrypt)
- [ ] CORS configured correctly
- [ ] Environment variables not committed
- [ ] API endpoints protected
- [ ] Input validation in place
- [ ] SQL injection prevented (using MongoDB)
- [ ] XSS prevention in place

## 📝 Documentation Checklist

- [ ] README.md complete
- [ ] QUICKSTART.md available
- [ ] SCRUM_MASTER_GUIDE.md available
- [ ] API documentation clear
- [ ] Code comments present
- [ ] Setup instructions tested
- [ ] Troubleshooting guide available

## 🎯 Hackathon Presentation Checklist

### Demo Preparation
- [ ] All services running
- [ ] Test account created
- [ ] Sample data loaded
- [ ] Demo script prepared
- [ ] Backup plan ready

### Key Features to Showcase
1. [ ] AI Scrum Master (star feature!)
   - Generate realistic schedule
   - Show season adjustments
   - Demonstrate delay handling
   - Show checklist tracking
   
2. [ ] Real-time Dashboard
   - Show live calculations
   - Demonstrate charts
   
3. [ ] Material Estimator
   - Quick calculation demo
   
4. [ ] Finance Tracking
   - Show budget management
   - Real expense tracking
   
5. [ ] Team Management
   - Show collaboration features

### Talking Points
- [ ] Real AI integration (not mock)
- [ ] Production-ready code
- [ ] Comprehensive feature set
- [ ] Real-time calculations
- [ ] Professional UI/UX
- [ ] Scalable architecture
- [ ] Industry-standard practices

## ✨ Final Checks

- [ ] All features working
- [ ] No console errors
- [ ] No network errors
- [ ] Performance acceptable
- [ ] UI/UX polished
- [ ] Documentation complete
- [ ] Code clean and commented
- [ ] Git repository organized
- [ ] Demo ready
- [ ] Presentation prepared

## 🎉 Ready to Deploy!

Once all checkboxes are checked, you're ready to:
1. Present at hackathon
2. Deploy to production
3. Share with users
4. Win the competition! 🏆

---

**Last Updated**: After fixing Scrum Master output issue
**Status**: ✅ All systems operational
**Confidence Level**: 💯 Production Ready
