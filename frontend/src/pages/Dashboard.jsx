import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { TrendingUp, DollarSign, Clock, CheckCircle } from 'lucide-react'
import { projects, expenses, tasks } from '../services/api'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [projectList, setProjectList] = useState([])
  const [expenseList, setExpenseList] = useState([])
  const [taskList, setTaskList] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [projectsRes, expensesRes, tasksRes] = await Promise.all([
        projects.getAll().catch(() => ({ data: { projects: [] } })),
        expenses.getAll().catch(() => ({ data: { expenses: [] } })),
        tasks.getAll().catch(() => ({ data: { tasks: [] } }))
      ])
      
      setProjectList(projectsRes.data.projects || [])
      setExpenseList(expensesRes.data.expenses || [])
      setTaskList(tasksRes.data.tasks || [])
    } catch (error) {
      console.error('Failed to load dashboard data', error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate metrics
  const totalBudget = projectList.reduce((sum, p) => {
    const budget = parseFloat(p.budget) || 0
    return sum + budget
  }, 0)
  const totalSpent = expenseList.reduce((sum, e) => {
    const amount = parseFloat(e.amount) || 0
    return sum + amount
  }, 0)
  const activeProjects = projectList.filter(p => p.status === 'active').length
  const completedTasks = taskList.filter(t => t.completed).length
  const completionRate = taskList.length > 0 ? Math.round((completedTasks / taskList.length) * 100) : 0

  // Monthly trend
  const monthlyData = {}
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  months.forEach(m => monthlyData[m] = 0)
  
  expenseList.forEach(exp => {
    const date = new Date(exp.created_at || Date.now())
    const month = date.toLocaleDateString('en-US', { month: 'short' })
    const amount = parseFloat(exp.amount) || 0
    if (monthlyData[month] !== undefined) {
      monthlyData[month] += amount
    }
  })

  const monthlyTrend = months.map(month => ({
    month,
    amount: monthlyData[month]
  }))

  // Category breakdown
  const categoryData = {}
  expenseList.forEach(exp => {
    const cat = exp.category || 'other'
    const amount = parseFloat(exp.amount) || 0
    categoryData[cat] = (categoryData[cat] || 0) + amount
  })

  const categoryBreakdown = Object.entries(categoryData).map(([category, amount]) => ({
    category,
    amount
  }))

  const stats = [
    { icon: DollarSign, label: 'Total Budget', value: `₹${totalBudget.toLocaleString()}`, color: 'blue' },
    { icon: TrendingUp, label: 'Total Spent', value: `₹${totalSpent.toLocaleString()}`, color: 'green' },
    { icon: Clock, label: 'Active Projects', value: activeProjects, color: 'purple' },
    { icon: CheckCircle, label: 'Completion Rate', value: `${completionRate}%`, color: 'pink' }
  ]

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>

      <div className="grid md:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center mb-4`}>
              <stat.icon className={`text-${stat.color}-600`} size={24} />
            </div>
            <p className="text-gray-600 text-sm">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Monthly Expense Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="amount" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Expense by Category</h2>
          {categoryBreakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="amount"
                >
                  {categoryBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              No expense data yet
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Budget Overview</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Budget Utilization</span>
                <span className="font-semibold">
                  {totalBudget > 0 ? ((totalSpent / totalBudget) * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full"
                  style={{ 
                    width: `${totalBudget > 0 ? Math.min((totalSpent / totalBudget) * 100, 100) : 0}%` 
                  }}
                />
              </div>
            </div>
            <div className="pt-4 border-t">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Remaining</span>
                <span className="text-green-600 font-bold">₹{(totalBudget - totalSpent).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Project Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="text-gray-700">Total Projects</span>
              <span className="text-2xl font-bold text-blue-600">{projectList.length}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="text-gray-700">Active</span>
              <span className="text-2xl font-bold text-green-600">{activeProjects}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
              <span className="text-gray-700">Completed</span>
              <span className="text-2xl font-bold text-purple-600">
                {projectList.filter(p => p.status === 'completed').length}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Task Progress</h2>
          <div className="text-center">
            <div className="relative inline-flex items-center justify-center w-32 h-32 mb-4">
              <svg className="transform -rotate-90 w-32 h-32">
                <circle cx="64" cy="64" r="56" stroke="#e5e7eb" strokeWidth="8" fill="none" />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="url(#gradient)"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 56}`}
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - completionRate / 100)}`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
              </svg>
              <span className="absolute text-2xl font-bold text-gray-800">{completionRate}%</span>
            </div>
            <p className="text-gray-600">
              {completedTasks} of {taskList.length} tasks completed
            </p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-xl shadow-lg text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Quick Actions</h2>
            <p className="opacity-90">Manage your construction projects efficiently</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => window.location.href = '/app/materials'}
              className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:shadow-lg transition-all font-semibold"
            >
              Estimate Materials
            </button>
            <button
              onClick={() => window.location.href = '/app/chat'}
              className="px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-all font-semibold"
            >
              Ask AI Assistant
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
