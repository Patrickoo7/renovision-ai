import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper'
import BeforeAfterSlider from '../components/BeforeAfterSlider'
import MaterialPicker from '../components/MaterialPicker'
import { getProject, applyMaterials, getMaterials } from '../lib/api'
import { useApi } from '../hooks/useApi'
import { FiPenTool, FiArrowRight, FiLoader, FiCheck } from 'react-icons/fi'

export default function DesignPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { loading, error, call } = useApi()
  const [project, setProject] = useState(null)
  const [assignments, setAssignments] = useState({}) // segId -> material
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerSegment, setPickerSegment] = useState(null)
  const [redesignedUrl, setRedesignedUrl] = useState(null)

  useEffect(() => {
    call(getProject, projectId).then(data => {
      setProject(data)
      if (data.redesigned_image) setRedesignedUrl(`/outputs/${data.redesigned_image}`)
    }).catch(console.error)
  }, [projectId])

  const openPicker = (seg) => {
    setPickerSegment(seg)
    setPickerOpen(true)
  }

  const handleMaterialSelect = (material) => {
    if (pickerSegment) {
      setAssignments(prev => ({ ...prev, [pickerSegment.id]: material }))
    }
  }

  const handleApply = async () => {
    const assignmentList = Object.entries(assignments).map(([segId, mat]) => ({
      segment_id: segId,
      material_id: mat._id || mat.id || mat.name,
    }))
    const data = await call(applyMaterials, projectId, assignmentList)
    if (data.redesigned_image_url) {
      setRedesignedUrl(data.redesigned_image_url)
    } else if (data.redesigned_filename) {
      setRedesignedUrl(`/outputs/${data.redesigned_filename}`)
    }
  }

  if (!project) return <div className="text-center py-20 text-gray-400">Loading...</div>

  const segments = project.segments || []

  return (
    <div>
      <Stepper currentStep={3} projectId={projectId} />
      
      {/* Before/After */}
      <div className="mb-6">
        <BeforeAfterSlider 
          beforeUrl={`/uploads/${project.original_image}`}
          afterUrl={redesignedUrl}
        />
      </div>

      {/* Material assignments */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="font-bold text-gray-800 mb-4">Assign Materials to Regions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {segments.map(seg => {
            const assigned = assignments[seg.id]
            return (
              <div key={seg.id} className="border rounded-xl p-4 hover:shadow transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium capitalize text-gray-700">{seg.label}</span>
                  {assigned && <FiCheck className="text-green-500" />}
                </div>
                {assigned ? (
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded border" style={{ backgroundColor: assigned.color }} />
                    <span className="text-sm text-gray-600">{assigned.name}</span>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 mb-2">No material selected</p>
                )}
                <button onClick={() => openPicker(seg)}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1">
                  <FiPenTool /> {assigned ? 'Change' : 'Choose Material'}
                </button>
              </div>
            )
          })}
        </div>

        <div className="mt-6 flex items-center gap-4 justify-center">
          <button onClick={handleApply} disabled={loading || Object.keys(assignments).length === 0}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium 
                      inline-flex items-center gap-2 shadow-lg disabled:opacity-50">
            {loading ? <><FiLoader className="animate-spin" /> Generating preview...</>
                     : <><FiPenTool /> Apply Materials</>}
          </button>
          {redesignedUrl && (
            <button onClick={() => navigate(`/cost/${projectId}`)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-medium 
                        inline-flex items-center gap-2 shadow-lg">
              <FiArrowRight /> Continue to Cost
            </button>
          )}
        </div>
      </div>

      <MaterialPicker
        isOpen={pickerOpen}
        onClose={() => setPickerOpen(false)}
        onSelect={handleMaterialSelect}
        segmentLabel={pickerSegment?.label || 'wall'}
        currentMaterialId={pickerSegment ? assignments[pickerSegment.id]?.name : null}
      />

      {error && <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>}
    </div>
  )
}
