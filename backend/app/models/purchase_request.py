"""
PurchaseRequest model for managing purchase applications
"""
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class PurchaseRequest(db.Model):
    """PurchaseRequest model for purchase applications"""
    __tablename__ = 'purchase_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    estimated_price = db.Column(db.Numeric(12, 2), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status enum values
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_PURCHASED = 'purchased'
    STATUS_REJECTED = 'rejected'
    
    def to_dict(self):
        """Convert purchase request to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'applicant': {
                'id': self.applicant.id,
                'username': self.applicant.username
            } if self.applicant else None,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'estimated_price': float(self.estimated_price) if self.estimated_price else None,
            'supplier': {
                'id': self.supplier.id,
                'name': self.supplier.name
            } if self.supplier else None,
            'reason': self.reason,
            'status': self.status,
            'approver': {
                'id': self.approver.id,
                'username': self.approver.username
            } if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PurchaseRequest {self.id} - {self.title}>'
