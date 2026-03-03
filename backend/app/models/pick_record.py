"""
PickRecord model for managing consumable picking requests
"""
from datetime import datetime
from app.extensions import db


class PickRecord(db.Model):
    """PickRecord model for consumable picking requests"""
    __tablename__ = 'pick_records'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('consumables.id'), nullable=False)
    picker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status enum values
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    def to_dict(self):
        """Convert pick record to dictionary"""
        return {
            'id': self.id,
            'item': {
                'id': self.item.id,
                'name': self.item.name,
                'code': self.item.code
            } if self.item else None,
            'picker': {
                'id': self.picker.id,
                'username': self.picker.username
            } if self.picker else None,
            'quantity': self.quantity,
            'purpose': self.purpose,
            'status': self.status,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PickRecord {self.id} - {self.item.code}>'
