import { useState, useEffect } from 'react'
import { Plus, Calendar as CalendarIcon, Bell } from 'lucide-react'
import { reminders } from '../services/api'
import toast from 'react-hot-toast'

const Calendar = () => {
  const [reminderList, setReminderList] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    loadReminders()
  }, [])

  const loadReminders = async () => {
    try {
      const response = await reminders.getAll()
      setReminderList(response.data.reminders)
    } catch (error) {
      toast.error('Failed to load reminders')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await reminders.create(formData)
      toast.success('Reminder added!')
      setShowModal(false)
      setFormData({ title: '', description: '', date: new Date().toISOString().split('T')[0] })
      loadReminders()
    } catch (error) {
      toast.error('Failed to add reminder')
    }
  }

  const getDaysInMonth = () => {
    const date = new Date()
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1).getDay()
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    
    const days = []
    for (let i = 0; i < firstDay; i++) {
      days.push(null)
    }
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i)
    }
    return days
  }

  const days = getDaysInMonth()
  const today = new Date().getDate()

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Calendar & Reminders</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Plus size={20} />
          Add Reminder
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-white p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">
              {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h2>
            <CalendarIcon className="text-blue-600" size={24} />
          </div>
          <div className="grid grid-cols-7 gap-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
              <div key={day} className="text-center font-semibold text-gray-600 text-sm py-2">
                {day}
              </div>
            ))}
            {days.map((day, index) => (
              <div
                key={index}
                className={`aspect-square flex items-center justify-center rounded-lg text-sm ${
                  day === null
                    ? ''
                    : day === today
                    ? 'bg-blue-600 text-white font-bold'
                    : 'bg-gray-50 hover:bg-gray-100 cursor-pointer'
                }`}
              >
                {day}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Upcoming Reminders</h2>
          <div className="space-y-3">
            {reminderList.length > 0 ? (
              reminderList.map((reminder) => (
                <div key={reminder._id} className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Bell className="text-blue-600 flex-shrink-0 mt-1" size={16} />
                    <div>
                      <h3 className="font-semibold text-gray-800">{reminder.title}</h3>
                      <p className="text-sm text-gray-600">{reminder.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{reminder.date}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No reminders</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Deadline Alerts</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-4 bg-red-50 border-l-4 border-red-600 rounded-lg">
            <Bell className="text-red-600" size={20} />
            <div>
              <h3 className="font-semibold text-gray-800">Foundation Inspection Due</h3>
              <p className="text-sm text-gray-600">Tomorrow at 10:00 AM</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-4 bg-yellow-50 border-l-4 border-yellow-600 rounded-lg">
            <Bell className="text-yellow-600" size={20} />
            <div>
              <h3 className="font-semibold text-gray-800">Material Payment Pending</h3>
              <p className="text-sm text-gray-600">Due in 3 days</p>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Add Reminder</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
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
    </div>
  )
}

export default Calendar
