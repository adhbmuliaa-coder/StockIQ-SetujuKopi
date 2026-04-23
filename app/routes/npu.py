from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Transaction
from app import db
from datetime import datetime
import json

npu_bp = Blueprint('npu', __name__)


@npu_bp.route('/npu', methods=['GET', 'POST'])
@login_required
def index():
    if 'branch_id' not in session:
        return redirect(url_for('auth.select_branch'))

    branch_id = session['branch_id']

    if request.method == 'POST':
        divisi = request.form.get('divisi', '')
        nama_bahan = request.form.get('nama_bahan', '')
        qty = request.form.get('qty', 0, type=float)
        satuan = request.form.get('satuan', '')
        tanggal = request.form.get('tanggal', '')
        keterangan = request.form.get('keterangan', '')

        if not all([divisi, nama_bahan, qty, satuan, tanggal]):
            flash('Semua field wajib diisi (kecuali keterangan).', 'error')
        else:
            try:
                tx_date = datetime.strptime(tanggal, '%Y-%m-%d').date()
            except ValueError:
                tx_date = datetime.utcnow().date()

            detail = json.dumps({
                'keterangan': keterangan
            })
            txn = Transaction(
                type='npu',
                branch_id=branch_id,
                divisi=divisi,
                nama_bahan=nama_bahan,
                qty=qty,
                satuan=satuan,
                transaction_date=tx_date,
                detail_json=detail,
                user_id=current_user.id
            )
            db.session.add(txn)
            db.session.commit()
            flash('NPU berhasil dicatat!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('forms/npu.html')
