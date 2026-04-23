from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from app.models import User, Branch, DbBahan, DbPrepareBahan, DbNpu
from app import db

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Akses ditolak. Hanya admin.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


# ── Users Management ─────────────────────────────────────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.username).all()
    all_branches = Branch.query.order_by(Branch.name).all()
    return render_template('admin/users.html', users=all_users, branches=all_branches)


@admin_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'staff')
    branch_ids = request.form.getlist('branch_ids')

    if not username or not password:
        flash('Username dan password wajib diisi.', 'error')
    elif User.query.filter_by(username=username).first():
        flash('Username sudah digunakan.', 'error')
    else:
        user = User(username=username, password_hash=generate_password_hash(password), role=role)
        for bid in branch_ids:
            branch = Branch.query.get(int(bid))
            if branch:
                user.allowed_branches.append(branch)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{username}" berhasil ditambahkan.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/update-branches/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_branches(user_id):
    user = User.query.get_or_404(user_id)
    branch_ids = request.form.getlist('branch_ids')
    for branch in user.allowed_branches.all():
        user.allowed_branches.remove(branch)
    for bid in branch_ids:
        branch = Branch.query.get(int(bid))
        if branch:
            user.allowed_branches.append(branch)
    db.session.commit()
    flash(f'Cabang untuk "{user.username}" diupdate.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri.', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" berhasil dihapus.', 'success')
    return redirect(url_for('admin.users'))


# ── Profile (change own username/password) ───────────────────────

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('new_username', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if new_username and new_username != current_user.username:
            existing = User.query.filter_by(username=new_username).first()
            if existing:
                flash('Username sudah digunakan.', 'error')
                return redirect(url_for('admin.profile'))
            current_user.username = new_username
            flash('Username berhasil diubah.', 'success')

        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
            flash('Password berhasil diubah.', 'success')

        db.session.commit()
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html')


# ── Branches Management ─────────────────────────────────────────

@admin_bp.route('/branches')
@login_required
@admin_required
def branches():
    all_branches = Branch.query.order_by(Branch.name).all()
    return render_template('admin/branches.html', branches=all_branches)


@admin_bp.route('/branches/add', methods=['POST'])
@login_required
@admin_required
def add_branch():
    name = request.form.get('name', '').strip().upper()
    if not name:
        flash('Nama cabang wajib diisi.', 'error')
    elif Branch.query.filter_by(name=name).first():
        flash('Cabang sudah ada.', 'error')
    else:
        db.session.add(Branch(name=name))
        db.session.commit()
        flash(f'Cabang "{name}" ditambahkan.', 'success')
    return redirect(url_for('admin.branches'))


@admin_bp.route('/branches/delete/<int:branch_id>', methods=['POST'])
@login_required
@admin_required
def delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    db.session.delete(branch)
    db.session.commit()
    flash(f'Cabang "{branch.name}" dihapus.', 'success')
    return redirect(url_for('admin.branches'))


# ── Master Data Management ───────────────────────────────────────

@admin_bp.route('/master-data')
@login_required
@admin_required
def master_data():
    bahan_list = DbBahan.query.order_by(DbBahan.divisi, DbBahan.nama_bahan).all()
    prepare_list = DbPrepareBahan.query.order_by(DbPrepareBahan.divisi, DbPrepareBahan.nama_bahan).all()
    npu_list = DbNpu.query.order_by(DbNpu.divisi, DbNpu.nama_bahan).all()
    all_branches = Branch.query.order_by(Branch.name).all()
    divisi_list = sorted(set(b.divisi for b in DbBahan.query.with_entities(DbBahan.divisi).distinct().all()))

    return render_template('admin/master_data.html',
                           bahan_list=bahan_list,
                           prepare_list=prepare_list,
                           npu_list=npu_list,
                           branches=all_branches,
                           divisi_list=divisi_list)


@admin_bp.route('/master-data/bahan/add', methods=['POST'])
@login_required
@admin_required
def add_bahan():
    divisi = request.form.get('divisi', '').strip().upper()
    nama_bahan = request.form.get('nama_bahan', '').strip().upper()
    satuan = request.form.get('satuan', '').strip().upper()
    is_prepare = request.form.get('is_prepare') == 'on'
    satuan_prepare = request.form.get('satuan_prepare', '').strip().upper()
    branch_ids = request.form.getlist('branch_ids')

    if not all([divisi, nama_bahan, satuan]):
        flash('Divisi, Nama Bahan, dan Satuan wajib diisi.', 'error')
    elif is_prepare and not satuan_prepare:
        flash('Satuan Prepare wajib diisi jika bahan ini prepare.', 'error')
    else:
        item = DbBahan(divisi=divisi, nama_bahan=nama_bahan, satuan=satuan, prepare=is_prepare)
        for bid in branch_ids:
            branch = Branch.query.get(int(bid))
            if branch:
                item.branches.append(branch)
        db.session.add(item)
        db.session.commit()

        # If prepare, also create DbPrepareBahan entry
        if is_prepare:
            prep = DbPrepareBahan(
                divisi=divisi, nama_bahan=nama_bahan,
                satuan_bahan=satuan, satuan_prepare=satuan_prepare
            )
            for bid in branch_ids:
                branch = Branch.query.get(int(bid))
                if branch:
                    prep.branches.append(branch)
            db.session.add(prep)
            db.session.commit()

        flash(f'Bahan "{nama_bahan}" ditambahkan.', 'success')

    return redirect(url_for('admin.master_data'))

@admin_bp.route('/master-data/bahan/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_bahan(item_id):
    item = DbBahan.query.get_or_404(item_id)
    # Also delete corresponding DbPrepareBahan if exists
    if item.prepare:
        prep = DbPrepareBahan.query.filter_by(nama_bahan=item.nama_bahan).first()
        if prep:
            db.session.delete(prep)
    db.session.delete(item)
    db.session.commit()
    flash(f'Bahan "{item.nama_bahan}" dihapus.', 'success')
    return redirect(url_for('admin.master_data'))


@admin_bp.route('/master-data/npu/add', methods=['POST'])
@login_required
@admin_required
def add_npu():
    divisi = request.form.get('divisi', '').strip().upper()
    nama_bahan = request.form.get('nama_bahan', '').strip().upper()
    satuan_npu = request.form.get('satuan_npu', '').strip().upper()
    branch_ids = request.form.getlist('branch_ids')

    if not all([divisi, nama_bahan, satuan_npu]):
        flash('Semua field wajib diisi.', 'error')
    else:
        item = DbNpu(divisi=divisi, nama_bahan=nama_bahan, satuan_npu=satuan_npu)
        for bid in branch_ids:
            branch = Branch.query.get(int(bid))
            if branch:
                item.branches.append(branch)
        db.session.add(item)
        db.session.commit()
        flash(f'NPU "{nama_bahan}" ditambahkan.', 'success')

    return redirect(url_for('admin.master_data'))


@admin_bp.route('/master-data/npu/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_npu(item_id):
    item = DbNpu.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f'NPU "{item.nama_bahan}" dihapus.', 'success')
    return redirect(url_for('admin.master_data'))
