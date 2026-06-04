import { useEffect } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { setUser, clearUser } from "../../features/user/userSlice";
import { RootState } from "../../app/store";
import Sidebar from "../Sidebar";
import VoiceAssistantUI from "../assistant/AssistantUI";
import { SendNotification } from "../SendNotification";

export default function MainLayout() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const {pathname} = useLocation();
  const { loading } = useSelector((state: RootState) => state.user);
  const isVoiceUiOpen = useSelector(
    (state: RootState) => state.assistant.isVoiceUiOpen,
  );

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        const headers: HeadersInit = {};
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch(
          `${import.meta.env.VITE_SERVER_URL}/api/auth/me`,
          {
            method: "GET",
            headers: headers,
            credentials: "include",
          },
        );
        const data = await res.json();
        if (res.ok) {
          dispatch(setUser(data));
        } else {
          console.log(data.detail)
          SendNotification(data.detail.toString(), "error")
          dispatch(clearUser());
          navigate("/auth");
        }
      } catch (err: any) {
        console.error("Auth check failed:", err);
        SendNotification(err.toString(), "error")
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

  if (isVoiceUiOpen) {
    return (
      <div className="flex h-screen">
        <VoiceAssistantUI />
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      {!pathname.includes("/settings") && <Sidebar />}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
