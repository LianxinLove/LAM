# 耗材模型 - 管理实验室用品和材料
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db


class Consumable(db.Model):
    """耗材模型 - 实验室用品和材料"""
    __tablename__ = 'consumables'

    id = db.Column(db.Integer, primary_key=True)
    # 耗材名称
    name = db.Column(db.String(200), nullable=False)
    # 耗材编号（自动生成格式：CON-XXXX）
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    # 类别ID（外键）
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    # 供应商ID（外键，可选）
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    # 品牌
    brand = db.Column(db.String(100), nullable=True)
    # 货号
    product_code = db.Column(db.String(100), nullable=False)
    # CAS号
    cas_number = db.Column(db.String(50), nullable=True)
    # 形态：固体/液体/气体
    form = db.Column(db.String(20), nullable=True)
    # 分类：耗材/试剂
    consumable_type = db.Column(db.String(20), nullable=False, default='consumable')
    # 是否危化品
    is_hazardous = db.Column(db.Boolean, nullable=False, default=False)
    # 规格
    specifications = db.Column(db.String(200), nullable=True)
    # 库存数量
    stock = db.Column(db.Integer, nullable=False, default=0)
    # 最低库存
    min_stock = db.Column(db.Integer, nullable=False, default=10)
    # 课题组保管人
    custodian_name = db.Column(db.String(50), nullable=False)
    # 课题组保管人联系方式
    custodian_phone = db.Column(db.String(20), nullable=False)
    # 产品最早生产日期
    production_date = db.Column(db.Date, nullable=True)
    # 产品保质期
    expiration_date = db.Column(db.Date, nullable=True)
    # 是否过期
    is_expired = db.Column(db.Boolean, nullable=True)
    # 存放区域
    storage_area = db.Column(db.String(100), nullable=True)
    # 存放房间
    room = db.Column(db.String(50), nullable=True)
    # 存放楼宇
    building = db.Column(db.String(100), nullable=True)
    # 存放校区
    campus = db.Column(db.String(50), nullable=True)
    # 单价
    price = db.Column(db.Numeric(10, 2), nullable=True)
    # 备注
    remarks = db.Column(db.Text, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    category = db.relationship('Category', backref='consumables')
    supplier = db.relationship('Supplier', backref='consumables')
    pick_records = db.relationship('PickRecord', backref='item', lazy='dynamic')

    # 形态枚举值
    FORM_SOLID = 'solid'      # 固体
    FORM_LIQUID = 'liquid'    # 液体
    FORM_GAS = 'gas'          # 气体

    # 分类枚举值
    TYPE_CONSUMABLE = 'consumable'  # 耗材
    TYPE_REAGENT = 'reagent'        # 试剂

    @property
    def is_low_stock(self):
        """检查库存是否低于最小值"""
        return self.stock < self.min_stock

    @property
    def check_expired(self):
        """检查产品是否过期"""
        if not self.expiration_date:
            return False
        return date.today() > self.expiration_date

    def to_dict(self):
        """将耗材转换为字典"""
        return {
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
            'brand': self.brand,
            'product_code': self.product_code,
            'cas_number': self.cas_number,
            'form': self.form,
            'consumable_type': self.consumable_type,
            'is_hazardous': self.is_hazardous,
            'specifications': self.specifications,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'custodian_name': self.custodian_name,
            'custodian_phone': self.custodian_phone,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'is_expired': self.is_expired if self.is_expired is not None else self.check_expired,
            'storage_area': self.storage_area,
            'room': self.room,
            'building': self.building,
            'campus': self.campus,
            'price': float(self.price) if self.price else None,
            'remarks': self.remarks,
            'is_low_stock': self.is_low_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Consumable {self.code} - {self.name}>'
