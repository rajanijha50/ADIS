import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");

    if (token) {
      // console.log("Got the token: ", token);
      localStorage.setItem("auth_token", token);
      // Post token to /api/auth/set-token to set the HttpOnly cookie in the current session
      fetch(`${import.meta.env.VITE_SERVER_URL}/api/auth/set-token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token }),
        credentials: "include",
      })
        .then(() => {
          navigate("/");
        })
        .catch((err) => {
          console.error("Failed to set auth cookie:", err);
          navigate("/");
        });
    } else {
      console.error("No token received. Authentication failed.");
      navigate("/auth");
    }
  }, [searchParams, navigate]);

  return (
    <div className="w-screen h-screen flex flex-col items-center justify-center bg-app text-primary">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary mb-4"></div>
      <p className="text-xl">Authenticating...</p>
    </div>
  );
}
