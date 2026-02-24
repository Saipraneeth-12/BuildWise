import { useNavigate } from 'react-router-dom'
import { Building2, Brain, Calculator, Clock, TrendingUp, Shield } from 'lucide-react'

const Landing = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Planning',
      description: 'Get intelligent construction advice powered by advanced AI'
    },
    {
      icon: Calculator,
      title: 'Material Estimation',
      description: 'Accurate material quantity calculations for your projects'
    },
    {
      icon: Clock,
      title: 'Smart Scheduling',
      description: 'Optimize timelines and manage dependencies efficiently'
    },
    {
      icon: TrendingUp,
      title: 'Progress Tracking',
      description: 'Monitor project milestones and completion rates'
    },
    {
      icon: Shield,
      title: 'Cost Management',
      description: 'Track expenses and stay within budget'
    },
    {
      icon: Building2,
      title: 'Architecture Tools',
      description: 'Design and visualize with integrated whiteboard'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navbar */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Building2 className="text-blue-600" size={32} />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              BuildWise
            </span>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-2 text-gray-700 hover:text-blue-600 transition-colors"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/signup')}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
          AI-Powered Construction Planning
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your construction projects with intelligent planning, accurate estimates, 
          and real-time tracking. BuildWise brings AI to construction management.
        </p>
        <button
          onClick={() => navigate('/signup')}
          className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg rounded-lg hover:shadow-2xl transform hover:scale-105 transition-all"
        >
          Start Planning Now
        </button>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <h2 className="text-4xl font-bold text-center mb-12 text-gray-800">
          Everything You Need to Build Better
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2"
            >
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                <feature.icon className="text-white" size={28} />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-gray-800">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* About Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold mb-6">Built for Modern Construction</h2>
          <p className="text-xl mb-8 max-w-3xl mx-auto opacity-90">
            BuildWise combines cutting-edge AI technology with practical construction management tools. 
            From material estimation to cost planning, we help you deliver projects on time and within budget.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Building2 size={24} />
            <span className="text-xl font-bold text-white">BuildWise</span>
          </div>
          <p className="mb-4">AI Construction Planning Platform</p>
          <p className="text-sm">&copy; 2024 BuildWise. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default Landing
