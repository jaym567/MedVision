// frontend/src/App.tsx (update)
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ToastProvider from './components/ToastProvider';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Studies from './pages/Studies';
import CreateStudy from './pages/CreateStudy';
import StudyDetail from './pages/StudyDetail';
import { useAuthStore } from './stores/authStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

const ProtectedLayout = ({ children }: { children: React.ReactNode }) => (
  <>
    <Header />
    <main className="min-h-screen bg-gray-900 pt-16">
      {children}
    </main>
  </>
);

const RootRedirect = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider />
      <BrowserRouter>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<RootRedirect />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <Dashboard />
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/studies"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <Studies />
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/studies/new"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <CreateStudy />
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/studies/:id"
              element={
                <ProtectedRoute>
                  <ProtectedLayout>
                    <StudyDetail />
                  </ProtectedLayout>
                </ProtectedRoute>
              }
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
