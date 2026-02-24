import requests
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

class AdvancedScrumMaster:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
        
        # Realistic construction data
        self.construction_phases = {
            "pre_construction": {
                "tasks": ["Site Clearing", "Layout Marking", "Soil Testing"],
                "base_duration": 2,  # weeks
                "checklist": ["Site cleared", "Layout approved by engineer", "Soil bearing capacity verified"]
            },
            "foundation": {
                "tasks": ["Excavation", "PCC (Plain Cement Concrete)", "Footing Reinforcement", "Footing Concrete"],
                "base_duration": 4,
                "checklist": ["Excavation depth verified", "PCC level checked", "Reinforcement inspected", "Concrete slump test passed"]
            },
            "structure_per_floor": {
                "tasks": ["Column Casting", "Beam Casting", "Slab Casting"],
                "base_duration": 6,  # weeks per floor
                "checklist": ["Reinforcement checked", "Shuttering aligned", "Electrical conduits installed", "Concrete curing started", "Cube samples taken"]
            },
            "brickwork": {
                "tasks": ["Brickwork All Floors", "Internal Wall Construction"],
                "base_duration": 8,
                "checklist": ["Masonry alignment verified", "Mortar quality verified", "Door/window openings checked"]
            },
            "finishing": {
                "tasks": ["Plastering", "Flooring", "Electrical Installation", "Plumbing Installation"],
                "base_duration": 8,
                "checklist": ["Electrical testing complete", "Plumbing pressure test passed", "Surface finish approved"]
            },
            "final": {
                "tasks": ["Painting", "Fixture Installation", "Final Inspection"],
                "base_duration": 4,
                "checklist": ["Paint curing complete", "Fixtures installed", "Final inspection passed"]
            }
        }
        
        self.season_multipliers = {
            "summer": 1.0,
            "monsoon": 1.35,  # 35% increase
            "winter": 1.15    # 15% increase
        }
        
        self.season_risks = {
            "summer": ["Heat affecting concrete curing", "Water scarcity", "Labour productivity in heat"],
            "monsoon": ["Rain delays slab curing", "Excavation flooding", "Material delivery delays", "Labour productivity reduction"],
            "winter": ["Concrete setting time increased", "Morning fog delays", "Shorter working hours"]
        }
    
    def generate_realistic_schedule(self, prompt: str, floors: str, season: str) -> Dict[str, Any]:
        """Generate realistic construction schedule using Granite LLM"""
        
        # Parse floor count
        floor_count = self._parse_floor_count(floors)
        season_multiplier = self.season_multipliers.get(season.lower(), 1.0)
        
        # Build comprehensive prompt for Granite
        granite_prompt = self._build_granite_prompt(prompt, floors, season, floor_count, season_multiplier)
        
        try:
            # Call Granite LLM
            payload = {
                "model": self.granite_model,
                "prompt": granite_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2000
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                granite_response = result.get('response', '')
                
                # Generate structured schedule
                schedule = self._generate_structured_schedule(
                    granite_response, prompt, floors, season, floor_count, season_multiplier
                )
                
                return schedule
            else:
                return self._generate_fallback_schedule(prompt, floors, season, floor_count, season_multiplier)
                
        except Exception as e:
            print(f"Granite LLM error: {str(e)}")
            return self._generate_fallback_schedule(prompt, floors, season, floor_count, season_multiplier)
    
    def _build_granite_prompt(self, user_prompt: str, floors: str, season: str, floor_count: int, multiplier: float) -> str:
        """Build comprehensive prompt for Granite LLM"""
        
        return f"""You are BuildWise AI, an expert Construction Scrum Master with 20+ years of experience in RCC construction.

USER REQUEST: {user_prompt}

IMPORTANT: Analyze the user's description carefully. Consider:
- Building area/size (if mentioned, e.g., 1000 sqft, 2000 sqft)
- Building type (residential, commercial, apartment, villa, etc.)
- Special requirements (basement, parking, amenities, etc.)
- Construction method preferences (fast-track, standard, etc.)

Adjust your schedule recommendations based on these details. Larger areas may need more time for finishing work.

PROJECT DETAILS:
- Building Type: RCC Residential Building
- Building Height: {floors} ({floor_count} floors total)
- Season: {season.capitalize()}
- Sprint Duration: 14 days (2 weeks) per sprint
- Season Impact: {int((multiplier - 1) * 100)}% duration adjustment

CONSTRUCTION METHODOLOGY:
You must follow standard RCC construction sequence:
1. Pre-construction (Site clearing, Layout, Soil testing)
2. Foundation (Excavation, PCC, Footing)
3. Structure (Column → Beam → Slab) - REPEAT FOR EACH FLOOR
4. Brickwork (After all slabs complete)
5. Finishing (Plastering, Flooring, MEP)
6. Final (Painting, Fixtures, Inspection)

CRITICAL CONSTRUCTION RULES:
- Slab curing: Minimum 28 days (normal), {int(28 * multiplier)} days ({season})
- Column to slab cycle: 6 weeks per floor (normal), {int(6 * multiplier)} weeks ({season})
- Cannot start next floor until previous slab cured
- Brickwork starts only after ALL structural slabs complete
- Finishing starts only after brickwork complete

SEASON-SPECIFIC CONSIDERATIONS ({season}):
{self._get_season_considerations(season)}

YOUR TASK:
Generate a detailed Scrum sprint plan following this EXACT format:

PROJECT SUMMARY
- Project Type: RCC Residential Building
- Building Height: {floors}
- Season: {season.capitalize()}
- Scrum Sprint Duration: 14 days per sprint
- Adjusted slab cycle: {int(28 * multiplier)} days
- Season impact: {self._get_season_impact_description(season, multiplier)}
- Estimated completion time: [Calculate total months]

SPRINT PLAN
[Generate Sprint 1, Sprint 2, etc. with:]
Sprint X (Week Y-Z)
Phase: [Phase name]
Tasks:
• [Task 1]
• [Task 2]
Checklist:
• [Checklist item 1]
• [Checklist item 2]
Dependencies:
• [What must complete before this]
Risks:
• [Season-specific risks]

CHECKLIST SUMMARY
[List all critical inspection points]

DEPENDENCIES
[Show construction dependency chain with arrows]

RISKS
[List major risks and mitigation strategies]

UPDATED COMPLETION DATE
[Calculate realistic completion timeline]

NEXT ACTIONS
[Recommend immediate next steps]

Be specific, realistic, and follow construction best practices. Calculate exact durations based on {floor_count} floors and {season} season."""

    def _get_season_considerations(self, season: str) -> str:
        """Get season-specific considerations"""
        considerations = {
            "summer": """- Concrete curing requires extra water
- Work hours: 6 AM - 6 PM (avoid peak heat)
- Increased water curing frequency
- Heat affecting concrete strength gain""",
            "monsoon": """- Excavation slower due to wet soil
- Concrete curing extended due to humidity
- Slab casting duration increased
- Rain-related work interruptions
- Material storage protection needed
- Dewatering pumps required""",
            "winter": """- Concrete setting time increased
- Morning fog delays (7 AM - 10 AM)
- Shorter effective working hours
- Curing duration extended
- Temperature below 5°C requires heating"""
        }
        return considerations.get(season.lower(), "Standard conditions")
    
    def _get_season_impact_description(self, season: str, multiplier: float) -> str:
        """Get season impact description"""
        impact = int((multiplier - 1) * 100)
        descriptions = {
            "summer": f"Normal duration (no adjustment)",
            "monsoon": f"Duration increased by {impact}% due to rain delays and extended curing",
            "winter": f"Duration increased by {impact}% due to cold weather and shorter working hours"
        }
        return descriptions.get(season.lower(), "Standard duration")
    
    def _parse_floor_count(self, floors: str) -> int:
        """Parse floor count from string like 'G+4'"""
        if 'G+' in floors:
            return int(floors.replace('G+', '')) + 1
        elif floors == 'G':
            return 1
        else:
            return 1
    
    def _generate_structured_schedule(self, granite_response: str, prompt: str, floors: str, 
                                     season: str, floor_count: int, multiplier: float) -> Dict[str, Any]:
        """Generate structured schedule from Granite response"""
        
        sprints = []
        current_week = 1
        sprint_num = 1
        
        # Phase 1: Pre-construction
        sprints.append({
            "sprint": f"Sprint {sprint_num}",
            "weeks": f"Week {current_week}-{current_week+1}",
            "phase": "Pre-construction",
            "tasks": ["Site clearing", "Layout marking", "Soil testing"],
            "duration": f"{int(2 * multiplier)} weeks",
            "checklist": ["Site cleared", "Layout approved by engineer", "Soil bearing capacity verified"],
            "dependencies": ["None - Starting phase"],
            "risks": self.season_risks.get(season.lower(), [])[:2],
            "status": "pending"
        })
        current_week += int(2 * multiplier)
        sprint_num += 1
        
        # Phase 2: Foundation
        sprints.append({
            "sprint": f"Sprint {sprint_num}",
            "weeks": f"Week {current_week}-{current_week+1}",
            "phase": "Foundation - Excavation",
            "tasks": ["Excavation", "PCC (Plain Cement Concrete)"],
            "duration": f"{int(2 * multiplier)} weeks",
            "checklist": ["Excavation depth verified", "PCC level checked", "Dewatering complete"],
            "dependencies": ["Layout marking must be complete"],
            "risks": ["Excavation flooding" if season.lower() == "monsoon" else "Soil stability"],
            "status": "pending"
        })
        current_week += int(2 * multiplier)
        sprint_num += 1
        
        sprints.append({
            "sprint": f"Sprint {sprint_num}",
            "weeks": f"Week {current_week}-{current_week+1}",
            "phase": "Foundation - Footing",
            "tasks": ["Reinforcement placement", "Footing concrete casting"],
            "duration": f"{int(2 * multiplier)} weeks",
            "checklist": ["Reinforcement inspected", "Concrete slump test passed", "Cube samples taken"],
            "dependencies": ["PCC must be complete"],
            "risks": ["Rain affecting concrete curing" if season.lower() == "monsoon" else "Concrete quality"],
            "status": "pending"
        })
        current_week += int(2 * multiplier)
        sprint_num += 1
        
        # Phase 3: Structure (per floor)
        floor_names = [
            "Ground Floor", "First Floor", "Second Floor", "Third Floor", "Fourth Floor", 
            "Fifth Floor", "Sixth Floor", "Seventh Floor", "Eighth Floor", "Ninth Floor", 
            "Tenth Floor", "Eleventh Floor"
        ]
        
        for floor_idx in range(floor_count):
            floor_name = floor_names[floor_idx] if floor_idx < len(floor_names) else f"Floor {floor_idx}"
            
            # Columns
            sprints.append({
                "sprint": f"Sprint {sprint_num}",
                "weeks": f"Week {current_week}-{current_week+1}",
                "phase": f"{floor_name} Structure - Columns",
                "tasks": ["Column reinforcement", "Column shuttering", "Column concrete casting"],
                "duration": f"{int(2 * multiplier)} weeks",
                "checklist": ["Reinforcement checked", "Shuttering aligned", "Concrete curing started"],
                "dependencies": [f"{'Footing' if floor_idx == 0 else floor_names[floor_idx-1] + ' slab'} must complete"],
                "risks": ["Verticality check critical", "Concrete segregation"],
                "status": "pending"
            })
            current_week += int(2 * multiplier)
            sprint_num += 1
            
            # Beams and Slab
            sprints.append({
                "sprint": f"Sprint {sprint_num}-{sprint_num+1}",
                "weeks": f"Week {current_week}-{current_week+3}",
                "phase": f"{floor_name} Structure - Beams & Slab",
                "tasks": ["Beam reinforcement", "Slab reinforcement", "Shuttering", "Concrete casting", "Curing"],
                "duration": f"{int(4 * multiplier)} weeks",
                "checklist": [
                    "Reinforcement inspected",
                    "Shuttering aligned",
                    "Electrical conduits installed",
                    "Concrete quality verified",
                    f"Curing for {int(28 * multiplier)} days"
                ],
                "dependencies": [f"{floor_name} columns must complete"],
                "risks": [
                    "Slab curing delay due to rain" if season.lower() == "monsoon" else "Concrete strength gain",
                    "Shuttering removal timing critical"
                ],
                "status": "pending"
            })
            current_week += int(4 * multiplier)
            sprint_num += 2
        
        # Phase 4: Brickwork
        sprints.append({
            "sprint": f"Sprint {sprint_num}-{sprint_num+3}",
            "weeks": f"Week {current_week}-{current_week+7}",
            "phase": "Brickwork and Masonry",
            "tasks": ["Brickwork all floors", "Internal wall construction", "Lintels"],
            "duration": f"{int(8 * multiplier)} weeks",
            "checklist": ["Masonry alignment verified", "Mortar quality verified", "Door/window openings checked"],
            "dependencies": ["All structural slabs must complete and cure"],
            "risks": ["Alignment issues", "Material quality"],
            "status": "pending"
        })
        current_week += int(8 * multiplier)
        sprint_num += 4
        
        # Phase 5: Finishing
        sprints.append({
            "sprint": f"Sprint {sprint_num}-{sprint_num+3}",
            "weeks": f"Week {current_week}-{current_week+7}",
            "phase": "Finishing Works",
            "tasks": ["Plastering", "Flooring", "Electrical installation", "Plumbing installation"],
            "duration": f"{int(8 * multiplier)} weeks",
            "checklist": [
                "Electrical testing complete",
                "Plumbing pressure test passed",
                "Surface finish approved",
                "Flooring level checked"
            ],
            "dependencies": ["Brickwork must complete"],
            "risks": ["Coordination between trades", "Material availability"],
            "status": "pending"
        })
        current_week += int(8 * multiplier)
        sprint_num += 4
        
        # Phase 6: Final
        sprints.append({
            "sprint": f"Sprint {sprint_num}-{sprint_num+1}",
            "weeks": f"Week {current_week}-{current_week+3}",
            "phase": "Final Completion",
            "tasks": ["Painting", "Fixture installation", "Final inspection", "Handover"],
            "duration": f"{int(4 * multiplier)} weeks",
            "checklist": [
                "Paint curing complete",
                "Fixtures installed",
                "Final inspection passed",
                "Occupancy certificate obtained"
            ],
            "dependencies": ["Finishing works must complete"],
            "risks": ["Final inspection delays", "Punch list items"],
            "status": "pending"
        })
        current_week += int(4 * multiplier)
        
        # Calculate total duration
        total_weeks = current_week - 1
        total_months = round(total_weeks / 4.33, 1)
        
        return {
            "project_summary": {
                "user_description": prompt,  # Store user's original description
                "project_type": "RCC Residential Building",
                "building_height": floors,
                "floor_count": floor_count,
                "season": season.capitalize(),
                "sprint_duration": "14 days per sprint",
                "adjusted_slab_cycle": f"{int(28 * multiplier)} days",
                "season_impact": self._get_season_impact_description(season, multiplier),
                "total_weeks": total_weeks,
                "total_months": total_months,
                "estimated_completion": f"{total_months} months"
            },
            "sprints": sprints,
            "granite_response": granite_response,
            "checklist_summary": self._generate_checklist_summary(),
            "dependencies": self._generate_dependency_chain(floor_count),
            "risks": self._generate_risk_summary(season, floor_count),
            "next_actions": [
                "Begin Sprint 1 immediately",
                "Monitor weather impact daily",
                "Track checklist completion",
                "Maintain material buffer stock",
                "Coordinate with structural engineer"
            ]
        }
    
    def _generate_fallback_schedule(self, prompt: str, floors: str, season: str, 
                                   floor_count: int, multiplier: float) -> Dict[str, Any]:
        """Generate fallback schedule if Granite fails"""
        return self._generate_structured_schedule("", prompt, floors, season, floor_count, multiplier)
    
    def _generate_checklist_summary(self) -> Dict[str, List[str]]:
        """Generate comprehensive checklist summary"""
        return {
            "Foundation": [
                "Soil inspection and bearing capacity test",
                "Reinforcement inspection before concrete",
                "Concrete slump test",
                "Cube sample collection"
            ],
            "Structure": [
                "Column verticality check",
                "Slab reinforcement inspection",
                "Concrete quality verification",
                "Curing monitoring",
                "Cube testing at 7, 14, 28 days"
            ],
            "Finishing": [
                "Electrical installation inspection",
                "Plumbing pressure test",
                "Surface finish quality check",
                "Final structural inspection"
            ]
        }
    
    def _generate_dependency_chain(self, floor_count: int) -> str:
        """Generate dependency chain visualization"""
        chain = """Site preparation
↓
Excavation
↓
Footing
↓"""
        
        for i in range(floor_count):
            floor_name = ["Ground", "First", "Second", "Third", "Fourth", "Fifth"][i] if i < 6 else f"Floor {i}"
            chain += f"""
{floor_name} Floor Columns
↓
{floor_name} Floor Slab
↓"""
        
        chain += """
Brickwork
↓
Plastering & Finishing
↓
Painting
↓
Handover"""
        
        return chain
    
    def _generate_risk_summary(self, season: str, floor_count: int) -> Dict[str, Any]:
        """Generate risk summary with mitigation"""
        risks = {
            "major_risks": self.season_risks.get(season.lower(), []),
            "mitigation": []
        }
        
        if season.lower() == "monsoon":
            risks["mitigation"] = [
                "Extend curing duration by 35%",
                "Maintain material buffer stock",
                "Plan parallel activities",
                "Install temporary rain protection",
                "Keep dewatering pumps ready"
            ]
        elif season.lower() == "winter":
            risks["mitigation"] = [
                "Start work after fog clears (10 AM)",
                "Use warm water for concrete mixing",
                "Extend curing duration by 15%",
                "Cover concrete during night"
            ]
        else:
            risks["mitigation"] = [
                "Increase water curing frequency",
                "Avoid concrete work during peak heat",
                "Maintain adequate water supply"
            ]
        
        return risks

    def handle_delay(self, schedule: Dict[str, Any], delay_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delay and recalculate schedule"""
        try:
            task_name = delay_info.get('task_name', '')
            delay_days = delay_info.get('delay_days', 0)
            
            if not task_name or delay_days <= 0:
                return schedule
            
            # Find the delayed task
            sprints = schedule.get('sprints', [])
            delayed_sprint_index = -1
            
            for idx, sprint in enumerate(sprints):
                if sprint.get('phase') == task_name:
                    delayed_sprint_index = idx
                    sprint['status'] = 'delayed'
                    sprint['delay_days'] = delay_days
                    break
            
            if delayed_sprint_index == -1:
                return schedule
            
            # Shift all subsequent tasks
            for idx in range(delayed_sprint_index + 1, len(sprints)):
                sprints[idx]['status'] = 'delayed'
            
            # Update project summary
            if 'project_summary' in schedule:
                old_weeks = schedule['project_summary'].get('total_weeks', 0)
                delay_weeks = delay_days / 7
                new_weeks = old_weeks + delay_weeks
                new_months = round(new_weeks / 4.33, 1)
                
                schedule['project_summary']['total_weeks'] = int(new_weeks)
                schedule['project_summary']['total_months'] = new_months
                schedule['project_summary']['estimated_completion'] = f"{new_months} months"
                schedule['project_summary']['delay_info'] = f"Delayed by {delay_days} days due to {task_name}"
            
            return schedule
            
        except Exception as e:
            print(f"Handle delay error: {str(e)}")
            return schedule
    
    def update_checklist(self, schedule: Dict[str, Any], task_name: str, checklist_item: str, completed: bool) -> Dict[str, Any]:
        """Update checklist item status"""
        try:
            sprints = schedule.get('sprints', [])
            
            for sprint in sprints:
                if sprint.get('phase') == task_name:
                    # Initialize checklist_status if not exists
                    if 'checklist_status' not in sprint:
                        sprint['checklist_status'] = {}
                    
                    # Update the specific checklist item
                    sprint['checklist_status'][checklist_item] = completed
                    
                    # Check if all checklist items are complete
                    checklist = sprint.get('checklist', [])
                    all_complete = all(
                        sprint['checklist_status'].get(item, False) 
                        for item in checklist
                    )
                    
                    # Update sprint status based on checklist completion
                    if all_complete and sprint.get('status') != 'delayed':
                        sprint['status'] = 'ready_for_next'
                    
                    break
            
            return schedule
            
        except Exception as e:
            print(f"Update checklist error: {str(e)}")
            return schedule
