import { Activity } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function Login() {
    const navigate = useNavigate()

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault()
        // TODO: Implement authentication
        navigate('/dashboard')
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center gap-2 mb-4">
                        <Activity className="w-10 h-10 text-primary-500" />
                        <h1 className="text-3xl font-bold">MedVision AI</h1>
                    </div>
                    <p className="text-slate-400">
                        Medical Imaging Workstation
                    </p>
                </div>

                <div className="bg-slate-900 rounded-lg p-8 border border-slate-800">
                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Username
                            </label>
                            <input
                                type="text"
                                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                                placeholder="Enter username"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Password
                            </label>
                            <input
                                type="password"
                                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                                placeholder="Enter password"
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-md font-medium transition-colors"
                        >
                            Sign In
                        </button>
                    </form>

                    <p className="text-center text-sm text-slate-500 mt-6">
                        Authentication will be implemented in the next phase
                    </p>
                </div>
            </div>
        </div>
    )
}