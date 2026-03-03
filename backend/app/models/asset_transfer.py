# 资产调拨模型 - 管理资产位置调拨
from datetime import datetime
from app.extensions import db


class AssetTransfer(db.Model):
    # 资产调拨模型 - 资产位置调拨
    __tablename__ = 'asset_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 状态枚举值
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    def to_dict(self):
        # 将资产调拨转换为字典
        return {
            'id': self.id,
            'asset': {
                'id': self.asset.id,
                'name': self.asset.name,
                'code': self.asset.code
            } if self.asset else None,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'reason': self.reason,
            'applicant': {
                'id': self.applicant.id,
                'username': self.applicant.username
            } if self.applicant else None,
            'status': self.status,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AssetTransfer {self.id} - {self.asset.code}>'
