import { Activity } from 'lucide-react'

export function Header() {
    return (
        <header className="toolbar justify-between">
            <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-primary-500" />
                <h1 className="text-lg font-semibold">MedVision AI</h1>
            </div>

            <div className="flex items-center gap-4">
                <span className="text-sm text-slate-400">
                    Dr. Smith
                </span>
                <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium">
                    DS
                </div>
            </div>
        </header>
    )
}