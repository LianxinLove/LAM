#!/usr/bin/env python3
"""
补充演示数据脚本
用于统计分析页面的图表展示
"""
from app import create_app
from app.extensions import db
from app.models import User, Asset, Consumable, PurchaseRequest, BorrowRecord, Category
from datetime import datetime, timedelta, timezone
import random

def add_demo_data():
    app = create_app()

    with app.app_context():
        print('=== 开始补充演示数据 ===\n')

        # 获取现有用户
        admin = User.query.filter_by(username='admin').first()
        test_user = User.query.filter_by(username='testuser').first()

        if not admin:
            print('错误: 未找到 admin 用户，请先初始化数据库')
            return

        # 1. 添加采购申请数据（多种状态）
        print('1. 添加采购申请...')
        purchase_data = [
            {
                'title': '采购高性能工作站',
                'item_name': 'Dell Precision 7960',
                'quantity': 5,
                'estimated_price': 75000,
                'reason': '用于AI模型训练，需要高性能计算资源',
                'status': 'pending',
                'applicant': admin
            },
            {
                'title': '采购实验室显微镜',
                'item_name': '奥林巴斯 BX53',
                'quantity': 3,
                'estimated_price': 120000,
                'reason': '生物实验项目需要',
                'status': 'approved',
                'applicant': test_user,
                'approver': admin,
                'approved_at': datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                'title': '采购实验试剂',
                'item_name': 'PCR试剂盒',
                'quantity': 50,
                'estimated_price': 15000,
                'reason': '常规实验消耗品',
                'status': 'purchased',
                'applicant': test_user,
                'approver': admin,
                'approved_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            {
                'title': '采购旧电脑显示器',
                'item_name': '27寸显示器',
                'quantity': 10,
                'estimated_price': 8000,
                'reason': '预算超限，暂不采购',
                'status': 'rejected',
                'applicant': test_user,
                'approver': admin,
                'approved_at': datetime.now(timezone.utc) - timedelta(days=5)
            },
            {
                'title': '采购实验台',
                'item_name': '不锈钢实验台',
                'quantity': 8,
                'estimated_price': 24000,
                'reason': '实验室扩建需要',
                'status': 'pending',
                'applicant': test_user
            },
            {
                'title': '采购离心机',
                'item_name': '高速离心机',
                'quantity': 2,
                'estimated_price': 35000,
                'reason': '生物分离实验需要',
                'status': 'approved',
                'applicant': admin,
                'approver': admin,
                'approved_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
        ]

        for data in purchase_data:
            # 检查是否已存在
            existing = PurchaseRequest.query.filter_by(
                title=data['title'],
                item_name=data['item_name']
            ).first()
            if not existing:
                purchase = PurchaseRequest(
                    title=data['title'],
                    applicant_id=data['applicant'].id,
                    item_name=data['item_name'],
                    quantity=data['quantity'],
                    estimated_price=data['estimated_price'],
                    reason=data['reason'],
                    status=data['status'],
                    approver_id=data.get('approver', {}).id if data.get('approver') else None,
                    approved_at=data.get('approved_at')
                )
                db.session.add(purchase)
                print(f'  + {data["title"]} ({data["status"]})')

        # 2. 更新资产状态，确保每种状态都有数据
        print('\n2. 更新资产状态...')
        assets = Asset.query.all()

        # 确保每种状态至少有一条
        status_updates = [
            (0, 'available'),
            (1, 'in_use'),
            (2, 'maintenance'),
            (3, 'retired'),
        ]

        for i, (asset_idx, new_status) in enumerate(status_updates):
            if i < len(assets):
                old_status = assets[asset_idx].status
                assets[asset_idx].status = new_status
                print(f'  ~ {assets[asset_idx].name}: {old_status} -> {new_status}')

        # 3. 添加借用记录数据
        print('\n3. 添加借用记录...')
        if len(assets) >= 4:
            borrow_data = [
                {
                    'asset': assets[0],  # available
                    'borrower': admin,
                    'purpose': '用于数据分析项目',
                    'status': 'borrowed'
                },
                {
                    'asset': assets[1],  # in_use
                    'borrower': test_user,
                    'purpose': '临时测试使用',
                    'status': 'borrowed'
                },
                {
                    'asset': assets[2],  # maintenance
                    'borrower': test_user,
                    'purpose': '已完成实验',
                    'status': 'returned',
                    'return_date': datetime.now(timezone.utc) - timedelta(days=5)
                },
            ]

            for data in borrow_data:
                # 检查是否已存在
                existing = BorrowRecord.query.filter_by(
                    asset_id=data['asset'].id,
                    borrower_id=data['borrower'].id,
                    purpose=data['purpose']
                ).first()
                if not existing:
                    borrow = BorrowRecord(
                        asset_id=data['asset'].id,
                        borrower_id=data['borrower'].id,
                        purpose=data['purpose'],
                        status=data['status'],
                        return_date=data.get('return_date')
                    )
                    db.session.add(borrow)
                    print(f'  + {data["asset"].name} - {data["borrower"].username} ({data["status"]})')

        # 4. 修改部分耗材库存，创建低库存情况
        print('\n4. 更新耗材库存状态...')
        consumables = Consumable.query.all()

        # 设置前3个耗材为低库存状态
        for i, consumable in enumerate(consumables[:3]):
            if consumable.min_stock >= 5:
                consumable.stock = consumable.min_stock - 2
                print(f'  - {consumable.name}: 库存设为 {consumable.stock} (最低: {consumable.min_stock})')

        # 设置一些耗材的价格（如果未设置）
        print('\n5. 更新耗材价格...')
        price_updates = [
            ('试剂', 150.00),
            ('试管', 2.50),
            ('手套', 45.00),
            ('酒精', 35.00),
            ('滤纸', 80.00),
        ]

        for name, price in price_updates:
            consumable = Consumable.query.filter(Consumable.name.like(f'%{name}%')).first()
            if consumable and not consumable.price:
                consumable.price = price
                print(f'  + {consumable.name}: ¥{price}')

        # 提交所有更改
        db.session.commit()

        print('\n=== 数据统计 ===')
        print(f'采购申请总数: {PurchaseRequest.query.count()}')
        print(f'  - 待审批: {PurchaseRequest.query.filter_by(status="pending").count()}')
        print(f'  - 已审批: {PurchaseRequest.query.filter_by(status="approved").count()}')
        print(f'  - 已采购: {PurchaseRequest.query.filter_by(status="purchased").count()}')
        print(f'  - 已拒绝: {PurchaseRequest.query.filter_by(status="rejected").count()}')

        from sqlalchemy import func
        asset_status = db.session.query(Asset.status, func.count(Asset.id)).group_by(Asset.status).all()
        print(f'\n资产状态分布:')
        for status, count in asset_status:
            print(f'  - {status}: {count}')

        print(f'\n借用记录总数: {BorrowRecord.query.count()}')
        print(f'  - 借用中: {BorrowRecord.query.filter_by(status="borrowed").count()}')
        print(f'  - 已归还: {BorrowRecord.query.filter_by(status="returned").count()}')
        print(f'低库存耗材: {Consumable.query.filter(Consumable.stock < Consumable.min_stock).count()}')

        print('\n=== 演示数据添加完成！===')

if __name__ == '__main__':
    add_demo_data()
