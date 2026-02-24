import { useEffect, useRef, useState } from 'react'
import { fabric } from 'fabric'
import { Square, Circle, Minus, Trash2, Download, Sparkles, Type, Ruler, Save, Image as ImageIcon } from 'lucide-react'
import { architecture } from '../services/api'
import toast from 'react-hot-toast'

const Architecture = () => {
  const canvasRef = useRef(null)
  const [canvas, setCanvas] = useState(null)
  const [showAIModal, setShowAIModal] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [blueprints, setBlueprints] = useState([])
  const [selectedBlueprint, setSelectedBlueprint] = useState(null)
  const [showBlueprintModal, setShowBlueprintModal] = useState(false)
  const [measurements, setMeasurements] = useState([])
  const [annotations, setAnnotations] = useState([])
  const [drawingMode, setDrawingMode] = useState('select') // select, line, rect, circle, text, measure

  useEffect(() => {
    const fabricCanvas = new fabric.Canvas(canvasRef.current, {
      width: 1000,
      height: 700,
      backgroundColor: '#ffffff',
      selection: true
    })
    
    // Grid background
    fabricCanvas.setBackgroundColor('#ffffff', fabricCanvas.renderAll.bind(fabricCanvas))
    
    setCanvas(fabricCanvas)
    loadBlueprints()

    return () => {
      fabricCanvas.dispose()
    }
  }, [])

  const loadBlueprints = async () => {
    try {
      const response = await architecture.getBlueprints()
      setBlueprints(response.data.blueprints)
    } catch (error) {
      console.error('Failed to load blueprints')
    }
  }

  const addRectangle = () => {
    if (!canvas) return
    const rect = new fabric.Rect({
      left: 100,
      top: 100,
      fill: 'transparent',
      stroke: '#000000',
      strokeWidth: 2,
      width: 100,
      height: 100
    })
    canvas.add(rect)
    canvas.setActiveObject(rect)
  }

  const addCircle = () => {
    if (!canvas) return
    const circle = new fabric.Circle({
      left: 150,
      top: 150,
      fill: 'transparent',
      stroke: '#000000',
      strokeWidth: 2,
      radius: 50
    })
    canvas.add(circle)
    canvas.setActiveObject(circle)
  }

  const addLine = () => {
    if (!canvas) return
    const line = new fabric.Line([50, 50, 200, 200], {
      stroke: '#000000',
      strokeWidth: 2
    })
    canvas.add(line)
    canvas.setActiveObject(line)
  }

  const addText = () => {
    if (!canvas) return
    const text = new fabric.IText('Text', {
      left: 100,
      top: 100,
      fontSize: 16,
      fill: '#000000',
      fontFamily: 'Arial'
    })
    canvas.add(text)
    canvas.setActiveObject(text)
    text.enterEditing()
  }

  const addMeasurement = () => {
    if (!canvas) return
    toast.info('Click two points to measure distance')
    
    let points = []
    const handleClick = (e) => {
      const pointer = canvas.getPointer(e.e)
      points.push({ x: pointer.x, y: pointer.y })
      
      if (points.length === 2) {
        const distance = Math.sqrt(
          Math.pow(points[1].x - points[0].x, 2) + 
          Math.pow(points[1].y - points[0].y, 2)
        )
        
        // Draw measurement line
        const line = new fabric.Line([points[0].x, points[0].y, points[1].x, points[1].y], {
          stroke: '#ff0000',
          strokeWidth: 1,
          selectable: false
        })
        
        // Add measurement text
        const midX = (points[0].x + points[1].x) / 2
        const midY = (points[0].y + points[1].y) / 2
        const text = new fabric.Text(`${(distance / 10).toFixed(2)}m`, {
          left: midX,
          top: midY - 10,
          fontSize: 12,
          fill: '#ff0000',
          backgroundColor: '#ffffff',
          selectable: false
        })
        
        canvas.add(line)
        canvas.add(text)
        
        setMeasurements([...measurements, { line, text, distance }])
        
        canvas.off('mouse:down', handleClick)
        points = []
      }
    }
    
    canvas.on('mouse:down', handleClick)
  }

  const clearCanvas = () => {
    if (!canvas) return
    canvas.clear()
    canvas.backgroundColor = '#ffffff'
    canvas.renderAll()
    setMeasurements([])
    setAnnotations([])
  }

  const downloadCanvas = () => {
    if (!canvas) return
    const dataURL = canvas.toDataURL({ format: 'png', quality: 1.0 })
    const link = document.createElement('a')
    link.download = 'architecture-design.png'
    link.href = dataURL
    link.click()
  }

  const saveDrawing = async () => {
    if (!canvas) return
    
    const name = prompt('Enter drawing name:')
    if (!name) return
    
    try {
      const canvasData = JSON.stringify(canvas.toJSON())
      const imageData = canvas.toDataURL({ format: 'png', quality: 1.0 })
      
      await architecture.saveDrawing({
        name,
        canvas_data: canvasData,
        image_data: imageData,
        measurements,
        annotations
      })
      
      toast.success('Drawing saved to documents!')
    } catch (error) {
      toast.error('Failed to save drawing')
    }
  }

  const handleAIGenerate = async (e) => {
    e.preventDefault()
    setAiLoading(true)
    try {
      const response = await architecture.generateWithAI({ prompt: aiPrompt })
      const blueprint = response.data.blueprint
      
      toast.success('Blueprint generated successfully!')
      setShowAIModal(false)
      setAiPrompt('')
      
      // Show generated blueprint
      setSelectedBlueprint(blueprint)
      setShowBlueprintModal(true)
      
      // Reload blueprints list
      loadBlueprints()
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to generate blueprint')
    } finally {
      setAiLoading(false)
    }
  }

  const saveBlueprintToDocuments = async (blueprint) => {
    try {
      const name = prompt('Enter document name:', `Blueprint - ${blueprint.metadata.configuration}`)
      if (!name) return
      
      await architecture.saveBlueprintToDocuments({
        name,
        prompt: blueprint.prompt,
        blueprint_image: blueprint.blueprint_image,
        layout: blueprint.layout,
        metadata: blueprint.metadata
      })
      
      toast.success('Blueprint saved to documents!')
    } catch (error) {
      toast.error('Failed to save to documents')
    }
  }

  const deleteBlueprint = async (id) => {
    if (!window.confirm('Delete this blueprint?')) return
    
    try {
      await architecture.deleteBlueprint(id)
      toast.success('Blueprint deleted')
      loadBlueprints()
      if (selectedBlueprint?._id === id) {
        setShowBlueprintModal(false)
        setSelectedBlueprint(null)
      }
    } catch (error) {
      toast.error('Failed to delete blueprint')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Architecture Assistant</h1>
        <button
          onClick={() => setShowAIModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Sparkles size={20} />
          AI Generate Blueprint
        </button>
      </div>

      {/* AI Generated Blueprints Section */}
      {blueprints.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">AI Generated Blueprints</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {blueprints.map((bp) => (
              <div key={bp._id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                   onClick={() => { setSelectedBlueprint(bp); setShowBlueprintModal(true); }}>
                <div className="aspect-video bg-gray-100 rounded mb-3 overflow-hidden">
                  <img src={bp.blueprint_image} alt="Blueprint" className="w-full h-full object-contain" />
                </div>
                <p className="font-semibold text-gray-800 truncate">{bp.metadata.configuration}</p>
                <p className="text-sm text-gray-600 truncate">{bp.prompt}</p>
                <p className="text-xs text-gray-500 mt-2">
                  {bp.layout.total_built_up_area} m² • {bp.layout.floors.length} floor(s)
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Drawing Section */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Drawing Tools</h2>
          <div className="space-y-2">
            <button
              onClick={addRectangle}
              className="w-full flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
            >
              <Square size={18} />
              Rectangle
            </button>
            <button
              onClick={addCircle}
              className="w-full flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm"
            >
              <Circle size={18} />
              Circle
            </button>
            <button
              onClick={addLine}
              className="w-full flex items-center gap-2 px-4 py-2 bg-pink-100 text-pink-700 rounded-lg hover:bg-pink-200 transition-colors text-sm"
            >
              <Minus size={18} />
              Line
            </button>
            <button
              onClick={addText}
              className="w-full flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors text-sm"
            >
              <Type size={18} />
              Add Text
            </button>
            <button
              onClick={addMeasurement}
              className="w-full flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors text-sm"
            >
              <Ruler size={18} />
              Measure
            </button>
            <button
              onClick={saveDrawing}
              className="w-full flex items-center gap-2 px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm"
            >
              <Save size={18} />
              Save Drawing
            </button>
            <button
              onClick={clearCanvas}
              className="w-full flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm"
            >
              <Trash2 size={18} />
              Clear Canvas
            </button>
            <button
              onClick={downloadCanvas}
              className="w-full flex items-center gap-2 px-4 py-2 bg-teal-100 text-teal-700 rounded-lg hover:bg-teal-200 transition-colors text-sm"
            >
              <Download size={18} />
              Download PNG
            </button>
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-3 text-sm">Guidelines</h3>
            <ul className="space-y-2 text-xs text-gray-600">
              <li>• Draw walls using rectangles and lines</li>
              <li>• Add room labels with text tool</li>
              <li>• Use measure tool for dimensions</li>
              <li>• Drag and resize elements freely</li>
              <li>• Save to documents when complete</li>
            </ul>
          </div>
        </div>

        <div className="md:col-span-3 bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Manual Drawing Canvas</h2>
          <div className="border-2 border-gray-200 rounded-lg overflow-hidden bg-white">
            <canvas ref={canvasRef} />
          </div>
          <p className="text-sm text-gray-600 mt-4">
            Click and drag elements to move. Use corner handles to resize. Double-click text to edit.
          </p>
        </div>
      </div>

      {/* AI Generate Modal */}
      {showAIModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="text-purple-600" size={24} />
              <h2 className="text-2xl font-bold">AI Generate Blueprint</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Describe your building requirements using natural language. The AI will generate a detailed architectural blueprint with room layouts and measurements.
            </p>
            <form onSubmit={handleAIGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Architecture Requirements</label>
                <textarea
                  required
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows="5"
                  placeholder="Example: 30x40 ft plot, G+1, 2BHK, internal staircase"
                />
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p className="text-sm text-purple-800 mb-2">
                  <strong>Supported formats:</strong>
                </p>
                <ul className="text-xs text-purple-700 space-y-1">
                  <li>• Plot dimensions: "30x40 ft" or "10x12 m"</li>
                  <li>• Floors: "G+1" (2 floors), "G+2" (3 floors), etc.</li>
                  <li>• Configuration: "1BHK", "2BHK", "3BHK"</li>
                  <li>• Options: "duplex", "internal staircase"</li>
                </ul>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAIModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  disabled={aiLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={aiLoading}
                  className="flex-1 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50"
                >
                  {aiLoading ? 'Generating...' : 'Generate Blueprint'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Blueprint View Modal */}
      {showBlueprintModal && selectedBlueprint && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold">{selectedBlueprint.metadata.configuration} Blueprint</h2>
                <p className="text-sm text-gray-600 mt-1">{selectedBlueprint.prompt}</p>
              </div>
              <button
                onClick={() => setShowBlueprintModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* Blueprint Image */}
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <img 
                src={selectedBlueprint.blueprint_image} 
                alt="Blueprint" 
                className="w-full h-auto"
              />
            </div>

            {/* Layout Details */}
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Plot Details</h3>
                <p className="text-sm text-gray-700">
                  Dimensions: {selectedBlueprint.layout.plot.width_m}m × {selectedBlueprint.layout.plot.length_m}m
                </p>
                <p className="text-sm text-gray-700">
                  Total Built-up: {selectedBlueprint.layout.total_built_up_area} m²
                </p>
                <p className="text-sm text-gray-700">
                  Efficiency: {(selectedBlueprint.layout.efficiency_ratio * 100).toFixed(0)}%
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Recommendations</h3>
                <p className="text-xs text-gray-700">
                  {selectedBlueprint.metadata.ventilation_notes}
                </p>
                <p className="text-xs text-gray-700 mt-1">
                  {selectedBlueprint.metadata.lighting_notes}
                </p>
              </div>
            </div>

            {/* Floor Details */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Floor Layout</h3>
              {selectedBlueprint.layout.floors.map((floor, idx) => (
                <div key={idx} className="bg-gray-50 p-3 rounded-lg mb-2">
                  <p className="font-medium">Floor {floor.floor_number}</p>
                  <p className="text-sm text-gray-600">
                    {floor.rooms.length} rooms • {floor.built_up_area} m²
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                    {floor.rooms.map((room, ridx) => (
                      <div key={ridx} className="text-xs bg-white p-2 rounded">
                        <p className="font-medium">{room.name}</p>
                        <p className="text-gray-600">{room.area} m²</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => saveBlueprintToDocuments(selectedBlueprint)}
                className="flex-1 flex items-center justify-center gap-2 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Save size={18} />
                Save to Documents
              </button>
              <button
                onClick={() => {
                  const link = document.createElement('a')
                  link.download = `blueprint-${selectedBlueprint._id}.png`
                  link.href = selectedBlueprint.blueprint_image
                  link.click()
                }}
                className="flex-1 flex items-center justify-center gap-2 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                <Download size={18} />
                Download Image
              </button>
              <button
                onClick={() => deleteBlueprint(selectedBlueprint._id)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Architecture
