import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import UploadPage from './pages/UploadPage'
import SegmentPage from './pages/SegmentPage'
import DesignPage from './pages/DesignPage'
import CostPage from './pages/CostPage'
import ReportPage from './pages/ReportPage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/segment/:projectId" element={<SegmentPage />} />
        <Route path="/design/:projectId" element={<DesignPage />} />
        <Route path="/cost/:projectId" element={<CostPage />} />
        <Route path="/report/:projectId" element={<ReportPage />} />
      </Routes>
    </Layout>
  )
}
