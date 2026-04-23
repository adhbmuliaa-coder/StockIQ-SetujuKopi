from flask import Blueprint, jsonify, request, session
from flask_login import login_required
from app.services.filter_service import get_bahan_for_branch, get_prepare_for_branch, get_npu_for_branch
from app import db

api_bp = Blueprint('api', __name__)


@api_bp.route('/bahan')
@login_required
def bahan_list():
    """AJAX endpoint: get bahan items filtered by branch, divisi, and prepare status."""
    branch_id = session.get('branch_id')
    divisi = request.args.get('divisi')
    prepare_filter_str = request.args.get('prepare_filter')
    if not branch_id:
        return jsonify([])

    # Parse prepare_filter: 'false' → False, 'true' → True, None → no filter
    prepare_filter = None
    if prepare_filter_str is not None:
        prepare_filter = prepare_filter_str.lower() == 'true'

    items = get_bahan_for_branch(branch_id, divisi, prepare_filter=prepare_filter)
    return jsonify([{
        'id': item.id,
        'nama_bahan': item.nama_bahan,
        'satuan': item.satuan,
        'divisi': item.divisi,
        'prepare': item.prepare
    } for item in items])


@api_bp.route('/prepare')
@login_required
def prepare_list():
    """AJAX endpoint: get prepare bahan items filtered by branch and optional divisi."""
    branch_id = session.get('branch_id')
    divisi = request.args.get('divisi')
    if not branch_id:
        return jsonify([])

    items = get_prepare_for_branch(branch_id, divisi)
    return jsonify([{
        'id': item.id,
        'nama_bahan': item.nama_bahan,
        'satuan_bahan': item.satuan_bahan,
        'satuan_prepare': item.satuan_prepare,
        'divisi': item.divisi
    } for item in items])


@api_bp.route('/npu')
@login_required
def npu_list():
    """AJAX endpoint: get NPU items filtered by branch and optional divisi."""
    branch_id = session.get('branch_id')
    divisi = request.args.get('divisi')
    if not branch_id:
        return jsonify([])

    items = get_npu_for_branch(branch_id, divisi)
    return jsonify([{
        'id': item.id,
        'nama_bahan': item.nama_bahan,
        'satuan_npu': item.satuan_npu,
        'divisi': item.divisi
    } for item in items])


@api_bp.route('/divisi-list')
@login_required
def divisi_list():
    """Get all distinct divisi values from DbBahan for dropdown."""
    from app.models import DbBahan
    divisi_values = db.session.query(DbBahan.divisi).distinct().order_by(DbBahan.divisi).all()
    return jsonify([d[0] for d in divisi_values])
