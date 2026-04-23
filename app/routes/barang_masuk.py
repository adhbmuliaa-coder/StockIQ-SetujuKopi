from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Transaction
from app.services.filter_service import get_divisi_list
from app import db
from datetime import datetime
import json

barang_masuk_bp = Blueprint('barang_masuk', __name__)


@barang_masuk_bp.route('/barang-masuk', methods=['GET', 'POST'])
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
        asal_barang = request.form.get('asal_barang', '')
        tanggal = request.form.get('tanggal', '')
        keterangan = request.form.get('keterangan', '')

        if not all([divisi, nama_bahan, qty, satuan, asal_barang, tanggal]):
            flash('Semua field wajib diisi (kecuali keterangan).', 'error')
        else:
            try:
                tx_date = datetime.strptime(tanggal, '%Y-%m-%d').date()
            except ValueError:
                tx_date = datetime.utcnow().date()

            detail = json.dumps({
                'asal_barang': asal_barang,
                'keterangan': keterangan
            })
            txn = Transaction(
                type='masuk',
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
            flash('Barang Masuk berhasil dicatat!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('forms/barang_masuk.html')
