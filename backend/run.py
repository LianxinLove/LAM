# 应用程序入口点
#
# 功能说明：
# - 使用应用工厂模式创建 Flask 应用
# - 加载配置
# - 启动开发服务器
#
# 技术要点：
# - 应用工厂模式：create_app() 函数创建应用
# - 配置分离：通过 config 字典选择配置类
# - 开发服务器：仅用于开发，生产环境应使用 WSGI 服务器
#
# 使用方式：
#     python run.py              # 开发环境
#     FLASK_ENV=production python run.py  # 生产环境
#
# 生产环境部署：
#     推荐使用 Gunicorn 或 uWSGI：
#     gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

from app import create_app
from app.config import config

# 创建 Flask 应用
# 技术要点：
# - config['default'] 根据环境选择配置
# - 开发环境：DevelopmentConfig（调试模式开启）
# - 生产环境：ProductionConfig（调试模式关闭）
app = create_app(config['default'])

if __name__ == '__main__':
    # """
    # 开发服务器启动
    #
    # 技术要点：
    # - host='0.0.0.0': 监听所有网络接口，允许外部访问
    # - port=5000: 监听端口
    # - debug=True: 开启调试模式（代码修改自动重载，错误显示详细信息）
    #
    # 注意：
    # - 此开发服务器不适合生产环境
    # - 生产环境应使用 Gunicorn、uWSGI 等 WSGI 服务器
    # """
    app.run(host='0.0.0.0', port=5000, debug=True)
