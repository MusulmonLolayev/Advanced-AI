import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The studio server (serve_presenter.py) answers on 8080. `npm run dev` proxies everything the app reads to it;
// `npm run build` writes to ../static/app, which the server already serves at /studio-static/app/.
const server = 'http://127.0.0.1:8080'
const proxy = Object.fromEntries(
  ['/api', '/studio-static', '/narration', '/lecture', '/m7_lecture', '/edit'].map((p) => [p, { target: server, changeOrigin: true }]),
)

export default defineConfig({
  base: '/studio-static/app/',
  plugins: [react()],
  build: { outDir: '../static/app', emptyOutDir: true },
  server: { port: 5173, proxy },
})
