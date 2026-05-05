/**
 * 图片URL处理工具
 */

/**
 * 获取完整的图片URL
 *
 * 开发环境：通过 Vite 代理访问 /uploads 路径
 * 生产环境：直接使用相对路径（由 Nginx 或服务器配置处理）
 *
 * @param url - 后端返回的图片URL（可能是相对路径）
 * @returns 完整的图片URL
 */
export function getImageUrl(url: string | null | undefined): string {
  if (!url) return '';

  // 如果已经是完整URL（http:// 或 https://），直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // 开发环境：确保 /uploads 路径通过代理访问
  // 生产环境：Nginx 应该配置了 /uploads 的反向代理
  return url;
}

/**
 * 获取多个图片URL的完整路径
 */
export function getImageUrls(urls: (string | null | undefined)[]): string[] {
  return urls.map(url => getImageUrl(url)).filter(Boolean);
}
