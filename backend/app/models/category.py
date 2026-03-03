"""
Category model for asset classification
"""
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    """Category model for organizing assets and consumables"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    parent = db.relationship('Category', remote_side=[id], backref='children')
    assets = db.relationship('Asset', backref='category', lazy='dynamic')
    consumables = db.relationship('Consumable', backref='category', lazy='dynamic')
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'parent': {
                'id': self.parent.id,
                'name': self.parent.name
            } if self.parent else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'
