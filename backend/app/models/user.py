"""
User model for authentication and authorization
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # Note: custodian_assets relationship removed - custodian is now a simple string field in Asset model
    purchase_requests = db.relationship('PurchaseRequest', foreign_keys='PurchaseRequest.applicant_id', backref='applicant', lazy='dynamic')
    approved_purchases = db.relationship('PurchaseRequest', foreign_keys='PurchaseRequest.approver_id', backref='approver', lazy='dynamic')
    transfer_requests = db.relationship('AssetTransfer', foreign_keys='AssetTransfer.applicant_id', backref='applicant', lazy='dynamic')
    approved_transfers = db.relationship('AssetTransfer', foreign_keys='AssetTransfer.approver_id', backref='approver', lazy='dynamic')
    borrow_records = db.relationship('BorrowRecord', backref='borrower', lazy='dynamic')
    pick_records = db.relationship('PickRecord', foreign_keys='PickRecord.picker_id', backref='picker', lazy='dynamic')
    approved_picks = db.relationship('PickRecord', foreign_keys='PickRecord.approver_id', backref='approver', lazy='dynamic')
    operation_logs = db.relationship('OperationLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_superuser': self.is_superuser,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
