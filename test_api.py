"""
Milestone 8: FastAPI Backend Test
Tests the REST API endpoints

Make sure the API server is running first:
    uvicorn api_server:app --reload

Then run this test:
    python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("MILESTONE 8: FastAPI Backend Test")
    print("=" * 60)

    print("\n[1/5] Testing API health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"OK API is healthy")
        print(f"  Lore documents: {data['lore_documents']}")
        print(f"  Model: {data['model']}")
    else:
        print(f"X ERROR: Health check failed ({response.status_code})")
        return False

    print("\n[2/5] Testing narrative generation (Turn 1)...")
    narrative_request = {
        "user_input": "I discover ancient ruins in the desert"
    }

    response = requests.post(f"{BASE_URL}/narrative", json=narrative_request)
    if response.status_code == 200:
        data = response.json()
        session_id = data['session_id']
        print(f"OK Narrative generated")
        print(f"  Session ID: {session_id}")
        print(f"  Lore used: {', '.join(data['lore_used'])}")
        print(f"\n  Narrative preview:")
        print(f"  {data['narrative'][:200]}...")
    else:
        print(f"X ERROR: Narrative generation failed ({response.status_code})")
        return False

    print("\n[3/5] Testing conversation continuity (Turn 2)...")
    narrative_request = {
        "user_input": "I examine the markings on the walls",
        "session_id": session_id  # Continue the same session
    }

    response = requests.post(f"{BASE_URL}/narrative", json=narrative_request)
    if response.status_code == 200:
        data = response.json()
        print(f"OK Narrative generated with conversation context")
        print(f"\n  Narrative preview:")
        print(f"  {data['narrative'][:200]}...")
    else:
        print(f"X ERROR: Narrative generation failed ({response.status_code})")
        return False

    print("\n[4/5] Testing session retrieval...")
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"OK Session retrieved")
        print(f"  Messages: {data['message_count']}")
        print(f"  Created: {data['created']}")
    else:
        print(f"X ERROR: Session retrieval failed ({response.status_code})")
        return False

    print("\n[5/5] Testing session list...")
    response = requests.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"OK Found {len(sessions)} sessions")
        if sessions:
            print(f"  Latest: {sessions[-1]}")
    else:
        print(f"X ERROR: Session list failed ({response.status_code})")
        return False

    print("\n" + "=" * 60)
    print("MILESTONE 8 COMPLETE!")
    print("=" * 60)
    print("\nFastAPI backend is fully operational!")
    print(f"\nAPI Documentation: {BASE_URL}/docs")
    print(f"Interactive API Explorer: {BASE_URL}/docs")
    print(f"\nEndpoints tested:")
    print(f"  GET  /health              - API health check")
    print(f"  POST /narrative           - Generate narratives")
    print(f"  GET  /session/{{id}}        - Get session info")
    print(f"  GET  /sessions            - List all sessions")
    print()

    return True

if __name__ == "__main__":
    print("\nMake sure the API server is running first:")
    print("  uvicorn api_server:app --reload\n")

    input("Press Enter to start the test...")

    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\nX ERROR: Could not connect to API server")
        print("Make sure it's running: uvicorn api_server:app --reload")
    except Exception as e:
        print(f"\nX ERROR: {e}")
