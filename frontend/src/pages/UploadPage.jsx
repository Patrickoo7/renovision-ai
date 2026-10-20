import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Stepper from '../components/Stepper'
import ImageUploader from '../components/ImageUploader'
import { uploadImage } from '../lib/api'
import { useApi } from '../hooks/useApi'
import { FiArrowRight, FiLoader } from 'react-icons/fi'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const { loading, error, call } = useApi()
  const navigate = useNavigate()

  const handleUpload = async () => {
    if (!file) return
    const data = await call(uploadImage, file)
    navigate(`/segment/${data.project_id}`)
  }

  return (
    <div>
      <Stepper currentStep={1} />
      <div className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">Upload Your House Photo</h2>
        <p className="text-gray-500 text-center mb-8">
          Take a clear front-facing photo of your house exterior
        </p>

        <ImageUploader onFileSelect={setFile} />

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{error}</div>
        )}

        {file && (
          <div className="mt-6 text-center">
            <button onClick={handleUpload} disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-medium
                        inline-flex items-center gap-2 transition shadow-lg disabled:opacity-50">
              {loading ? <><FiLoader className="animate-spin" /> Uploading...</> 
                       : <><FiArrowRight /> Upload & Continue</>}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
