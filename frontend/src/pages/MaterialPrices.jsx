import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Minus, RefreshCw, Download, Filter, Calendar } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const MaterialPrices = () => {
  const [summary, setSummary] = useState(null)
  const [prices, setPrices] = useState([])
  const [history, setHistory] = useState([])
  const [trends, setTrends] = useState(null)
  const [filters, setFilters] = useState({
    material: 'Cement',
    type: 'OPC 53',
    state: 'Maharashtra',
    location: 'Mumbai',
    days: 30
  })
  const [filterOptions, setFilterOptions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

  useEffect(() => {
    fetchFilterOptions()
    fetchSummary()
    fetchTrends()
    fetchLivePrices()
    fetchHistory()
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [filters])

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(`${API_URL}/materials/filters`)
      setFilterOptions(response.data)
    } catch (error) {
      console.error('Error fetching filter options:', error)
    }
  }

  const fetchSummary = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/materials/summary`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setSummary(response.data.summary)
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  const fetchTrends = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/materials/trends`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTrends(response.data.trends)
    } catch (error) {
      console.error('Error fetching trends:', error)
    }
  }


  const fetchLivePrices = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/materials/live`, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          material: filters.material,
          type: filters.type,
          state: filters.state,
          location: filters.location
        }
      })
      setPrices(response.data.prices)
    } catch (error) {
      toast.error('Failed to fetch live prices')
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_URL}/materials/history`, {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          material: filters.material,
          type: filters.type,
          location: filters.location,
          days: filters.days
        }
      })
      setHistory(response.data.history)
    } catch (error) {
      console.error('Error fetching history:', error)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      const token = localStorage.getItem('token')
      await axios.post(`${API_URL}/materials/refresh`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      toast.success('Prices refreshed successfully!')
      
      // Reload all data
      await Promise.all([
        fetchSummary(),
        fetchTrends(),
        fetchLivePrices(),
        fetchHistory()
      ])
    } catch (error) {
      toast.error('Failed to refresh prices')
    } finally {
      setRefreshing(false)
    }
  }

  const downloadCSV = () => {
    if (prices.length === 0) {
      toast.error('No data to download')
      return
    }

    const headers = ['Material', 'Type', 'Price', 'Unit', 'Location', 'State', 'Date']
    const rows = prices.map(p => [
      p.material,
      p.type,
      p.price,
      p.unit,
      p.location,
      p.state,
      new Date(p.scraped_at).toLocaleDateString()
    ])

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `material-prices-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    toast.success('CSV downloaded!')
  }

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp className="text-red-500" size={20} />
    if (trend === 'down') return <TrendingDown className="text-green-500" size={20} />
    return <Minus className="text-gray-500" size={20} />
  }

  const getTrendColor = (changePercent) => {
    if (changePercent > 0) return 'text-red-600'
    if (changePercent < 0) return 'text-green-600'
    return 'text-gray-600'
  }

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Live Material Rates</h1>
          <p className="text-gray-600 mt-1">Real-time construction material prices across India</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={downloadCSV}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
          >
            <Download size={20} />
            Export CSV
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
          >
            <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh Prices'}
          </button>
        </div>
      </div>


      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Cement Card */}
          {summary.cement && (
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-blue-100 text-sm">Cement Average</p>
                  <p className="text-3xl font-bold mt-1">₹{summary.cement.avg_price}</p>
                  <p className="text-blue-100 text-sm">per {summary.cement.unit}</p>
                </div>
                {getTrendIcon(summary.cement.change_percent > 0 ? 'up' : summary.cement.change_percent < 0 ? 'down' : 'same')}
              </div>
              <div className={`text-sm font-semibold ${summary.cement.change_percent >= 0 ? 'text-red-200' : 'text-green-200'}`}>
                {summary.cement.change_percent > 0 ? '+' : ''}{summary.cement.change_percent}% from yesterday
              </div>
            </div>
          )}

          {/* Steel Card */}
          {summary.steel && (
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-lg text-white">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-purple-100 text-sm">Steel Average</p>
                  <p className="text-3xl font-bold mt-1">₹{summary.steel.avg_price.toLocaleString()}</p>
                  <p className="text-purple-100 text-sm">per {summary.steel.unit}</p>
                </div>
                {getTrendIcon(summary.steel.change_percent > 0 ? 'up' : summary.steel.change_percent < 0 ? 'down' : 'same')}
              </div>
              <div className={`text-sm font-semibold ${summary.steel.change_percent >= 0 ? 'text-red-200' : 'text-green-200'}`}>
                {summary.steel.change_percent > 0 ? '+' : ''}{summary.steel.change_percent}% from yesterday
              </div>
            </div>
          )}

          {/* Sand Card */}
          {summary.sand && (
            <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-green-100 text-sm">Sand Average</p>
                  <p className="text-3xl font-bold mt-1">₹{summary.sand.avg_price}</p>
                  <p className="text-green-100 text-sm">per {summary.sand.unit}</p>
                </div>
                {getTrendIcon('same')}
              </div>
              <div className="text-sm font-semibold text-green-100">
                Stable pricing
              </div>
            </div>
          )}

          {/* Aggregates Card */}
          {summary.aggregates && (
            <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-lg text-white">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-orange-100 text-sm">Aggregates Average</p>
                  <p className="text-3xl font-bold mt-1">₹{summary.aggregates.avg_price}</p>
                  <p className="text-orange-100 text-sm">per {summary.aggregates.unit}</p>
                </div>
                {getTrendIcon('same')}
              </div>
              <div className="text-sm font-semibold text-orange-100">
                Stable pricing
              </div>
            </div>
          )}
        </div>
      )}


      {/* Filters */}
      {filterOptions && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="text-blue-600" size={24} />
            <h2 className="text-xl font-semibold">Filters</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Material</label>
              <select
                value={filters.material}
                onChange={(e) => {
                  setFilters({ ...filters, material: e.target.value, type: filterOptions.types[e.target.value][0] })
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {filterOptions.materials.map(mat => (
                  <option key={mat} value={mat}>{mat}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {filterOptions.types[filters.material]?.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
              <select
                value={filters.state}
                onChange={(e) => {
                  setFilters({ ...filters, state: e.target.value, location: filterOptions.locations[e.target.value][0] })
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {filterOptions.states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
              <select
                value={filters.location}
                onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {filterOptions.locations[filters.state]?.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Period</label>
              <select
                value={filters.days}
                onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Price Trend Chart */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Calendar className="text-blue-600" size={24} />
          Price Trend - {filters.material} ({filters.type})
        </h2>
        {history.length > 0 ? (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fontSize: 12 }}
                interval={Math.floor(history.length / 6)}
              />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Legend />
              <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} name="Price" dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>No historical data available</p>
            <p className="text-sm mt-2">Data will be generated automatically on first request</p>
          </div>
        )}
      </div>


      {/* Material Comparison */}
      {trends && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Material Price Comparison</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={Object.entries(trends).map(([key, value]) => ({
              name: key,
              price: value.current_avg,
              change: value.change_percent
            }))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `₹${value}`} />
              <Legend />
              <Bar dataKey="price" fill="#3b82f6" name="Average Price" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Live Prices Table */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Live Prices - {filters.location}, {filters.state}</h2>
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading prices...</p>
          </div>
        ) : prices.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Material</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Type</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Price</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-700">Unit</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-700">Trend</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Source</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Updated</th>
                </tr>
              </thead>
              <tbody>
                {prices.map((price, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{price.material}</td>
                    <td className="py-3 px-4 text-gray-600">{price.type}</td>
                    <td className="py-3 px-4 text-right font-semibold text-blue-600">
                      ₹{price.price.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-center text-gray-600">{price.unit}</td>
                    <td className="py-3 px-4 text-center">
                      {getTrendIcon(price.trend)}
                    </td>
                    <td className="py-3 px-4 text-gray-600 text-sm">{price.source}</td>
                    <td className="py-3 px-4 text-gray-600 text-sm">
                      {new Date(price.scraped_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No prices available for selected filters
          </div>
        )}
      </div>

      {/* Price Alerts Info */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 p-6 rounded-xl">
        <h3 className="font-semibold text-yellow-800 mb-2">📊 Price Intelligence</h3>
        <p className="text-yellow-700 text-sm">
          Prices are updated automatically every day at 6:00 AM. Significant price changes (&gt;5%) are logged for alerts.
          Historical data is maintained for 90 days for trend analysis.
        </p>
      </div>
    </div>
  )
}

export default MaterialPrices
