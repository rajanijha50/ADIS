import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import Auth from "./components/Auth";
import AuthCallback from "./components/AuthCallback";
import Sidebar from "./components/Sidebar";
import HeroSection from "./components/HeroSection";
import MessageContainer from "./components/MessageContainer";
import VoiceAssistantUI from "./components/AssistantUI";
import VoiceAssistantNewUI from "./components/AssistantNewUI";
import Settings from "./components/settings/Settings";
import GeneralSettings from "./components/settings/GeneralSettings";
import AssistantSettings from "./components/settings/AssistantSettings";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setUser, clearUser } from "./features/user/userSlice";
import { RootState } from "./app/store";
import { CustomToaster } from "./components/SendNotification";

const Home = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, loading } = useSelector((state: RootState) => state.user);
  const [opened, setOpened] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/auth/me", {
          method: "GET",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          console.log("logged in: ", data)
          dispatch(setUser(data));
        } else {
          console.log("not logged in: ", res);
          dispatch(clearUser());
          navigate("/auth");
        }
      } catch (err) {
        console.error("Auth check failed:", err);
        dispatch(clearUser());
        navigate("/auth");
      }
    };
    checkAuth();
  }, [dispatch, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-app">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-w-screen min-h-screen flex justify-between overflow-hidden relative">
      <Sidebar />
      {opened ? <VoiceAssistantNewUI setOpened={setOpened} /> : <HeroSection setOpened={setOpened} />}
    </div>
  );
};

const IpcAuthHandler = () => {
  const navigate = useNavigate();

  useEffect(() => {
    if (typeof window !== "undefined" && window.ipcRenderer) {
      const handleAuthToken = (_event: any, token: string) => {
        console.log("Received auth token via IPC:", token);
        navigate(`/api/auth/callback?token=${token}`);
      };

      window.ipcRenderer.on("auth-token-received", handleAuthToken);
    }
  }, [navigate]);

  return null;
};

export default function App() {
  return (
    <BrowserRouter>
      <IpcAuthHandler />
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/api/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={<Home />} />
        <Route path="/settings" element={<Settings />}>
          <Route index element={<Navigate to="general" replace />} />
          <Route path="general" element={<GeneralSettings />} />
          <Route path="assistant" element={<AssistantSettings />} />
        </Route>
      </Routes>
      <CustomToaster />
    </BrowserRouter>

  );
}
