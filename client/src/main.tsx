import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import ReduxProvider from "./app/ReduxProvider.tsx";

const MS_CLIENT_ID = import.meta.env.VITE_MS_CLIENT_ID;
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

const msalConfig = {
  auth: {
    clientId: MS_CLIENT_ID,
    authority: "https://login.microsoftonline.com/common",
    redirectUri: "http://localhost:5173",
  },
};
const msalInstance = new PublicClientApplication(msalConfig);

ReactDOM.createRoot(document.getElementById("root")!).render(

    <ReduxProvider>
      <MsalProvider instance={msalInstance}>
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
          <App />
        </GoogleOAuthProvider>
      </MsalProvider>
    </ReduxProvider>

);

// Use contextBridge
window.ipcRenderer.on("main-process-message", (_event, message) => {
  console.log(message);
});
