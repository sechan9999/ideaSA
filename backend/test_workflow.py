import requests
import json
import time

API_BASE = "http://localhost:8000"

def log(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] {msg}")

def run_test():
    log("Starting IdeaSA Workflow Test...")
    
    # 1. Start Workflow (Topic: 'Autonomous Drone Delivery')
    topic = "Autonomous Drone Delivery"
    log(f"Step 1: Starting Workflow with topic '{topic}'")
    
    try:
        response = requests.post(f"{API_BASE}/workflow/start", params={"topic": topic})
        response.raise_for_status()
        seeds = response.json()
        log(f"Received {len(seeds)} Seeds:")
        for s in seeds:
            print(f"  - [{s['id']}] {s['title']}")
            
        if not seeds:
            log("No seeds returned! Exiting.")
            return

        idea_id = seeds[0]['id']
        log(f"Selected Idea ID: {idea_id}")

        # 2. Refine Idea
        log(f"Step 2: Refining Idea {idea_id}")
        response = requests.post(f"{API_BASE}/workflow/refine/{idea_id}")
        response.raise_for_status()
        refined_idea = response.json()
        print(f"  Refined Description Sample: {refined_idea['description'][:100]}...")
        print(f"  System Status: {refined_idea['status']}")

        # 3. Evaluate Idea
        log(f"Step 3: Evaluating Idea {idea_id}")
        response = requests.post(f"{API_BASE}/workflow/evaluate/{idea_id}")
        response.raise_for_status()
        evaluated_idea = response.json()
        print(f"  Scores: Market={evaluated_idea['market_score']}, Tech={evaluated_idea['tech_score']}")
        print(f"  Evaluations: {[e['reviewer_role'] + ': ' + str(e['score']) for e in evaluated_idea['evaluations']]}")

        # 4. Generate Artifact (PDF)
        log(f"Step 4: Generating PDF Artifact for Idea {idea_id}")
        response = requests.post(f"{API_BASE}/workflow/artifact/{idea_id}", params={"artifact_type": "pdf"})
        response.raise_for_status()
        artifact_url = response.json()
        print(f"  PDF URL: {artifact_url}")

        # 5. Leaderboard
        log("Step 5: Checking Leaderboard")
        response = requests.get(f"{API_BASE}/leaderboard")
        leaderboard = response.json()
        print(f"  Top Idea: {leaderboard[0]['title']} (Score: {leaderboard[0]['total_score']})")
        
        log("Test Complete: SUCCESS")

    except Exception as e:
        log(f"Test Failed: {e}")
        try:
            if 'response' in locals():
                print(f"Response Body: {response.text}")
        except:
            pass

if __name__ == "__main__":
    run_test()
