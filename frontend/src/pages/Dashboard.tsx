// frontend/src/pages/Dashboard.tsx
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/services/api'  // Changed from named to default import

interface HealthResponse {
  status: string
  database: string
  timestamp: string
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await apiClient.get<HealthResponse>('api/v1/health')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">
          Error loading health data: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">MedVision AI Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">System Health</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Status:</span>
              <span className={`font-semibold ${
                data?.status === 'healthy' ? 'text-green-400' : 'text-red-400'
              }`}>
                {data?.status || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Database:</span>
              <span className={`font-semibold ${
                data?.database === 'healthy' ? 'text-green-400' : 'text-red-400'
              }`}>
                {data?.database || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Last Check:</span>
              <span className="text-sm text-gray-300">
                {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
          <div className="space-y-2 text-gray-400">
            <p>Coming in Sprint 3</p>
            <p className="text-sm">• Total Studies</p>
            <p className="text-sm">• Active Users</p>
            <p className="text-sm">• Recent Activity</p>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Features</h2>
          <div className="space-y-2 text-gray-400">
            <p className="text-sm">✅ Health Monitoring</p>
            <p className="text-sm">✅ Authentication (Sprint 2)</p>
            <p className="text-sm">✅ Study Management (Sprint 2)</p>
            <p className="text-sm">🔜 DICOM Viewer (Sprint 4)</p>
            <p className="text-sm">🔜 AI Analysis (Sprint 6)</p>
          </div>
        </div>
      </div>
    </div>
  )
}
