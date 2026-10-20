import { useNavigate } from 'react-router-dom'
import { FiUpload, FiScissors, FiPenTool, FiDollarSign, FiFileText } from 'react-icons/fi'

const steps = [
  { label: 'Upload', icon: FiUpload, path: '/' },
  { label: 'Segment', icon: FiScissors, path: '/segment' },
  { label: 'Design', icon: FiPenTool, path: '/design' },
  { label: 'Cost', icon: FiDollarSign, path: '/cost' },
  { label: 'Report', icon: FiFileText, path: '/report' },
]

export default function Stepper({ currentStep, projectId }) {
  const navigate = useNavigate()

  return (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, i) => {
        const Icon = step.icon
        const isActive = i + 1 === currentStep
        const isCompleted = i + 1 < currentStep
        const isClickable = isCompleted && projectId

        return (
          <div key={step.label} className="flex items-center">
            <button
              onClick={() => {
                if (isClickable) {
                  const path = i === 0 ? '/' : `${step.path}/${projectId}`
                  navigate(path)
                }
              }}
              disabled={!isClickable}
              className={`flex flex-col items-center gap-1 px-4 py-2 rounded-lg transition
                ${isActive ? 'bg-blue-600 text-white shadow-md' : ''}
                ${isCompleted ? 'text-green-600 cursor-pointer hover:bg-green-50' : ''}
                ${!isActive && !isCompleted ? 'text-gray-400' : ''}
              `}
            >
              <Icon className="text-lg" />
              <span className="text-xs font-medium">{step.label}</span>
            </button>
            {i < steps.length - 1 && (
              <div className={`w-12 h-0.5 ${isCompleted ? 'bg-green-400' : 'bg-gray-300'}`} />
            )}
          </div>
        )
      })}
    </div>
  )
}
