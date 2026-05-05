# 资产业务申请模型 - 管理资产相关业务申请
from datetime import datetime
import json
from app.extensions import db


class AssetApplication(db.Model):
    """资产业务申请模型 - 处理保管人变更、资产调拨、设备维修、资产处置等业务"""
    __tablename__ = 'asset_applications'

    id = db.Column(db.Integer, primary_key=True)
    # 资产ID
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    # 申请类型：custodian_change保管人变更、allocation资产调拨、repair设备维修、return退库、scrap报废、loss报失报损
    application_type = db.Column(db.String(30), nullable=False, index=True)
    # 申请人ID
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 申请人姓名（冗余字段，方便查询）
    applicant_name = db.Column(db.String(50), nullable=False)
    # 申请时间
    application_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 状态
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    # 申请内容（JSON格式，存储不同类型申请的具体信息）
    content = db.Column(db.Text, nullable=False)
    # 审批意见
    approval_comment = db.Column(db.Text, nullable=True)
    # 审批人ID
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # 审批时间
    approval_time = db.Column(db.DateTime, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    asset = db.relationship('Asset', backref='applications')
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='asset_applications')
    approver = db.relationship('User', foreign_keys=[approver_id])

    # 申请类型枚举值
    TYPE_CUSTODIAN_CHANGE = 'custodian_change'  # 保管人变更
    TYPE_ALLOCATION = 'allocation'              # 资产调拨
    TYPE_REPAIR = 'repair'                      # 设备维修
    TYPE_RETURN = 'return'                      # 退库
    TYPE_SCRAP = 'scrap'                        # 报废
    TYPE_LOSS = 'loss'                          # 报失报损

    # 状态枚举值
    STATUS_PENDING = 'pending'      # 待审批
    STATUS_APPROVED = 'approved'    # 已审批
    STATUS_REJECTED = 'rejected'    # 已拒绝
    STATUS_PROCESSING = 'processing'  # 处理中
    STATUS_COMPLETED = 'completed'  # 已完成

    def set_content(self, data):
        """设置申请内容（将字典转换为JSON字符串）"""
        self.content = json.dumps(data, ensure_ascii=False)

    def get_content(self):
        """获取申请内容（将JSON字符串转换为字典）"""
        if self.content:
            return json.loads(self.content)
        return {}

    def to_dict(self):
        """将申请转换为字典"""
        return {
            'id': self.id,
            'asset': {
                'id': self.asset.id,
                'lab_asset_code': self.asset.lab_asset_code,
                'name': self.asset.name
            } if self.asset else None,
            'application_type': self.application_type,
            'applicant': {
                'id': self.applicant.id,
                'username': self.applicant.username
            } if self.applicant else None,
            'applicant_name': self.applicant_name,
            'application_time': self.application_time.isoformat() if self.application_time else None,
            'status': self.status,
            'content': self.get_content(),
            'approval_comment': self.approval_comment,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<AssetApplication {self.id} - {self.application_type}>'
