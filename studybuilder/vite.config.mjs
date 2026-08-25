import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'node:child_process'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'

function tokenCompilerPlugin() {
  return {
    name: 'token-compiler-plugin',
    buildStart() {
      try {
        execSync('node scripts/compile-tokens.js', { stdio: 'inherit' })
      } catch (err) {
        console.error('Failed to compile tokens during build:', err)
      }
    },
    handleHotUpdate({ file }) {
      if (file.endsWith('design-tokens.json')) {
        try {
          execSync('node scripts/compile-tokens.js', { stdio: 'inherit' })
        } catch (err) {
          console.error('Failed to compile tokens on HMR:', err)
        }
      }
    },
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: true,
  },
  css: {
    preprocessorOptions: {
      sass: {
        api: 'modern-compiler',
        silenceDeprecations: ['if-function'],
      },
      scss: {
        api: 'modern-compiler',
        silenceDeprecations: ['if-function'],
      },
    },
  },
  plugins: [
    tokenCompilerPlugin(),
    vue(),
    vuetify({ styles: { configFile: 'src/styles/settings.scss' } }),
    {
      name: 'spa-fallback-for-dots',
      configureServer(server) {
        server.middlewares.use((req, _res, next) => {
          // Handle routes with version numbers (e.g., /overview/4.1, /parent-class-overview/1.0)
          // Vite treats dots as file extensions, so we need to handle these specially
          if (req.url.match(/\/\d+\.\d+$/)) {
            req.url = '/'
          }
          next()
        })
      },
    },
  ],
  assetsInclude: ['**/*.md'],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
