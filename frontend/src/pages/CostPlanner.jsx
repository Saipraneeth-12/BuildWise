import { useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { cost } from '../services/api'
import toast from 'react-hot-toast'

const CostPlanner = () => {
  const [materials, setMaterials] = useState({
    cement: 0,
    steel: 0,
    bricks: 0,
    sand: 0,
    aggregate: 0
  })
  const [prices, setPrices] = useState({
    cement: 400,
    steel: 60,
    bricks: 8,
    sand: 50,
    aggregate: 45
  })
  const [costBreakdown, setCostBreakdown] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await cost.calculate({ materials, prices })
      setCostBreakdown(response.data.cost)
      toast.success('Cost calculated!')
    } catch (error) {
      toast.error('Failed to calculate cost')
    } finally {
      setLoading(false)
    }
  }

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981']

  const chartData = costBreakdown ? [
    { name: 'Materials', value: costBreakdown.material_cost },
    { name: 'Labour', value: costBreakdown.labour_cost },
    { name: 'Equipment', value: costBreakdown.equipment_cost },
    { name: 'Contingency', value: costBreakdown.contingency }
  ] : []

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Cost Planner</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Material Quantities</h2>
          <form onSubmit={handleCalculate} className="space-y-4">
            {Object.keys(materials).map((material) => (
              <div key={material}>
                <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                  {material}
                </label>
                <input
                  type="number"
                  value={materials[material]}
                  onChange={(e) => setMaterials({ ...materials, [material]: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                />
              </div>
            ))}

            <h2 className="text-xl font-semibold mt-6 mb-4">Price per Unit</h2>
            {Object.keys(prices).map((material) => (
              <div key={material}>
                <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                  {material} (₹)
                </label>
                <input
                  type="number"
                  value={prices[material]}
                  onChange={(e) => setPrices({ ...prices, [material]: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate Total Cost'}
            </button>
          </form>
        </div>

        {costBreakdown && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h2 className="text-xl font-semibold mb-4">Cost Breakdown</h2>
              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium">Material Cost</span>
                  <span className="text-blue-600 font-semibold">₹{costBreakdown.material_cost}</span>
                </div>
                <div className="flex justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="font-medium">Labour Cost</span>
                  <span className="text-purple-600 font-semibold">₹{costBreakdown.labour_cost}</span>
                </div>
                <div className="flex justify-between p-3 bg-pink-50 rounded-lg">
                  <span className="font-medium">Equipment Cost</span>
                  <span className="text-pink-600 font-semibold">₹{costBreakdown.equipment_cost}</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium">Contingency</span>
                  <span className="text-green-600 font-semibold">₹{costBreakdown.contingency}</span>
                </div>
                <div className="flex justify-between p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg mt-4">
                  <span className="font-bold text-lg">Total Cost</span>
                  <span className="font-bold text-lg">₹{costBreakdown.total}</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h2 className="text-xl font-semibold mb-4">Visual Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CostPlanner
