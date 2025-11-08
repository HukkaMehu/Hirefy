export default function VerifyPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Verification in Progress</h1>
        
        <div className="bg-white rounded-lg shadow p-8">
          <p className="text-gray-500">Real-time agent progress coming soon...</p>
          <p className="text-sm text-gray-400 mt-2">Verification ID: {params.id}</p>
        </div>
      </div>
    </div>
  )
}
