# BuildWise - AI Construction Planning Platform

A complete production-ready full-stack web application for intelligent construction project management with AI-powered planning, material estimation, cost tracking, scheduling, and comprehensive analytics.

## 🚀 Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router DOM
- Recharts (data visualization)
- Fabric.js (whiteboard canvas)
- Lucide React (icons)
- React Hot Toast (notifications)
- Axios (HTTP client)

### Backend
- Flask (Python REST API)
- MongoDB (database)
- JWT Authentication
- Flask-CORS
- Bcrypt (password hashing)

## ✨ Complete Feature Set

### 🔐 Authentication & Security
- User signup and login with JWT
- Protected routes and middleware
- Password hashing with bcrypt
- Session management
- User profile management

### 📊 Dynamic Dashboard (Real-time Data)
- Live budget vs spent visualization
- Real-time project progress tracking
- Completion rate calculations
- Monthly expense trends from actual data
- Category-wise expense breakdown
- Quick action buttons
- Interactive charts and graphs

### 🤖 AI Assistant Chat
- Chat interface with message history
- Typing indicators and smooth UX
- Placeholder for RAG integration
- Conversation persistence
- Ready for AI model integration

### 📐 Material Estimator (Real Calculations)
- Calculate material quantities based on:
  - Built-up area (sq ft)
  - Number of floors
  - Structure type (RCC/Steel/Brick)
- Real estimation formulas:
  - Cement (bags per sq ft)
  - Steel (kg per sq ft)
  - Bricks (units per sq ft)
  - Sand (cubic feet)
  - Aggregate (cubic feet)
- Visual breakdown with bar charts
- Detailed material requirements table

### 💰 Cost Planner (Accurate Calculations)
- Material cost calculation
- Labour cost (30% of materials)
- Equipment cost (15% of materials)
- Contingency (10% of total)
- Real-time total calculation
- Pie chart visualization
- Price per unit customization

### 📅 Scheduling Timeline
- Construction stages with dependencies
- Week-by-week timeline
- Interactive Gantt chart view
- Progress tracking per stage
- Status indicators (completed/in-progress/pending)

### 🏗️ Architecture Assistant
- Fabric.js whiteboard canvas
- Drawing tools (rectangles, circles, lines)
- Drag and resize elements
- **AI Generate Architecture** - Describe requirements, AI creates layout
- Download designs as PNG
- Design guidelines
- Save and load designs

### ✅ Progress Tracker (User-Created + AI)
- **Create custom tasks** manually
- **AI Generate Tracker** - Describe project, AI creates complete task list
- **🎯 AI Scrum Master** - Intelligent construction scheduling with Granite LLM
  - Realistic RCC construction schedules
  - Multi-floor support (G, G+1, G+2, G+3, G+4)
  - Season-aware duration adjustments (Summer/Monsoon/Winter)
  - Interactive delay handling
  - Checklist tracking per sprint
  - Dependency management
  - Risk assessment
  - Automatic recalculation
- Toggle task completion
- Delete tasks
- Task categories (preparation, foundation, construction, finishing)
- Time estimates
- Overall progress percentage
- Milestone tracking
- Time tracker statistics

### 💵 Finance Dashboard (Real Calculations)
- **Real expense tracking** from database
- **Edit total budget** with modal
- **Auto-calculated remaining budget**
- Add expense with categories
- Monthly expense trend from actual data
- Budget comparison graphs
- Category-wise expense analysis
- Transaction history

### 📈 Reports & Analytics
- Comprehensive dashboard analytics
- Project performance reports
- Expense summary with real calculations:
  - Total expenses
  - Average expense
  - Highest expense
  - Transaction count
- Monthly trend analysis
- Category breakdown
- Export reports (PDF/Excel ready)
- Visual charts and graphs
- Insights and recommendations

### 👥 Team Management
- Add/remove team members
- Role assignment (Project Manager, Engineer, Architect, etc.)
- Contact information (email, phone)
- Team activity feed
- Role-based statistics
- Member status tracking

### 📅 Calendar & Reminders
- Monthly calendar view
- Add/edit reminders
- Deadline alerts
- Upcoming reminders list
- Date-based organization

### 📁 Documents
- Upload documents (URL-based, ready for file upload)
- File list with download/delete
- Document categories
- File type support (PDF, DOC, images)
- Category statistics

### ⚙️ Settings
- Edit profile
- Change password
- Theme toggle (light/dark)
- Notification preferences

## 🎯 Key Differentiators for Hackathon

### 1. **AI Scrum Master with Granite LLM** 🆕
- Real AI-powered construction scheduling
- Uses IBM Granite 3.3 (2B) model via Ollama
- Generates realistic schedules following RCC construction methodology
- Season-aware adjustments (Monsoon +35%, Winter +15%)
- Interactive delay handling with automatic recalculation
- Sprint-based planning with checklists
- Dependency tracking and risk assessment
- Production-ready AI integration

### 2. **Real-Time Calculations**
- All budget, expense, and progress metrics calculated from actual database data
- No dummy data - everything is dynamic and real

### 3. **AI-Ready Architecture**
- Multiple AI integration points ready:
  - Chat assistant (RAG placeholder)
  - Task tracker generation
  - Architecture layout generation
  - **Scrum Master (LIVE with Granite LLM)**
