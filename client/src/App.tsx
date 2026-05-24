import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setUser, clearUser } from "./features/user/userSlice";
import { RootState } from "./app/store";
import { CustomToaster } from "./components/SendNotification";
import Auth from "./components/Auth";
import AuthCallback from "./components/AuthCallback";
import HeroSection from "./components/HeroSection";
import MessageContainer from "./components/MessageContainer";
import VoiceAssistantNewUI from "./components/AssistantNewUI";
import Settings from "./components/settings/Settings";
import GeneralSettings from "./components/settings/GeneralSettings";
import AssistantSettings from "./components/settings/AssistantSettings";
import MainLayout from "./components/layout/MainLayout";

const Home = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state: RootState) => state.user);
  const [opened, setOpened] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/auth/me`, {
          method: "GET",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          dispatch(setUser(data));
        } else {
          console.log("not logged in: ", res);
          dispatch(clearUser());
          navigate("/auth");
        }
      } catch (err) {
        console.error("Auth check failed:", err);
        dispatch(clearUser());
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
    <div className="w-full h-full flex flex-col justify-between overflow-hidden relative">
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
        <Route path="/auth/callback" element={<AuthCallback />} />

        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/chat/:session_id" element={<MessageContainer />} />
        </Route>
        <Route path="/settings" element={<Settings />}>
          <Route index element={<Navigate to="general" replace />} />
          <Route path="general" element={<GeneralSettings />} />
          <Route path="assistant" element={<AssistantSettings />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <CustomToaster />
    </BrowserRouter>

  );
}
