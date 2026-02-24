import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import MaterialEstimator from './pages/MaterialEstimator'
import CostPlanner from './pages/CostPlanner'
import Scheduling from './pages/Scheduling'
import Architecture from './pages/Architecture'
import Progress from './pages/Progress'
import Finance from './pages/Finance'
import Reports from './pages/Reports'
import Team from './pages/Team'
import Calendar from './pages/Calendar'
import Documents from './pages/Documents'
import MaterialPrices from './pages/MaterialPrices'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="materials" element={<MaterialEstimator />} />
          <Route path="cost" element={<CostPlanner />} />
          <Route path="scheduling" element={<Scheduling />} />
          <Route path="architecture" element={<Architecture />} />
          <Route path="progress" element={<Progress />} />
          <Route path="finance" element={<Finance />} />
          <Route path="reports" element={<Reports />} />
          <Route path="team" element={<Team />} />
          <Route path="calendar" element={<Calendar />} />
          <Route path="documents" element={<Documents />} />
          <Route path="material-prices" element={<MaterialPrices />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
