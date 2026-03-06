# 测试数据填充脚本
"""
用于生成测试数据的脚本

运行方式：
    flask shell
    >>> exec(open('seed_data.py', encoding='utf-8').read())
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from random import choice, randint, uniform
from app.extensions import db
from app.models import User, Asset, Consumable, Category, Supplier, PurchaseRequest
from app.models import AssetTransfer, BorrowRecord, PickRecord


def seed_users():
    """创建测试用户"""
    print("正在创建用户...")

    users_data = [
        {'username': 'admin', 'email': 'admin@lam.com', 'is_superuser': True},
        {'username': '张伟', 'email': 'zhangwei@lam.com', 'is_superuser': True},
        {'username': '李娜', 'email': 'lina@lam.com', 'is_superuser': False},
        {'username': '王芳', 'email': 'wangfang@lam.com', 'is_superuser': False},
        {'username': '刘洋', 'email': 'liuyang@lam.com', 'is_superuser': False},
        {'username': '陈静', 'email': 'chenjing@lam.com', 'is_superuser': False},
        {'username': '赵强', 'email': 'zhaoqiang@lam.com', 'is_superuser': False},
        {'username': '孙丽', 'email': 'sunli@lam.com', 'is_superuser': False},
    ]

    users = []
    for data in users_data:
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            user = User(**data)
            user.set_password('123456')  # 默认密码
            db.session.add(user)
        users.append(user)

    db.session.commit()
    print(f"已创建 {len(users)} 个用户")
    return users


def seed_categories():
    """创建测试类别"""
    print("正在创建类别...")

    categories_data = [
        '通用试剂',
        '有机溶剂',
        '无机盐',
        '缓冲液',
        '培养基',
        '色谱耗材',
        '实验器皿',
        '防护用品',
        '移液器',
        '离心管',
    ]

    categories = []
    for name in categories_data:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name)
            db.session.add(cat)
        categories.append(cat)

    db.session.commit()
    print(f"已创建 {len(categories)} 个类别")
    return categories


def seed_suppliers():
    """创建测试供应商"""
    print("正在创建供应商...")

    suppliers_data = [
        {'name': '国药集团化学试剂有限公司', 'contact': '张经理', 'phone': '010-12345678', 'email': 'sales@sinopharm.com'},
        {'name': '西格玛奥德里奇（上海）贸易有限公司', 'contact': '李经理', 'phone': '021-87654321', 'email': 'order@sigma.com'},
        {'name': '北京索莱宝科技有限公司', 'contact': '王经理', 'phone': '010-11112222', 'email': 'info@solarbio.com'},
        {'name': '赛默飞世尔科技（中国）有限公司', 'contact': '刘经理', 'phone': '400-1234567', 'email': 'china@thermo.com'},
        {'name': '广州赛国生物科技有限公司', 'contact': '陈经理', 'phone': '020-33334444', 'email': 'sales@saiguo.com'},
        {'name': '上海麦克林生化科技有限公司', 'contact': '赵经理', 'phone': '021-55556666', 'email': 'order@macklin.com'},
        {'name': '北京鼎国昌盛生物技术有限责任公司', 'contact': '孙经理', 'phone': '010-77778888', 'email': 'sales@dingguo.com'},
        {'name': '阿拉丁试剂（上海）有限公司', 'contact': '周经理', 'phone': '400-8888888', 'email': 'service@aladdin.com'},
    ]

    suppliers = []
    for data in suppliers_data:
        supplier = Supplier.query.filter_by(name=data['name']).first()
        if not supplier:
            supplier = Supplier(**data)
            db.session.add(supplier)
        suppliers.append(supplier)

    db.session.commit()
    print(f"已创建 {len(suppliers)} 个供应商")
    return suppliers


def seed_assets(users):
    """创建测试资产"""
    print("正在创建资产...")

    equipment_names = [
        '离心机', 'PCR仪', '电泳仪', '显微镜', '分光光度计',
        '高压灭菌锅', '超净工作台', '培养箱', '摇床', '涡旋振荡器',
        '天平', 'pH计', '水浴锅', '超声波清洗器', '冷冻干燥机',
        '液相色谱仪', '气相色谱仪', '质谱仪', '酶标仪', '流式细胞仪',
    ]

    models = ['TGL-16M', 'PCR-9600', 'DYY-6C', 'BX53', 'UV-1800',
              'LDZM-80KCS', 'SW-CJ-1F', 'LRH-250', 'HZQ-Q', 'XH-C',
              'BT-125D', 'PHS-3C', 'HH-4', 'KQ-300DE', 'FD-1A-50',
              'LC-20AT', 'GC-2014', 'API 3200', 'Multiskan MK3', 'FACSCalibur']

    manufacturers = [
        '湖南湘仪', '杭州朗基', '北京六一', '奥林巴斯', '岛津',
        '申安医疗器械', '苏净安泰', '上海一恒', '太仓强乐', '江苏康健',
        '赛多利斯', '上海精密', '江苏金坛', '昆山市超声', '北京博医康',
        '岛津', '岛津', 'AB Sciex', 'Thermo', 'BD'
    ]

    departments = ['化学系', '生物系', '物理系', '材料科学系', '环境科学系']
    campuses = ['紫金港校区', '玉泉校区', '西溪校区', '华家池校区']
    buildings = ['教十楼', '教三楼', '实验楼A', '实验楼B', '科研楼']
    custodians = ['张伟', '李娜', '王芳', '刘洋', '陈静', '赵强', '孙丽']

    statuses = ['in_use', 'borrowed', 'repair', 'returned', 'scrapped']
    status_weights = [0.6, 0.15, 0.1, 0.1, 0.05]  # 加权随机

    assets = []
    asset_count = 50  # 创建50个资产

    for i in range(asset_count):
        # 生成资产编号
        year = 2023 + (i // 20)
        asset_num = (i % 20) + 1
        lab_asset_code = f"DC{year}{asset_num:03d}"
        school_asset_code = f"ZJ{year}{asset_num:04d}" if i % 3 == 0 else None

        # 加权随机选择状态
        rand = uniform(0, 1)
        cumulative = 0
        current_status = 'in_use'
        for status, weight in zip(statuses, status_weights):
            cumulative += weight
            if rand <= cumulative:
                current_status = status
                break

        purchase_date = date(2023, 1, 1) + timedelta(days=randint(0, 730))

        asset_data = {
            'lab_asset_code': lab_asset_code,
            'school_asset_code': school_asset_code,
            'name': equipment_names[i % len(equipment_names)],
            'asset_type': 'equipment',
            'model': models[i % len(models)],
            'specifications': f'标准配置，功率{randint(100, 2000)}W',
            'manufacturer': manufacturers[i % len(manufacturers)],
            'purchase_price': Decimal(str(round(uniform(500, 500000), 2))),
            'department': departments[i % len(departments)],
            'current_status': current_status,
            'campus': campuses[i % len(campuses)],
            'building': buildings[i % len(buildings)],
            'room': f'{randint(1, 5)}0{randint(1, 9)}',
            'purchase_date': purchase_date,
            'custodian_name': custodians[i % len(custodians)],
            'custodian_phone': f'13{randint(0, 9)}{randint(1000, 9999)}{randint(1000, 9999)}',
            'manager_id': users[i % len(users)].id,
        }

        asset = Asset.query.filter_by(lab_asset_code=lab_asset_code).first()
        if not asset:
            asset = Asset(**asset_data)
            db.session.add(asset)
        assets.append(asset)

    db.session.commit()
    print(f"已创建 {len(assets)} 个资产")
    return assets


def seed_consumables(categories, suppliers):
    """创建测试耗材"""
    print("正在创建耗材...")

    consumables_data = [
        {'name': '乙醇', 'code': 'CON-0001', 'product_code': 'ETH-500', 'cas_number': '64-17-5', 'form': 'liquid',
         'consumable_type': 'reagent', 'is_hazardous': True, 'specifications': '500ml',
         'price': Decimal('25.00'), 'category_idx': 1},
        {'name': '甲醇', 'code': 'CON-0002', 'product_code': 'MET-500', 'cas_number': '67-56-1', 'form': 'liquid',
         'consumable_type': 'reagent', 'is_hazardous': True, 'specifications': '500ml',
         'price': Decimal('30.00'), 'category_idx': 1},
        {'name': '异丙醇', 'code': 'CON-0003', 'product_code': 'IPA-500', 'cas_number': '67-63-0', 'form': 'liquid',
         'consumable_type': 'reagent', 'is_hazardous': True, 'specifications': '500ml',
         'price': Decimal('28.00'), 'category_idx': 1},
        {'name': '氯化钠', 'code': 'CON-0004', 'product_code': 'NACL-500', 'cas_number': '7647-14-5', 'form': 'solid',
         'consumable_type': 'reagent', 'is_hazardous': False, 'specifications': '500g',
         'price': Decimal('45.00'), 'category_idx': 2},
        {'name': 'PBS缓冲液', 'code': 'CON-0005', 'product_code': 'PBS-1L', 'cas_number': None, 'form': 'liquid',
         'consumable_type': 'reagent', 'is_hazardous': False, 'specifications': '1L',
         'price': Decimal('60.00'), 'category_idx': 3},
        {'name': 'LB培养基', 'code': 'CON-0006', 'product_code': 'LB-500', 'cas_number': None, 'form': 'solid',
         'consumable_type': 'reagent', 'is_hazardous': False, 'specifications': '500g',
         'price': Decimal('120.00'), 'category_idx': 4},
        {'name': 'C18色谱柱', 'code': 'CON-0007', 'product_code': 'C18-4.6', 'cas_number': None, 'form': 'solid',
         'consumable_type': 'consumable', 'is_hazardous': False, 'specifications': '4.6×250mm',
         'price': Decimal('3500.00'), 'category_idx': 5},
        {'name': '0.22μm滤膜', 'code': 'CON-0008', 'product_code': 'FLT-022', 'cas_number': None, 'form': 'solid',
         'consumable_type': 'consumable', 'is_hazardous': False, 'specifications': '50片/盒',
         'price': Decimal('80.00'), 'category_idx': 5},
        {'name': 'EP管', 'code': 'CON-0009', 'product_code': 'EP-1.5', 'cas_number': None, 'form': 'solid',
         'consumable_type': 'consumable', 'is_hazardous': False, 'specifications': '1.5ml',
         'price': Decimal('35.00'), 'category_idx': 6},
        {'name': '乳胶手套', 'code': 'CON-0010', 'product_code': 'GLV-L', 'cas_number': None, 'form': 'solid',
         'consumable_type': 'consumable', 'is_hazardous': False, 'specifications': 'L号',
         'price': Decimal('45.00'), 'category_idx': 7},
    ]

    custodians = ['张伟', '李娜', '王芳', '刘洋']
    campuses = ['紫金港校区', '玉泉校区']
    buildings = ['实验楼A', '实验楼B']
    brands = ['国药', '西格玛', '索莱宝', '赛默飞', '麦克林']

    consumables = []
    for i, data in enumerate(consumables_data):
        category_idx = data.pop('category_idx')
        category = categories[category_idx]

        # 随机设置库存，部分设为低库存
        stock = randint(0, 100)
        min_stock = 10
        if i % 5 == 0:  # 20%设置为低库存
            stock = randint(0, 5)

        # 随机设置过期日期，部分设为已过期
        expiration_days = randint(-30, 365) if i % 4 == 0 else randint(30, 730)
        expiration_date = date.today() + timedelta(days=expiration_days)

        consumable_data = {
            **data,
            'category_id': category.id,
            'supplier_id': suppliers[i % len(suppliers)].id,
            'brand': brands[i % len(brands)],
            'stock': stock,
            'min_stock': min_stock,
            'custodian_name': custodians[i % len(custodians)],
            'custodian_phone': f'13{randint(0, 9)}{randint(1000, 9999)}{randint(1000, 9999)}',
            'production_date': date.today() - timedelta(days=randint(30, 365)),
            'expiration_date': expiration_date,
            'campus': campuses[i % len(campuses)],
            'building': buildings[i % len(buildings)],
            'room': f'{randint(1, 3)}0{randint(1, 9)}',
        }

        consumable = Consumable.query.filter_by(code=data['code']).first()
        if not consumable:
            consumable = Consumable(**consumable_data)
            db.session.add(consumable)
        consumables.append(consumable)

    db.session.commit()
    print(f"已创建 {len(consumables)} 个耗材")
    return consumables


def seed_purchase_requests(users):
    """创建测试采购申请"""
    print("正在创建采购申请...")

    items = [
        {'name': '高精度电子天平', 'code': 'BAL-001', 'brand': '赛多利斯'},
        {'name': '超低温冰箱', 'code': 'FRG-001', 'brand': '海尔'},
        {'name': '倒置显微镜', 'code': 'MIC-001', 'brand': '奥林巴斯'},
        {'name': '液氮罐', 'code': 'TNK-001', 'brand': '金凤'},
        {'name': '超声波破碎仪', 'code': 'SON-001', 'brand': '洁特'},
        {'name': '凝胶成像系统', 'code': 'GEL-001', 'brand': 'Bio-Rad'},
        {'name': '生物安全柜', 'code': 'BSC-001', 'brand': '洁特'},
        {'name': '旋转蒸发仪', 'code': 'EVA-001', 'brand': '亚荣'},
    ]

    projects = ['国家自然基金', '科技部重大专项', '省重点项目', '企业合作项目']
    purposes = ['实验需要', '设备更新', '新建实验室', '补充设备']
    delivery_infos = ['紫金港校区实验楼A301', '玉泉校区教三楼502', '西溪校区科研楼201', '华家池校区实验楼B101']

    statuses = ['pending', 'approved', 'purchased', 'rejected']
    status_weights = [0.2, 0.3, 0.3, 0.2]

    requests = []
    for i in range(15):
        rand = uniform(0, 1)
        cumulative = 0
        status = 'pending'
        for s, weight in zip(statuses, status_weights):
            cumulative += weight
            if rand <= cumulative:
                status = s
                break

        item = items[i % len(items)]

        req_data = {
            'sequence_number': i + 1,
            'product_name': item['name'],
            'product_code': item['code'],
            'brand': item['brand'],
            'specifications': f'规格型号{randint(1, 100)}',
            'quantity': randint(1, 10),
            'purpose': purposes[i % len(purposes)],
            'applicant_id': users[(i + 1) % len(users)].id,
            'project_name': projects[i % len(projects)],
            'application_date': date.today() - timedelta(days=randint(1, 60)),
            'delivery_info': delivery_infos[i % len(delivery_infos)],
            'query_price': Decimal(str(round(uniform(1000, 100000), 2))),
            'campus': '紫金港校区' if i % 2 == 0 else '玉泉校区',
            'building': '实验楼A' if i % 2 == 0 else '教三楼',
            'room': f'{randint(1, 5)}0{randint(1, 9)}',
            'approver_id': users[0].id if status in ['approved', 'purchased', 'rejected'] else None,
            'status': status,
            'approval_comment': '同意采购' if status == 'approved' else ('已采购完成' if status == 'purchased' else ('暂不需要' if status == 'rejected' else None)),
        }

        req = PurchaseRequest(**req_data)
        db.session.add(req)
        requests.append(req)

    db.session.commit()
    print(f"已创建 {len(requests)} 个采购申请")
    return requests


def seed_transfers(users, assets):
    """创建测试资产转移记录"""
    print("正在创建资产转移记录...")

    campuses = ['紫金港校区', '玉泉校区', '西溪校区']
    buildings = ['教十楼', '教三楼', '实验楼A', '科研楼']

    transfers = []
    for i in range(10):
        asset = assets[i % len(assets)]

        transfer_data = {
            'asset_id': asset.id,
            'applicant_id': users[(i + 1) % len(users)].id,
            'approver_id': users[0].id if i % 3 != 0 else None,
            'receiver_id': users[(i + 2) % len(users)].id if i % 2 == 0 else None,
            'from_campus': asset.campus,
            'from_building': asset.building,
            'from_room': asset.room,
            'to_campus': campuses[i % len(campuses)],
            'to_building': buildings[i % len(buildings)],
            'to_room': f'{randint(1, 5)}0{randint(1, 9)}',
            'reason': f'实验需要转移设备到{campuses[i % len(campuses)]}',
            'status': choice(['pending', 'approved', 'rejected']),
        }

        transfer = AssetTransfer(**transfer_data)
        db.session.add(transfer)
        transfers.append(transfer)

    db.session.commit()
    print(f"已创建 {len(transfers)} 个资产转移记录")
    return transfers


def seed_borrow_records(users, assets):
    """创建测试借用记录"""
    print("正在创建借用记录...")

    records = []

    for i in range(12):
        asset = assets[(i * 2) % len(assets)]

        # 生成借用日期
        borrow_date = datetime.utcnow() - timedelta(days=randint(1, 60))

        record_data = {
            'asset_id': asset.id,
            'borrower_id': users[(i + 1) % len(users)].id,
            'borrow_date': borrow_date,
            'return_date': borrow_date + timedelta(days=randint(1, 20)) if i % 3 == 0 else None,
            'purpose': '实验需要临时使用',
            'status': 'returned' if i % 3 == 0 else 'borrowed',
        }

        record = BorrowRecord(**record_data)
        db.session.add(record)
        records.append(record)

    db.session.commit()
    print(f"已创建 {len(records)} 个借用记录")
    return records


def seed_pick_records(users, consumables):
    """创建测试耗材领用记录"""
    print("正在创建耗材领用记录...")

    records = []

    for i in range(15):
        consumable = consumables[i % len(consumables)]

        record_data = {
            'item_id': consumable.id,
            'picker_id': users[(i + 1) % len(users)].id,
            'approver_id': users[0].id if i % 4 != 0 else None,
            'quantity': randint(1, 10),
            'purpose': '日常实验使用',
            'status': 'approved' if i % 4 != 0 else 'pending',
        }

        record = PickRecord(**record_data)
        db.session.add(record)
        records.append(record)

    db.session.commit()
    print(f"已创建 {len(records)} 个耗材领用记录")
    return records


def seed_all():
    """生成所有测试数据"""
    print("=" * 50)
    print("开始生成测试数据...")
    print("=" * 50)

    users = seed_users()
    categories = seed_categories()
    suppliers = seed_suppliers()
    assets = seed_assets(users)
    consumables = seed_consumables(categories, suppliers)
    purchase_requests = seed_purchase_requests(users)
    transfers = seed_transfers(users, assets)
    borrow_records = seed_borrow_records(users, assets)
    pick_records = seed_pick_records(users, consumables)

    print("=" * 50)
    print("测试数据生成完成！")
    print(f"用户: {len(users)} 个")
    print(f"类别: {len(categories)} 个")
    print(f"供应商: {len(suppliers)} 个")
    print(f"资产: {len(assets)} 个")
    print(f"耗材: {len(consumables)} 个")
    print(f"采购申请: {len(purchase_requests)} 个")
    print(f"资产转移: {len(transfers)} 个")
    print(f"借用记录: {len(borrow_records)} 个")
    print(f"耗材领用: {len(pick_records)} 个")
    print("=" * 50)


if __name__ == '__main__':
    seed_all()
