import requests
import json
from typing import Dict, List, Any

class ScrumMasterService:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.vision_model = "llava:13b"
        self.granite_model = "granite3.3:2b"
    
    def analyze_blueprint(self, image_path: str) -> Dict[str, Any]:
        """Use Ollama Vision model to extract blueprint data"""
        try:
            prompt = """Analyze this construction blueprint image and extract:
1. Construction phases (e.g., Foundation, Structure, Finishing)
2. Tasks within each phase
3. Estimated durations for each task
4. Task dependencies
5. Checklist items for each task

Return the data in this JSON format:
{
    "phases": [
        {
            "name": "Phase name",
            "tasks": [
                {
                    "name": "Task name",
                    "duration": "X days/weeks",
                    "dependencies": ["task1", "task2"],
                    "checklist": ["item1", "item2"]
                }
            ]
        }
    ]
}"""
            
            # Read image and encode to base64
            import base64
            with open(image_path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                # Parse the response to extract structured data
                return self._parse_vision_response(result.get('response', ''))
            else:
                return self._get_default_blueprint_data()
                
        except Exception as e:
            print(f"Vision model error: {str(e)}")
            return self._get_default_blueprint_data()
    
    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse vision model response into structured data"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_default_blueprint_data()
        except:
            return self._get_default_blueprint_data()
    
    def _get_default_blueprint_data(self) -> Dict[str, Any]:
        """Default blueprint structure if vision fails"""
        return {
            "phases": [
                {
                    "name": "Site Preparation",
                    "tasks": [
                        {
                            "name": "Site Survey & Marking",
                            "duration": "3 days",
                            "dependencies": [],
                            "checklist": ["Survey equipment ready", "Boundary marked", "Level checked"]
                        },
                        {
                            "name": "Excavation",
                            "duration": "5 days",
                            "dependencies": ["Site Survey & Marking"],
                            "checklist": ["Depth verified", "Soil tested", "Debris removed"]
                        }
                    ]
                },
                {
                    "name": "Foundation",
                    "tasks": [
                        {
                            "name": "Foundation Layout",
                            "duration": "2 days",
                            "dependencies": ["Excavation"],
                            "checklist": ["Layout marked", "Levels checked", "Approved by engineer"]
                        },
                        {
                            "name": "Foundation Concrete",
                            "duration": "7 days",
                            "dependencies": ["Foundation Layout"],
                            "checklist": ["Reinforcement placed", "Concrete tested", "Curing started"]
                        }
                    ]
                },
                {
                    "name": "Structure",
                    "tasks": [
                        {
                            "name": "Column Casting",
                            "duration": "10 days",
                            "dependencies": ["Foundation Concrete"],
                            "checklist": ["Shuttering erected", "Steel tied", "Concrete poured", "Curing done"]
                        },
                        {
                            "name": "Beam & Slab",
                            "duration": "14 days",
                            "dependencies": ["Column Casting"],
                            "checklist": ["Shuttering checked", "Reinforcement inspected", "Concrete quality verified"]
                        }
                    ]
                },
                {
                    "name": "Finishing",
                    "tasks": [
                        {
                            "name": "Plastering",
                            "duration": "12 days",
                            "dependencies": ["Beam & Slab"],
                            "checklist": ["Surface prepared", "Mix ratio correct", "Curing arranged"]
                        },
                        {
                            "name": "Flooring & Painting",
                            "duration": "10 days",
                            "dependencies": ["Plastering"],
                            "checklist": ["Surface leveled", "Materials approved", "Quality checked"]
                        }
                    ]
                }
            ]
        }
    
    def generate_scrum_schedule(self, blueprint_data: Dict[str, Any], floors: str, season: str) -> Dict[str, Any]:
        """Use Granite model to generate Scrum schedule"""
        try:
            prompt = f"""You are BuildWise AI, expert Construction Scrum Master.

BLUEPRINT DATA:
{json.dumps(blueprint_data, indent=2)}

PROJECT DETAILS:
- Building Type: {floors}
- Season: {season}

SEASON ADJUSTMENTS:
- Summer: Normal duration
- Monsoon: Increase duration by 30-40%
- Winter: Increase duration by 10-20%

Generate a detailed Scrum sprint plan with:
1. PROJECT SUMMARY
2. SPRINT PLAN (2-week sprints)
3. CHECKLIST SUMMARY
4. DEPENDENCIES
5. RISKS
6. UPDATED COMPLETION DATE
7. NEXT ACTIONS

Format as structured text with clear sections."""

            payload = {
                "model": self.granite_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                scrum_response = result.get('response', '')
                return self._structure_scrum_response(scrum_response, blueprint_data, floors, season)
            else:
                return self._get_default_scrum_schedule(blueprint_data, floors, season)
                
        except Exception as e:
            print(f"Granite model error: {str(e)}")
            return self._get_default_scrum_schedule(blueprint_data, floors, season)
    
    def _structure_scrum_response(self, response: str, blueprint_data: Dict, floors: str, season: str) -> Dict[str, Any]:
        """Structure the Granite response into JSON"""
        # Calculate adjusted durations based on season
        season_multiplier = {
            'summer': 1.0,
            'monsoon': 1.35,
            'winter': 1.15
        }.get(season.lower(), 1.0)
        
        # Extract floor count
        floor_count = int(floors.replace('G+', '')) + 1 if 'G+' in floors else 1
        
        sprints = []
        sprint_num = 1
        current_day = 0
        
        for phase in blueprint_data.get('phases', []):
            for task in phase.get('tasks', []):
                # Parse duration
                duration_str = task.get('duration', '5 days')
                base_days = int(duration_str.split()[0])
                adjusted_days = int(base_days * season_multiplier * floor_count)
                
                sprints.append({
                    'sprint': f'Sprint {sprint_num}',
                    'phase': phase.get('name'),
                    'task': task.get('name'),
                    'duration': f'{adjusted_days} days',
                    'start_day': current_day,
                    'end_day': current_day + adjusted_days,
                    'dependencies': task.get('dependencies', []),
                    'checklist': task.get('checklist', []),
                    'status': 'pending'
                })
                
                current_day += adjusted_days
                if sprint_num % 2 == 0:  # Every 2 tasks = 1 sprint
                    sprint_num += 1
        
        return {
            'project_summary': {
                'building_type': floors,
                'season': season,
                'total_duration': f'{current_day} days',
                'total_sprints': sprint_num,
                'season_impact': f'{int((season_multiplier - 1) * 100)}% duration increase'
            },
            'sprints': sprints,
            'granite_response': response,
            'completion_date': f'{current_day} days from start'
        }
    
    def _get_default_scrum_schedule(self, blueprint_data: Dict, floors: str, season: str) -> Dict[str, Any]:
        """Default schedule if Granite fails"""
        return self._structure_scrum_response("Default schedule generated", blueprint_data, floors, season)
    
    def handle_delay(self, schedule: Dict[str, Any], delay_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delay and recalculate schedule"""
        try:
            delayed_task = delay_info.get('task_name')
            delay_days = delay_info.get('delay_days', 0)
            
            sprints = schedule.get('sprints', [])
            task_found = False
            
            # Find the delayed task and shift all dependent tasks
            for i, sprint in enumerate(sprints):
                if sprint['task'] == delayed_task:
                    task_found = True
                    sprint['status'] = 'delayed'
                    sprint['delay'] = f'{delay_days} days'
                
                # Shift all tasks after the delayed one
                if task_found and i > 0:
                    sprint['start_day'] += delay_days
                    sprint['end_day'] += delay_days
            
            # Recalculate total duration
            if sprints:
                new_duration = sprints[-1]['end_day']
                schedule['project_summary']['total_duration'] = f'{new_duration} days'
                schedule['project_summary']['delay_impact'] = f'{delay_days} days delay'
            
            return schedule
            
        except Exception as e:
            print(f"Delay handling error: {str(e)}")
            return schedule
    
    def update_checklist(self, schedule: Dict[str, Any], task_name: str, checklist_item: str, completed: bool) -> Dict[str, Any]:
        """Update checklist item status"""
        try:
            sprints = schedule.get('sprints', [])
            
            for sprint in sprints:
                if sprint['task'] == task_name:
                    if 'checklist_status' not in sprint:
                        sprint['checklist_status'] = {}
                    sprint['checklist_status'][checklist_item] = completed
                    
                    # Check if all checklist items are complete
                    all_complete = all(
                        sprint['checklist_status'].get(item, False)
                        for item in sprint.get('checklist', [])
                    )
                    
                    if all_complete:
                        sprint['status'] = 'ready_for_next'
            
            return schedule
            
        except Exception as e:
            print(f"Checklist update error: {str(e)}")
            return schedule
