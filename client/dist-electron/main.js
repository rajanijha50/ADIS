import { app, ipcMain, shell, BrowserWindow } from "electron";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { spawn, execSync } from "child_process";
import fs from "node:fs";
let pyProcess = null;
function killProcessOnPort(port) {
  try {
    console.log(`[Python Bridge] Checking if port ${port} is already in use...`);
    if (process.platform === "win32") {
      const output = execSync(`netstat -ano`).toString();
      const lines = output.split("\r\n");
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 5 && (parts[1].endsWith(`:${port}`) || parts[1].endsWith(`127.0.0.1:${port}`))) {
          const pid = parts[parts.length - 1];
          if (pid && pid !== "0") {
            console.log(`[Python Bridge] Port ${port} in use by PID ${pid}. Killing it...`);
            execSync(`taskkill /f /pid ${pid}`);
          }
        }
      }
    } else {
      try {
        execSync(`lsof -t -i:${port} | xargs kill -9`);
        console.log(`[Python Bridge] Port ${port} processes killed.`);
      } catch (e) {
      }
    }
  } catch (err) {
  }
}
function startPythonServer() {
  killProcessOnPort(8e3);
  const appRoot = process.env.APP_ROOT || path.join(__dirname, "..");
  const serverPath = path.resolve(appRoot, "..", "server");
  console.log("[Python Bridge] Server path resolved to:", serverPath);
  if (!fs.existsSync(serverPath)) {
    console.error(`[Python Bridge] Server directory not found at ${serverPath}`);
    return;
  }
  let pythonExec = "python";
  const isWin = process.platform === "win32";
  const venvPythonWin = path.join(serverPath, ".adis", "Scripts", "python.exe");
  const venvPythonUnix = path.join(serverPath, ".adis", "bin", "python");
  if (isWin && fs.existsSync(venvPythonWin)) {
    pythonExec = venvPythonWin;
    console.log("[Python Bridge] Using Windows virtualenv Python:", venvPythonWin);
  } else if (!isWin && fs.existsSync(venvPythonUnix)) {
    pythonExec = venvPythonUnix;
    console.log("[Python Bridge] Using Unix virtualenv Python:", venvPythonUnix);
  } else {
    console.log("[Python Bridge] Virtualenv Python not found. Falling back to system python.");
  }
  const args = ["-m", "uvicorn", "main:app", "--port", "8000"];
  console.log(`[Python Bridge] Starting FastAPI server: ${pythonExec} ${args.join(" ")}`);
  try {
    pyProcess = spawn(pythonExec, args, {
      cwd: serverPath,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
      shell: false
      // Spawn directly so pyProcess.pid is the actual Python process
    });
    pyProcess.stdout.on("data", (data) => {
      const msg = data.toString().trim();
      if (msg) {
        console.log(`[FastAPI stdout] ${msg}`);
      }
    });
    pyProcess.stderr.on("data", (data) => {
      const msg = data.toString().trim();
      if (msg) {
        console.error(`[FastAPI stderr] ${msg}`);
      }
    });
    pyProcess.on("close", (code) => {
      console.log(`[Python Bridge] FastAPI process exited with code ${code}`);
      pyProcess = null;
      console.log("[Python Bridge] Server stopped. Quitting Electron app...");
      app.quit();
    });
    pyProcess.on("error", (err) => {
      console.error("[Python Bridge] Failed to start FastAPI process:", err);
      app.quit();
    });
  } catch (error) {
    console.error("[Python Bridge] Error spawning FastAPI process:", error);
    app.quit();
  }
}
function killPythonServer() {
  if (pyProcess) {
    console.log("[Python Bridge] Killing FastAPI server process...");
    try {
      if (process.platform === "win32") {
        execSync(`taskkill /pid ${pyProcess.pid} /t /f`);
      } else {
        pyProcess.kill("SIGINT");
      }
    } catch (err) {
      console.error("[Python Bridge] Error killing process:", err);
    }
    pyProcess = null;
  }
}
process.on("exit", () => {
  killPythonServer();
});
createRequire(import.meta.url);
const __dirname$1 = path.dirname(fileURLToPath(import.meta.url));
process.env.APP_ROOT = path.join(__dirname$1, "..");
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
const MAIN_DIST = path.join(process.env.APP_ROOT, "dist-electron");
const RENDERER_DIST = path.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, "public") : RENDERER_DIST;
let win = null;
let pendingDeepLink = null;
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient("adis", process.execPath, [path.resolve(process.argv[1])]);
  }
} else {
  app.setAsDefaultProtocolClient("adis");
}
function handleDeepLink(urlStr) {
  if (!win) {
    pendingDeepLink = urlStr;
    return;
  }
  try {
    const url = new URL(urlStr);
    const token = url.searchParams.get("token");
    if (token) {
      win.webContents.send("auth-token-received", token);
      if (win.isMinimized()) win.restore();
      win.focus();
    }
  } catch (e) {
    console.error("Error handling deep link URL:", e);
  }
}
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on("second-instance", (event, commandLine) => {
    if (win) {
      if (win.isMinimized()) win.restore();
      win.focus();
    }
    const url = commandLine.find((arg) => arg.startsWith("adis://"));
    if (url) {
      handleDeepLink(url);
    }
  });
}
app.on("open-url", (event, url) => {
  event.preventDefault();
  handleDeepLink(url);
});
ipcMain.on("open-external-url", (_event, url) => {
  shell.openExternal(url);
});
function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, "adis.png"),
    webPreferences: {
      preload: path.join(__dirname$1, "preload.mjs")
    }
  });
  win.webContents.on("did-finish-load", () => {
    win == null ? void 0 : win.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
    if (pendingDeepLink) {
      handleDeepLink(pendingDeepLink);
      pendingDeepLink = null;
    }
  });
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL);
  } else {
    win.loadFile(path.join(RENDERER_DIST, "index.html"));
  }
}
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
    win = null;
  }
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
app.on("will-quit", () => {
  killPythonServer();
});
app.whenReady().then(() => {
  startPythonServer();
  createWindow();
  const startUrl = process.argv.find((arg) => arg.startsWith("adis://"));
  if (startUrl) {
    handleDeepLink(startUrl);
  }
});
export {
  MAIN_DIST,
  RENDERER_DIST,
  VITE_DEV_SERVER_URL
};
