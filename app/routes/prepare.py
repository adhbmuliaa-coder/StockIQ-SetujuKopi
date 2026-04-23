from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import Transaction
from app.services.filter_service import get_divisi_list
from app import db
from datetime import datetime
import json

prepare_bp = Blueprint('prepare', __name__)


@prepare_bp.route('/prepare', methods=['GET', 'POST'])
@login_required
def index():
    if 'branch_id' not in session:
        return redirect(url_for('auth.select_branch'))

    branch_id = session['branch_id']

    if request.method == 'POST':
        divisi = request.form.get('divisi', '')
        nama_bahan = request.form.get('nama_bahan', '')
        qty_prepare = request.form.get('qty_prepare', 0, type=float)
        satuan_prepare = request.form.get('satuan_prepare', '')
        qty_jadi = request.form.get('qty_jadi', 0, type=float)
        satuan_bahan = request.form.get('satuan_bahan', '')
        tanggal = request.form.get('tanggal', '')
        keterangan = request.form.get('keterangan', '')

        if not all([divisi, nama_bahan, satuan_prepare, satuan_bahan, tanggal]):
            flash('Semua field wajib diisi (kecuali keterangan).', 'error')
        elif qty_prepare <= 0 and qty_jadi <= 0:
            flash('Minimal salah satu qty harus diisi.', 'error')
        else:
            try:
                tx_date = datetime.strptime(tanggal, '%Y-%m-%d').date()
            except ValueError:
                tx_date = datetime.utcnow().date()

            # ── Record 1: PREPARE (bahan yang digunakan) ──
            detail_prepare = json.dumps({
                'qty_prepare': qty_prepare,
                'satuan_prepare': satuan_prepare,
                'qty_jadi': qty_jadi,
                'satuan_bahan': satuan_bahan,
                'keterangan': keterangan
            })
            txn_prepare = Transaction(
                type='prepare',
                branch_id=branch_id,
                divisi=divisi,
                nama_bahan=nama_bahan,
                qty=qty_prepare,
                satuan=satuan_prepare,
                transaction_date=tx_date,
                detail_json=detail_prepare,
                user_id=current_user.id
            )
            db.session.add(txn_prepare)

            # ── Record 2: PREPARE_IN (hasil jadi) ──
            detail_in = json.dumps({
                'qty_prepare': qty_prepare,
                'satuan_prepare': satuan_prepare,
                'qty_jadi': qty_jadi,
                'satuan_bahan': satuan_bahan,
                'keterangan': keterangan
            })
            txn_in = Transaction(
                type='prepare_in',
                branch_id=branch_id,
                divisi=divisi,
                nama_bahan=nama_bahan,
                qty=qty_jadi,
                satuan=satuan_bahan,
                transaction_date=tx_date,
                detail_json=detail_in,
                user_id=current_user.id
            )
            db.session.add(txn_in)

            db.session.commit()
            flash('Prepare berhasil dicatat! (2 record: prepare & prepare in)', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('forms/prepare.html')
