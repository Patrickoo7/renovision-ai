import { useRef, useEffect } from 'react'

const LABEL_COLORS = {
  wall: 'rgba(66, 133, 244, 0.35)',
  window: 'rgba(234, 67, 53, 0.35)',
  balcony: 'rgba(52, 168, 83, 0.35)',
  pillar: 'rgba(251, 188, 4, 0.35)',
  parapet: 'rgba(255, 109, 0, 0.35)',
  gate: 'rgba(171, 71, 188, 0.35)',
  roof: 'rgba(0, 172, 193, 0.35)',
  other: 'rgba(158, 158, 158, 0.35)',
}

const LABEL_BORDERS = {
  wall: '#4285F4',
  window: '#EA4335',
  balcony: '#34A853',
  pillar: '#FBBC04',
  parapet: '#FF6D00',
  gate: '#AB47BC',
  roof: '#00ACC1',
  other: '#9E9E9E',
}

export default function SegmentCanvas({ imageUrl, segments, selectedSegmentId, onSegmentClick }) {
  const canvasRef = useRef(null)
  const imgRef = useRef(null)

  useEffect(() => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      imgRef.current = img
      draw()
    }
    img.src = imageUrl
  }, [imageUrl])

  useEffect(() => {
    if (imgRef.current) draw()
  }, [segments, selectedSegmentId])

  const draw = () => {
    const canvas = canvasRef.current
    const img = imgRef.current
    if (!canvas || !img) return

    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight
    const ctx = canvas.getContext('2d')

    // Draw base image
    ctx.drawImage(img, 0, 0)

    // Draw segments
    segments?.forEach((seg) => {
      if (!seg.polygon || seg.polygon.length < 3) return

      const color = LABEL_COLORS[seg.label] || LABEL_COLORS.other
      const border = LABEL_BORDERS[seg.label] || LABEL_BORDERS.other

      // Fill polygon
      ctx.beginPath()
      ctx.moveTo(seg.polygon[0][0], seg.polygon[0][1])
      seg.polygon.forEach(([x, y]) => ctx.lineTo(x, y))
      ctx.closePath()
      ctx.fillStyle = color
      ctx.fill()

      // Border
      ctx.strokeStyle = seg.id === selectedSegmentId ? '#FFFFFF' : border
      ctx.lineWidth = seg.id === selectedSegmentId ? 3 : 2
      ctx.stroke()

      // Label
      const cx = seg.bbox[0] + seg.bbox[2] / 2
      const cy = seg.bbox[1] + seg.bbox[3] / 2
      ctx.font = 'bold 14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillStyle = '#FFFFFF'
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = 3
      ctx.strokeText(seg.label, cx, cy)
      ctx.fillText(seg.label, cx, cy)
    })
  }

  const handleClick = (e) => {
    if (!segments?.length || !canvasRef.current) return
    const rect = canvasRef.current.getBoundingClientRect()
    const scaleX = canvasRef.current.width / rect.width
    const scaleY = canvasRef.current.height / rect.height
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    // Find clicked segment (check if point is inside any polygon)
    for (const seg of segments) {
      if (isPointInPolygon(x, y, seg.polygon)) {
        onSegmentClick?.(seg.id)
        return
      }
    }
    onSegmentClick?.(null)
  }

  return (
    <canvas
      ref={canvasRef}
      onClick={handleClick}
      className="w-full rounded-lg shadow cursor-crosshair"
      style={{ maxHeight: '500px', objectFit: 'contain' }}
    />
  )
}

function isPointInPolygon(x, y, polygon) {
  if (!polygon || polygon.length < 3) return false
  let inside = false
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0], yi = polygon[i][1]
    const xj = polygon[j][0], yj = polygon[j][1]
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside
    }
  }
  return inside
}
