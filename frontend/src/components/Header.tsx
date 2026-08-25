// frontend/src/components/Header.tsx
import { LogOut } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { formatRole, getUserInitials } from '../utils/formatting';

const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated || !user) {
    return (
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">MedVision AI</h1>
        </div>
      </header>
    );
  }

  const initials = getUserInitials(user.full_name);
  const roleDisplay = formatRole(user.role);

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">MedVision AI</h1>

        <div className="flex items-center gap-4">
          {/* User Info */}
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
              <span className="text-white font-semibold text-sm">{initials}</span>
            </div>

            {/* Name and Role */}
            <div className="text-right">
              <p className="text-sm font-medium text-white">{user.full_name}</p>
              <p className="text-xs text-gray-400">{roleDisplay}</p>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title="Logout"
          >
            <LogOut size={18} />
            <span className="text-sm">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
