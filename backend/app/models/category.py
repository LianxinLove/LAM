# 类别模型 - 资产分类
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    # 类别模型 - 组织资产和耗材
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    parent = db.relationship('Category', remote_side=[id], backref='children')
    assets = db.relationship('Asset', backref='category', lazy='dynamic')
    consumables = db.relationship('Consumable', backref='category', lazy='dynamic')

    def to_dict(self):
        # 将类别转换为字典
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'parent': {
                'id': self.parent.id,
                'name': self.parent.name
            } if self.parent else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'
