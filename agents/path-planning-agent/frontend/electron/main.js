import { app, BrowserWindow, Menu, dialog } from 'electron'
import path from 'path'
import { spawn } from 'child_process'
import os from 'os'
import { fileURLToPath } from 'url'
import fs from 'fs'
import http from 'http'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow = null
let backendProcess = null
let backendPort = 8000
let backendStarted = false

// 日志函数
function log(message) {
  const timestamp = new Date().toISOString()
  console.log(`[${timestamp}] ${message}`)
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    title: '无人机配送路径规划智能体',
    icon: path.join(__dirname, '../public/favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      sandbox: true
    }
  })

  // 加载前端页面
  mainWindow.loadURL(`http://localhost:${backendPort}`)

  // 处理加载失败
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    log(`Failed to load: ${errorCode} - ${errorDescription}`)
    if (!backendStarted) {
      showErrorPage(errorDescription)
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function showErrorPage(errorDescription) {
  const errorHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>启动错误</title>
      <style>
        body { 
          font-family: Arial, sans-serif; 
          padding: 40px; 
          background: #f5f5f5;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
        }
        .error-container {
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          max-width: 600px;
          width: 100%;
        }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        p { color: #666; line-height: 1.6; }
        .code { 
          background: #f8f8f8; 
          padding: 10px; 
          border-radius: 4px; 
          font-family: monospace;
          margin: 10px 0;
          word-break: break-all;
        }
      </style>
    </head>
    <body>
      <div class="error-container">
        <h1>⚠️ 启动失败</h1>
        <p><strong>无法连接到后端服务</strong></p>
        <p>错误信息：${errorDescription}</p>
        <p>可能的原因：</p>
        <ul>
          <li>后端服务未能正确启动</li>
          <li>后端可执行文件缺失或损坏</li>
          <li>端口 ${backendPort} 被占用</li>
        </ul>
        <p>请尝试重新安装应用程序，或联系技术支持。</p>
      </div>
    </body>
    </html>
  `
  mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(errorHtml)}`)
}

function checkBackendAvailable(callback, retries = 30) {
  if (retries <= 0) {
    callback(false)
    return
  }

  const req = http.get(`http://localhost:${backendPort}/api/health`, (res) => {
    if (res.statusCode === 200) {
      callback(true)
    } else {
      setTimeout(() => checkBackendAvailable(callback, retries - 1), 1000)
    }
  })

  req.on('error', () => {
    setTimeout(() => checkBackendAvailable(callback, retries - 1), 1000)
  })

  req.setTimeout(5000, () => {
    req.destroy()
    setTimeout(() => checkBackendAvailable(callback, retries - 1), 1000)
  })
}

function startBackend() {
  const platform = os.platform()
  const exeName = platform === 'win32' ? 'drone-planner.exe' : 'drone-planner'

  log(`Starting backend on platform: ${platform}`)
  log(`Process resourcesPath: ${process.resourcesPath}`)
  log(`App path: ${app.getAppPath()}`)
  log(`__dirname: ${__dirname}`)

  // 尝试多个可能的路径
  const possiblePaths = [
    // 打包后的路径：extraResources 中的文件会放在 resources/ 下
    path.join(process.resourcesPath, 'backend', 'dist', exeName),
    // 开发环境路径
    path.join(__dirname, '../backend/dist', exeName),
    // app.asar.unpacked 中的路径
    path.join(app.getAppPath(), '..', 'backend', 'dist', exeName),
    // 相对于 exe 的路径
    path.join(path.dirname(process.execPath), 'resources', 'backend', 'dist', exeName),
  ]

  let backendPath = null
  for (const p of possiblePaths) {
    log(`Checking path: ${p}`)
    if (fs.existsSync(p)) {
      log(`✓ Found backend at: ${p}`)
      backendPath = p
      break
    }
  }

  if (!backendPath) {
    log(`✗ Backend executable not found!`)
    dialog.showErrorBox(
      '启动失败',
      `无法找到后端服务程序：${exeName}\n\n` +
      `已尝试路径：\n${possiblePaths.join('\n')}\n\n` +
      `请重新安装应用程序。`
    )
    return false
  }

  try {
    // 设置后端工作目录为可执行文件所在目录
    const backendDir = path.dirname(backendPath)
    
    backendProcess = spawn(backendPath, [], {
      cwd: backendDir,  // 设置工作目录
      env: {
        ...process.env,
        PORT: backendPort.toString()
      },
      stdio: ['pipe', 'pipe', 'pipe']
    })

    backendProcess.stdout.on('data', (data) => {
      log(`Backend stdout: ${data.toString().trim()}`)
    })

    backendProcess.stderr.on('data', (data) => {
      log(`Backend stderr: ${data.toString().trim()}`)
    })

    backendProcess.on('error', (error) => {
      log(`Failed to start backend process: ${error.message}`)
      dialog.showErrorBox('后端启动错误', `无法启动后端服务：${error.message}`)
    })

    backendProcess.on('close', (code) => {
      log(`Backend process exited with code ${code}`)
      backendStarted = false
    })

    return true
  } catch (error) {
    log(`Failed to start backend: ${error.message}`)
    dialog.showErrorBox('启动失败', `无法启动后端服务：${error.message}`)
    return false
  }
}

function setupMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            if (backendProcess) backendProcess.kill()
            app.quit()
          }
        }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => {
            dialog.showMessageBox({
              title: '关于',
              message: '无人机配送路径规划智能体 v1.0.0',
              detail: '版权所有 (C) 2026 洗秋人午言\n\n本软件仅供授权用户使用。'
            })
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

app.whenReady().then(() => {
  setupMenu()
  
  const started = startBackend()
  
  if (started) {
    // 等待后端服务可用
    checkBackendAvailable((available) => {
      if (available) {
        log('✓ Backend is ready, creating window...')
        backendStarted = true
        createWindow()
      } else {
        log('✗ Backend failed to start within timeout')
        dialog.showErrorBox(
          '启动失败',
          '后端服务未能在规定时间内启动。\n\n请检查：\n1. 后端可执行文件是否完整\n2. 端口 8000 是否被占用\n3. 系统是否有足够的权限'
        )
        createWindow()
      }
    })
  } else {
    createWindow()
  }
})

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})
