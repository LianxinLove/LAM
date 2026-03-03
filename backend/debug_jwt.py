# 调试 JWT 令牌验证
import sys
import json
from flask import Flask
from flask_jwt_extended import JWTManager, decode_token, create_access_token
from app.config import Config
from app.models import User
from app.extensions import db

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

# 测试令牌
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MDk1NjU1MiwianRpIjoiYjUyZjUzZTctNzUzZi00YjU3LWEwM2UtMzY4ZjUzZjUzZjUzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzQwOTU2NTUyLCJleHAiOjE3NDEwNDI5NTJ9.7xKp9Q3rT7mN8vK2lP5qR6sT8uV1wX2yZ3aB4cD5eF6"

print("=" * 60)
print("JWT 令牌调试")
print("=" * 60)

print(f"\nJWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")
print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config['JWT_ACCESS_TOKEN_EXPIRES']}")

# 尝试解码令牌
try:
    with app.app_context():
        decoded = decode_token(test_token)
        print(f"\n✓ Token decoded successfully!")
        print(f"  Decoded data: {json.dumps(decoded, indent=2)}")
except Exception as e:
    print(f"\n✗ Failed to decode token: {e}")

# 尝试创建新令牌
try:
    with app.app_context():
        user = User.query.get(1)
        if user:
            new_token = create_access_token(identity=user.id)
            print(f"\n✓ New token created successfully!")
            print(f"  User: {user.username}")
            print(f"  Token: {new_token}")

            # 尝试解码新令牌
            decoded_new = decode_token(new_token)
            print(f"  Decoded new token: {json.dumps(decoded_new, indent=2)}")
        else:
            print(f"\n✗ User with ID 1 not found")
except Exception as e:
    print(f"\n✗ Failed to create token: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
