import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper'
import SegmentCanvas from '../components/SegmentCanvas'
import { getProject, segmentImage, updateProjectSegments } from '../lib/api'
import { useApi } from '../hooks/useApi'
import { FiPlay, FiArrowRight, FiLoader } from 'react-icons/fi'

const LABELS = ['wall', 'window', 'balcony', 'pillar', 'parapet', 'gate', 'roof', 'other']

export default function SegmentPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { loading, error, call } = useApi()
  const [project, setProject] = useState(null)
  const [segments, setSegments] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [segmented, setSegmented] = useState(false)

  useEffect(() => {
    call(getProject, projectId).then(data => {
      setProject(data)
      if (data.segments?.length) {
        setSegments(data.segments)
        setSegmented(true)
      }
    }).catch(console.error)
  }, [projectId])

  const runSegmentation = async () => {
    const data = await call(segmentImage, projectId)
    setSegments(data.segments)
    setSegmented(true)
  }

  const relabelSegment = (segId, newLabel) => {
    setSegments(prev => prev.map(s => s.id === segId ? { ...s, label: newLabel } : s))
  }

  const deleteSegment = (segId) => {
    setSegments(prev => prev.filter(s => s.id !== segId))
  }

  const handleConfirm = async () => {
    try {
      await call(updateProjectSegments, projectId, segments)
      navigate(`/design/${projectId}`)
    } catch (err) {
      console.error(err)
    }
  }

  if (!project) return <div className="text-center py-20 text-gray-400">Loading project...</div>

  return (
    <div>
      <Stepper currentStep={2} projectId={projectId} />
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Canvas */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow p-4">
            <SegmentCanvas
              imageUrl={`/uploads/${project.original_image}`}
              segments={segments}
              selectedSegmentId={selectedId}
              onSegmentClick={setSelectedId}
            />
          </div>
          {!segmented && (
            <div className="mt-4 text-center">
              <button onClick={runSegmentation} disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium 
                          inline-flex items-center gap-2 shadow-lg disabled:opacity-50">
                {loading ? <><FiLoader className="animate-spin" /> Analyzing structure...</>
                         : <><FiPlay /> Run Segmentation</>}
              </button>
            </div>
          )}
        </div>

        {/* Segment list */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-800 mb-4">Detected Regions ({segments.length})</h3>
            {segments.length === 0 && (
              <p className="text-gray-400 text-sm py-8 text-center">
                Click "Run Segmentation" to detect building regions
              </p>
            )}
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {segments.map(seg => (
                <div key={seg.id}
                  onClick={() => setSelectedId(seg.id)}
                  className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition
                    ${selectedId === seg.id ? 'bg-blue-50 ring-2 ring-blue-400' : 'hover:bg-gray-50'}`}>
                  <div className="w-4 h-4 rounded-full border"
                    style={{ backgroundColor: `var(--${seg.label}-color, #ccc)` }} />
                  <select value={seg.label} onChange={(e) => relabelSegment(seg.id, e.target.value)}
                    className="text-sm border rounded px-2 py-1 flex-1 bg-white"
                    onClick={(e) => e.stopPropagation()}>
                    {LABELS.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                  <span className="text-xs text-gray-400">{seg.area_px}px</span>
                  <button onClick={(e) => { e.stopPropagation(); deleteSegment(seg.id) }}
                    className="text-red-400 hover:text-red-600 text-xs">✕</button>
                </div>
              ))}
            </div>
          </div>

          {segmented && segments.length > 0 && (
            <div className="mt-4 text-center">
              <button onClick={handleConfirm} disabled={loading}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-medium 
                          inline-flex items-center gap-2 shadow-lg disabled:opacity-50">
                {loading ? <><FiLoader className="animate-spin" /> Saving...</>
                         : <><FiArrowRight /> Confirm & Continue</>}
              </button>
            </div>
          )}
        </div>
      </div>
      {error && <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>}
    </div>
  )
}
