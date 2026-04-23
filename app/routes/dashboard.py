from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required, current_user
from app.models import Transaction
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    if 'branch_id' not in session:
        return redirect(url_for('auth.select_branch'))

    branch_id = session['branch_id']
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    query = Transaction.query.filter(
        Transaction.branch_id == branch_id,
        Transaction.created_at >= today_start
    )

    transactions = query.order_by(Transaction.created_at.desc()).limit(50).all()

    counts = {
        'masuk': Transaction.query.filter_by(branch_id=branch_id, type='masuk').filter(Transaction.created_at >= today_start).count(),
        'transfer': Transaction.query.filter_by(branch_id=branch_id, type='transfer').filter(Transaction.created_at >= today_start).count(),
        'prepare': Transaction.query.filter_by(branch_id=branch_id, type='prepare').filter(Transaction.created_at >= today_start).count(),
        'prepare_in': Transaction.query.filter_by(branch_id=branch_id, type='prepare_in').filter(Transaction.created_at >= today_start).count(),
        'npu': Transaction.query.filter_by(branch_id=branch_id, type='npu').filter(Transaction.created_at >= today_start).count(),
        'kejadian': Transaction.query.filter_by(branch_id=branch_id, type='kejadian').filter(Transaction.created_at >= today_start).count(),
    }

    return render_template('dashboard.html',
                           transactions=transactions,
                           counts=counts,
                           branch_name=session.get('branch_name', ''))
