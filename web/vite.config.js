import { defineConfig } from 'vite'
import svgLoader from 'vite-svg-loader'

export default defineConfig({
  server: {
    port: 5173
  },
  plugins: [
    svgLoader({ defaultImport: 'raw' }),
  ],
  build: {
    outDir: '../static/dist',
    rollupOptions: {
      input: {
        index: 'src/main.js',
        autofilter: 'src/autofilter.js',
      },
      output: {
        entryFileNames: `assets/[name].js`,
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`
      }
    }
  }
})
