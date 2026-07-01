import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { Suspense, lazy } from "react";
import "@/App.css";

import { AuthProvider, useAuth } from "@/context/AuthContext";
import { ThemeProvider, useTheme } from "@/context/ThemeContext";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { Loader2 } from "lucide-react";

import Login from "@/pages/Login";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const AISearch = lazy(() => import("@/pages/AISearch"));
const Compare = lazy(() => import("@/pages/Compare"));
const ComponentLibrary = lazy(() => import("@/pages/ComponentLibrary"));
const ComponentCategory = lazy(() => import("@/pages/ComponentCategory"));
const ProductDetail = lazy(() => import("@/pages/ProductDetail"));
const Documents = lazy(() => import("@/pages/Documents"));
const BOMBuilder = lazy(() => import("@/pages/BOMBuilder"));
const AIAssistant = lazy(() => import("@/pages/AIAssistant"));
const Favorites = lazy(() => import("@/pages/Favorites"));
const RecentSearches = lazy(() => import("@/pages/RecentSearches"));
const Settings = lazy(() => import("@/pages/Settings"));
const Admin = lazy(() => import("@/pages/Admin"));
const NotFound = lazy(() => import("@/pages/NotFound"));

function PageLoader() {
  return (
    <div className="flex h-64 w-full items-center justify-center">
      <Loader2 className="h-5 w-5 animate-spin text-primary" />
    </div>
  );
}

function RootRedirect() {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return null;
  return <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />;
}

function ThemedToaster() {
  const { theme } = useTheme();
  return <Toaster theme={theme} position="top-right" richColors closeButton />;
}

function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<RootRedirect />} />
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/search" element={<AISearch />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/library" element={<ComponentLibrary />} />
          <Route path="/library/:categoryName" element={<ComponentCategory />} />
          <Route path="/product/:productId" element={<ProductDetail />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/bom-builder" element={<BOMBuilder />} />
          <Route path="/assistant" element={<AIAssistant />} />
          <Route path="/favorites" element={<Favorites />} />
          <Route path="/recent-searches" element={<RecentSearches />} />
          <Route path="/settings" element={<Settings />} />
          <Route
            path="/admin"
            element={<ProtectedRoute roles={["admin"]}><Admin /></ProtectedRoute>}
          />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <div className="App">
      <ThemeProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppRoutes />
            <ThemedToaster />
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </div>
  );
}

export default App;
