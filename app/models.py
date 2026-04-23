from app import db
from flask_login import UserMixin
from datetime import datetime


# ── Junction Tables ──────────────────────────────────────────────

bahan_branch = db.Table(
    'bahan_branch',
    db.Column('bahan_id', db.Integer, db.ForeignKey('db_bahan.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('branches.id'), primary_key=True),
)

prepare_branch = db.Table(
    'prepare_branch',
    db.Column('prepare_id', db.Integer, db.ForeignKey('db_prepare_bahan.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('branches.id'), primary_key=True),
)

npu_branch = db.Table(
    'npu_branch',
    db.Column('npu_id', db.Integer, db.ForeignKey('db_npu.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('branches.id'), primary_key=True),
)

user_branch = db.Table(
    'user_branch',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('branches.id'), primary_key=True),
)


# ── Users ────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    allowed_branches = db.relationship('Branch', secondary=user_branch, backref='allowed_users', lazy='dynamic')

    def is_admin(self):
        return self.role == 'admin'


# ── Branches ─────────────────────────────────────────────────────

class Branch(db.Model):
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    transactions = db.relationship('Transaction', backref='branch', lazy='dynamic')


# ── Master Data: Bahan ───────────────────────────────────────────

class DbBahan(db.Model):
    __tablename__ = 'db_bahan'

    id = db.Column(db.Integer, primary_key=True)
    divisi = db.Column(db.String(100), nullable=False)
    nama_bahan = db.Column(db.String(200), nullable=False)
    satuan = db.Column(db.String(50), nullable=False)
    prepare = db.Column(db.Boolean, default=False)
    selisih = db.Column(db.Boolean, default=False)
    dispensasi = db.Column(db.Integer, default=0)

    branches = db.relationship('Branch', secondary=bahan_branch, backref='bahan_items', lazy='dynamic')


# ── Master Data: Prepare Bahan ───────────────────────────────────

class DbPrepareBahan(db.Model):
    __tablename__ = 'db_prepare_bahan'

    id = db.Column(db.Integer, primary_key=True)
    divisi = db.Column(db.String(100), nullable=False)
    nama_bahan = db.Column(db.String(200), nullable=False)
    satuan_bahan = db.Column(db.String(50), nullable=False)
    satuan_prepare = db.Column(db.String(100), nullable=False)

    branches = db.relationship('Branch', secondary=prepare_branch, backref='prepare_items', lazy='dynamic')


# ── Master Data: NPU ────────────────────────────────────────────

class DbNpu(db.Model):
    __tablename__ = 'db_npu'

    id = db.Column(db.Integer, primary_key=True)
    divisi = db.Column(db.String(100), nullable=False)
    nama_bahan = db.Column(db.String(200), nullable=False)
    satuan_npu = db.Column(db.String(50), nullable=False)

    branches = db.relationship('Branch', secondary=npu_branch, backref='npu_items', lazy='dynamic')


# ── Transactions ─────────────────────────────────────────────────

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # masuk, transfer, prepare, npu, kejadian
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    divisi = db.Column(db.String(100), nullable=False)
    nama_bahan = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Float, nullable=False, default=0)
    satuan = db.Column(db.String(100), nullable=False, default='-')
    transaction_date = db.Column(db.Date, nullable=True)
    detail_json = db.Column(db.Text, default='{}')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
