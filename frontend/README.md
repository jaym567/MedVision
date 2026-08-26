# MedVision AI - Frontend

Production-quality React frontend for medical imaging workstation with JWT authentication, study management, and DICOM viewer interface.

## 🚀 Features (Sprint 3)

### Authentication & Security
- **User Registration**: Full name, email, password, role selection (Radiologist/Technician/Administrator)
- **Secure Login**: JWT token-based authentication with localStorage persistence
- **Protected Routes**: Automatic redirect to login for unauthenticated access
- **Session Management**: Token validation with automatic logout on expiry
- **PHI Warnings**: Safety notices on forms for research/mock data use

### Study Management
- **Create Studies**: Form with nested patient + study data, full validation
- **List Studies**: Paginated table with filters (patient name, modality, status)
- **Study Details**: Three-column workstation layout with patient summary, study details, metadata viewer
- **Status Tracking**: Visual badges for study lifecycle (created, uploaded, processing, ready, failed, archived)

### User Experience
- **Dashboard**: Welcome stats (total/ready/recent studies), quick actions, recent studies list, feature previews
- **Toast Notifications**: User feedback for all actions (success, error, info)
- **Loading States**: Spinners for async operations
- **Error Handling**: ErrorBoundary for crashes, ErrorState components with retry
- **Empty States**: Contextual messages with actions
- **Form Validation**: Client-side validation before API calls
- **Dark Theme**: Medical workstation UI (gray-900 background)

### Sprint 4-7 Previews
- **DICOM Viewer** (Sprint 4): Placeholder in study detail center panel
- **AI Analysis** (Sprint 5): Placeholder in study detail right sidebar
- **Reports** (Sprint 6): Placeholder in study detail right sidebar
- **AI Copilot** (Sprint 7): Placeholder in study detail right sidebar

## 🛠️ Tech Stack

- **React 18** + **TypeScript** (strict mode)
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing with protected routes
- **React Query v5**: Server state management, caching, invalidation
- **Zustand**: Client auth state with localStorage persistence
- **Axios**: HTTP client with interceptors for JWT and error handling
- **react-hot-toast**: Toast notifications
- **date-fns**: Date formatting and manipulation
- **Lucide React**: Icon library
- **Tailwind CSS**: Utility-first styling

## 📦 Installation

```bash
cd frontend
npm install
🔧 Configuration
Create .env file:

env
VITE_API_BASE_URL=http://localhost:8000/api/v1
🚀 Development
bash
npm run dev
# Opens http://localhost:5174
🏗️ Build
bash
npm run build
# Outputs to frontend/dist
📁 Project Structure
python
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ErrorBoundary.tsx
│   │   ├── ErrorState.tsx
│   │   ├── EmptyState.tsx
│   │   ├── FormButton.tsx
│   │   ├── FormInput.tsx
│   │   ├── Header.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── SafetyNotice.tsx
│   │   ├── StatusBadge.tsx
│   │   └── ToastProvider.tsx
│   ├── hooks/              # React Query hooks
│   │   ├── useAuth.ts
│   │   ├── useCreateStudy.ts
│   │   ├── useStudies.ts
│   │   ├── useStudy.ts
│   │   └── useUpdateStudy.ts
│   ├── pages/              # Route components
│   │   ├── CreateStudy.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Studies.tsx
│   │   └── StudyDetail.tsx
│   ├── services/           # API clients
│   │   ├── api.ts          # Axios instance with interceptors
│   │   ├── authApi.ts      # Auth endpoints
│   │   └── studiesApi.ts   # Study CRUD endpoints
│   ├── stores/             # Zustand stores
│   │   └── authStore.ts    # Auth state with persistence
│   ├── types/              # TypeScript interfaces
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── patient.ts
│   │   ├── study.ts
│   │   └── user.ts
│   ├── utils/              # Utility functions
│   │   ├── date.ts         # Date formatting, age calculation
│   │   ├── formatting.ts   # Display formatters
│   │   └── validation.ts   # Form validation helpers
│   ├── App.tsx             # Route configuration
│   └── main.tsx            # React entry point
└── package.json
🧩 Component Library
Form Components
FormInput: Text/email/password/textarea with label, validation, error display
FormButton: Primary/secondary/danger variants with loading state
Feedback Components
LoadingSpinner: sm/md/lg sizes for async operations
EmptyState: No data state with optional action button
ErrorState: Error display with retry button
SafetyNotice: Yellow PHI warning banner
StatusBadge: Colored study status indicators
ToastProvider: Global toast notifications
Layout Components
Header: User avatar, name, role, logout button
ProtectedRoute: Auth guard wrapper for routes
ErrorBoundary: Page-level crash recovery
🔑 Authentication Flow
Register: POST /api/v1/auth/register → Success toast → Redirect to /login
Login: POST /api/v1/auth/login → TokenResponse → Save to localStorage → Redirect to /dashboard
Protected Requests: Authorization header with Bearer token from localStorage
401 Response: Clear auth state → Redirect to /login (unless already on /login or /register)
Logout: Clear localStorage → Clear React Query cache → Redirect to /login → Toast
📊 React Query Keys
['health']: Health check
['currentUser']: Current authenticated user
['validateSession']: Token validation
['studies', filters]: Paginated study list with filters
['study', id]: Individual study detail
🎨 UI Patterns
Medical Dark Theme: gray-900 background, gray-800 cards, blue accents
Consistent Spacing: Tailwind spacing scale (p-4, p-6, p-8)
Focus States: Blue ring on interactive elements
Hover Effects: Subtle transitions on buttons/cards
Loading Priority: Skeleton states → LoadingSpinner → Data
Error Recovery: ErrorState with retry, ErrorBoundary for crashes
🧪 Manual Testing
See Phase 10 testing checklist in checkpoint for comprehensive test scenarios covering:

Registration/login flows
Dashboard stats and navigation
Study CRUD operations
Form validation
Loading/error/empty states
Protected routes
Token expiry
ErrorBoundary
🔗 API Integration
Backend API base: http://localhost:8000/api/v1

Endpoints Used:
POST /auth/register: User registration
POST /auth/login: User authentication
GET /auth/me: Current user details
POST /auth/logout: Session termination
GET /studies: List studies (with pagination/filters)
GET /studies/{id}: Study details
POST /studies: Create study
PATCH /studies/{id}: Update study
🚧 Future Enhancements (Sprint 4+)
DICOM viewer with viewport controls
AI model inference and visualization
Report generation and management
AI copilot chat interface
Skeleton loaders for tables
Debounced search
Date range picker
CSV export
Breadcrumb navigation
Keyboard shortcuts
📝 License
MIT

