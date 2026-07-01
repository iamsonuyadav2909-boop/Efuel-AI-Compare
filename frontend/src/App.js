import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import "@/App.css";

import { AuthProvider, useAuth } from "@/context/AuthContext";
import { ThemeProvider, useTheme } from "@/context/ThemeContext";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";

import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Dashboard from "@/pages/Dashboard";
import AISearch from "@/pages/AISearch";
import Compare from "@/pages/Compare";
import ComponentLibrary from "@/pages/ComponentLibrary";
import ComponentCategory from "@/pages/ComponentCategory";
import ProductDetail from "@/pages/ProductDetail";
import Documents from "@/pages/Documents";
import BOMBuilder from "@/pages/BOMBuilder";
import AIAssistant from "@/pages/AIAssistant";
import Favorites from "@/pages/Favorites";
import RecentSearches from "@/pages/RecentSearches";
import Settings from "@/pages/Settings";
import Admin from "@/pages/Admin";
import NotFound from "@/pages/NotFound";

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
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

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
