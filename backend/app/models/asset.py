# 资产模型 - 管理实验室设备和仪器
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class Asset(db.Model):
    """资产模型 - 实验室设备和仪器"""
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)

    # 课题组资产编号（格式：DC+年份+序号）
    lab_asset_code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    # 学校资产编号（可选）
    school_asset_code = db.Column(db.String(50), nullable=True)
    # 资产名称
    name = db.Column(db.String(200), nullable=False)
    # 资产类型：equipment-仪器设备，software-软件
    asset_type = db.Column(db.String(20), nullable=False, default='equipment', index=True)
    # 型号
    model = db.Column(db.String(100), nullable=False)
    # 规格
    specifications = db.Column(db.Text, nullable=True)
    # 生产厂家
    manufacturer = db.Column(db.String(200), nullable=True)
    # 采购价格
    purchase_price = db.Column(db.Numeric(12, 2), nullable=True)
    # 院系归属
    department = db.Column(db.String(100), nullable=False)
    # 资产现状
    current_status = db.Column(db.String(20), nullable=False, default='in_use', index=True)
    # 存放校区
    campus = db.Column(db.String(50), nullable=False)
    # 存放楼宇
    building = db.Column(db.String(100), nullable=False)
    # 存放房间
    room = db.Column(db.String(50), nullable=True)
    # 采购日期
    purchase_date = db.Column(db.Date, nullable=True)
    # 课题组保管人姓名
    custodian_name = db.Column(db.String(50), nullable=False)
    # 课题组保管人联系电话
    custodian_phone = db.Column(db.String(20), nullable=False)
    # 资产管理人ID（外键）
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 资产全貌照片URL
    photo_full_url = db.Column(db.String(500), nullable=True)
    # 资产型号铭牌近照URL
    photo_model_url = db.Column(db.String(500), nullable=True)
    # 学校固定资产铭牌近照URL
    photo_tag_url = db.Column(db.String(500), nullable=True)
    # 备注
    remarks = db.Column(db.Text, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_assets')
    # 注意：borrow_records和transfer_requests关系由对应模型通过backref定义
    # 这样可以避免backref冲突

    def get_borrow_records(self):
        """获取该资产的借用记录"""
        from app.models.borrow_record import BorrowRecord
        return BorrowRecord.query.filter_by(asset_id=self.id).all()

    def get_transfer_requests(self):
        """获取该资产的调拨申请"""
        from app.models.asset_transfer import AssetTransfer
        return AssetTransfer.query.filter_by(asset_id=self.id).all()

    # 资产类型枚举值
    TYPE_EQUIPMENT = 'equipment'  # 仪器设备
    TYPE_SOFTWARE = 'software'     # 软件

    # 资产现状枚举值
    STATUS_IN_USE = 'in_use'       # 在用
    STATUS_SCRAPPED = 'scrapped'   # 报废
    STATUS_REPAIR = 'repair'       # 报修
    STATUS_RETURNED = 'returned'   # 退库
    STATUS_BORROWED = 'borrowed'   # 外借

    @property
    def is_available(self):
        """检查资产是否可借用"""
        return self.current_status == self.STATUS_IN_USE

    def to_dict_lite(self):
        """将资产转换为简化字典（用于列表展示）"""
        data = {
            'id': self.id,
            'lab_asset_code': self.lab_asset_code,
            'name': self.name,
            'department': self.department,
            'current_status': self.current_status,
            'campus': self.campus,
            'building': self.building,
            'room': self.room,
            'custodian_name': self.custodian_name,
            'manager': {
                'id': self.manager.id,
                'username': self.manager.username
            } if self.manager else None,
        }
        # 存放位置（组合字段，方便前端显示）
        data['location'] = f"{self.campus} {self.building}"
        if self.room:
            data['location'] += f" {self.room}"
        return data

    def to_dict(self, include_details=False):
        """将资产转换为字典"""
        data = {
            'id': self.id,
            'lab_asset_code': self.lab_asset_code,
            'school_asset_code': self.school_asset_code,
            'name': self.name,
            'asset_type': self.asset_type,
            'model': self.model,
            'specifications': self.specifications,
            'manufacturer': self.manufacturer,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'department': self.department,
            'current_status': self.current_status,
            'campus': self.campus,
            'building': self.building,
            'room': self.room,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'custodian_name': self.custodian_name,
            'custodian_phone': self.custodian_phone,
            'manager': {
                'id': self.manager.id,
                'username': self.manager.username
            } if self.manager else None,
            'photo_full_url': self.photo_full_url,
            'photo_model_url': self.photo_model_url,
            'photo_tag_url': self.photo_tag_url,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # 存放位置（组合字段，方便前端显示）
        data['location'] = f"{self.campus} {self.building}"
        if self.room:
            data['location'] += f" {self.room}"

        return data

    def __repr__(self):
        return f'<Asset {self.lab_asset_code} - {self.name}>'


# 资产管理人交接记录模型
class AssetManagerTransfer(db.Model):
    """资产管理人交接记录"""
    __tablename__ = 'asset_manager_transfers'

    id = db.Column(db.Integer, primary_key=True)
    # 资产ID
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    # 原管理人ID
    old_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 新管理人ID
    new_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 交接时间
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 交接原因
    transfer_reason = db.Column(db.Text, nullable=True)
    # 备注
    remarks = db.Column(db.Text, nullable=True)
    # 创建人ID
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    asset = db.relationship('Asset', foreign_keys=[asset_id])
    old_manager = db.relationship('User', foreign_keys=[old_manager_id])
    new_manager = db.relationship('User', foreign_keys=[new_manager_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def to_dict(self):
        """将交接记录转换为字典"""
        return {
            'id': self.id,
            'asset': {
                'id': self.asset.id,
                'lab_asset_code': self.asset.lab_asset_code,
                'name': self.asset.name
            } if self.asset else None,
            'old_manager': {
                'id': self.old_manager.id,
                'username': self.old_manager.username
            } if self.old_manager else None,
            'new_manager': {
                'id': self.new_manager.id,
                'username': self.new_manager.username
            } if self.new_manager else None,
            'transfer_time': self.transfer_time.isoformat() if self.transfer_time else None,
            'transfer_reason': self.transfer_reason,
            'remarks': self.remarks,
            'created_by': {
                'id': self.created_by.id,
                'username': self.created_by.username
            } if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AssetManagerTransfer {self.id}>'
