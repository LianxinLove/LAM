import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    // 插件配置
    plugins: [react()],

    // 路径别名配置
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@api': path.resolve(__dirname, './src/api'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@types': path.resolve(__dirname, './src/types'),
        '@assets': path.resolve(__dirname, './src/assets'),
        '@styles': path.resolve(__dirname, './src/styles'),
      }
    },
    // 确保 React 被正确处理
    esbuild: {
      jsx: 'automatic',
      jsxImportSource: 'react'
    },

    // 开发服务器配置
    server: {
      port: 3000,
      host: true,
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('proxyReq', (proxyReq, req, res) => {
              // 确保请求头（包括 Cookie）被正确转发
              if (req.headers.cookie) {
                proxyReq.setHeader('Cookie', req.headers.cookie);
              }
            });
            proxy.on('proxyRes', (proxyRes, req, res) => {
              // 确保 Set-Cookie 头被正确转发
              if (proxyRes.headers['set-cookie']) {
                proxyRes.headers['set-cookie'] = proxyRes.headers['set-cookie'].map((cookie: string) => {
                  // 移除 Secure 和 SameSite 属性，以便在 http://localhost 开发环境下正常工作
                  return cookie
                    .replace(/; Secure/gi, '')
                    .replace(/; SameSite=None/gi, '')
                    .replace(/; SameSite=Lax/gi, '; SameSite=Lax');
                });
              }
            });
          },
          // 重写路径（如果后端不需要 /api 前缀）
          // rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/uploads': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
        }
      }
    },

    // 预览服务器配置
    preview: {
      port: 4173,
      host: true,
      open: true
    },

    // CSS 配置
    css: {
      // CSS 代码拆分
      modules: {
        localsConvention: 'camelCase'
      },
      preprocessorOptions: {
        scss: {
          // javascriptEnabled: true
          // 全局 SCSS 变量（如果需要，取消注释并创建文件）
          // additionalData: `@import "@styles/variables.scss";`
        }
      },
      // 开发环境下使用 source map
      devSourcemap: true
    },

    // 构建配置
    build: {
      // 输出目录
      outDir: 'dist',
      // 静态资源目录
      assetsDir: 'assets',
      // 生成源码映射（生产环境使用 false 以减小体积）
      sourcemap: mode === 'development',
      // 构建后是否生成 manifest.json
      manifest: false,
      // chunk 大小警告的限制（KB）
      chunkSizeWarningLimit: 1000,
      // 压缩配置（使用 esbuild，速度更快）
      minify: 'esbuild',
      // 生产环境删除 console 的配置需要使用插件或 terser
      target: 'es2015',
      // Rollup 配置
      rollupOptions: {
        output: {
          // 静态资源命名规则
          chunkFileNames: 'js/[name]-[hash].js',
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const fileName = assetInfo.names?.[0] || assetInfo.name || ''

            // 根据文件类型分类
            if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/i.test(fileName)) {
              return `media/[name]-[hash][extname]`
            }
            if (/\.(png|jpe?g|gif|svg|ico|avif|webp)(\?.*)?$/i.test(fileName)) {
              return `images/[name]-[hash][extname]`
            }
            if (/\.(woff2?|eot|ttf|otf)(\?.*)?$/i.test(fileName)) {
              return `fonts/[name]-[hash][extname]`
            }
            // 默认放在 assets 目录
            return `assets/[name]-[hash][extname]`
          }
        }
      }
    },

    // 依赖优化
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        'antd',
        'axios'
      ],
      exclude: []
    }
  }
})
