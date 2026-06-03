import { spawn, execSync } from 'child_process'
import path from 'node:path'
import fs from 'node:fs'
import { app } from 'electron'

let pyProcess: any = null

function killProcessOnPort(port: number) {
  try {
    console.log(`[Python Bridge] Checking if port ${port} is already in use...`)
    if (process.platform === 'win32') {
      const output = execSync(`netstat -ano`).toString()
      const lines = output.split('\r\n')
      for (const line of lines) {
        const parts = line.trim().split(/\s+/)
        // parts format: [ 'TCP', '127.0.0.1:8000', '0.0.0.0:0', 'LISTENING', '1234' ]
        if (parts.length >= 5 && (parts[1].endsWith(`:${port}`) || parts[1].endsWith(`127.0.0.1:${port}`))) {
          const pid = parts[parts.length - 1]
          if (pid && pid !== '0') {
            console.log(`[Python Bridge] Port ${port} in use by PID ${pid}. Killing it...`)
            execSync(`taskkill /f /pid ${pid}`)
          }
        }
      }
    } else {
      try {
        execSync(`lsof -t -i:${port} | xargs kill -9`)
        console.log(`[Python Bridge] Port ${port} processes killed.`)
      } catch (e) {
        // ignore if lsof fails or returns nothing
      }
    }
  } catch (err) {
    // Port not in use or error querying, ignore
  }
}

export function startPythonServer() {
  // Free the port first to prevent address conflicts
  killProcessOnPort(8000)

  const appRoot = process.env.APP_ROOT || path.join(__dirname, '..')
  const serverPath = path.resolve(appRoot, '..', 'server')

  console.log('[Python Bridge] Server path resolved to:', serverPath)

  if (!fs.existsSync(serverPath)) {
    console.error(`[Python Bridge] Server directory not found at ${serverPath}`)
    return
  }

  // Determine python executable path
  let pythonExec = 'python'
  const isWin = process.platform === 'win32'
  const venvPythonWin = path.join(serverPath, '.adis', 'Scripts', 'python.exe')
  const venvPythonUnix = path.join(serverPath, '.adis', 'bin', 'python')

  if (isWin && fs.existsSync(venvPythonWin)) {
    pythonExec = venvPythonWin
    console.log('[Python Bridge] Using Windows virtualenv Python:', venvPythonWin)
  } else if (!isWin && fs.existsSync(venvPythonUnix)) {
    pythonExec = venvPythonUnix
    console.log('[Python Bridge] Using Unix virtualenv Python:', venvPythonUnix)
  } else {
    console.log('[Python Bridge] Virtualenv Python not found. Falling back to system python.')
  }

  const args = ['-m', 'uvicorn', 'main:app', '--port', '8000']
  console.log(`[Python Bridge] Starting FastAPI server: ${pythonExec} ${args.join(' ')}`)

  try {
    pyProcess = spawn(pythonExec, args, {
      cwd: serverPath,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
      shell: false // Spawn directly so pyProcess.pid is the actual Python process
    })

    pyProcess.stdout.on('data', (data: any) => {
      const msg = data.toString().trim()
      if (msg) {
        console.log(`[FastAPI stdout] ${msg}`)
      }
    })

    pyProcess.stderr.on('data', (data: any) => {
      const msg = data.toString().trim()
      if (msg) {
        console.error(`[FastAPI stderr] ${msg}`)
      }
    })

    pyProcess.on('close', (code: number) => {
      console.log(`[Python Bridge] FastAPI process exited with code ${code}`)
      pyProcess = null
      // "make it simple like, any of the client or server stops. both will stop"
      console.log('[Python Bridge] Server stopped. Quitting Electron app...')
      app.quit()
    })

    pyProcess.on('error', (err: any) => {
      console.error('[Python Bridge] Failed to start FastAPI process:', err)
      app.quit()
    })

  } catch (error) {
    console.error('[Python Bridge] Error spawning FastAPI process:', error)
    app.quit()
  }
}

export function killPythonServer() {
  if (pyProcess) {
    console.log('[Python Bridge] Killing FastAPI server process...')
    try {
      if (process.platform === 'win32') {
        execSync(`taskkill /pid ${pyProcess.pid} /t /f`)
      } else {
        pyProcess.kill('SIGINT')
      }
    } catch (err) {
      console.error('[Python Bridge] Error killing process:', err)
    }
    pyProcess = null
  }
}

// Handle clean exit if Electron main process gets terminated
process.on('exit', () => {
  killPythonServer()
})
