import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Auto-detect GitHub Actions environment. 
// If true, deploy to the repo subdirectory. If false (local), serve from root directory.
const isGitHubActions = process.env.GITHUB_ACTIONS === 'true';

export default defineConfig({
  plugins: [react()],
  base: isGitHubActions ? '/country-info-agent/' : '/',
})
