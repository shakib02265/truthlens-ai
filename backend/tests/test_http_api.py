import httpx
import time

def test_via_http():
    base_url = "http://localhost:8000/api"
    
    # 1. Login
    login_res = httpx.post(f"{base_url}/auth/login", json={
        "email": "investigator@truthlens.ai",
        "password": "SecurePassword123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Investigation
    claim_text = "The Earth revolves around the Sun."
    inv_res = httpx.post(f"{base_url}/investigations", json={
        "claim": claim_text,
        "mode": "DEMO"
    }, headers=headers)
    inv_id = inv_res.json()["id"]
    print(f"\nSubmitted Claim to HTTP API. Investigation ID: {inv_id}")

    # Poll until graph completes
    data = {}
    for i in range(15):
        time.sleep(1.0)
        detail_res = httpx.get(f"{base_url}/investigations/{inv_id}", headers=headers)
        data = detail_res.json()
        print(f"Waiting for completion... current status: {data.get('status')}")
        if data.get('status') in ["COMPLETED", "AWAITING_HUMAN_REVIEW"]:
            break

    conf = data.get('confidence_score') or 0.0

    print("\n===================================================")
    print(f"Investigation ID:  {data.get('id')}")
    print(f"Claim Text:        {data.get('claim', {}).get('text')}")
    print(f"Verdict Status:    {data.get('verdict_status')}")
    print(f"Confidence Score:  {conf * 100:.1f}%")
    print(f"Pipeline Status:   {data.get('status')}")
    if data.get('verdicts'):
        print(f"Reasoning Summary: {data['verdicts'][0].get('reasoning_summary')}")
    print("===================================================\n")

if __name__ == '__main__':
    test_via_http()
