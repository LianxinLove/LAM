/**
 * 文件上传 API
 */

import axios from 'axios';

// 创建专用的上传实例，不设置默认的 Content-Type
const uploadApi = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 60000, // 上传文件可能需要更长时间
  withCredentials: true,
});

// 响应拦截器
uploadApi.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error.response?.data || error);
  }
);

/**
 * 上传图片
 * @param file 图片文件
 * @returns 图片URL
 */
export async function uploadImage(file: File): Promise<{ success: boolean; data: { url: string; filename: string }; message: string }> {
  const formData = new FormData();
  formData.append('file', file);

  // 不要设置 Content-Type，让浏览器自动设置 multipart/form-data boundary
  return uploadApi.post('/upload/image', formData);
}

/**
 * 批量上传图片
 * @param files 图片文件数组
 * @returns 图片URL列表
 */
export async function uploadImages(files: File[]): Promise<{ success: boolean; data: { files: Array<{ url: string; filename: string }> }; message: string }> {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  return uploadApi.post('/upload/images', formData);
}
