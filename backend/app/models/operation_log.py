"""
OperationLog model for tracking system operations
"""
from datetime import datetime
from app.extensions import db


class OperationLog(db.Model):
    """OperationLog model for tracking system operations"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    object_id = db.Column(db.Integer, nullable=False)
    object_repr = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert operation log to dictionary"""
        return {
            'id': self.id,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None,
            'action': self.action,
            'model': self.model,
            'object_id': self.object_id,
            'object_repr': self.object_repr,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<OperationLog {self.id} - {self.user.username} - {self.action}>'
