import { useState, useRef } from 'react'
import { FiUploadCloud, FiImage, FiX } from 'react-icons/fi'

export default function ImageUploader({ onFileSelect, maxSize = 10 * 1024 * 1024 }) {
  const [dragActive, setDragActive] = useState(false)
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState(null)
  const [fileName, setFileName] = useState('')
  const inputRef = useRef(null)

  const validateFile = (file) => {
    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
      return 'Only JPG and PNG files are allowed'
    }
    if (file.size > maxSize) {
      return `File too large (max ${Math.round(maxSize / 1024 / 1024)}MB)`
    }
    return null
  }

  const handleFile = (file) => {
    setError(null)
    const err = validateFile(file)
    if (err) {
      setError(err)
      return
    }
    setFileName(file.name)
    setPreview(URL.createObjectURL(file))
    onFileSelect(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0])
  }

  const clear = () => {
    setPreview(null)
    setFileName('')
    setError(null)
    onFileSelect(null)
  }

  return (
    <div className="w-full">
      {preview ? (
        <div className="relative rounded-xl overflow-hidden border-2 border-blue-200 bg-white">
          <img src={preview} alt="Preview" className="w-full max-h-96 object-contain bg-gray-50" />
          <button onClick={clear}
            className="absolute top-3 right-3 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 shadow">
            <FiX />
          </button>
          <div className="px-4 py-2 bg-blue-50 text-sm text-blue-700 flex items-center gap-2">
            <FiImage /> {fileName}
          </div>
        </div>
      ) : (
        <div
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-16 text-center cursor-pointer transition-all
            ${dragActive ? 'border-blue-500 bg-blue-50 scale-[1.02]' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
          `}
        >
          <FiUploadCloud className="text-5xl mx-auto mb-4 text-blue-400" />
          <p className="text-lg font-medium text-gray-700">Drop your house exterior photo here</p>
          <p className="text-sm text-gray-400 mt-2">or click to browse — JPG, PNG up to 10MB</p>
        </div>
      )}
      {error && <p className="mt-3 text-red-500 text-sm bg-red-50 px-4 py-2 rounded-lg">{error}</p>}
      <input ref={inputRef} type="file" accept="image/jpeg,image/png" className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
    </div>
  )
}
