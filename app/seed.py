"""
Seed script: import CSV data into SQLite database.
Run with: python -m app.seed
"""
import os
import sys
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Branch, DbBahan, DbPrepareBahan, DbNpu, User
from werkzeug.security import generate_password_hash


BRANCH_COLUMNS = ['SIBOLANGIT', 'REST AREA', 'BASKET', 'CADIKA', 'HARVEST MOON']

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def seed_branches():
    """Create branch records from the known column names."""
    for name in BRANCH_COLUMNS:
        if not Branch.query.filter_by(name=name).first():
            db.session.add(Branch(name=name))
    db.session.commit()
    print(f"[OK] Branches: {Branch.query.count()} total")


def seed_bahan():
    """Import val_bahan.csv (new master data) and select_bahan_by_cabang.csv."""
    # Master data — now reading from val_bahan.csv
    master_file = os.path.join(DATA_DIR, 'val_bahan.csv')
    if not os.path.exists(master_file):
        print(f"[!] Skipping bahan: {master_file} not found")
        return

    df = pd.read_csv(master_file)
    # Filter out empty rows (lines with no ID)
    df = df.dropna(subset=['ID VAL_BAHAN'])
    df = df[df['ID VAL_BAHAN'].astype(str).str.strip() != '']

    for _, row in df.iterrows():
        item_id = int(row['ID VAL_BAHAN'])
        if not DbBahan.query.filter_by(id=item_id).first():
            # Parse PREPARE (Y/N) and SELISIH (Y/N) columns
            prepare_val = str(row.get('PREPARE (Y/N)', 'FALSE')).strip().upper()
            selisih_val = str(row.get('SELISIH (Y/N)', 'FALSE')).strip().upper()
            dispensasi_val = row.get('DISPENSASI BAHAN PER PRODUK', 0)

            item = DbBahan(
                id=item_id,
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip(),
                satuan=str(row['SATUAN']).strip(),
                prepare=(prepare_val == 'TRUE'),
                selisih=(selisih_val == 'TRUE'),
                dispensasi=int(dispensasi_val) if pd.notna(dispensasi_val) else 0
            )
            db.session.add(item)
    db.session.commit()

    # Junction: branch assignments
    junction_file = os.path.join(DATA_DIR, 'select_bahan_by_cabang.csv')
    if os.path.exists(junction_file):
        jdf = pd.read_csv(junction_file)
        for _, row in jdf.iterrows():
            item = DbBahan.query.filter_by(
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip()
            ).first()
            if item:
                for col in BRANCH_COLUMNS:
                    if col in jdf.columns and row.get(col) == True:
                        branch = Branch.query.filter_by(name=col).first()
                        if branch and branch not in item.branches.all():
                            item.branches.append(branch)
        db.session.commit()

    print(f"[OK] Bahan: {DbBahan.query.count()} items")
    print(f"     Prepare=TRUE: {DbBahan.query.filter_by(prepare=True).count()}")
    print(f"     Prepare=FALSE: {DbBahan.query.filter_by(prepare=False).count()}")


def seed_prepare():
    """Import db_prepare_bahan.csv and select_prepare_bahan_by_cabang.csv."""
    master_file = os.path.join(DATA_DIR, 'db_prepare_bahan.csv')
    if not os.path.exists(master_file):
        print(f"[!] Skipping prepare: {master_file} not found")
        return

    df = pd.read_csv(master_file)
    for _, row in df.iterrows():
        if not DbPrepareBahan.query.filter_by(id=int(row['ID DB_PREPARE_BAHAN'])).first():
            item = DbPrepareBahan(
                id=int(row['ID DB_PREPARE_BAHAN']),
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip(),
                satuan_bahan=str(row['SATUAN BAHAN']).strip(),
                satuan_prepare=str(row['SATUAN PREPARE']).strip()
            )
            db.session.add(item)
    db.session.commit()

    junction_file = os.path.join(DATA_DIR, 'select_prepare_bahan_by_cabang.csv')
    if os.path.exists(junction_file):
        jdf = pd.read_csv(junction_file)
        for _, row in jdf.iterrows():
            item = DbPrepareBahan.query.filter_by(
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip()
            ).first()
            if item:
                for col in BRANCH_COLUMNS:
                    if col in jdf.columns and row.get(col) == True:
                        branch = Branch.query.filter_by(name=col).first()
                        if branch and branch not in item.branches.all():
                            item.branches.append(branch)
        db.session.commit()

    print(f"[OK] Prepare Bahan: {DbPrepareBahan.query.count()} items")


def seed_npu():
    """Import db_npu.csv and select_npu_by_cabang.csv."""
    master_file = os.path.join(DATA_DIR, 'db_npu.csv')
    if not os.path.exists(master_file):
        print(f"[!] Skipping NPU: {master_file} not found")
        return

    df = pd.read_csv(master_file)
    for _, row in df.iterrows():
        if not DbNpu.query.filter_by(id=int(row['ID DB_NPU'])).first():
            item = DbNpu(
                id=int(row['ID DB_NPU']),
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip(),
                satuan_npu=str(row['SATUAN NPU']).strip()
            )
            db.session.add(item)
    db.session.commit()

    junction_file = os.path.join(DATA_DIR, 'select_npu_by_cabang.csv')
    if os.path.exists(junction_file):
        jdf = pd.read_csv(junction_file)
        for _, row in jdf.iterrows():
            item = DbNpu.query.filter_by(
                divisi=str(row['DIVISI']).strip(),
                nama_bahan=str(row['NAMA BAHAN']).strip()
            ).first()
            if item:
                for col in BRANCH_COLUMNS:
                    if col in jdf.columns and row.get(col) == True:
                        branch = Branch.query.filter_by(name=col).first()
                        if branch and branch not in item.branches.all():
                            item.branches.append(branch)
        db.session.commit()

    print(f"[OK] NPU: {DbNpu.query.count()} items")


def seed_default_admin():
    """Create a default admin user if none exists."""
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("[OK] Default admin created: admin / admin123")
    else:
        print("[OK] Admin user already exists")


def run_seed():
    app = create_app()
    with app.app_context():
        print("=== StockIQ Database Seeding ===\n")
        seed_branches()
        seed_bahan()
        seed_prepare()
        seed_npu()
        seed_default_admin()
        print("\n=== Seeding Complete! ===")


if __name__ == '__main__':
    run_seed()
