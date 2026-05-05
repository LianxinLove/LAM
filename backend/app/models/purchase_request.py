# 采购申请模型 - 管理采购申请
from datetime import datetime, date
from decimal import Decimal
from app.extensions import db


class PurchaseRequest(db.Model):
    """采购申请模型"""
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True)
    # 序号
    sequence_number = db.Column(db.Integer, nullable=False)
    # 产品名称
    product_name = db.Column(db.String(200), nullable=False)
    # 品牌
    brand = db.Column(db.String(100), nullable=True)
    # 货号
    product_code = db.Column(db.String(100), nullable=False)
    # CAS号
    cas_number = db.Column(db.String(50), nullable=True)
    # 形态（固体/液体/气体/设备）
    form = db.Column(db.String(20), nullable=True)
    # 规格
    specifications = db.Column(db.String(200), nullable=True)
    # 数量
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # 用途
    purpose = db.Column(db.Text, nullable=False)
    # 申请人ID
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 申请项目
    project_name = db.Column(db.String(200), nullable=False)
    # 申请日期
    application_date = db.Column(db.Date, nullable=False)
    # 申请人收货信息
    delivery_info = db.Column(db.Text, nullable=False)
    # 查询单价
    query_price = db.Column(db.Numeric(12, 2), nullable=True)
    # 订购单价
    order_price = db.Column(db.Numeric(12, 2), nullable=True)
    # 订购数量
    order_quantity = db.Column(db.Integer, nullable=True)
    # 到货日期
    delivery_date = db.Column(db.Date, nullable=True)
    # 到货数量
    delivery_quantity = db.Column(db.Integer, nullable=True)
    # 存放校区
    campus = db.Column(db.String(50), nullable=True)
    # 存放楼宇
    building = db.Column(db.String(100), nullable=True)
    # 存放房间
    room = db.Column(db.String(50), nullable=True)
    # 是否危化品平台采购
    is_hazardous_platform = db.Column(db.Boolean, nullable=False, default=False)
    # 是否生科院试剂中心采购
    is_institute_center = db.Column(db.Boolean, nullable=False, default=False)
    # 是否学校仓库采购
    is_school_warehouse = db.Column(db.Boolean, nullable=False, default=False)
    # 质量问题说明及证据
    quality_issue_info = db.Column(db.Text, nullable=True)
    # 备注
    remarks = db.Column(db.Text, nullable=True)
    # 状态
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    # 审批人ID
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # 审批意见
    approval_comment = db.Column(db.Text, nullable=True)
    # 审批时间
    approved_at = db.Column(db.DateTime, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='purchase_requests')
    approver = db.relationship('User', foreign_keys=[approver_id])

    # 状态枚举值
    STATUS_PENDING = 'pending'    # 待审批
    STATUS_APPROVED = 'approved'  # 已审批
    STATUS_PURCHASED = 'purchased'  # 已采购
    STATUS_REJECTED = 'rejected'  # 已拒绝

    def to_dict(self):
        """将采购申请转换为字典"""
        return {
            'id': self.id,
            'sequence_number': self.sequence_number,
            'product_name': self.product_name,
            'brand': self.brand,
            'product_code': self.product_code,
            'cas_number': self.cas_number,
            'form': self.form,
            'specifications': self.specifications,
            'quantity': self.quantity,
            'purpose': self.purpose,
            'applicant': {
                'id': self.applicant.id,
                'username': self.applicant.username
            } if self.applicant else None,
            'project_name': self.project_name,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'delivery_info': self.delivery_info,
            'query_price': float(self.query_price) if self.query_price else None,
            'order_price': float(self.order_price) if self.order_price else None,
            'order_quantity': self.order_quantity,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_quantity': self.delivery_quantity,
            'campus': self.campus,
            'building': self.building,
            'room': self.room,
            'is_hazardous_platform': self.is_hazardous_platform,
            'is_institute_center': self.is_institute_center,
            'is_school_warehouse': self.is_school_warehouse,
            'quality_issue_info': self.quality_issue_info,
            'remarks': self.remarks,
            'status': self.status,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approval_comment': self.approval_comment,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<PurchaseRequest {self.id} - {self.product_name}>'
