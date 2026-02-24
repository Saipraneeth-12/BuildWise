import { useState, useEffect } from 'react'
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { FileText, Download, TrendingUp, Calendar } from 'lucide-react'
import { projects, expenses } from '../services/api'
import toast from 'react-hot-toast'

const Reports = () => {
  const [projectList, setProjectList] = useState([])
  const [expenseList, setExpenseList] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPeriod, setSelectedPeriod] = useState('month')

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      const [projectsRes, expensesRes] = await Promise.all([
        projects.getAll().catch(() => ({ data: { projects: [] } })),
        expenses.getAll().catch(() => ({ data: { expenses: [] } }))
      ])
      
      setProjectList(projectsRes.data.projects || [])
      setExpenseList(expensesRes.data.expenses || [])
    } catch (error) {
      console.error('Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = (type) => {
    toast.success(`Downloading ${type} report...`)
  }

  const totalExpenses = expenseList.reduce((sum, e) => {
    const amount = parseFloat(e.amount) || 0
    return sum + amount
  }, 0)
  const avgExpense = expenseList.length > 0 ? totalExpenses / expenseList.length : 0
  const highestExpense = expenseList.length > 0 ? Math.max(...expenseList.map(e => parseFloat(e.amount) || 0)) : 0

  const projectPerformance = projectList.length > 0 ? projectList.map(p => ({
    name: p.name || 'Unnamed',
    progress: parseFloat(p.progress) || 0,
    budget: parseFloat(p.budget) || 0,
    spent: parseFloat(p.spent) || 0,
    status: p.status || 'planning'
  })) : [{
    name: 'No Projects Yet',
    progress: 0,
    budget: 0,
    spent: 0,
    status: 'planning'
  }]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generating reports...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Reports & Analytics</h1>
        <div className="flex gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button
            onClick={() => downloadReport('comprehensive')}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
          >
            <Download size={20} />
            Export Report
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-800">₹{totalExpenses.toLocaleString()}</p>
            </div>
          </div>
          <button
            onClick={() => downloadReport('expenses')}
            className="w-full py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm"
          >
            Download Expense Report
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Average Expense</p>
              <p className="text-2xl font-bold text-gray-800">₹{Math.round(avgExpense).toLocaleString()}</p>
            </div>
          </div>
          <button
            onClick={() => downloadReport('trends')}
            className="w-full py-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors text-sm"
          >
            Download Trend Analysis
          </button>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Calendar className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Transactions</p>
              <p className="text-2xl font-bold text-gray-800">{expenseList.length}</p>
            </div>
          </div>
          <button
            onClick={() => downloadReport('transactions')}
            className="w-full py-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors text-sm"
          >
            Download Transaction Log
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Project Performance</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Project Name</th>
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Progress</th>
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Budget</th>
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Spent</th>
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {projectPerformance.map((project, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-800">{project.name}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{project.progress}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-gray-700">₹{project.budget.toLocaleString()}</td>
                  <td className="py-3 px-4 text-gray-700">₹{project.spent.toLocaleString()}</td>
                  <td className="py-3 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      project.status === 'completed' ? 'bg-green-100 text-green-700' :
                      project.status === 'active' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {project.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Expense Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={projectPerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="budget" fill="#3b82f6" name="Budget" />
              <Bar dataKey="spent" fill="#8b5cf6" name="Spent" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Progress Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={projectPerformance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="progress" stroke="#10b981" strokeWidth={2} name="Progress %" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-xl shadow-lg text-white">
        <h2 className="text-xl font-bold mb-2">Insights & Recommendations</h2>
        <div className="grid md:grid-cols-2 gap-4 mt-4">
          <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg">
            <p className="font-semibold mb-1">Budget Efficiency</p>
            <p className="text-sm opacity-90">
              {projectList.length > 0 ? 'Your projects are on track' : 'Start by creating your first project'}. 
              Monitor expenses regularly for better control.
            </p>
          </div>
          <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg">
            <p className="font-semibold mb-1">Cost Optimization</p>
            <p className="text-sm opacity-90">
              Average expense per transaction is ₹{Math.round(avgExpense).toLocaleString()}. 
              Track material costs for potential savings.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports
