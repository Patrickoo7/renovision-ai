import axios from 'axios'

const API = axios.create({ baseURL: '/api' })

export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return API.post('/upload', formData)
}

export const segmentImage = (projectId) => API.post(`/segment/${projectId}`)

export const updateProjectSegments = (projectId, segments) =>
  API.put(`/project/${projectId}/segments`, { segments })

export const applyMaterials = (projectId, assignments) =>
  API.post('/apply-materials', { project_id: projectId, assignments })

export const getEstimate = (projectId, refSegmentId, refDimensionFt) =>
  API.post('/estimate', {
    project_id: projectId,
    reference_segment_id: refSegmentId,
    reference_dimension_ft: refDimensionFt,
  })

export const getMaterials = () => API.get('/materials')

export const getProject = (projectId) => API.get(`/project/${projectId}`)

export const downloadReport = (projectId) =>
  API.get(`/report/${projectId}`, { responseType: 'blob' })
