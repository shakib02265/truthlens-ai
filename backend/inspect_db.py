"""
TruthLens AI - Database Inspector CLI
Usage:
    python inspect_db.py
    python inspect_db.py "postgresql://user:pass@host/db?sslmode=require"
"""

import sys
import os

# Ensure backend root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import User, Claim, Investigation, Verdict, Evidence, Source

def inspect(database_url: str = None):
    url = database_url or settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    connect_args = {}
    if "sqlite" in url:
        connect_args = {"check_same_thread": False}

    print("=" * 70)
    print("  TRUTHLENS AI - DATABASE RECORD INSPECTOR")
    print("=" * 70)
    # Mask password in URL for display
    display_url = url
    if "@" in display_url:
        prefix, rest = display_url.split("@", 1)
        if ":" in prefix:
            proto_user = prefix.split(":", 2)
            display_url = f"{proto_user[0]}:{proto_user[1]}:****@{rest}"
    print(f"Connecting to: {display_url}\n")

    try:
        engine = create_engine(url, connect_args=connect_args)
        Session = sessionmaker(bind=engine)
        db = Session()

        # 1. USERS
        users = db.query(User).order_by(User.created_at.desc()).all()
        print(f"--- 1. USERS ({len(users)} registered) ---")
        if not users:
            print("  (No users found)")
        else:
            for u in users:
                print(f"  • ID: {u.id[:8]}... | Email: {u.email} | Name: {u.full_name or 'N/A'} | Role: {u.role}")

        # 2. INVESTIGATIONS
        invs = db.query(Investigation).order_by(Investigation.created_at.desc()).limit(15).all()
        total_invs = db.query(Investigation).count()
        print(f"\n--- 2. INVESTIGATIONS (Showing latest {len(invs)} of {total_invs}) ---")
        if not invs:
            print("  (No investigations found)")
        else:
            for inv in invs:
                verdict_str = inv.verdict_status or "PENDING"
                conf = f"{inv.confidence_score*100:.0f}%" if inv.confidence_score is not None else "N/A"
                print(f"  • [{inv.id[:8]}] [{inv.status}] Verdict: {verdict_str:<12} | Conf: {conf:<4} | Claim: \"{inv.title[:45]}\"")

        # 3. COUNTS
        evidence_count = db.query(Evidence).count()
        source_count = db.query(Source).count()
        verdict_count = db.query(Verdict).count()

        print("\n--- 3. SYSTEM TOTALS ---")
        print(f"  • Total Users:          {len(users)}")
        print(f"  • Total Investigations: {total_invs}")
        print(f"  • Total Sources Found:  {source_count}")
        print(f"  • Total Evidence Items: {evidence_count}")
        print(f"  • Total Verdicts:       {verdict_count}")
        print("=" * 70)

        db.close()
    except Exception as e:
        print(f"\n[ERROR] Failed to connect or query database: {e}")

if __name__ == "__main__":
    db_arg = sys.argv[1] if len(sys.argv) > 1 else None
    inspect(db_arg)
