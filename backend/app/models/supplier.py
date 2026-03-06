# 供应商模型 - 供应商信息
from datetime import datetime
from app.extensions import db


class Supplier(db.Model):
    # 供应商模型 - 供应商信息
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    contact = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    # 注意：Asset模型已移除supplier_id字段，移除assets关系
    # 注意：PurchaseRequest模型已移除supplier_id字段，移除purchase_requests关系
    # 注意：consumables关系由Consumable模型通过backref定义，此处不重复定义
    # 这样可以避免backref冲突

    def get_consumables(self):
        """获取该供应商提供的耗材"""
        from app.models.consumable import Consumable
        return Consumable.query.filter_by(supplier_id=self.id).all()

    def get_assets(self):
        """获取该供应商提供的资产（如有需要可通过其他方式关联）"""
        return []  # 目前Asset模型无supplier关联

    def get_purchase_requests(self):
        """获取该供应商的采购申请（如有需要可通过其他方式关联）"""
        return []  # 目前PurchaseRequest模型无supplier关联

    def to_dict(self):
        # 将供应商转换为字典
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
