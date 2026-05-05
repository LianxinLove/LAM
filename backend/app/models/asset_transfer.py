# 资产调拨模型 - 管理资产位置调拨
from datetime import datetime
from app.extensions import db


class AssetTransfer(db.Model):
    """资产调拨模型 - 资产位置调拨"""
    __tablename__ = 'asset_transfers'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    # 原位置（分开存储校区/楼宇/房间）
    from_campus = db.Column(db.String(50), nullable=False)
    from_building = db.Column(db.String(100), nullable=False)
    from_room = db.Column(db.String(50), nullable=True)
    # 新位置（分开存储校区/楼宇/房间）
    to_campus = db.Column(db.String(50), nullable=False)
    to_building = db.Column(db.String(100), nullable=False)
    to_room = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关系定义
    asset = db.relationship('Asset', backref='transfer_requests')
    applicant = db.relationship('User', foreign_keys=[applicant_id])
    approver = db.relationship('User', foreign_keys=[approver_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    # 状态枚举值
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    @property
    def from_location(self):
        """组合原位置字符串"""
        location = f"{self.from_campus} {self.from_building}"
        if self.from_room:
            location += f" {self.from_room}"
        return location

    @property
    def to_location(self):
        """组合新位置字符串"""
        location = f"{self.to_campus} {self.to_building}"
        if self.to_room:
            location += f" {self.to_room}"
        return location

    def to_dict(self):
        """将资产调拨转换为字典"""
        return {
            'id': self.id,
            'asset': {
                'id': self.asset.id,
                'name': self.asset.name,
                'lab_asset_code': self.asset.lab_asset_code
            } if self.asset else None,
            'from_campus': self.from_campus,
            'from_building': self.from_building,
            'from_room': self.from_room,
            'from_location': self.from_location,
            'to_campus': self.to_campus,
            'to_building': self.to_building,
            'to_room': self.to_room,
            'to_location': self.to_location,
            'reason': self.reason,
            'applicant': {
                'id': self.applicant.id,
                'username': self.applicant.username
            } if self.applicant else None,
            'status': self.status,
            'receiver': {
                'id': self.receiver.id,
                'username': self.receiver.username
            } if self.receiver else None,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AssetTransfer {self.id}>'
