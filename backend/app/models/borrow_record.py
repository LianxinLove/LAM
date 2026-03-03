"""
BorrowRecord model for managing asset borrowing and returning
"""
from datetime import datetime
from app.extensions import db


class BorrowRecord(db.Model):
    """BorrowRecord model for asset borrowing and returning"""
    __tablename__ = 'borrow_records'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='borrowed', index=True)
    
    # Status enum values
    STATUS_BORROWED = 'borrowed'
    STATUS_RETURNED = 'returned'
    
    def to_dict(self):
        """Convert borrow record to dictionary"""
        return {
            'id': self.id,
            'asset': {
                'id': self.asset.id,
                'name': self.asset.name,
                'code': self.asset.code
            } if self.asset else None,
            'borrower': {
                'id': self.borrower.id,
                'username': self.borrower.username
            } if self.borrower else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'purpose': self.purpose,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<BorrowRecord {self.id} - {self.asset.code}>'
