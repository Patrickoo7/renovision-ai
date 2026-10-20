import { useState, useEffect } from 'react'
import { FiX, FiCheck } from 'react-icons/fi'
import { getMaterials } from '../lib/api'

const SEGMENT_MATERIAL_MAP = {
  wall: ['Paint', 'Texture', 'Cladding', 'Tiles', 'Panel'],
  window: [],
  balcony: ['Paint', 'Tiles', 'Railing'],
  pillar: ['Paint', 'Texture', 'Cladding', 'Tiles'],
  parapet: ['Paint', 'Cladding', 'Railing'],
  gate: ['Paint', 'Railing'],
  roof: ['Paint'],
  other: ['Paint', 'Texture', 'Cladding', 'Tiles', 'Panel'],
}

export default function MaterialPicker({ isOpen, onClose, onSelect, segmentLabel, currentMaterialId }) {
  const [materials, setMaterials] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)

  useEffect(() => {
    if (isOpen) {
      getMaterials().then(res => {
        const allowed = SEGMENT_MATERIAL_MAP[segmentLabel] || SEGMENT_MATERIAL_MAP.other
        const filtered = res.data.filter(m => allowed.includes(m.category))
        setMaterials(filtered)
        if (allowed.length > 0) setActiveCategory(allowed[0])
      }).catch(console.error)
    }
  }, [isOpen, segmentLabel])

  if (!isOpen) return null

  const categories = [...new Set(materials.map(m => m.category))]
  const filtered = activeCategory ? materials.filter(m => m.category === activeCategory) : materials

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <h3 className="text-lg font-bold text-gray-800">
            Choose Material for <span className="text-blue-600 capitalize">{segmentLabel}</span>
          </h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full"><FiX /></button>
        </div>

        {/* Category tabs */}
        <div className="px-6 py-3 border-b flex gap-2 flex-wrap">
          {categories.map(cat => (
            <button key={cat} onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition
                ${activeCategory === cat ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
              {cat}
            </button>
          ))}
        </div>

        {/* Material grid */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-2 gap-4">
          {filtered.map(mat => (
            <button key={mat._id || mat.name} onClick={() => { onSelect(mat); onClose() }}
              className={`flex items-start gap-3 p-4 rounded-xl border-2 text-left transition hover:shadow-md
                ${(mat._id || mat.name) === currentMaterialId 
                  ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}>
              {/* Color swatch */}
              <div className="w-12 h-12 rounded-lg border shadow-inner flex-shrink-0"
                style={{ backgroundColor: mat.color }} />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm text-gray-800 flex items-center gap-2">
                  {mat.name}
                  {(mat._id || mat.name) === currentMaterialId && <FiCheck className="text-blue-600" />}
                </div>
                <div className="text-xs text-gray-500 mt-1">₹{mat.rate}/{mat.unit}</div>
                <div className="text-xs text-gray-400">{mat.description}</div>
              </div>
            </button>
          ))}
          {filtered.length === 0 && (
            <p className="col-span-2 text-center text-gray-400 py-8">No materials available for this region</p>
          )}
        </div>
      </div>
    </div>
  )
}
