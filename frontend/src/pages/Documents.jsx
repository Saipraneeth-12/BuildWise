import { useState, useEffect } from 'react'
import { Upload, FileText, Download, Trash2, Image as ImageIcon, Ruler } from 'lucide-react'
import { documents } from '../services/api'
import toast from 'react-hot-toast'

const Documents = () => {
  const [documentList, setDocumentList] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    type: 'pdf',
    url: '',
    size: 0
  })
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [showViewModal, setShowViewModal] = useState(false)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const response = await documents.getAll()
      setDocumentList(response.data.documents)
    } catch (error) {
      toast.error('Failed to load documents')
    }
  }

  const blueprints = documentList.filter(doc => doc.type === 'blueprint')
  const manualDrawings = documentList.filter(doc => doc.type === 'manual_drawing')
  const regularDocs = documentList.filter(doc => doc.type !== 'blueprint' && doc.type !== 'manual_drawing')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await documents.upload(formData)
      toast.success('Document uploaded!')
      setShowModal(false)
      setFormData({ name: '', type: 'pdf', url: '', size: 0 })
      loadDocuments()
    } catch (error) {
      toast.error('Failed to upload document')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this document?')) {
      try {
        await documents.delete(id)
        toast.success('Document deleted')
        loadDocuments()
      } catch (error) {
        toast.error('Failed to delete document')
      }
    }
  }

  const getFileIcon = (type) => {
    if (type === 'blueprint') return <Ruler className="text-purple-600" size={24} />
    if (type === 'manual_drawing') return <ImageIcon className="text-green-600" size={24} />
    return <FileText className="text-blue-600" size={24} />
  }

  const viewDocument = (doc) => {
    setSelectedDoc(doc)
    setShowViewModal(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Documents</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Upload size={20} />
          Upload Document
        </button>
      </div>

      {/* AI Generated Blueprints Section */}
      {blueprints.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Ruler className="text-purple-600" />
            AI Generated Blueprints
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {blueprints.map((doc) => (
              <div key={doc._id} className="p-4 border border-purple-200 rounded-lg hover:shadow-md transition-shadow bg-purple-50">
                <div className="aspect-video bg-white rounded mb-3 overflow-hidden cursor-pointer"
                     onClick={() => viewDocument(doc)}>
                  <img src={doc.blueprint_image} alt={doc.name} className="w-full h-full object-contain" />
                </div>
                <div className="flex items-start gap-3">
                  {getFileIcon(doc.type)}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 truncate">{doc.name}</h3>
                    <p className="text-xs text-gray-600 truncate">{doc.prompt}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {doc.layout?.total_built_up_area} m² • {doc.layout?.floors?.length} floor(s)
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => viewDocument(doc)}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm"
                  >
                    <ImageIcon size={16} />
                    View
                  </button>
                  <button
                    onClick={() => handleDelete(doc._id)}
                    className="flex items-center justify-center px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manual Drawings Section */}
      {manualDrawings.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <ImageIcon className="text-green-600" />
            Manual Drawings
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {manualDrawings.map((doc) => (
              <div key={doc._id} className="p-4 border border-green-200 rounded-lg hover:shadow-md transition-shadow bg-green-50">
                <div className="aspect-video bg-white rounded mb-3 overflow-hidden cursor-pointer"
                     onClick={() => viewDocument(doc)}>
                  <img src={doc.image_data} alt={doc.name} className="w-full h-full object-contain" />
                </div>
                <div className="flex items-start gap-3">
                  {getFileIcon(doc.type)}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 truncate">{doc.name}</h3>
                    <p className="text-xs text-gray-500">{(doc.size / 1024).toFixed(2)} KB</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => viewDocument(doc)}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm"
                  >
                    <ImageIcon size={16} />
                    View
                  </button>
                  <button
                    onClick={() => handleDelete(doc._id)}
                    className="flex items-center justify-center px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Regular Documents Section */}
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">All Documents</h2>
        {regularDocs.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {regularDocs.map((doc) => (
              <div key={doc._id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  {getFileIcon(doc.type)}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800 truncate">{doc.name}</h3>
                    <p className="text-sm text-gray-600">{doc.type.toUpperCase()}</p>
                    <p className="text-xs text-gray-500">{(doc.size / 1024).toFixed(2)} KB</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => window.open(doc.url, '_blank')}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm"
                  >
                    <Download size={16} />
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(doc._id)}
                    className="flex items-center justify-center px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-500">No documents uploaded yet</p>
          </div>
        )}
      </div>

      {/* Document View Modal */}
      {showViewModal && selectedDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold">{selectedDoc.name}</h2>
                {selectedDoc.type === 'blueprint' && (
                  <p className="text-sm text-gray-600 mt-1">{selectedDoc.prompt}</p>
                )}
              </div>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {selectedDoc.type === 'blueprint' && (
              <div>
                <img src={selectedDoc.blueprint_image} alt={selectedDoc.name} className="w-full h-auto mb-4" />
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">Layout Details</h3>
                    <p className="text-sm">Configuration: {selectedDoc.metadata?.configuration}</p>
                    <p className="text-sm">Built-up Area: {selectedDoc.layout?.total_built_up_area} m²</p>
                    <p className="text-sm">Floors: {selectedDoc.layout?.floors?.length}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-semibold mb-2">Recommendations</h3>
                    <p className="text-xs">{selectedDoc.metadata?.ventilation_notes}</p>
                    <p className="text-xs mt-1">{selectedDoc.metadata?.lighting_notes}</p>
                  </div>
                </div>
              </div>
            )}

            {selectedDoc.type === 'manual_drawing' && (
              <div>
                <img src={selectedDoc.image_data} alt={selectedDoc.name} className="w-full h-auto" />
              </div>
            )}

            <div className="flex gap-3 mt-4">
              <button
                onClick={() => {
                  const link = document.createElement('a')
                  link.download = `${selectedDoc.name}.png`
                  link.href = selectedDoc.blueprint_image || selectedDoc.image_data
                  link.click()
                }}
                className="flex-1 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Download
              </button>
              <button
                onClick={() => setShowViewModal(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Document Categories</h2>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg text-center">
            <FileText className="mx-auto text-blue-600 mb-2" size={32} />
            <p className="font-semibold text-gray-800">Contracts</p>
            <p className="text-sm text-gray-600">3 files</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg text-center">
            <FileText className="mx-auto text-purple-600 mb-2" size={32} />
            <p className="font-semibold text-gray-800">Plans</p>
            <p className="text-sm text-gray-600">5 files</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg text-center">
            <FileText className="mx-auto text-green-600 mb-2" size={32} />
            <p className="font-semibold text-gray-800">Permits</p>
            <p className="text-sm text-gray-600">2 files</p>
          </div>
          <div className="p-4 bg-pink-50 rounded-lg text-center">
            <FileText className="mx-auto text-pink-600 mb-2" size={32} />
            <p className="font-semibold text-gray-800">Reports</p>
            <p className="text-sm text-gray-600">4 files</p>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Upload Document</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="pdf">PDF</option>
                  <option value="doc">DOC</option>
                  <option value="image">Image</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">URL</label>
                <input
                  type="url"
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/document.pdf"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Size (KB)</label>
                <input
                  type="number"
                  required
                  value={formData.size}
                  onChange={(e) => setFormData({ ...formData, size: parseFloat(e.target.value) })}
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
                  Upload
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Documents
