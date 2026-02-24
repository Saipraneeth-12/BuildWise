import { CheckCircle, Circle, Clock } from 'lucide-react'

const Scheduling = () => {
  const stages = [
    { name: 'Site Preparation', duration: '2 weeks', status: 'completed', dependencies: [] },
    { name: 'Foundation', duration: '3 weeks', status: 'in-progress', dependencies: ['Site Preparation'] },
    { name: 'Structure', duration: '8 weeks', status: 'pending', dependencies: ['Foundation'] },
    { name: 'Roofing', duration: '2 weeks', status: 'pending', dependencies: ['Structure'] },
    { name: 'Electrical', duration: '3 weeks', status: 'pending', dependencies: ['Structure'] },
    { name: 'Plumbing', duration: '3 weeks', status: 'pending', dependencies: ['Structure'] },
    { name: 'Finishing', duration: '4 weeks', status: 'pending', dependencies: ['Electrical', 'Plumbing'] },
    { name: 'Final Inspection', duration: '1 week', status: 'pending', dependencies: ['Finishing'] }
  ]

  const timeline = [
    { week: 'Week 1-2', task: 'Site Preparation', progress: 100 },
    { week: 'Week 3-5', task: 'Foundation Work', progress: 60 },
    { week: 'Week 6-13', task: 'Structure Construction', progress: 0 },
    { week: 'Week 14-15', task: 'Roofing', progress: 0 }
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Scheduling Timeline</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Construction Stages</h2>
          <div className="space-y-3">
            {stages.map((stage, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3 mb-2">
                  {stage.status === 'completed' ? (
                    <CheckCircle className="text-green-600" size={20} />
                  ) : stage.status === 'in-progress' ? (
                    <Clock className="text-blue-600" size={20} />
                  ) : (
                    <Circle className="text-gray-400" size={20} />
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800">{stage.name}</h3>
                    <p className="text-sm text-gray-600">{stage.duration}</p>
                  </div>
                </div>
                {stage.dependencies.length > 0 && (
                  <p className="text-xs text-gray-500 ml-8">
                    Depends on: {stage.dependencies.join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Week-by-Week Timeline</h2>
          <div className="space-y-4">
            {timeline.map((item, index) => (
              <div key={index}>
                <div className="flex justify-between mb-2">
                  <span className="font-medium text-gray-800">{item.week}</span>
                  <span className="text-sm text-gray-600">{item.progress}%</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{item.task}</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Gantt Chart View</h2>
        <div className="overflow-x-auto">
          <div className="min-w-[800px] space-y-2">
            {stages.map((stage, index) => (
              <div key={index} className="flex items-center gap-4">
                <div className="w-40 text-sm font-medium text-gray-700">{stage.name}</div>
                <div className="flex-1 bg-gray-100 rounded-full h-8 relative">
                  <div
                    className={`h-8 rounded-full flex items-center px-3 text-white text-xs ${
                      stage.status === 'completed'
                        ? 'bg-green-500'
                        : stage.status === 'in-progress'
                        ? 'bg-blue-500'
                        : 'bg-gray-300'
                    }`}
                    style={{ width: `${30 + index * 10}%` }}
                  >
                    {stage.duration}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Scheduling
