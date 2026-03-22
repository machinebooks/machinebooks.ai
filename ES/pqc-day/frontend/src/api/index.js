// Extraído de: LibroPQC/cap-19-dashboard.md
// frontend/src/api/index.js (fragmento)
import api from './axios'

export const dashboardApi = {
  getStats: () => api.get('/dashboard'),
}

export const analysisApi = {
  getJobs: () => api.get('/analysis'),
  getJob: (id) => api.get(`/analysis/${id}`),
  createJob: (data) => api.post('/analysis', data),
  getFindings: (jobId) => api.get(`/analysis/${jobId}/findings`),
  downloadReport: (jobId, format = 'full') =>
    api.get(`/analysis/${jobId}/report?format=${format}`,
      { responseType: 'blob' }),
}

export const complianceApi = {
  getFrameworks: () => api.get('/compliance/frameworks'),
  getAssessments: (params = {}) =>
    api.get('/compliance/assessments', { params }),
  getAISuggestions: (assessmentId) =>
    api.post(`/compliance/assessments/${assessmentId}/ai/suggest-mappings`),
}
