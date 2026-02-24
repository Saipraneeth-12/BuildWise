import { useState, useEffect } from 'react'
import { CheckCircle, Circle, Clock, Plus, Trash2, Sparkles, Calendar, AlertTriangle } from 'lucide-react'
import { tasks, scrum } from '../services/api'
import toast from 'react-hot-toast'

const Progress = () => {
  const [taskList, setTaskList] = useState([])
  const [scrumSchedule, setScrumSchedule] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showAIModal, setShowAIModal] = useState(false)
  const [showScrumModal, setShowScrumModal] = useState(false)
  const [showDelayModal, setShowDelayModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    time: '',
    category: 'general'
  })
  const [aiPrompt, setAiPrompt] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const [scrumFormData, setScrumFormData] = useState({
    prompt: '',
    floors: 'G+1',
    season: 'summer'
  })
  const [delayFormData, setDelayFormData] = useState({
    task_name: '',
    delay_days: 0
  })

  useEffect(() => {
    loadTasks()
    loadScrumSchedules()
  }, [])

  const loadTasks = async () => {
    try {
      const response = await tasks.getAll()
      setTaskList(response.data.tasks)
    } catch (error) {
      toast.error('Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  const loadScrumSchedules = async () => {
    try {
      const response = await scrum.getSchedules()
      if (response.data.schedules && response.data.schedules.length > 0) {
        // Get the most recent schedule (last one in array or sort by updated_at)
        const schedules = response.data.schedules
        const latestSchedule = schedules.sort((a, b) => 
          new Date(b.updated_at) - new Date(a.updated_at)
        )[0]
        setScrumSchedule(latestSchedule)
      }
    } catch (error) {
      console.error('Failed to load scrum schedules')
    }
  }

  const handleGenerateScrum = async (e) => {
    e.preventDefault()
    setAiLoading(true)
    try {
      const response = await scrum.generate(scrumFormData)
      setScrumSchedule(response.data.schedule)
      toast.success('Scrum schedule generated!')
      setShowScrumModal(false)
    } catch (error) {
      toast.error('Failed to generate scrum schedule')
    } finally {
      setAiLoading(false)
    }
  }

  const handleReportDelay = async (e) => {
    e.preventDefault()
    try {
      const response = await scrum.handleDelay({
        schedule_id: scrumSchedule._id,
        ...delayFormData
      })
      setScrumSchedule(response.data.schedule)
      toast.success('Delay handled and schedule updated!')
      setShowDelayModal(false)
      setDelayFormData({ task_name: '', delay_days: 0 })
    } catch (error) {
      toast.error('Failed to handle delay')
    }
  }

  const handleChecklistToggle = async (taskName, checklistItem, currentStatus) => {
    try {
      const response = await scrum.updateChecklist({
        schedule_id: scrumSchedule._id,
        task_name: taskName,
        checklist_item: checklistItem,
        completed: !currentStatus
      })
      setScrumSchedule(response.data.schedule)
      toast.success('Checklist updated!')
    } catch (error) {
      toast.error('Failed to update checklist')
    }
  }

  // Calculate overall progress from Scrum schedule checklists
  const calculateScrumProgress = () => {
    if (!scrumSchedule?.schedule?.sprints) return 0
    
    let totalChecklistItems = 0
    let completedChecklistItems = 0
    
    scrumSchedule.schedule.sprints.forEach(sprint => {
      const checklist = sprint.checklist || []
      const checklistStatus = sprint.checklist_status || {}
      
      totalChecklistItems += checklist.length
      completedChecklistItems += checklist.filter(item => checklistStatus[item]).length
    })
    
    return totalChecklistItems > 0 ? Math.round((completedChecklistItems / totalChecklistItems) * 100) : 0
  }

  // Get Scrum checklist counts
  const getScrumChecklistCounts = () => {
    if (!scrumSchedule?.schedule?.sprints) return { total: 0, completed: 0, remaining: 0 }
    
    let total = 0
    let completed = 0
    
    scrumSchedule.schedule.sprints.forEach(sprint => {
      const checklist = sprint.checklist || []
      const checklistStatus = sprint.checklist_status || {}
      
      total += checklist.length
      completed += checklist.filter(item => checklistStatus[item]).length
    })
    
    return { total, completed, remaining: total - completed }
  }

  // Calculate remaining time from Scrum schedule
  const getRemainingTime = () => {
    if (!scrumSchedule?.schedule?.project_summary) return null
    
    const totalWeeks = scrumSchedule.schedule.project_summary.total_weeks || 0
    const totalMonths = scrumSchedule.schedule.project_summary.total_months || 0
    
    // Calculate completed percentage
    const scrumCounts = getScrumChecklistCounts()
    const completionPercent = scrumCounts.total > 0 ? (scrumCounts.completed / scrumCounts.total) : 0
    
    // Calculate remaining
    const remainingWeeks = Math.round(totalWeeks * (1 - completionPercent))
    const remainingMonths = (totalMonths * (1 - completionPercent)).toFixed(1)
    
    return {
      totalWeeks,
      totalMonths,
      remainingWeeks,
      remainingMonths,
      completionPercent: Math.round(completionPercent * 100)
    }
  }

  // Generate dynamic milestones from Scrum schedule
  const generateMilestones = () => {
    if (!scrumSchedule?.schedule?.sprints) {
      // Default milestones if no scrum schedule
      return [
        { name: 'Project Kickoff', date: '2024-01-15', status: 'completed' },
        { name: 'Foundation Complete', date: '2024-02-20', status: 'in-progress' },
        { name: 'Structure Complete', date: '2024-04-30', status: 'pending' },
        { name: 'Final Handover', date: '2024-06-15', status: 'pending' }
      ]
    }

    const sprints = scrumSchedule.schedule.sprints
    const milestones = []
    
    // Key phases to track as milestones
    const keyPhases = [
      { pattern: /pre-construction/i, name: 'Project Kickoff' },
      { pattern: /foundation|footing/i, name: 'Foundation Complete' },
      { pattern: /structure.*slab|slab.*complete/i, name: 'Structure Complete' },
      { pattern: /brickwork/i, name: 'Brickwork Complete' },
      { pattern: /finishing/i, name: 'Finishing Complete' },
      { pattern: /final|handover/i, name: 'Final Handover' }
    ]

    keyPhases.forEach(({ pattern, name }) => {
      const sprint = sprints.find(s => pattern.test(s.phase))
      if (sprint) {
        // Determine status based on checklist completion
        const checklist = sprint.checklist || []
        const checklistStatus = sprint.checklist_status || {}
        const completedItems = checklist.filter(item => checklistStatus[item]).length
        const allComplete = checklist.length > 0 && completedItems === checklist.length
        
        let status = 'pending'
        if (sprint.status === 'delayed') {
          status = 'delayed'
        } else if (allComplete || sprint.status === 'ready_for_next') {
          status = 'completed'
        } else if (completedItems > 0) {
          status = 'in-progress'
        }

        milestones.push({
          name,
          date: sprint.weeks || 'TBD',
          status,
          phase: sprint.phase
        })
      }
    })

    return milestones.length > 0 ? milestones : [
      { name: 'Project Kickoff', date: '2024-01-15', status: 'completed' },
      { name: 'Foundation Complete', date: '2024-02-20', status: 'in-progress' },
      { name: 'Structure Complete', date: '2024-04-30', status: 'pending' },
      { name: 'Final Handover', date: '2024-06-15', status: 'pending' }
    ]
  }

  const milestones = generateMilestones()
  const scrumProgress = calculateScrumProgress()
  const scrumCounts = getScrumChecklistCounts()
  const remainingTime = getRemainingTime()
  const completedTasks = taskList.filter(t => t.completed).length
  const taskProgress = taskList.length > 0 ? Math.round((completedTasks / taskList.length) * 100) : 0
  
  // Use scrum progress if available, otherwise use task progress
  const completionPercentage = scrumSchedule ? scrumProgress : taskProgress
  
  // Use scrum counts if available, otherwise use task counts
  const displayCounts = scrumSchedule ? scrumCounts : {
    total: taskList.length,
    completed: completedTasks,
    remaining: taskList.length - completedTasks
  }

  const toggleTask = async (task) => {
    try {
      await tasks.update(task._id, { completed: !task.completed })
      setTaskList(taskList.map(t =>
        t._id === task._id ? { ...t, completed: !t.completed } : t
      ))
      toast.success(task.completed ? 'Task marked incomplete' : 'Task completed!')
    } catch (error) {
      toast.error('Failed to update task')
    }
  }

  const handleAddTask = async (e) => {
    e.preventDefault()
    try {
      const response = await tasks.create(formData)
      setTaskList([...taskList, response.data.task])
      toast.success('Task added!')
      setShowAddModal(false)
      setFormData({ name: '', time: '', category: 'general' })
    } catch (error) {
      toast.error('Failed to add task')
    }
  }

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Delete this task?')) {
      try {
        await tasks.delete(taskId)
        setTaskList(taskList.filter(t => t._id !== taskId))
        toast.success('Task deleted')
      } catch (error) {
        toast.error('Failed to delete task')
      }
    }
  }

  const handleAIGenerate = async (e) => {
    e.preventDefault()
    setAiLoading(true)
    try {
      const response = await tasks.generateWithAI({
        prompt: aiPrompt,
        auto_create: true
      })
      
      toast.success(response.data.message)
      setShowAIModal(false)
      setAiPrompt('')
      loadTasks() // Reload to show new AI-generated tasks
    } catch (error) {
      toast.error('Failed to generate tasks')
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Progress Tracker</h1>
        <div className="flex gap-3">
          <button
            onClick={() => setShowScrumModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg transition-all"
          >
            <Calendar size={20} />
            AI Scrum Master
          </button>
          <button
            onClick={() => setShowAIModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all"
          >
            <Sparkles size={20} />
            AI Generate Tracker
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
          >
            <Plus size={20} />
            Add Task
          </button>
        </div>
      </div>

      {/* Scrum Schedule Display */}
      {scrumSchedule && (
        <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-xl shadow-lg border-2 border-green-200">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <Calendar className="text-green-600" size={28} />
                AI Scrum Master Schedule
              </h2>
              {scrumSchedule.schedule?.project_summary?.user_description && (
                <p className="text-gray-700 mt-2 font-medium">
                  📋 {scrumSchedule.schedule.project_summary.user_description}
                </p>
              )}
              <p className="text-gray-600 mt-1">
                {scrumSchedule.schedule?.project_summary?.building_type} • {scrumSchedule.schedule?.project_summary?.season} season
              </p>
            </div>
            <button
              onClick={() => setShowDelayModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
            >
              <AlertTriangle size={18} />
              Report Delay
            </button>
          </div>

          <div className="grid md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total Duration</p>
              <p className="text-xl font-bold text-gray-800">
                {scrumSchedule.schedule?.project_summary?.estimated_completion || 
                 scrumSchedule.schedule?.project_summary?.total_duration}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total Weeks</p>
              <p className="text-xl font-bold text-gray-800">
                {scrumSchedule.schedule?.project_summary?.total_weeks} weeks
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600">Floor Count</p>
              <p className="text-xl font-bold text-gray-800">
                {scrumSchedule.schedule?.project_summary?.floor_count} floors
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <p className="text-sm text-gray-600">Season Impact</p>
              <p className="text-xl font-bold text-gray-800">
                {scrumSchedule.schedule?.project_summary?.season_impact}
              </p>
            </div>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {scrumSchedule.schedule?.sprints?.map((sprint, index) => (
              <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">
                        {sprint.sprint}
                      </span>
                      <span className="text-xs text-gray-500">{sprint.weeks}</span>
                    </div>
                    <h3 className="font-bold text-gray-800 text-lg">{sprint.phase}</h3>
                    <p className="text-sm text-gray-600 mt-1">Duration: {sprint.duration}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    sprint.status === 'delayed' ? 'bg-red-100 text-red-700' :
                    sprint.status === 'ready_for_next' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {sprint.status}
                  </span>
                </div>

                {sprint.tasks && sprint.tasks.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Tasks:</p>
                    <ul className="space-y-1">
                      {sprint.tasks.map((task, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-green-600 mt-1">•</span>
                          <span>{task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {sprint.checklist && sprint.checklist.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Checklist:</p>
                    <div className="space-y-1">
                      {sprint.checklist.map((item, idx) => {
                        const isChecked = sprint.checklist_status?.[item] || false
                        return (
                          <label key={idx} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => handleChecklistToggle(sprint.phase, item, isChecked)}
                              className="w-4 h-4 text-green-600 rounded"
                            />
                            <span className={`text-sm ${isChecked ? 'line-through text-gray-500' : 'text-gray-700'}`}>
                              {item}
                            </span>
                          </label>
                        )
                      })}
                    </div>
                  </div>
                )}

                {sprint.dependencies && sprint.dependencies.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-600 mb-1">Dependencies:</p>
                    <p className="text-xs text-gray-600">
                      {sprint.dependencies.join(', ')}
                    </p>
                  </div>
                )}

                {sprint.risks && sprint.risks.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-orange-600 mb-1">Risks:</p>
                    <ul className="space-y-1">
                      {sprint.risks.map((risk, idx) => (
                        <li key={idx} className="text-xs text-orange-700 flex items-start gap-2">
                          <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Granite Response Section */}
          {scrumSchedule.schedule?.granite_response && (
            <div className="mt-6 pt-6 border-t border-green-200">
              <details className="cursor-pointer">
                <summary className="font-semibold text-gray-800 mb-2">View AI Granite LLM Response</summary>
                <div className="mt-3 p-4 bg-white rounded-lg text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
                  {scrumSchedule.schedule.granite_response}
                </div>
              </details>
            </div>
          )}
        </div>
      )}

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Overall Progress</h2>
          <span className="text-3xl font-bold text-blue-600">{completionPercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-4 rounded-full transition-all"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
        <p className="text-sm text-gray-600 mt-2">
          {displayCounts.completed} of {displayCounts.total} {scrumSchedule ? 'checklist items' : 'tasks'} completed
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Task Checklist</h2>
          {loading ? (
            <p className="text-gray-500">Loading tasks...</p>
          ) : taskList.length > 0 ? (
            <div className="space-y-3">
              {taskList.map((task) => (
                <div
                  key={task._id}
                  className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <button
                    onClick={() => toggleTask(task)}
                    className="flex-shrink-0"
                  >
                    {task.completed ? (
                      <CheckCircle className="text-green-600" size={24} />
                    ) : (
                      <Circle className="text-gray-400" size={24} />
                    )}
                  </button>
                  <div className="flex-1">
                    <h3 className={`font-medium ${task.completed ? 'text-gray-500 line-through' : 'text-gray-800'}`}>
                      {task.name}
                    </h3>
                    <p className="text-sm text-gray-600">{task.time}</p>
                    {task.category && (
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                        {task.category}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteTask(task._id)}
                    className="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Circle className="mx-auto text-gray-400 mb-3" size={48} />
              <p className="text-gray-500 mb-4">No tasks yet</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="text-blue-600 hover:underline"
              >
                Add your first task
              </button>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Milestones</h2>
          <div className="space-y-4">
            {milestones.map((milestone, index) => (
              <div key={index} className="relative pl-8">
                <div className={`absolute left-0 top-1 w-4 h-4 rounded-full ${
                  milestone.status === 'completed' ? 'bg-green-600' :
                  milestone.status === 'in-progress' ? 'bg-blue-600' :
                  milestone.status === 'delayed' ? 'bg-red-600' :
                  'bg-gray-300'
                }`} />
                {index < milestones.length - 1 && (
                  <div className="absolute left-2 top-5 w-0.5 h-12 bg-gray-300" />
                )}
                <div>
                  <h3 className="font-semibold text-gray-800">{milestone.name}</h3>
                  <p className="text-sm text-gray-600">{milestone.date}</p>
                  {milestone.phase && (
                    <p className="text-xs text-gray-500 mt-1">{milestone.phase}</p>
                  )}
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    milestone.status === 'completed' ? 'bg-green-100 text-green-700' :
                    milestone.status === 'in-progress' ? 'bg-blue-100 text-blue-700' :
                    milestone.status === 'delayed' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {milestone.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">
          {scrumSchedule ? 'Project Timeline' : 'Time Tracker'}
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="text-blue-600" size={20} />
              <span className="font-medium text-gray-800">
                {scrumSchedule ? 'Total Items' : 'Total Tasks'}
              </span>
            </div>
            <p className="text-2xl font-bold text-blue-600">{displayCounts.total}</p>
            {scrumSchedule && remainingTime && (
              <p className="text-xs text-gray-600 mt-1">
                {remainingTime.totalWeeks} weeks ({remainingTime.totalMonths} months)
              </p>
            )}
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="text-green-600" size={20} />
              <span className="font-medium text-gray-800">Completed</span>
            </div>
            <p className="text-2xl font-bold text-green-600">{displayCounts.completed}</p>
            {scrumSchedule && remainingTime && (
              <p className="text-xs text-gray-600 mt-1">
                {remainingTime.completionPercent}% complete
              </p>
            )}
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="text-purple-600" size={20} />
              <span className="font-medium text-gray-800">Remaining</span>
            </div>
            <p className="text-2xl font-bold text-purple-600">{displayCounts.remaining}</p>
            {scrumSchedule && remainingTime && (
              <p className="text-xs text-gray-600 mt-1">
                ~{remainingTime.remainingWeeks} weeks ({remainingTime.remainingMonths} months)
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Add Task Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold mb-4">Add New Task</h2>
            <form onSubmit={handleAddTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Task Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Foundation excavation"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Estimated Time</label>
                <input
                  type="text"
                  required
                  value={formData.time}
                  onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 8 hours"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="general">General</option>
                  <option value="preparation">Preparation</option>
                  <option value="foundation">Foundation</option>
                  <option value="construction">Construction</option>
                  <option value="finishing">Finishing</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg"
                >
                  Add Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* AI Generate Modal */}
      {showAIModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="text-purple-600" size={24} />
              <h2 className="text-2xl font-bold">AI Generate Tracker</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Describe your project and AI will generate a complete task tracker for you.
            </p>
            <form onSubmit={handleAIGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Project Description</label>
                <textarea
                  required
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows="4"
                  placeholder="e.g., Building a 2-story residential house with RCC structure, 2000 sq ft area..."
                />
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                <p className="text-sm text-purple-800">
                  <strong>Note:</strong> RAG integration is pending. AI will generate placeholder tasks that you can customize.
                </p>
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
                  {aiLoading ? 'Generating...' : 'Generate Tasks'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Scrum Master Modal */}
      {showScrumModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="text-green-600" size={24} />
              <h2 className="text-2xl font-bold">AI Scrum Master</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Generate intelligent construction schedule using AI Granite LLM with realistic timelines
            </p>
            <form onSubmit={handleGenerateScrum} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Project Description</label>
                <textarea
                  required
                  value={scrumFormData.prompt}
                  onChange={(e) => setScrumFormData({ ...scrumFormData, prompt: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  rows="3"
                  placeholder="e.g., RCC residential building with standard construction..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Building Type</label>
                <select
                  value={scrumFormData.floors}
                  onChange={(e) => setScrumFormData({ ...scrumFormData, floors: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="G">Ground Floor Only</option>
                  <option value="G+1">G+1 (2 Floors)</option>
                  <option value="G+2">G+2 (3 Floors)</option>
                  <option value="G+3">G+3 (4 Floors)</option>
                  <option value="G+4">G+4 (5 Floors)</option>
                  <option value="G+5">G+5 (6 Floors)</option>
                  <option value="G+6">G+6 (7 Floors)</option>
                  <option value="G+7">G+7 (8 Floors)</option>
                  <option value="G+8">G+8 (9 Floors)</option>
                  <option value="G+9">G+9 (10 Floors)</option>
                  <option value="G+10">G+10 (11 Floors)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Season</label>
                <select
                  value={scrumFormData.season}
                  onChange={(e) => setScrumFormData({ ...scrumFormData, season: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="summer">Summer (Normal Duration)</option>
                  <option value="monsoon">Monsoon (+30-40% Duration)</option>
                  <option value="winter">Winter (+10-20% Duration)</option>
                </select>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm text-green-800">
                  <strong>AI Granite LLM:</strong> Generates realistic construction schedules with proper dependencies, 
                  season adjustments, detailed checklists, and risk mitigation strategies.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowScrumModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  disabled={aiLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={aiLoading}
                  className="flex-1 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50"
                >
                  {aiLoading ? 'Generating...' : 'Generate Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delay Report Modal */}
      {showDelayModal && scrumSchedule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="text-orange-600" size={24} />
              <h2 className="text-2xl font-bold">Report Delay</h2>
            </div>
            <form onSubmit={handleReportDelay} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Task</label>
                <select
                  required
                  value={delayFormData.task_name}
                  onChange={(e) => setDelayFormData({ ...delayFormData, task_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Choose task...</option>
                  {scrumSchedule.schedule?.sprints?.map((sprint, idx) => (
                    <option key={idx} value={sprint.phase}>{sprint.phase}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Delay (days)</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={delayFormData.delay_days}
                  onChange={(e) => setDelayFormData({ ...delayFormData, delay_days: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  placeholder="Enter delay in days"
                />
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                <p className="text-sm text-orange-800">
                  AI will automatically adjust all dependent tasks and recalculate the completion date.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowDelayModal(false)}
                  className="flex-1 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-lg hover:shadow-lg"
                >
                  Report Delay
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Progress
