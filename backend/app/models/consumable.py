"""
Consumable model for managing lab supplies and materials
"""
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class Consumable(db.Model):
    """Consumable model for lab supplies and materials"""
    __tablename__ = 'consumables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    unit = db.Column(db.String(20), nullable=False, default='个')
    stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock = db.Column(db.Integer, nullable=False, default=10)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    pick_records = db.relationship('PickRecord', backref='item', lazy='dynamic')
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum"""
        return self.stock < self.min_stock
    
    def to_dict(self):
        """Convert consumable to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'category': {
                'id': self.category.id,
                'name': self.category.name
            } if self.category else None,
            'supplier': {
                'id': self.supplier.id,
                'name': self.supplier.name
            } if self.supplier else None,
            'unit': self.unit,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'price': float(self.price) if self.price else None,
            'location': self.location,
            'is_low_stock': self.is_low_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Consumable {self.code} - {self.name}>'
