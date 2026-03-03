# 资产模型 - 管理实验室设备和仪器
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class Asset(db.Model):
    # 资产模型 - 实验室设备和仪器
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    specifications = db.Column(db.Text, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='available', index=True)
    location = db.Column(db.String(100), nullable=True)
    custodian = db.Column(db.String(100), nullable=True)  # 保管人名称（字符串）
    custodian_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 已弃用，保留以兼容
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系定义
    borrow_records = db.relationship('BorrowRecord', backref='asset', lazy='dynamic')
    transfer_requests = db.relationship('AssetTransfer', backref='asset', lazy='dynamic')

    # 状态枚举值
    STATUS_AVAILABLE = 'available'
    STATUS_IN_USE = 'in_use'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_RETIRED = 'retired'

    @property
    def is_available(self):
        # 检查资产是否可借用
        return self.status == self.STATUS_AVAILABLE

    def to_dict(self, include_details=False):
        # 将资产转换为字典
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': {
                'id': self.category.id,
                'name': self.category.name
            } if self.category else None,
            'supplier': {
                'id': self.supplier.id,
                'name': self.supplier.name
            } if self.supplier else None,
            'status': self.status,
            'location': self.location,
            'custodian': self.custodian,
            'specifications': self.specifications,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        return data
    
    def __repr__(self):
        return f'<Asset {self.code} - {self.name}>'
