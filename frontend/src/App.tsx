import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import VerificationDetail from './pages/VerificationDetail'
import CreateVerification from './pages/CreateVerification'
import CandidatePortal from './pages/CandidatePortal'

function AnimatedRoutes() {
  const location = useLocation()
  
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="verifications/create" element={<CreateVerification />} />
          <Route path="verifications/:sessionId" element={<VerificationDetail />} />
        </Route>
        {/* Candidate portal without layout */}
        <Route path="candidate-portal/:sessionId" element={<CandidatePortal />} />
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return (
    <Router>
      <AnimatedRoutes />
    </Router>
  )
}

export default App
