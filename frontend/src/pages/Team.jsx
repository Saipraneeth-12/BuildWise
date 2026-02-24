import { useState } from 'react'
import { Users, Plus, Mail, Phone, Trash2, Edit } from 'lucide-react'
import toast from 'react-hot-toast'

const Team = () => {
  const [teamMembers, setTeamMembers] = useState([
    { id: 1, name: 'John Doe', role: 'Project Manager', email: 'john@example.com', phone: '+1234567890', status: 'active' },
    { id: 2, name: 'Jane Smith', role: 'Site Engineer', email: 'jane@example.com', phone: '+1234567891', status: 'active' },
    { id: 3, name: 'Mike Johnson', role: 'Architect', email: 'mike@example.com', phone: '+1234567892', status: 'active' }
  ])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    email: '',
    phone: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    const newMember = {
      id: teamMembers.length + 1,
      ...formData,
      status: 'active'
    }
    setTeamMembers([...teamMembers, newMember])
    toast.success('Team member added!')
    setShowModal(false)
    setFormData({ name: '', role: '', email: '', phone: '' })
  }

  const handleDelete = (id) => {
    if (window.confirm('Remove this team member?')) {
      setTeamMembers(teamMembers.filter(m => m.id !== id))
      toast.success('Team member removed')
    }
  }

  const roles = [
    { name: 'Project Manager', count: 1, color: 'blue' },
    { name: 'Site Engineer', count: 1, color: 'green' },
    { name: 'Architect', count: 1, color: 'purple' },
    { name: 'Contractor', count: 0, color: 'pink' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Team Management</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Plus size={20} />
          Add Team Member
        </button>
      </div>

      <div className="grid md:grid-cols-4 gap-6">
        {roles.map((role, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-lg">
            <div className={`w-12 h-12 bg-${role.color}-100 rounded-lg flex items-center justify-center mb-4`}>
              <Users className={`text-${role.color}-600`} size={24} />
            </div>
            <p className="text-gray-600 text-sm">{role.name}</p>
            <p className="text-2xl font-bold text-gray-800">{role.count}</p>
          </div>
        ))}
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Team Members</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teamMembers.map((member) => (
            <div key={member.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {member.name.charAt(0)}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => toast.info('Edit feature coming soon')}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Edit size={16} className="text-gray-600" />
                  </button>
                  <button
                    onClick={() => handleDelete(member.id)}
                    className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} className="text-red-600" />
                  </button>
                </div>
              </div>
              <h3 className="font-semibold text-gray-800 mb-1">{member.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{member.role}</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail size={14} />
                  <span className="truncate">{member.email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone size={14} />
                  <span>{member.phone}</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-200">
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                  {member.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Team Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-600 rounded-full" />
            <div className="flex-1">
              <p className="font-medium text-gray-800">John Doe updated project timeline</p>
              <p className="text-sm text-gray-600">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <div className="w-2 h-2 bg-green-600 rounded-full" />
            <div className="flex-1">
              <p className="font-medium text-gray-800">Jane Smith completed site inspection</p>
              <p className="text-sm text-gray-600">5 hours ago</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-2 h-2 bg-purple-600 rounded-full" />
            <div className="flex-1">
              <p className="font-medium text-gray-800">Mike Johnson uploaded new design</p>
              <p className="text-sm text-gray-600">1 day ago</p>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Add Team Member</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                <select
                  required
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select role</option>
                  <option value="Project Manager">Project Manager</option>
                  <option value="Site Engineer">Site Engineer</option>
                  <option value="Architect">Architect</option>
                  <option value="Contractor">Contractor</option>
                  <option value="Supervisor">Supervisor</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
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
                  Add Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Team
