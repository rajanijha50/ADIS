import { app, BrowserWindow, shell, ipcMain } from 'electron'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { startPythonServer, killPythonServer } from './python_bridge'

const require = createRequire(import.meta.url)
const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null = null
let pendingDeepLink: string | null = null

// Register custom protocol 'adis://'
if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient('adis', process.execPath, [path.resolve(process.argv[1])])
  }
} else {
  app.setAsDefaultProtocolClient('adis')
}

function handleDeepLink(urlStr: string) {
  if (!win) {
    pendingDeepLink = urlStr
    return
  }
  
  try {
    const url = new URL(urlStr)
    const token = url.searchParams.get('token')
    if (token) {
      win.webContents.send('auth-token-received', token)
      if (win.isMinimized()) win.restore()
      win.focus()
    }
  } catch (e) {
    console.error('Error handling deep link URL:', e)
  }
}

// Request single-instance lock to handle deep links correctly on Windows/Linux
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', (event, commandLine) => {
    if (win) {
      if (win.isMinimized()) win.restore()
      win.focus()
    }
    const url = commandLine.find(arg => arg.startsWith('adis://'))
    if (url) {
      handleDeepLink(url)
    }
  })
}

// Handle deep link on macOS when the app is already running
app.on('open-url', (event, url) => {
  event.preventDefault()
  handleDeepLink(url)
})

// IPC Main Handlers
ipcMain.on('open-external-url', (_event, url) => {
  shell.openExternal(url)
})

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'adis.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
    },
  })

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
    if (pendingDeepLink) {
      handleDeepLink(pendingDeepLink)
      pendingDeepLink = null
    }
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.on('will-quit', () => {
  killPythonServer()
})

app.whenReady().then(() => {
  startPythonServer()
  createWindow()
  
  // Check for deep link on startup (Windows/Linux)
  const startUrl = process.argv.find(arg => arg.startsWith('adis://'))
  if (startUrl) {
    handleDeepLink(startUrl)
  }
})
