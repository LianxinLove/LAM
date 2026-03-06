# 类别模型 - 资产分类
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    """类别模型 - 组织资产和耗材"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    parent = db.relationship('Category', remote_side=[id], backref='children')
    # 注意：Asset模型已移除category_id字段，移除assets关系
    # 注意：consumables关系由Consumable模型通过backref定义，此处不重复定义
    # 这样可以避免backref冲突

    def get_consumables(self):
        """获取该类别下的所有耗材"""
        from app.models.consumable import Consumable
        return Consumable.query.filter_by(category_id=self.id).all()

    def to_dict(self):
        """将类别转换为字典"""
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
