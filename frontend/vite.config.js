import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'
import os from 'node:os'

const sslDir = path.resolve(__dirname, 'ssl')

function getLanIPs() {
  const ifaces = os.networkInterfaces()
  const ips = []
  for (const name of Object.keys(ifaces)) {
    for (const net of ifaces[name] || []) {
      if (net.family === 'IPv4' && !net.internal) {
        ips.push(net.address)
      }
    }
  }
  return ips
}

const lanIPs = getLanIPs()

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    {
      name: 'inject-lan-ip',
      configureServer(server) {
        server.middlewares.use('/__lan_ips', (_req, res) => {
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(lanIPs))
        })
      },
      configurePreviewServer(server) {
        server.middlewares.use('/__lan_ips', (_req, res) => {
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(lanIPs))
        })
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5175,
    host: true,
    https: process.env.VITE_HTTP === 'true' ? false : {
      cert: fs.readFileSync(path.join(sslDir, 'cert.pem')),
      key: fs.readFileSync(path.join(sslDir, 'key.pem')),
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  }
})
