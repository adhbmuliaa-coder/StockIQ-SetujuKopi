from app.models import DbBahan, DbPrepareBahan, DbNpu


def get_bahan_for_branch(branch_id, divisi=None, prepare_filter=None):
    """Get bahan items available for a branch, optionally filtered by divisi and prepare status."""
    query = DbBahan.query.filter(DbBahan.branches.any(id=branch_id))
    if divisi:
        query = query.filter_by(divisi=divisi)
    if prepare_filter is not None:
        query = query.filter_by(prepare=prepare_filter)
    return query.order_by(DbBahan.nama_bahan).all()


def get_prepare_for_branch(branch_id, divisi=None):
    """Get prepare bahan items available for a branch."""
    query = DbPrepareBahan.query.filter(DbPrepareBahan.branches.any(id=branch_id))
    if divisi:
        query = query.filter_by(divisi=divisi)
    return query.order_by(DbPrepareBahan.nama_bahan).all()


def get_npu_for_branch(branch_id, divisi=None):
    """Get NPU items available for a branch."""
    query = DbNpu.query.filter(DbNpu.branches.any(id=branch_id))
    if divisi:
        query = query.filter_by(divisi=divisi)
    return query.order_by(DbNpu.nama_bahan).all()


def get_divisi_list(item_type, branch_id, prepare_filter=None):
    """Get distinct divisi values for a given item type filtered by branch."""
    if item_type == 'bahan':
        items = get_bahan_for_branch(branch_id, prepare_filter=prepare_filter)
    elif item_type == 'prepare':
        items = get_prepare_for_branch(branch_id)
    elif item_type == 'npu':
        items = get_npu_for_branch(branch_id)
    else:
        return []
    return sorted(set(item.divisi for item in items))
