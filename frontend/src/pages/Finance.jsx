import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Plus, DollarSign, Edit } from 'lucide-react'
import { expenses, budget } from '../services/api'
import toast from 'react-hot-toast'

const Finance = () => {
  const [expenseList, setExpenseList] = useState([])
  const [budgetData, setBudgetData] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [showBudgetModal, setShowBudgetModal] = useState(false)
  const [trendView, setTrendView] = useState('monthly') // daily, weekly, monthly
  const [formData, setFormData] = useState({
    category: 'materials',
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [budgetAmount, setBudgetAmount] = useState('')

  useEffect(() => {
    loadExpenses()
    loadBudget()
  }, [])

  const loadExpenses = async () => {
    try {
      const response = await expenses.getAll()
      setExpenseList(response.data.expenses)
    } catch (error) {
      toast.error('Failed to load expenses')
    }
  }

  const loadBudget = async () => {
    try {
      const response = await budget.get()
      setBudgetData(response.data.budget)
      setBudgetAmount(response.data.budget.total_budget)
    } catch (error) {
      console.error('Failed to load budget')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await expenses.create(formData)
      toast.success('Expense added!')
      setShowModal(false)
      setFormData({ category: 'materials', amount: '', description: '', date: new Date().toISOString().split('T')[0] })
      loadExpenses()
      loadBudget() // Reload to update remaining budget
    } catch (error) {
      toast.error('Failed to add expense')
    }
  }

  const handleBudgetUpdate = async (e) => {
    e.preventDefault()
    try {
      await budget.update({ total_budget: parseFloat(budgetAmount) })
      toast.success('Budget updated!')
      setShowBudgetModal(false)
      loadBudget()
    } catch (error) {
      toast.error('Failed to update budget')
    }
  }

  const totalExpenses = expenseList.reduce((sum, exp) => {
    const amount = parseFloat(exp.amount) || 0
    return sum + amount
  }, 0)
  const totalBudget = budgetData ? parseFloat(budgetData.total_budget) || 0 : 0
  const budgetRemaining = totalBudget - totalExpenses
  
  // Calculate trend data based on selected view
  const getChartData = () => {
    const data = {}
    
    expenseList.forEach(exp => {
      // Use the expense date field (user-selected date) instead of created_at
      const date = new Date(exp.date || exp.created_at)
      const amount = parseFloat(exp.amount) || 0
      let key
      
      if (trendView === 'daily') {
        // Format: "Feb 21" with full date for sorting
        const dateStr = date.toISOString().split('T')[0] // "2026-02-21"
        key = dateStr
      } else if (trendView === 'weekly') {
        // Get week number and year
        const startOfYear = new Date(date.getFullYear(), 0, 1)
        const days = Math.floor((date - startOfYear) / (24 * 60 * 60 * 1000))
        const weekNum = Math.ceil((days + startOfYear.getDay() + 1) / 7)
        const year = date.getFullYear()
        key = `${year}-W${weekNum}` // For sorting
      } else {
        // Monthly: "2026-02" for sorting
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        key = `${year}-${month}`
      }
      
      data[key] = (data[key] || 0) + amount
    })
    
    // Convert to array
    let chartData = Object.entries(data).map(([period, expenses]) => ({
      period,
      expenses,
      sortKey: period
    }))
    
    // Sort by date
    chartData.sort((a, b) => a.sortKey.localeCompare(b.sortKey))
    
    // For daily view, fill in missing dates
    if (trendView === 'daily' && chartData.length > 0) {
      const filledData = []
      const startDate = new Date(chartData[0].sortKey)
      const endDate = new Date(chartData[chartData.length - 1].sortKey)
      
      // Create a map for quick lookup
      const dataMap = {}
      chartData.forEach(item => {
        dataMap[item.sortKey] = item.expenses
      })
      
      // Fill in all dates
      for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        const dateStr = d.toISOString().split('T')[0]
        const displayDate = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        filledData.push({
          period: displayDate,
          expenses: dataMap[dateStr] || 0,
          sortKey: dateStr
        })
      }
      
      chartData = filledData
    } else {
      // Format period labels for display
      chartData = chartData.map(item => {
        let displayPeriod = item.period
        
        if (trendView === 'weekly') {
          // Extract week number from "2026-W8" format
          const weekNum = item.period.split('-W')[1]
          displayPeriod = `Week ${weekNum}`
        } else if (trendView === 'monthly') {
          // Convert "2026-02" to "Feb 2026"
          const [year, month] = item.period.split('-')
          const date = new Date(year, parseInt(month) - 1)
          displayPeriod = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
        }
        
        return {
          period: displayPeriod,
          expenses: item.expenses
        }
      })
    }
    
    // Limit data points based on view
    if (trendView === 'daily') {
      chartData = chartData.slice(-30) // Last 30 days
    } else if (trendView === 'weekly') {
      chartData = chartData.slice(-12) // Last 12 weeks
    } else {
      chartData = chartData.slice(-6) // Last 6 months
    }
    
    return chartData
  }
  
  const chartData = getChartData()

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Finance Dashboard</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Plus size={20} />
          Add Expense
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <DollarSign className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-800">₹{totalExpenses.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <DollarSign className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-gray-600 text-sm">Budget Remaining</p>
                <p className="text-2xl font-bold text-gray-800">₹{budgetRemaining.toLocaleString()}</p>
              </div>
            </div>
            <button
              onClick={() => setShowBudgetModal(true)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Edit Budget"
            >
              <Edit className="text-gray-600" size={20} />
            </button>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total Budget</p>
              <p className="text-2xl font-bold text-gray-800">
                ₹{budgetData ? budgetData.total_budget.toLocaleString() : '0'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Expense Trend</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setTrendView('daily')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                trendView === 'daily'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Daily
            </button>
            <button
              onClick={() => setTrendView('weekly')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                trendView === 'weekly'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Weekly
            </button>
            <button
              onClick={() => setTrendView('monthly')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                trendView === 'monthly'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Monthly
            </button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip 
              formatter={(value) => [`₹${value.toLocaleString()}`, 'Expenses']}
              labelFormatter={(label) => `${label}`}
            />
            <Line type="monotone" dataKey="expenses" stroke="#8b5cf6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
        <p className="text-sm text-gray-500 mt-2 text-center">
          {trendView === 'daily' && 'Showing last 30 days'}
          {trendView === 'weekly' && 'Showing last 12 weeks'}
          {trendView === 'monthly' && 'Showing last 6 months'}
        </p>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Recent Expenses</h2>
        <div className="space-y-3">
          {expenseList.length > 0 ? (
            expenseList.map((expense) => (
              <div key={expense._id} className="flex justify-between items-center p-4 border border-gray-200 rounded-lg">
                <div>
                  <h3 className="font-semibold text-gray-800">{expense.description}</h3>
                  <p className="text-sm text-gray-600">{expense.category} • {expense.date}</p>
                </div>
                <span className="text-lg font-bold text-blue-600">₹{parseFloat(expense.amount).toLocaleString()}</span>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No expenses yet</p>
          )}
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Add Expense</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="materials">Materials</option>
                  <option value="labour">Labour</option>
                  <option value="equipment">Equipment</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amount (₹)</label>
                <input
                  type="number"
                  required
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <input
                  type="text"
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <input
                  type="date"
                  required
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg"
                >
                  Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Budget Edit Modal */}
      {showBudgetModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Update Total Budget</h2>
            <form onSubmit={handleBudgetUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Total Budget (₹)</label>
                <input
                  type="number"
                  required
                  value={budgetAmount}
                  onChange={(e) => setBudgetAmount(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter total budget"
                />
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800">
                  Current expenses: ₹{totalExpenses.toLocaleString()}<br />
                  New remaining: ₹{(parseFloat(budgetAmount || 0) - totalExpenses).toLocaleString()}
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowBudgetModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg"
                >
                  Update Budget
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Finance
