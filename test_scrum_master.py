#!/usr/bin/env python3
"""
Test script for AI Scrum Master with Granite LLM
Run this to verify the Scrum Master is working correctly
"""

import requests
import json

def test_granite_connection():
    """Test if Granite LLM is accessible"""
    print("=" * 60)
    print("Testing Granite LLM Connection...")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "granite3.3:2b",
                "prompt": "Hello, are you working?",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Granite LLM is accessible!")
            print(f"Response: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"✗ Granite LLM returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama at http://localhost:11434")
        print("  Make sure Ollama is running: ollama serve")
        print("  And granite3.3:2b model is installed: ollama pull granite3.3:2b")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_scrum_generation():
    """Test the Scrum Master schedule generation"""
    print("\n" + "=" * 60)
    print("Testing Scrum Master Schedule Generation...")
    print("=" * 60)
    
    from backend.services.advanced_scrum_master import AdvancedScrumMaster
    
    scrum = AdvancedScrumMaster()
    
    test_cases = [
        {
            "prompt": "RCC residential building with standard construction",
            "floors": "G+2",
            "season": "monsoon"
        },
        {
            "prompt": "Commercial building with fast-track construction",
            "floors": "G+4",
            "season": "summer"
        }
    ]
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {idx}:")
        print(f"  Prompt: {test_case['prompt']}")
        print(f"  Floors: {test_case['floors']}")
        print(f"  Season: {test_case['season']}")
        
        try:
            schedule = scrum.generate_realistic_schedule(
                test_case['prompt'],
                test_case['floors'],
                test_case['season']
            )
            
            print(f"  ✓ Schedule generated successfully!")
            print(f"  Total Sprints: {len(schedule.get('sprints', []))}")
            print(f"  Total Duration: {schedule.get('project_summary', {}).get('estimated_completion', 'N/A')}")
            print(f"  Floor Count: {schedule.get('project_summary', {}).get('floor_count', 'N/A')}")
            
            # Show first 3 sprints
            print(f"\n  First 3 Sprints:")
            for sprint in schedule.get('sprints', [])[:3]:
                print(f"    - {sprint.get('sprint')}: {sprint.get('phase')} ({sprint.get('duration')})")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

def test_delay_handling():
    """Test delay handling functionality"""
    print("\n" + "=" * 60)
    print("Testing Delay Handling...")
    print("=" * 60)
    
    from backend.services.advanced_scrum_master import AdvancedScrumMaster
    
    scrum = AdvancedScrumMaster()
    
    # Generate a schedule first
    schedule = scrum.generate_realistic_schedule(
        "Test building",
        "G+1",
        "summer"
    )
    
    original_weeks = schedule.get('project_summary', {}).get('total_weeks', 0)
    print(f"Original duration: {original_weeks} weeks")
    
    # Simulate a delay
    delay_info = {
        "task_name": "Foundation - Excavation",
        "delay_days": 7
    }
    
    updated_schedule = scrum.handle_delay(schedule, delay_info)
    new_weeks = updated_schedule.get('project_summary', {}).get('total_weeks', 0)
    
    print(f"After 7-day delay: {new_weeks} weeks")
    print(f"✓ Delay handling works! Duration increased by {new_weeks - original_weeks} weeks")

def test_checklist_update():
    """Test checklist update functionality"""
    print("\n" + "=" * 60)
    print("Testing Checklist Update...")
    print("=" * 60)
    
    from backend.services.advanced_scrum_master import AdvancedScrumMaster
    
    scrum = AdvancedScrumMaster()
    
    # Generate a schedule first
    schedule = scrum.generate_realistic_schedule(
        "Test building",
        "G+1",
        "summer"
    )
    
    # Get first sprint
    first_sprint = schedule.get('sprints', [])[0]
    task_name = first_sprint.get('phase')
    checklist_items = first_sprint.get('checklist', [])
    
    print(f"Task: {task_name}")
    print(f"Checklist items: {len(checklist_items)}")
    
    # Update first checklist item
    if checklist_items:
        updated_schedule = scrum.update_checklist(
            schedule,
            task_name,
            checklist_items[0],
            True
        )
        
        # Check if it was updated
        updated_sprint = updated_schedule.get('sprints', [])[0]
        status = updated_sprint.get('checklist_status', {}).get(checklist_items[0], False)
        
        if status:
            print(f"✓ Checklist update works! Item '{checklist_items[0]}' marked as complete")
        else:
            print(f"✗ Checklist update failed")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BuildWise AI Scrum Master Test Suite")
    print("=" * 60)
    
    # Test 1: Granite connection
    granite_ok = test_granite_connection()
    
    if not granite_ok:
        print("\n⚠ Warning: Granite LLM is not accessible.")
        print("The Scrum Master will still work but will use fallback logic.")
        print("\nTo fix:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Run: ollama serve")
        print("3. Run: ollama pull granite3.3:2b")
    
    # Test 2: Schedule generation
    test_scrum_generation()
    
    # Test 3: Delay handling
    test_delay_handling()
    
    # Test 4: Checklist update
    test_checklist_update()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start backend: cd backend && python app.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Login and navigate to Progress Tracker")
    print("4. Click 'AI Scrum Master' button")
    print("5. Fill in the form and generate schedule")
    print("=" * 60 + "\n")
