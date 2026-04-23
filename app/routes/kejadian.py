from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Transaction
from app import db
from datetime import datetime
import json

kejadian_bp = Blueprint('kejadian', __name__)


@kejadian_bp.route('/kejadian', methods=['GET', 'POST'])
@login_required
def index():
    if 'branch_id' not in session:
        return redirect(url_for('auth.select_branch'))

    branch_id = session['branch_id']

    if request.method == 'POST':
        divisi = request.form.get('divisi', '')
        isi_kejadian = request.form.get('isi_kejadian', '')
        tanggal = request.form.get('tanggal', '')

        if not all([divisi, isi_kejadian, tanggal]):
            flash('Divisi, isi kejadian, dan tanggal wajib diisi.', 'error')
        else:
            try:
                tx_date = datetime.strptime(tanggal, '%Y-%m-%d').date()
            except ValueError:
                tx_date = datetime.utcnow().date()

            detail = json.dumps({'isi_kejadian': isi_kejadian})
            txn = Transaction(
                type='kejadian',
                branch_id=branch_id,
                divisi=divisi,
                nama_bahan=isi_kejadian[:100],
                qty=0,
                satuan='-',
                transaction_date=tx_date,
                detail_json=detail,
                user_id=current_user.id
            )
            db.session.add(txn)
            db.session.commit()
            flash('Kejadian berhasil dicatat!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('forms/kejadian.html')
