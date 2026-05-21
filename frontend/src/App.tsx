import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { MainLayout } from './components/layout/MainLayout';
import { FunctionalView } from './pages/FunctionalView';
import { DataView } from './pages/DataView';
import { InterfaceView } from './pages/InterfaceView';
import { ProcessFlowView } from './pages/ProcessFlowView';
import { QAView } from './pages/QAView';
import { QAWrite } from './pages/QAWrite';
import { QADetail } from './pages/QADetail';
import { SettingsView } from './pages/SettingsView';
import { MemberManagementView } from './pages/MemberManagementView';
import { useAuthStore } from './store/authStore';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function ProtectedTeamRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user);
  
  if (!user?.teamCode) {
    return <Navigate to="/onboarding" replace />;
  }
  
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const isAdmin = useAuthStore((state) => state.user?.isAdmin);
  
  if (!isAdmin) {
    return <Navigate to="/functional" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth & Onboarding Routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/onboarding" 
          element={
            <ProtectedRoute>
              <OnboardingPage />
            </ProtectedRoute>
          } 
        />
        
        {/* Main App Routes */}
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <ProtectedTeamRoute>
                <MainLayout />
              </ProtectedTeamRoute>
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/functional" replace />} />
          <Route path="functional" element={<FunctionalView />} />
          <Route path="data" element={<DataView />} />
          <Route path="interface" element={<InterfaceView />} />
          <Route path="process-flow" element={<ProcessFlowView />} />
          <Route path="qa">
            <Route index element={<QAView />} />
            <Route path="write" element={<QAWrite />} />
            <Route path=":id" element={<QADetail />} />
          </Route>
          <Route path="settings" element={<SettingsView />} />
          <Route 
            path="members" 
            element={
              <AdminRoute>
                <MemberManagementView />
              </AdminRoute>
            } 
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
