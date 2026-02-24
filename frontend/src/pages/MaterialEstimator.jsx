import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { Calculator, Sparkles, Users, Clock, DollarSign, Package } from 'lucide-react'
import axios from 'axios'
import toast from 'react-hot-toast'

const MaterialEstimator = () => {
  const [mode, setMode] = useState('manual') // 'manual', 'ai', or 'blueprint'
  const [formData, setFormData] = useState({
    area: '',
    floors: 2,
    wage: 500,
    steel_type: 'Fe500',
    cement_type: 'OPC 53',
    location: 'India'
  })
  const [aiPrompt, setAiPrompt] = useState('')
  const [blueprintImages, setBlueprintImages] = useState([])
  const [blueprintParams, setBlueprintParams] = useState({
    wage: 500,
    steel_type: 'Fe500',
    cement_type: 'OPC 53',
    location: 'India'
  })
  const [estimate, setEstimate] = useState(null)
  const [loading, setLoading] = useState(false)
  const [extractedParams, setExtractedParams] = useState(null)
  const [extractionDetails, setExtractionDetails] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

  const handleManualEstimate = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_URL}/estimate`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setEstimate(response.data.estimate)
      setExtractedParams(null)
      toast.success('Estimate calculated successfully!')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to calculate estimate')
    } finally {
      setLoading(false)
    }
  }

  const handleAIEstimate = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${API_URL}/ai-estimate`,
        { prompt: aiPrompt },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setEstimate(response.data.estimate)
      setExtractedParams(response.data.extracted_parameters)
      toast.success('AI estimate generated successfully!')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate AI estimate')
    } finally {
      setLoading(false)
    }
  }

  const handleBlueprintEstimate = async (e) => {
    e.preventDefault()
    
    if (blueprintImages.length === 0) {
      toast.error('Please upload at least one blueprint image')
      return
    }
    
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const formDataObj = new FormData()
      
      // Append all images
      blueprintImages.forEach((file) => {
        formDataObj.append('images', file)
      })
      
      // Append parameters
      formDataObj.append('wage', blueprintParams.wage)
      formDataObj.append('steel_type', blueprintParams.steel_type)
      formDataObj.append('cement_type', blueprintParams.cement_type)
      formDataObj.append('location', blueprintParams.location)
      
      const response = await axios.post(
        `${API_URL}/blueprint-estimate`,
        formDataObj,
        { 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          } 
        }
      )
      
      setEstimate(response.data.estimate)
      setExtractionDetails(response.data.extraction_details)
      setExtractedParams(null)
      toast.success('Blueprint estimate generated successfully!')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to process blueprint images')
    } finally {
      setLoading(false)
    }
  }

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files)
    setBlueprintImages(files)
    toast.success(`${files.length} image(s) uploaded`)
  }

  const removeImage = (index) => {
    const newImages = blueprintImages.filter((_, i) => i !== index)
    setBlueprintImages(newImages)
  }

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#ef4444']

  const materialChartData = estimate ? [
    { name: 'Cement', value: estimate.cement_bags, unit: 'bags' },
    { name: 'Steel', value: estimate.steel_tons, unit: 'tons' },
    { name: 'Bricks', value: estimate.bricks / 1000, unit: 'k units' },
    { name: 'Sand', value: estimate.sand_cft, unit: 'cft' },
    { name: 'Aggregate', value: estimate.aggregate_cft, unit: 'cft' }
  ] : []

  const workerChartData = estimate ? [
    { name: 'Masons', value: estimate.masons },
    { name: 'Helpers', value: estimate.helpers },
    { name: 'Carpenters', value: estimate.carpenters },
    { name: 'Supervisors', value: estimate.supervisors }
  ] : []

  const costChartData = estimate ? [
    { name: 'Labour', value: estimate.labour_cost },
    { name: 'Material', value: estimate.material_cost }
  ] : []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Construction Estimator</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setMode('manual')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              mode === 'manual'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Calculator size={20} />
            Manual
          </button>
          <button
            onClick={() => setMode('ai')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              mode === 'ai'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Sparkles size={20} />
            AI Estimator
          </button>
          <button
            onClick={() => setMode('blueprint')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              mode === 'blueprint'
                ? 'bg-gradient-to-r from-green-600 to-teal-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Package size={20} />
            Blueprint
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">
            {mode === 'manual' ? 'Project Details' : mode === 'ai' ? 'AI Prompt' : 'Blueprint Images'}
          </h2>

          {mode === 'manual' ? (
            <form onSubmit={handleManualEstimate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Built-up Area (sqft per floor)
                </label>
                <input
                  type="number"
                  required
                  value={formData.area}
                  onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Floors (G+1 = 2, G+2 = 3)
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  value={formData.floors}
                  onChange={(e) => setFormData({ ...formData, floors: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Steel Type
                </label>
                <select
                  value={formData.steel_type}
                  onChange={(e) => setFormData({ ...formData, steel_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Fe415">Fe415 (₹58,000/ton)</option>
                  <option value="Fe500">Fe500 (₹62,000/ton)</option>
                  <option value="Fe550">Fe550 (₹65,000/ton)</option>
                  <option value="TMT Premium">TMT Premium (₹68,000/ton)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cement Type
                </label>
                <select
                  value={formData.cement_type}
                  onChange={(e) => setFormData({ ...formData, cement_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="OPC 43">OPC 43 (₹350/bag)</option>
                  <option value="OPC 53">OPC 53 (₹400/bag)</option>
                  <option value="PPC">PPC (₹380/bag)</option>
                  <option value="PSC">PSC (₹360/bag)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Daily Wage per Worker (₹)
                </label>
                <input
                  type="number"
                  required
                  value={formData.wage}
                  onChange={(e) => setFormData({ ...formData, wage: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="India"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Estimate'}
              </button>
            </form>
          ) : mode === 'ai' ? (
            <form onSubmit={handleAIEstimate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe Your Project
                </label>
                <textarea
                  required
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows="6"
                  placeholder="Example: Build G+2 residential building of 1500 sqft using Fe500 steel and OPC 53 cement with wage 500"
                />
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <p className="text-sm text-purple-800">
                  <strong>AI will extract:</strong> Area, Floors, Steel Type, Cement Type, Wage, Location
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Sparkles size={20} />
                {loading ? 'Generating...' : 'AI Generate Estimate'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleBlueprintEstimate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Blueprint Images (one per floor)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Upload one image per floor. System will extract dimensions from each image.
                </p>
              </div>

              {blueprintImages.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <p className="text-sm font-semibold text-green-800 mb-2">
                    Uploaded Images ({blueprintImages.length} floor{blueprintImages.length > 1 ? 's' : ''}):
                  </p>
                  <div className="space-y-1">
                    {blueprintImages.map((file, index) => (
                      <div key={index} className="flex justify-between items-center text-sm text-green-700">
                        <span>Floor {index + 1}: {file.name}</span>
                        <button
                          type="button"
                          onClick={() => removeImage(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Steel Type
                </label>
                <select
                  value={blueprintParams.steel_type}
                  onChange={(e) => setBlueprintParams({ ...blueprintParams, steel_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="Fe415">Fe415 (₹58,000/ton)</option>
                  <option value="Fe500">Fe500 (₹62,000/ton)</option>
                  <option value="Fe550">Fe550 (₹65,000/ton)</option>
                  <option value="TMT Premium">TMT Premium (₹68,000/ton)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cement Type
                </label>
                <select
                  value={blueprintParams.cement_type}
                  onChange={(e) => setBlueprintParams({ ...blueprintParams, cement_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="OPC 43">OPC 43 (₹350/bag)</option>
                  <option value="OPC 53">OPC 53 (₹400/bag)</option>
                  <option value="PPC">PPC (₹380/bag)</option>
                  <option value="PSC">PSC (₹360/bag)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Daily Wage per Worker (₹)
                </label>
                <input
                  type="number"
                  required
                  value={blueprintParams.wage}
                  onChange={(e) => setBlueprintParams({ ...blueprintParams, wage: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={blueprintParams.location}
                  onChange={(e) => setBlueprintParams({ ...blueprintParams, location: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="India"
                />
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm text-green-800">
                  <strong>System will extract:</strong> Room dimensions from images using OCR/Vision AI
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || blueprintImages.length === 0}
                className="w-full py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Package size={20} />
                {loading ? 'Processing Images...' : 'Estimate from Blueprint'}
              </button>
            </form>
          )}

          {extractedParams && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm font-semibold text-green-800 mb-2">AI Extracted Parameters:</p>
              <div className="text-sm text-green-700 space-y-1">
                <p>• Area: {extractedParams.area} sqft</p>
                <p>• Floors: {extractedParams.floors}</p>
                <p>• Steel Type: {extractedParams.steel_type || 'Fe500'}</p>
                <p>• Cement Type: {extractedParams.cement_type || 'OPC 53'}</p>
                <p>• Wage: ₹{extractedParams.wage}/day</p>
                <p>• Location: {extractedParams.location || 'India'}</p>
              </div>
            </div>
          )}

          {extractionDetails && (
            <div className="mt-4 p-4 bg-teal-50 border border-teal-200 rounded-lg">
              <p className="text-sm font-semibold text-teal-800 mb-2">Blueprint Extraction Results:</p>
              <div className="text-sm text-teal-700 space-y-2">
                <p>• Total Floors: {extractionDetails.floors}</p>
                <p>• Total Area: {extractionDetails.total_area_sqft} sqft</p>
                <p>• Steel Type: {blueprintParams.steel_type}</p>
                <p>• Cement Type: {blueprintParams.cement_type}</p>
                {extractionDetails.dimensions_extracted && extractionDetails.dimensions_extracted.map((floor, idx) => (
                  <div key={idx} className="ml-4 mt-2">
                    <p className="font-semibold">Floor {floor.floor}: {floor.area_sqft} sqft</p>
                    {floor.dimensions && floor.dimensions.length > 0 && (
                      <p className="text-xs ml-2">
                        Rooms: {floor.dimensions.map(d => `${d.length}×${d.width}`).join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Quick Summary */}
        {estimate && (
          <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-6 rounded-xl shadow-lg text-white">
            <h2 className="text-xl font-semibold mb-4">Project Summary</h2>
            <div className="space-y-4">
              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="text-white" size={24} />
                  <span className="font-semibold">Timeline</span>
                </div>
                <p className="text-2xl font-bold">{estimate.timeline_months} months</p>
                <p className="text-sm opacity-90">{estimate.timeline_days} days / {estimate.timeline_weeks} weeks</p>
              </div>

              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <Users className="text-white" size={24} />
                  <span className="font-semibold">Total Workers</span>
                </div>
                <p className="text-2xl font-bold">{estimate.total_workers}</p>
                <p className="text-sm opacity-90">
                  {estimate.masons} masons, {estimate.helpers} helpers, {estimate.carpenters} carpenters
                </p>
              </div>

              <div className="bg-white/20 backdrop-blur-sm p-4 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  <DollarSign className="text-white" size={24} />
                  <span className="font-semibold">Total Cost</span>
                </div>
                <p className="text-2xl font-bold">₹{estimate.total_cost.toLocaleString()}</p>
                <p className="text-sm opacity-90">
                  Labour: ₹{estimate.labour_cost.toLocaleString()} | Material: ₹{estimate.material_cost.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {estimate && (
        <>
          {/* Workers & Labor */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Users className="text-blue-600" size={24} />
              Workers & Labor
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={workerChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium">Masons</span>
                  <span className="text-blue-600 font-semibold">{estimate.masons}</span>
                </div>
                <div className="flex justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="font-medium">Helpers</span>
                  <span className="text-purple-600 font-semibold">{estimate.helpers}</span>
                </div>
                <div className="flex justify-between p-3 bg-pink-50 rounded-lg">
                  <span className="font-medium">Carpenters</span>
                  <span className="text-pink-600 font-semibold">{estimate.carpenters}</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium">Supervisors</span>
                  <span className="text-green-600 font-semibold">{estimate.supervisors}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Clock className="text-purple-600" size={24} />
              Timeline
            </h2>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Days</p>
                <p className="text-3xl font-bold text-blue-600">{estimate.timeline_days}</p>
              </div>
              <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Weeks</p>
                <p className="text-3xl font-bold text-purple-600">{estimate.timeline_weeks}</p>
              </div>
              <div className="p-4 bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Months</p>
                <p className="text-3xl font-bold text-pink-600">{estimate.timeline_months}</p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <strong>Productivity Rate:</strong> 250 sqft/day | 
                <strong> Total Area:</strong> {estimate.total_sqft} sqft
              </p>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="text-green-600" size={24} />
              Cost Breakdown
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={costChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {costChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3">
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Labour Cost</p>
                  <p className="text-2xl font-bold text-green-600">₹{estimate.labour_cost.toLocaleString()}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {estimate.total_workers} workers × ₹{estimate.wage_per_day}/day × {estimate.timeline_days} days
                  </p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Material Cost</p>
                  <p className="text-2xl font-bold text-blue-600">₹{estimate.material_cost.toLocaleString()}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {estimate.area_sqyards} sq yards × {estimate.floors} floors × ₹{estimate.cost_per_sqyard}
                  </p>
                </div>
                <div className="p-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg">
                  <p className="text-sm opacity-90 mb-1">Total Project Cost</p>
                  <p className="text-3xl font-bold">₹{estimate.total_cost.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Materials Required */}
          <div className="bg-white p-6 rounded-xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Package className="text-orange-600" size={24} />
              Materials Required
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={materialChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium">Cement ({estimate.cement_type})</span>
                  <span className="text-blue-600 font-semibold">{estimate.cement_bags} bags</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium">Cement Cost</span>
                  <span className="text-green-600 font-semibold">₹{estimate.cement_cost.toLocaleString()} @ ₹{estimate.cement_price_per_bag}/bag</span>
                </div>
                <div className="flex justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="font-medium">Steel ({estimate.steel_type})</span>
                  <span className="text-purple-600 font-semibold">{estimate.steel_tons} tons ({estimate.steel_kg} kg)</span>
                </div>
                <div className="flex justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium">Steel Cost</span>
                  <span className="text-blue-600 font-semibold">₹{estimate.steel_cost.toLocaleString()} @ ₹{estimate.steel_price_per_ton.toLocaleString()}/ton</span>
                </div>
                <div className="flex justify-between p-3 bg-pink-50 rounded-lg">
                  <span className="font-medium">Bricks</span>
                  <span className="text-pink-600 font-semibold">{estimate.bricks.toLocaleString()} units</span>
                </div>
                <div className="flex justify-between p-3 bg-green-50 rounded-lg">
                  <span className="font-medium">Sand</span>
                  <span className="text-green-600 font-semibold">{estimate.sand_cft} cft</span>
                </div>
                <div className="flex justify-between p-3 bg-yellow-50 rounded-lg">
                  <span className="font-medium">Aggregate</span>
                  <span className="text-yellow-600 font-semibold">{estimate.aggregate_cft} cft</span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MaterialEstimator
