import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { useMsal } from "@azure/msal-react";

export default function Auth() {
  const { instance } = useMsal();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [externalAuthSuccess, setExternalAuthSuccess] = useState(false);
  const navigate = useNavigate();

  const isElectron = typeof window !== "undefined" && !!window.ipcRenderer;

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = isLogin ? "/api/auth/email/login" : "/api/auth/email/signup";
    const body: any = { email, password };
    if (!isLogin) body.full_name = fullName;

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        credentials: "include",
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || "Authentication failed");

      navigate("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    console.log(credentialResponse);
    try {
      const res = await fetch("http://localhost:8000/api/auth/google/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: credentialResponse.credential }),
        credentials: "include",
      });
      const data = await res.json();
      console.log("google auth data: ", data);
      if (!res.ok) throw new Error(data.detail || "Google auth failed");

      const urlParams = new URLSearchParams(window.location.search);
      const isFromElectron = urlParams.get("source") === "electron";

      if (isFromElectron && data.token) {
        setExternalAuthSuccess(true);
        window.location.href = `adis://auth-callback?token=${data.token}`;
      } else {
        navigate("/");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };
  const handleMicrosoftLogin = async () => {
    try {
      const loginResponse = await instance.loginPopup({
        scopes: ["user.read", "openid", "profile", "email"],
      });
      const res = await fetch("http://localhost:8000/api/auth/microsoft/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_token: loginResponse.accessToken }),
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Microsoft auth failed");

      const urlParams = new URLSearchParams(window.location.search);
      const isFromElectron = urlParams.get("source") === "electron";

      if (isFromElectron && data.token) {
        setExternalAuthSuccess(true);
        window.location.href = `adis://auth-callback?token=${data.token}`;
      } else {
        navigate("/");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-app px-4 font-sans relative overflow-hidden text-primary">


      <div className="max-w-md w-full bg-card border border-card rounded-3xl shadow-[0_0_40px_var(--color-shadow-card)] p-8 relative overflow-hidden backdrop-blur-xl animate-fade-in-up">

        {externalAuthSuccess ? (
          <div className="text-center py-8 space-y-6 relative z-10">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-950/30 border border-green-500/40 text-green-400">
              <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-extrabold text-green-400">Successfully Authenticated!</h2>
            <p className="text-sm text-secondary leading-relaxed">
              You have successfully logged in. You can now close this browser tab and return to the ADIS application.
            </p>
            <div className="pt-2">
              <button
                onClick={() => window.close()}
                className="px-6 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 hover:opacity-90 text-white font-semibold rounded-xl transition-all shadow-md cursor-pointer animate-pulse"
              >
                Close Tab
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Toggle Switch */}
            <div className="relative flex p-1 bg-input border border-input rounded-full w-full max-w-[280px] mx-auto mb-6">
              {/* Sliding indicator */}
              <div
                className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-main border border-card rounded-full shadow-[0_0_10px_var(--color-shadow-glow)] transition-transform duration-300 ease-in-out ${isLogin ? "translate-x-0" : "translate-x-[calc(100%+4px)]"
                  }`}
              ></div>

              <button
                onClick={() => {
                  setIsLogin(true);
                  setError("");
                }}
                type="button"
                className={`relative flex-1 py-1.5 text-sm font-semibold transition-colors duration-300 z-10 ${isLogin ? "text-primary" : "text-muted hover:text-secondary"
                  }`}
              >
                Log in
              </button>
              <button
                onClick={() => {
                  setIsLogin(false);
                  setError("");
                }}
                type="button"
                className={`relative flex-1 py-1.5 text-sm font-semibold transition-colors duration-300 z-10 ${!isLogin ? "text-primary" : "text-muted hover:text-secondary"
                  }`}
              >
                Sign up
              </button>
            </div>

            <div className="text-center relative z-10 mb-6 space-y-2">
              <h2 className="text-3xl font-extrabold text-gradient-accent tracking-tight">
                {isLogin ? "Welcome back" : "Create an account"}
              </h2>
              <p className="text-sm text-secondary">
                {isLogin ? "Enter your credentials to continue" : "Join us to get started"}
              </p>
            </div>

            {error && (
              <div className="relative z-10 bg-red-950/40 border border-red-500/30 text-red-200 px-4 py-3 rounded-xl text-sm text-center mb-6 animate-fade-in-up">
                {error}
              </div>
            )}

            <form className="relative z-10" onSubmit={handleEmailAuth}>
              <div className={`transition-all duration-300 ease-in-out overflow-hidden ${isLogin ? 'max-h-0 opacity-0' : 'max-h-[100px] opacity-100'}`}>
                <div className="pb-4">
                  <label className="block text-sm font-medium text-secondary mb-1.5 ml-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required={!isLogin}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-4 py-3 bg-[var(--color-bg-input)] text-primary rounded-xl border border-[var(--color-border-input)] focus:border-[var(--color-border-input-focus)] focus:bg-[var(--color-bg-input-focus)] focus:ring-1 focus:ring-[var(--color-focus-glow)] transition-all outline-none placeholder-[var(--color-text-placeholder)] shadow-inner"
                    placeholder="John Doe"
                    tabIndex={isLogin ? -1 : 0}
                  />
                </div>
              </div>

              <div className="pb-4">
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5 ml-1">
                  Email address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-[var(--color-bg-input)] text-primary rounded-xl border border-[var(--color-border-input)] focus:border-[var(--color-border-input-focus)] focus:bg-[var(--color-bg-input-focus)] focus:ring-1 focus:ring-[var(--color-focus-glow)] transition-all outline-none placeholder-[var(--color-text-placeholder)] shadow-inner"
                  placeholder="you@example.com"
                />
              </div>

              <div className="pb-6">
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5 ml-1">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-[var(--color-bg-input)] text-primary rounded-xl border border-[var(--color-border-input)] focus:border-[var(--color-border-input-focus)] focus:bg-[var(--color-bg-input-focus)] focus:ring-1 focus:ring-[var(--color-focus-glow)] transition-all outline-none placeholder-[var(--color-text-placeholder)] shadow-inner"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 px-4 bg-gradient-to-r from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] hover:opacity-90 text-[var(--color-bg-app)] font-bold rounded-xl transition-all flex justify-center items-center shadow-[0_4px_14px_0_var(--color-shadow-glow)] hover:shadow-[0_6px_20px_var(--color-focus-glow)] hover:-translate-y-0.5"
              >
                {loading ? (
                  <svg
                    className="animate-spin h-5 w-5 text-[var(--color-bg-app)]"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                ) : isLogin ? (
                  "Submit"
                ) : (
                  "Create Account"
                )}
              </button>
            </form>

            <div className="relative flex items-center py-6 z-10">
              <div className="flex-grow border-t border-[var(--color-border-divider)]"></div>
              <span className="flex-shrink-0 mx-4 text-[var(--color-text-muted)] text-sm font-medium">
                or continue with
              </span>
              <div className="flex-grow border-t border-[var(--color-border-divider)]"></div>
            </div>

            <div className="space-y-4 relative z-10">
              <div className="flex justify-center flex-col items-center gap-3 w-full">
                {isElectron ? (
                  <>
                    <button
                      onClick={() => {
                        window.ipcRenderer.send(
                          "open-external-url",
                          "http://localhost:5173/auth?source=electron"
                        );
                      }}
                      type="button"
                      className="w-full bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 py-2.5 px-4 rounded-xl flex items-center justify-center gap-3 transition-all duration-200 cursor-pointer shadow-sm"
                    >
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path
                          fill="#4285F4"
                          d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v3.92h6.69a5.74 5.74 0 0 1-2.49 3.77v3.12h4.02c2.35-2.16 3.7-5.35 3.7-9.03z"
                        />
                        <path
                          fill="#34A853"
                          d="M12 24c3.24 0 5.97-1.08 7.96-2.91l-4.02-3.12c-1.12.75-2.55 1.19-3.94 1.19-3.03 0-5.6-2.05-6.52-4.82H1.31v3.23A12 12 0 0 0 12 24z"
                        />
                        <path
                          fill="#FBBC05"
                          d="M5.48 14.34a7.15 7.15 0 0 1 0-4.68V6.43H1.31a12 12 0 0 0 0 11.14l4.17-3.23z"
                        />
                        <path
                          fill="#EA4335"
                          d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0A12 12 0 0 0 1.31 6.43l4.17 3.23c.92-2.77 3.49-4.82 6.52-4.82z"
                        />
                      </svg>
                      <span className="text-sm font-semibold">
                        Sign in with Google
                      </span>
                    </button>

                    <button
                      onClick={() => {
                        window.ipcRenderer.send(
                          "open-external-url",
                          "http://localhost:5173/auth?source=electron"
                        );
                      }}
                      type="button"
                      className="w-full bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 py-2.5 px-4 rounded-xl flex items-center justify-center gap-3 transition-all duration-200 cursor-pointer shadow-sm"
                    >
                      <img src="/microsoft.svg" alt="Microsoft" className="w-5 h-5" />
                      <span className="text-sm font-semibold">
                        Sign in with Microsoft
                      </span>
                    </button>
                  </>
                ) : (
                  <>
                    <div className="w-full flex justify-center">
                      <GoogleLogin
                        onSuccess={handleGoogleSuccess}
                        onError={() => setError("Google Login Failed")}
                        theme="outline"
                        size="large"
                        shape="rectangular"
                        width="100%"
                        type="standard"
                        text="signin_with"
                      />
                    </div>

                    <button
                      onClick={handleMicrosoftLogin}
                      type="button"
                      className="w-full bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 cursor-pointer shadow-sm"
                    >
                      <img src="/microsoft.svg" alt="Microsoft" className="w-5 h-5" />
                      <span className="text-sm font-semibold">
                        Sign in with Microsoft
                      </span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
