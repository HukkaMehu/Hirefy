import { motion } from 'framer-motion'
import VerificationList from '@/components/VerificationList'
import PageTransition from '@/components/PageTransition'

export default function Dashboard() {
  return (
    <PageTransition>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        <VerificationList />
      </motion.div>
    </PageTransition>
  )
}
