import { NavLink } from 'react-router-dom'
import { LayoutDashboard, FileImage, Settings } from 'lucide-react'
import clsx from 'clsx'

const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Studies', href: '/studies', icon: FileImage },
    { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
    return (
        <aside className="sidebar-panel w-64">
            <nav className="p-4 space-y-1">
                {navigation.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.href}
                        className={({ isActive }) =>
                            clsx(
                                'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-primary-600 text-white'
                                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                            )
                        }
                    >
                        <item.icon className="w-5 h-5" />
                        {item.name}
                    </NavLink>
                ))}
            </nav>
        </aside>
    )
}