# 实验室资产管理系统数据模型
from app.models.user import User
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.asset import Asset, AssetManagerTransfer
from app.models.consumable import Consumable
from app.models.purchase_request import PurchaseRequest
from app.models.asset_application import AssetApplication
from app.models.asset_transfer import AssetTransfer
from app.models.borrow_record import BorrowRecord
from app.models.pick_record import PickRecord
from app.models.operation_log import OperationLog

__all__ = [
    'User',
    'Category',
    'Supplier',
    'Asset',
    'AssetManagerTransfer',
    'Consumable',
    'PurchaseRequest',
    'AssetApplication',
    'AssetTransfer',
    'BorrowRecord',
    'PickRecord',
    'OperationLog'
]
