from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import verify_user
from app.models import Branch

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if 'branch_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.select_branch'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = verify_user(username, password)
        if user:
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('auth.select_branch'))
        else:
            flash('Username atau password salah.', 'error')

    return render_template('login.html')


@auth_bp.route('/select-branch', methods=['GET', 'POST'])
@login_required
def select_branch():
    # Admin can access all branches, staff only allowed branches
    if current_user.is_admin():
        branches = Branch.query.order_by(Branch.name).all()
    else:
        branches = current_user.allowed_branches.order_by(Branch.name).all()

    if request.method == 'POST':
        branch_id = request.form.get('branch_id')
        if branch_id:
            branch = Branch.query.get(int(branch_id))
            if branch:
                # Check if user has access to this branch
                if current_user.is_admin() or branch in current_user.allowed_branches.all():
                    session['branch_id'] = branch.id
                    session['branch_name'] = branch.name
                    flash(f'Cabang "{branch.name}" dipilih.', 'success')
                    return redirect(url_for('dashboard.index'))
                else:
                    flash('Anda tidak memiliki akses ke cabang ini.', 'error')
        flash('Pilih cabang yang valid.', 'error')

    return render_template('select_branch.html', branches=branches)


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('branch_id', None)
    session.pop('branch_name', None)
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))
