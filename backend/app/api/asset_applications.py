# 资产业务申请 API 路由
# 处理保管人变更、资产调拨、设备维修、退库、报废、报失报损等业务
from flask import Blueprint, request, g
from datetime import datetime
from app.models import AssetApplication, Asset, User
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_required_fields, validate_pagination


asset_applications_bp = Blueprint('asset_applications', __name__)


@asset_applications_bp.route('', methods=['GET'])
@login_required
def get_applications():
    """获取业务申请列表（支持过滤和分页）"""
    # 获取查询参数
    application_type = request.args.get('application_type')
    status = request.args.get('status')
    applicant_id = request.args.get('applicant_id', type=int)
    my_applications = request.args.get('my', type=bool)  # 获取我的申请
    page, page_size = validate_pagination()

    # 构建查询
    query = AssetApplication.query

    # 应用过滤条件
    if application_type:
        query = query.filter_by(application_type=application_type)
    if status:
        query = query.filter_by(status=status)
    if applicant_id:
        query = query.filter_by(applicant_id=applicant_id)
    if my_applications and g.user:
        query = query.filter_by(applicant_id=g.user.id)

    # 按申请时间降序排列
    query = query.order_by(AssetApplication.application_time.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    # 转换为字典
    items = [app.to_dict() for app in pagination.items]

    return paginated_response(items, pagination.total, page, page_size)


@asset_applications_bp.route('/<int:application_id>', methods=['GET'])
@login_required
def get_application(application_id):
    """获取业务申请详情"""
    application = AssetApplication.query.get(application_id)

    if not application:
        return error_response('申请不存在', error_code='NOT_FOUND', status=404)

    return success_response(data=application.to_dict())


@asset_applications_bp.route('', methods=['POST'])
@login_required
def create_application():
    """创建新的业务申请"""
    data = request.get_json()

    # 验证必填字段
    is_valid, error_msg = validate_required_fields(data, ['asset_id', 'application_type'])
    if not is_valid:
        return error_response(error_msg, error_code='VALIDATION_ERROR')

    # 验证资产是否存在
    asset = Asset.query.get(data['asset_id'])
    if not asset:
        return error_response('资产不存在', error_code='NOT_FOUND', status=404)

    # 验证申请类型
    valid_types = [
        AssetApplication.TYPE_CUSTODIAN_CHANGE,
        AssetApplication.TYPE_ALLOCATION,
        AssetApplication.TYPE_REPAIR,
        AssetApplication.TYPE_RETURN,
        AssetApplication.TYPE_SCRAP,
        AssetApplication.TYPE_LOSS
    ]
    if data['application_type'] not in valid_types:
        return error_response('申请类型无效', error_code='VALIDATION_ERROR')

    # 根据不同类型验证不同的字段
    content = {}
    app_type = data['application_type']

    if app_type == AssetApplication.TYPE_CUSTODIAN_CHANGE:
        # 保管人变更：需要新管理人ID和原因
        is_valid, error_msg = validate_required_fields(data, ['new_custodian_id', 'reason'])
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        # 验证新管理人是否存在
        new_manager = User.query.get(data['new_custodian_id'])
        if not new_manager:
            return error_response('新保管人不存在', error_code='NOT_FOUND', status=404)
        content = {
            'new_custodian_id': data['new_custodian_id'],
            'new_custodian_name': new_manager.username,
            'reason': data.get('reason', ''),
            'old_custodian_id': asset.manager_id,
            'old_custodian_name': asset.manager.username if asset.manager else ''
        }

    elif app_type == AssetApplication.TYPE_ALLOCATION:
        # 资产调拨：需要新位置信息和原因
        is_valid, error_msg = validate_required_fields(data, ['campus', 'building', 'reason'])
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        content = {
            'campus': data['campus'],
            'building': data['building'],
            'room': data.get('room', ''),
            'reason': data.get('reason', ''),
            'old_location': {
                'campus': asset.campus,
                'building': asset.building,
                'room': asset.room or ''
            }
        }

    elif app_type == AssetApplication.TYPE_REPAIR:
        # 设备维修：需要故障描述
        is_valid, error_msg = validate_required_fields(data, ['fault_description'])
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        content = {
            'fault_description': data.get('fault_description', ''),
            'repair_notes': data.get('repair_notes', '')
        }

    elif app_type in [AssetApplication.TYPE_RETURN, AssetApplication.TYPE_SCRAP, AssetApplication.TYPE_LOSS]:
        # 退库、报废、报失报损：需要原因
        is_valid, error_msg = validate_required_fields(data, ['reason'])
        if not is_valid:
            return error_response(error_msg, error_code='VALIDATION_ERROR')
        content = {
            'reason': data.get('reason', ''),
            'notes': data.get('notes', '')
        }

    # 创建申请
    application = AssetApplication(
        asset_id=data['asset_id'],
        application_type=data['application_type'],
        applicant_id=g.user.id,
        applicant_name=g.user.username,
        status=AssetApplication.STATUS_PENDING
    )
    application.set_content(content)

    try:
        from app.extensions import db
        db.session.add(application)
        db.session.commit()

        return success_response(
            message='业务申请已提交',
            data={
                'id': application.id,
                'application_type': application.application_type,
                'status': application.status
            },
            status=201
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        print(f"Application creation error: {e}")
        print(traceback.format_exc())
        return error_response(f'申请提交失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@asset_applications_bp.route('/<int:application_id>/approve', methods=['POST'])
@admin_required
def approve_application(application_id):
    """审批业务申请（仅管理员）"""
    application = AssetApplication.query.get(application_id)

    if not application:
        return error_response('申请不存在', error_code='NOT_FOUND', status=404)

    if application.status != AssetApplication.STATUS_PENDING:
        return error_response('该申请已被处理', error_code='INVALID_OPERATION')

    data = request.get_json()
    action = data.get('action', 'approve')  # approve 或 reject
    approval_comment = data.get('approval_comment', '')

    try:
        from app.extensions import db

        if action == 'approve':
            # 批准申请
            application.status = AssetApplication.STATUS_APPROVED
            application.approver_id = g.user.id
            application.approval_comment = approval_comment
            application.approval_time = datetime.utcnow()

            # 根据不同类型执行相应的操作
            content = application.get_content()

            if application.application_type == AssetApplication.TYPE_CUSTODIAN_CHANGE:
                # 保管人变更 - 更新资产管理人
                application.asset.manager_id = content.get('new_custodian_id')

            elif application.application_type == AssetApplication.TYPE_ALLOCATION:
                # 资产调拨 - 更新存放位置
                application.asset.campus = content.get('campus')
                application.asset.building = content.get('building')
                application.asset.room = content.get('room', '') or None

            elif application.application_type == AssetApplication.TYPE_REPAIR:
                # 设备维修 - 更新状态为报修
                application.asset.current_status = Asset.STATUS_REPAIR
                application.status = AssetApplication.STATUS_PROCESSING

            elif application.application_type == AssetApplication.TYPE_RETURN:
                # 退库 - 更新状态为退库
                application.asset.current_status = Asset.STATUS_RETURNED
                application.status = AssetApplication.STATUS_COMPLETED

            elif application.application_type == AssetApplication.TYPE_SCRAP:
                # 报废 - 更新状态为报废
                application.asset.current_status = Asset.STATUS_SCRAPPED
                application.status = AssetApplication.STATUS_COMPLETED

            elif application.application_type == AssetApplication.TYPE_LOSS:
                # 报失报损 - 更新状态为报废
                application.asset.current_status = Asset.STATUS_SCRAPPED
                application.status = AssetApplication.STATUS_COMPLETED

        elif action == 'reject':
            # 拒绝申请
            application.status = AssetApplication.STATUS_REJECTED
            application.approver_id = g.user.id
            application.approval_comment = approval_comment
            application.approval_time = datetime.utcnow()
        else:
            return error_response('无效的操作', error_code='VALIDATION_ERROR')

        db.session.commit()

        return success_response(
            message=f'申请已{"批准" if action == "approve" else "拒绝"}',
            data={
                'id': application.id,
                'status': application.status
            }
        )
    except Exception as e:
        from app.extensions import db
        import traceback
        db.session.rollback()
        print(f"Application approval error: {e}")
        print(traceback.format_exc())
        return error_response(f'审批失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


@asset_applications_bp.route('/<int:application_id>/complete', methods=['POST'])
@admin_required
def complete_application(application_id):
    """完成业务申请（仅管理员，用于维修完成后等场景）"""
    application = AssetApplication.query.get(application_id)

    if not application:
        return error_response('申请不存在', error_code='NOT_FOUND', status=404)

    if application.status != AssetApplication.STATUS_PROCESSING:
        return error_response('该申请状态不正确', error_code='INVALID_OPERATION')

    try:
        from app.extensions import db

        # 标记为完成
        application.status = AssetApplication.STATUS_COMPLETED

        # 如果是维修申请，恢复资产状态
        if application.application_type == AssetApplication.TYPE_REPAIR:
            application.asset.current_status = Asset.STATUS_IN_USE

        db.session.commit()

        return success_response(
            message='申请已完成',
            data={
                'id': application.id,
                'status': application.status
            }
        )
    except Exception as e:
        from app.extensions import db
        db.session.rollback()
        return error_response(f'操作失败: {str(e)}', error_code='INTERNAL_ERROR', status=500)


# 导入Asset模型（用于状态常量）
from app.models.asset import Asset
