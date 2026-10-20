import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper'
import CostTable from '../components/CostTable'
import { getProject, getEstimate } from '../lib/api'
import { useApi } from '../hooks/useApi'
import { FiDollarSign, FiArrowRight, FiLoader } from 'react-icons/fi'

export default function CostPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { loading, error, call } = useApi()
  const [project, setProject] = useState(null)
  const [estimates, setEstimates] = useState(null)
  const [refSegmentId, setRefSegmentId] = useState('')
  const [refDimension, setRefDimension] = useState(10)

  useEffect(() => {
    call(getProject, projectId).then(data => {
      setProject(data)
      if (data.segments?.length) setRefSegmentId(data.segments[0].id)
      if (data.estimates) setEstimates(data.estimates)
    }).catch(console.error)
  }, [projectId])

  const calculateEstimate = async () => {
    const data = await call(getEstimate, projectId, refSegmentId, refDimension)
    setEstimates(data)
  }

  const handleRateChange = (segmentId, field, newRate) => {
    if (isNaN(newRate)) return
    setEstimates(prev => {
      if (!prev || !prev.breakdown) return prev
      let totalMat = 0
      let totalLabor = 0
      const newBreakdown = prev.breakdown.map(row => {
        if (row.segment_id === segmentId) {
          const matRate = field === 'material_rate' ? newRate : row.material_rate
          const laborRate = field === 'labor_rate' ? newRate : row.labor_rate
          const matCost = row.quantity * matRate
          const laborCost = (row.area_sqft || row.quantity) * laborRate
          const total = matCost + laborCost
          totalMat += matCost
          totalLabor += laborCost
          return {
            ...row,
            [field]: newRate,
            material_cost: Math.round(matCost),
            labor_cost: Math.round(laborCost),
            total_cost: Math.round(total)
          }
        } else {
          totalMat += row.material_cost
          totalLabor += row.labor_cost
          return row
        }
      })
      return {
        ...prev,
        breakdown: newBreakdown,
        total_material_cost: Math.round(totalMat),
        total_labor_cost: Math.round(totalLabor),
        grand_total: Math.round(totalMat + totalLabor)
      }
    })
  }

  if (!project) return <div className="text-center py-20 text-gray-400">Loading...</div>

  const segments = project.segments || []

  return (
    <div>
      <Stepper currentStep={4} projectId={projectId} />

      {/* Reference dimension input */}
      <div className="bg-white rounded-xl shadow p-6 mb-6">
        <h3 className="font-bold text-gray-800 mb-4">Set Reference Dimension</h3>
        <p className="text-sm text-gray-500 mb-4">
          Select a region and enter its known dimension (in feet) for accurate area estimation.
        </p>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Reference Region</label>
            <select value={refSegmentId} onChange={(e) => setRefSegmentId(e.target.value)}
              className="border rounded-lg px-3 py-2 w-48">
              {segments.map(seg => (
                <option key={seg.id} value={seg.id}>{seg.label} ({seg.id})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Known Height/Width (feet)</label>
            <input type="number" value={refDimension} onChange={(e) => setRefDimension(parseFloat(e.target.value))}
              className="border rounded-lg px-3 py-2 w-32" min="1" step="0.5" />
          </div>
          <button onClick={calculateEstimate} disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium
                      inline-flex items-center gap-2 disabled:opacity-50">
            {loading ? <><FiLoader className="animate-spin" /> Calculating...</>
                     : <><FiDollarSign /> Calculate Estimate</>}
          </button>
        </div>
      </div>

      {/* Cost breakdown */}
      <CostTable estimates={estimates} onRateChange={handleRateChange} />

      {/* line items / summary cards */}
      {estimates && (
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-white rounded-xl shadow p-5 text-center">
            <p className="text-sm text-gray-500">Material Cost</p>
            <p className="text-2xl font-bold text-gray-800">₹{estimates.total_material_cost?.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5 text-center">
            <p className="text-sm text-gray-500">Labor Cost</p>
            <p className="text-2xl font-bold text-gray-800">₹{estimates.total_labor_cost?.toLocaleString()}</p>
          </div>
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl shadow p-5 text-center text-white">
            <p className="text-sm text-blue-200">Grand Total</p>
            <p className="text-2xl font-bold">₹{estimates.grand_total?.toLocaleString()}</p>
          </div>
        </div>
      )}

      {estimates && (
        <div className="mt-6 text-center">
          <button onClick={() => navigate(`/report/${projectId}`)}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-xl font-medium 
                      inline-flex items-center gap-2 shadow-lg">
            <FiArrowRight /> Generate Report
          </button>
        </div>
      )}

      {error && <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>}
    </div>
  )
}
