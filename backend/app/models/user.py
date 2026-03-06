# 用户模型 - 认证和授权
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """用户模型 - 用于认证"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义 - 注意：不需要显式定义反向关系，因为backref已在目标模型中定义
    # 这些关系由目标模型的 backref 自动创建
    # - purchase_requests (作为申请人的采购申请)
    # - approved_purchases (作为审批人的采购申请)
    # - transfer_requests (作为申请人的调拨申请)
    # - approved_transfers (作为审批人的调拨申请)
    # - borrow_records (借用记录)
    # - pick_records (作为领用人的记录)
    # - approved_picks (作为审批人的领用记录)
    # - operation_logs (操作日志)
    # - managed_assets (管理的资产)
    # - asset_applications (资产业务申请)

    def set_password(self, password):
        """对密码进行哈希并设置"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查提供的密码是否与哈希匹配"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """将用户转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_superuser': self.is_superuser,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
