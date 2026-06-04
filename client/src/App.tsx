import {
  Routes,
  Route,
  Navigate,
  useNavigate,
  HashRouter,
} from "react-router-dom";
import { useEffect } from "react";
import { CustomToaster } from "./components/SendNotification";
import Auth from "./components/Auth";
import AuthCallback from "./components/AuthCallback";
import HeroSection from "./components/HeroSection";
import MessageContainer from "./components/MessageContainer";
import Settings from "./components/settings/Settings";
import GeneralSettings from "./components/settings/GeneralSettings";
import AssistantSettings from "./components/settings/AssistantSettings";
import MainLayout from "./components/layout/MainLayout";

const IpcAuthHandler = () => {
  const navigate = useNavigate();

  useEffect(() => {
    if (typeof window !== "undefined" && window.ipcRenderer) {
      const handleAuthToken = (_event: any, token: string) => {
        // console.log("Received auth token via IPC:", token);
        navigate(`/auth/callback?token=${token}`);
      };

      window.ipcRenderer.on("auth-token-received", handleAuthToken);
    }
  }, [navigate]);

  return null;
};

export default function App() {
  return (
    <HashRouter>
      <IpcAuthHandler />
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/auth/callback" element={<AuthCallback />} />

        <Route element={<MainLayout />}>
          <Route path="/" element={<HeroSection />} />
          <Route path="/chat/:session_id" element={<MessageContainer />} />
          <Route path="/settings" element={<Settings />}>
            <Route index element={<Navigate to="general" replace />} />
            <Route path="general" element={<GeneralSettings />} />
            <Route path="assistant" element={<AssistantSettings />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <CustomToaster />
    </HashRouter>
  );
}
