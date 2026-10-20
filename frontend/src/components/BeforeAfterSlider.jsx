import { useState, useRef } from 'react'

export default function BeforeAfterSlider({ beforeUrl, afterUrl }) {
  const [position, setPosition] = useState(50)
  const containerRef = useRef(null)
  const dragging = useRef(false)

  const handleMove = (clientX) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const x = ((clientX - rect.left) / rect.width) * 100
    setPosition(Math.max(0, Math.min(100, x)))
  }

  const handleMouseDown = () => { dragging.current = true }
  const handleMouseUp = () => { dragging.current = false }
  const handleMouseMove = (e) => { if (dragging.current) handleMove(e.clientX) }
  const handleTouchMove = (e) => { handleMove(e.touches[0].clientX) }

  if (!afterUrl) {
    return (
      <div className="relative rounded-xl overflow-hidden border bg-gray-100">
        <img src={beforeUrl} alt="Original" className="w-full max-h-96 object-contain" />
        <div className="absolute inset-0 flex items-center justify-center bg-black/20">
          <p className="bg-white/90 px-4 py-2 rounded-lg text-gray-600 font-medium">
            Select materials and click "Apply" to see the redesigned preview
          </p>
        </div>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="relative rounded-xl overflow-hidden shadow-lg cursor-col-resize select-none"
      onMouseDown={handleMouseDown} onMouseUp={handleMouseUp} onMouseLeave={handleMouseUp}
      onMouseMove={handleMouseMove} onTouchMove={handleTouchMove}>

      {/* After image (full) */}
      <img src={afterUrl} alt="After" className="w-full max-h-[500px] object-contain block" />

      {/* Before image (clipped) */}
      <div className="absolute inset-0 overflow-hidden" style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}>
        <img src={beforeUrl} alt="Before" className="w-full max-h-[500px] object-contain block" />
      </div>

      {/* Slider line */}
      <div className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg" style={{ left: `${position}%` }}>
        <div className="absolute top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-full w-10 h-10 shadow-lg flex items-center justify-center">
          <span className="text-gray-600 text-sm font-bold">⟷</span>
        </div>
      </div>

      {/* Labels */}
      <div className="absolute top-3 left-3 bg-black/60 text-white text-xs px-2 py-1 rounded">Before</div>
      <div className="absolute top-3 right-3 bg-black/60 text-white text-xs px-2 py-1 rounded">After</div>
    </div>
  )
}
