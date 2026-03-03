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
    assets = db.relationship('Asset', backref='supplier', lazy='dynamic')
    consumables = db.relationship('Consumable', backref='supplier', lazy='dynamic')
    purchase_requests = db.relationship('PurchaseRequest', backref='supplier', lazy='dynamic')

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
