import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.models import User, Investigation
from app.services.investigation_service import InvestigationService

async def run_direct_test():
    db = SessionLocal()
    try:
        # Get or create user
        user = db.query(User).filter(User.email == "test_direct@truthlens.ai").first()
        if not user:
            user = User(email="test_direct@truthlens.ai", hashed_password="hashed_pass_test", full_name="Direct Tester")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 1. Create Investigation
        claim_text = "The Earth revolves around the Sun."
        inv = InvestigationService.create_investigation(db=db, user_id=user.id, claim_text=claim_text, mode="DEMO")
        print(f"\nCreated Investigation ID: {inv.id} for claim: '{claim_text}'")

        # 2. Run Multi-Agent Graph synchronously
        print("Executing LangGraph multi-agent pipeline...")
        await InvestigationService.run_investigation(db=db, investigation_id=inv.id)

        # 3. Reload investigation from DB
        db.refresh(inv)
        print("\n===================================================")
        print(f"Investigation ID:  {inv.id}")
        print(f"Claim Text:        {inv.claim.text}")
        print(f"Verdict Status:    {inv.verdict_status}")
        print(f"Confidence Score:  {inv.confidence_score * 100:.1f}%")
        print(f"Pipeline Status:   {inv.status}")
        if inv.verdicts:
            print(f"Reasoning Summary: {inv.verdicts[0].reasoning_summary}")
        print("===================================================\n")

        assert inv.verdict_status == "TRUE", f"Expected TRUE, got {inv.verdict_status}"
        print("SUCCESS: Live test verified that verdict_status is TRUE!")

    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(run_direct_test())
