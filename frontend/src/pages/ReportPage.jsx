import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper'
import { getProject, downloadReport } from '../lib/api'
import { useApi } from '../hooks/useApi'
import { FiDownload, FiRefreshCw, FiLoader, FiCheckCircle } from 'react-icons/fi'

export default function ReportPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { loading, error, call } = useApi()
  const [project, setProject] = useState(null)

  useEffect(() => {
    call(getProject, projectId).then(setProject).catch(console.error)
  }, [projectId])

  const handleDownload = async () => {
    const blob = await call(downloadReport, projectId)
    const url = URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.download = `E2M_Renovation_Estimate_${projectId}.pdf`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (!project) return <div className="text-center py-20 text-gray-400">Loading...</div>

  return (
    <div>
      <Stepper currentStep={5} projectId={projectId} />
      <div className="max-w-2xl mx-auto text-center">
        <FiCheckCircle className="text-6xl text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Your Renovation Estimate is Ready!</h2>
        <p className="text-gray-500 mb-8">Download the PDF report to share with contractors</p>

        {/* Preview images */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow overflow-hidden">
            <img src={`/uploads/${project.original_image}`} alt="Original" 
              className="w-full h-48 object-cover" />
            <p className="py-2 text-sm text-gray-500">Original</p>
          </div>
          {project.redesigned_image && (
            <div className="bg-white rounded-xl shadow overflow-hidden">
              <img src={`/outputs/${project.redesigned_image}`} alt="Redesigned"
                className="w-full h-48 object-cover" />
              <p className="py-2 text-sm text-gray-500">Redesigned</p>
            </div>
          )}
        </div>

        {project.estimates && (
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white mb-8">
            <p className="text-blue-200">Estimated Total Cost</p>
            <p className="text-4xl font-bold mt-2">₹{project.estimates.grand_total?.toLocaleString()}</p>
          </div>
        )}

        <div className="flex items-center justify-center gap-4">
          <button onClick={handleDownload} disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-medium
                      inline-flex items-center gap-2 shadow-lg disabled:opacity-50">
            {loading ? <><FiLoader className="animate-spin" /> Generating PDF...</>
                     : <><FiDownload /> Download PDF Report</>}
          </button>
          <button onClick={() => navigate('/')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-8 py-3 rounded-xl font-medium
                      inline-flex items-center gap-2">
            <FiRefreshCw /> New Project
          </button>
        </div>

        {error && <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>}
      </div>
    </div>
  )
}
