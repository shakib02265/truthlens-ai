import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "TruthLens AI"
    assert data["status"] == "operational"

def test_auth_and_investigation_flow():
    # 1. Register User
    email = "investigator@truthlens.ai"
    password = "SecurePassword123!"
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Lead Investigator"
    })
    
    if reg_res.status_code == 400:
        # User already registered in previous test run
        login_res = client.post("/api/auth/login", json={"email": email, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
    else:
        assert reg_res.status_code == 201
        token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 3. Create Investigation
    inv_res = client.post("/api/investigations", json={
        "claim": "Artificial intelligence causes permanent memory loss.",
        "mode": "DEMO"
    }, headers=headers)
    assert inv_res.status_code == 201
    inv_id = inv_res.json()["id"]

    # 4. Get Investigation Detail
    detail_res = client.get(f"/api/investigations/{inv_id}", headers=headers)
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["claim"]["text"] == "Artificial intelligence causes permanent memory loss."

    # 5. Get Evidence Graph
    graph_res = client.get(f"/api/investigations/{inv_id}/graph", headers=headers)
    assert graph_res.status_code == 200
    assert "nodes" in graph_res.json()

@pytest.mark.asyncio
async def test_verification_agent_pipeline_execution():
    from app.services.investigation_service import InvestigationService
    from app.core.database import SessionLocal
    from app.models.models import Investigation, Verdict, User

    db = SessionLocal()
    try:
        user = db.query(User).first()
        assert user is not None

        # Create investigation
        inv = InvestigationService.create_investigation(
            db=db,
            user_id=user.id,
            claim_text="The Earth revolves around the Sun.",
            mode="DEMO"
        )
        
        # Run graph workflow
        await InvestigationService.run_investigation(inv.id, db=db)

        # Reload investigation
        db.refresh(inv)
        assert inv.status in ["COMPLETED", "AWAITING_HUMAN_REVIEW"]
        assert inv.verdict_status is not None

        # Check Verdict & Verification status
        verdict = db.query(Verdict).filter(Verdict.investigation_id == inv.id).first()
        assert verdict is not None
        assert verdict.verified is True
        assert verdict.verification_notes is not None
        assert len(verdict.verification_notes) > 0
    finally:
        db.close()
