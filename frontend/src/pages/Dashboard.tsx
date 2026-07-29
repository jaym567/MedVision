import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/services/api'

export function Dashboard() {
    const { data: healthData, isLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => apiClient.getHealth(),
    })

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">Dashboard</h2>
                <p className="text-slate-400 mt-1">
                    Welcome to MedVision AI Medical Imaging Workstation
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
                    <h3 className="text-sm font-medium text-slate-400">System Status</h3>
                    <p className="text-2xl font-semibold mt-2">
                        {isLoading ? 'Loading...' : healthData?.status === 'ok' ? 'Healthy' : 'Degraded'}
                    </p>
                </div>

                <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
                    <h3 className="text-sm font-medium text-slate-400">Environment</h3>
                    <p className="text-2xl font-semibold mt-2 capitalize">
                        {isLoading ? 'Loading...' : healthData?.environment || 'Unknown'}
                    </p>
                </div>

                <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
                    <h3 className="text-sm font-medium text-slate-400">Version</h3>
                    <p className="text-2xl font-semibold mt-2">
                        {isLoading ? 'Loading...' : healthData?.version || 'N/A'}
                    </p>
                </div>
            </div>

            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
                <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-4">
                    <button className="px-4 py-3 bg-primary-600 hover:bg-primary-700 rounded-md font-medium transition-colors">
                        Upload Study
                    </button>
                    <button className="px-4 py-3 bg-slate-800 hover:bg-slate-700 rounded-md font-medium transition-colors">
                        View Recent Studies
                    </button>
                </div>
            </div>
        </div>
    )
}