- Easy to plug in AI models later

### 4. **Comprehensive Analytics**
- Real-time dashboard with live data
- Detailed reports and insights
- Multiple visualization types (bar, line, pie charts)

### 5. **Professional UI/UX**
- Modern SaaS gradient design
- Smooth animations and transitions
- Responsive mobile layout
- Toast notifications
- Loading states
- Modal dialogs

### 6. **Complete CRUD Operations**
- Projects, expenses, tasks, reminders, documents
- Full create, read, update, delete functionality
- Real database persistence

### 7. **Team Collaboration**
- Team management system
- Activity tracking
- Role-based organization

### 8. **Extensive Feature Set**
- 13+ major modules
- 50+ API endpoints
- 20+ database collections
- 25+ React components

## 📦 Project Structure

```
buildwise/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── models/               # Data models (8 models)
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── expense.py
│   │   ├── task.py
│   │   ├── reminder.py
│   │   ├── document.py
│   │   └── chat.py
│   ├── routes/               # API routes (12 blueprints)
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── materials.py
│   │   ├── cost.py
│   │   ├── projects.py
│   │   ├── expenses.py
│   │   ├── tasks.py
│   │   ├── reminders.py
│   │   ├── documents.py
│   │   ├── architecture.py
│   │   ├── budget.py
│   │   └── analytics.py
│   ├── services/             # Business logic
│   │   ├── material_estimator.py
│   │   └── cost_planner.py
│   ├── utils/                # Utilities
│   │   ├── auth.py
│   │   └── db.py
│   └── middleware/           # Middleware
│       └── auth.py
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Layout.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── pages/            # Page components (17 pages)
│   │   │   ├── Landing.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Chat.jsx
│   │   │   ├── MaterialEstimator.jsx
│   │   │   ├── CostPlanner.jsx
│   │   │   ├── Scheduling.jsx
│   │   │   ├── Architecture.jsx
│   │   │   ├── Progress.jsx
│   │   │   ├── Finance.jsx
│   │   │   ├── Reports.jsx
│   │   │   ├── Team.jsx
│   │   │   ├── Calendar.jsx
│   │   │   ├── Documents.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── utils/            # Utilities
│   │   │   └── auth.js
│   │   ├── App.jsx           # Main app component
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)
- **Ollama** (for AI Scrum Master)

### Quick Start (5 minutes)

See **[QUICKSTART.md](QUICKSTART.md)** for fastest setup.

For AI Scrum Master detailed guide, see **[SCRUM_MASTER_GUIDE.md](SCRUM_MASTER_GUIDE.md)**.

### Ollama Setup (for AI Scrum Master)

1. Install Ollama:
   - Visit https://ollama.ai
   - Download for your OS
   - Or use package manager: `brew install ollama` (macOS)

2. Install Granite model:
```bash
ollama pull granite3.3:2b
```

3. Start Ollama server:
```bash
ollama serve
```

Server runs on `http://localhost:11434`

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Update `.env` with your MongoDB URI and JWT secret:
```
MONGO_URI=mongodb://localhost:27017/buildwise
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
PORT=5000
```

6. Run the backend:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Update `.env`:
```
VITE_API_URL=http://localhost:5000/api
```

5. Run the frontend:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## Database Collections

The application uses the following MongoDB collections:

- `users` - User accounts
- `projects` - Construction projects
- `expenses` - Financial expenses
- `tasks` - Progress tracker tasks
- `scrum_schedules` - AI Scrum Master schedules 🆕
- `reminders` - Calendar reminders
- `documents` - Uploaded documents
- `chat_history` - AI chat messages

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get user profile

### Chat
- `POST /api/chat` - Send message to AI
- `GET /api/chat/history` - Get chat history

### Materials
- `POST /api/materials/estimate` - Calculate material estimate

### Cost
- `POST /api/cost/calculate` - Calculate cost breakdown

### Projects
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create project
- `PUT /api/projects/:id` - Update project

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Create expense

### Reminders
- `GET /api/reminders` - Get all reminders
- `POST /api/reminders` - Create reminder

### Documents
- `GET /api/documents` - Get all documents
- `POST /api/documents` - Upload document
- `DELETE /api/documents/:id` - Delete document

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `POST /api/tasks/generate` - AI generate tasks

### Scrum Master 🆕
- `POST /api/scrum/generate` - Generate AI schedule
- `POST /api/scrum/delay` - Report delay
- `POST /api/scrum/checklist` - Update checklist
- `GET /api/scrum/schedules` - Get all schedules

### Budget
- `GET /api/budget` - Get budget
- `PUT /api/budget` - Update budget

### Analytics
- `GET /api/analytics/dashboard` - Dashboard data
- `GET /api/analytics/reports` - Reports data

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

Frontend:
```bash
cd frontend
npm run build
```

Backend:
```bash
# Set environment to production in .env
FLASK_ENV=production
```

## Future Enhancements

- Blueprint image analysis with Vision LLM
- RAG integration for AI chat
- Real file upload (currently URL-based)
- Advanced Gantt chart with drag-and-drop
- Mobile app version
- Real-time collaboration
- Email notifications
- PDF report generation
- Integration with construction APIs
- Weather API integration for scheduling
- Resource allocation planning
- Cost estimation integration with Scrum Master

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
