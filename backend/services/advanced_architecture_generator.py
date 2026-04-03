"""
Advanced Architecture Generator - Production-Grade System
Combines multiple AI models and approaches for professional architecture design
Uses: Granite LLM, Professional AI Logic, Generative Models, Optimization Algorithms
"""

import requests
import json
import random
from typing import Dict, List, Tuple, Optional
from services.professional_architect_ai import ProfessionalArchitectAI
from services.deterministic_layout_engine import DeterministicLayoutEngine

class AdvancedArchitectureGenerator:
    """
    Production-grade architecture generator combining:
    1. Professional Architect AI (rule-based + intelligent extraction)
    2. Granite LLM (reasoning and recommendations)
    3. Generative optimization (multiple variants)
    4. Structural validation (engineering rules)
    5. Cost optimization (budget-aware design)
    """
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.granite_model = "granite3.3:2b"
        self.llama_model = "llama3.2:1b"
        self.professional_ai = ProfessionalArchitectAI()
        self.deterministic_engine = DeterministicLayoutEngine()
        
        # Generative model parameters
        self.generation_modes = {
            'conservative': {'creativity': 0.2, 'optimization': 'space'},
            'balanced': {'creativity': 0.5, 'optimization': 'balanced'},
            'creative': {'creativity': 0.8, 'optimization': 'aesthetics'},
            'cost_optimized': {'creativity': 0.3, 'optimization': 'cost'},
            'luxury': {'creativity': 0.7, 'optimization': 'premium'}
        }
    
    def generate_multi_variant_layouts(self, user_input: str, num_variants: int = 3) -> List[Dict]:
        """
        Generate multiple layout variants using different approaches
        
        Args:
            user_input: User requirements in any format
            num_variants: Number of variants to generate (default 3)
            
        Returns:
            List of layout variants with scores and recommendations
        """
        
        print(f"Generating {num_variants} professional layout variants...")
        
        # Step 1: Extract parameters using Professional AI
        base_params = self.professional_ai.extract_parameters(user_input)
        
        # Step 2: Generate variants using different strategies
        variants = []
        
        for i in range(num_variants):
            variant_mode = list(self.generation_modes.keys())[i % len(self.generation_modes)]
            
            variant = self._generate_single_variant(
                base_params, 
                variant_mode, 
                variant_number=i+1
            )
            
            variants.append(variant)
        
        # Step 3: Score and rank variants
        scored_variants = self._score_variants(variants, base_params)
        
        # Step 4: Add AI recommendations for each variant
        for variant in scored_variants:
            variant['ai_recommendation'] = self._generate_variant_recommendation(
                variant, base_params
            )
        
        return scored_variants
    
    def _generate_single_variant(self, base_params: Dict, mode: str, variant_number: int) -> Dict:
        """Generate a single layout variant with specific optimization mode"""
        
        mode_config = self.generation_modes[mode]
        creativity = mode_config['creativity']
        optimization = mode_config['optimization']
        
        # Apply mode-specific modifications
        modified_params = self._apply_mode_modifications(base_params, mode, creativity)
        
        # Generate layout using professional AI
        layout = self.professional_ai.generate_professional_layout(
            self._params_to_prompt(modified_params)
        )
        
        # Add variant-specific metadata
        layout['variant_number'] = variant_number
        layout['generation_mode'] = mode
        layout['optimization_focus'] = optimization
        layout['creativity_level'] = creativity
        
        return layout
    
    def _apply_mode_modifications(self, params: Dict, mode: str, creativity: float) -> Dict:
        """Apply mode-specific modifications to parameters"""
        
        modified = params.copy()
        
        if mode == 'conservative':
            # Maximize space efficiency, minimize cost
            modified['room_size_factor'] = 1.0  # Standard sizes
            modified['circulation_factor'] = 0.15  # Minimal circulation
            
        elif mode == 'balanced':
            # Balance between space, cost, and comfort
            modified['room_size_factor'] = 1.1  # Slightly larger
            modified['circulation_factor'] = 0.18  # Standard circulation
            
        elif mode == 'creative':
            # Unique layouts, aesthetic focus
            modified['room_size_factor'] = 1.2  # Larger rooms
            modified['circulation_factor'] = 0.20  # More circulation
            modified['add_features'] = ['balcony', 'study_nook', 'reading_corner']
            
        elif mode == 'cost_optimized':
            # Minimize construction cost
            modified['room_size_factor'] = 0.95  # Compact but standard
            modified['circulation_factor'] = 0.15  # Minimal
            modified['structural_optimization'] = 'cost'
            
        elif mode == 'luxury':
            # Premium features, spacious
            modified['room_size_factor'] = 1.3  # Larger rooms
            modified['circulation_factor'] = 0.22  # Generous circulation
            modified['add_features'] = ['walk_in_closet', 'powder_room', 'home_office', 'balcony']
        
        return modified
    
    def _score_variants(self, variants: List[Dict], base_params: Dict) -> List[Dict]:
        """Score variants based on multiple criteria"""
        
        for variant in variants:
            scores = {
                'space_efficiency': self._score_space_efficiency(variant),
                'structural_feasibility': self._score_structural_feasibility(variant),
                'cost_effectiveness': self._score_cost_effectiveness(variant, base_params),
                'comfort_livability': self._score_comfort_livability(variant),
                'aesthetic_appeal': self._score_aesthetic_appeal(variant),
                'nbc_compliance': self._score_nbc_compliance(variant)
            }
            
            # Calculate overall score (weighted average)
            weights = {
                'space_efficiency': 0.20,
                'structural_feasibility': 0.20,
                'cost_effectiveness': 0.15,
                'comfort_livability': 0.20,
                'aesthetic_appeal': 0.10,
                'nbc_compliance': 0.15
            }
            
            overall_score = sum(scores[k] * weights[k] for k in scores)
            
            variant['scores'] = scores
            variant['overall_score'] = round(overall_score, 2)
            variant['grade'] = self._score_to_grade(overall_score)
        
        # Sort by overall score (descending)
        variants.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return variants
    
    def _score_space_efficiency(self, variant: Dict) -> float:
        """Score space efficiency (0-100)"""
        
        floors = variant['3_floor_layouts']
        total_builtup = sum(f['built_up_area'] for f in floors)
        total_circulation = sum(f['circulation_area'] for f in floors)
        
        # Ideal circulation: 15-20%
        circulation_ratio = total_circulation / (total_builtup + total_circulation)
        
        if 0.15 <= circulation_ratio <= 0.20:
            circulation_score = 100
        elif circulation_ratio < 0.15:
            circulation_score = 70 + (circulation_ratio / 0.15) * 30
        else:
            circulation_score = 100 - ((circulation_ratio - 0.20) / 0.10) * 30
        
        # Room size efficiency
        room_sizes_ok = all(
            room['area'] >= 100 for floor in floors 
            for room in floor['rooms'] 
            if 'Bedroom' in room['name'] or 'Living' in room['name']
        )
        
        room_score = 100 if room_sizes_ok else 70
        
        return (circulation_score * 0.6 + room_score * 0.4)
    
    def _score_structural_feasibility(self, variant: Dict) -> float:
        """Score structural feasibility (0-100)"""
        
        grid = variant['4_structural_grid']
        feasibility_notes = variant['9_structural_feasibility']
        
        # Count positive vs warning notes
        positive_count = sum(1 for note in feasibility_notes if '✓' in note)
        warning_count = sum(1 for note in feasibility_notes if '⚠️' in note)
        
        total_checks = len(feasibility_notes)
        
        if total_checks == 0:
            return 80
        
        score = (positive_count / total_checks) * 100
        
        return max(50, min(100, score))
    
    def _score_cost_effectiveness(self, variant: Dict, base_params: Dict) -> float:
        """Score cost effectiveness (0-100)"""
        
        floors = variant['3_floor_layouts']
        total_area = sum(f['total_area'] for f in floors)
        
        # Cost per sqft (assumed ₹1800)
        total_cost = total_area * 1800
        
        # Ideal cost for configuration
        bedrooms = base_params.get('bedrooms', 2)
        ideal_area = bedrooms * 500  # 500 sqft per bedroom
        ideal_cost = ideal_area * 1800
        
        # Score based on how close to ideal
        cost_ratio = total_cost / ideal_cost
        
        if 0.9 <= cost_ratio <= 1.2:
            score = 100
        elif cost_ratio < 0.9:
            score = 80 + (cost_ratio / 0.9) * 20
        else:
            score = 100 - ((cost_ratio - 1.2) / 0.3) * 30
        
        return max(50, min(100, score))
    
    def _score_comfort_livability(self, variant: Dict) -> float:
        """Score comfort and livability (0-100)"""
        
        floors = variant['3_floor_layouts']
        
        # Check for essential features
        has_entrance_foyer = any(
            'Foyer' in room['name'] or 'Entrance' in room['name']
            for floor in floors for room in floor['rooms']
        )
        
        has_attached_bath = any(
            'attached' in room.get('notes', '').lower()
            for floor in floors for room in floor['rooms']
        )
        
        has_proper_ventilation = variant['7_ventilation_strategy']['strategy'] == 'Cross-ventilation'
        
        has_circulation = all(f['circulation_area'] > 0 for f in floors)
        
        # Calculate score
        score = 60  # Base score
        if has_entrance_foyer: score += 10
        if has_attached_bath: score += 10
        if has_proper_ventilation: score += 10
        if has_circulation: score += 10
        
        return score
    
    def _score_aesthetic_appeal(self, variant: Dict) -> float:
        """Score aesthetic appeal (0-100)"""
        
        # Based on room proportions, symmetry, and features
        floors = variant['3_floor_layouts']
        
        # Check room proportions (ideal: 1:1.2 to 1:1.5)
        good_proportions = 0
        total_rooms = 0
        
        for floor in floors:
            for room in floor['rooms']:
                if 'Bedroom' in room['name'] or 'Living' in room['name']:
                    dims = room['dimensions'].split('×')
                    if len(dims) == 2:
                        try:
                            w = float(dims[0].replace('ft', '').strip())
                            l = float(dims[1].replace('ft', '').strip())
                            ratio = max(w, l) / min(w, l)
                            if 1.0 <= ratio <= 1.5:
                                good_proportions += 1
                            total_rooms += 1
                        except:
                            pass
        
        proportion_score = (good_proportions / total_rooms * 100) if total_rooms > 0 else 70
        
        # Bonus for special features
        has_balcony = any(
            'balcony' in room['name'].lower()
            for floor in floors for room in floor['rooms']
        )
        
        has_study = any(
            'study' in room['name'].lower() or 'office' in room['name'].lower()
            for floor in floors for room in floor['rooms']
        )
        
        feature_bonus = 0
        if has_balcony: feature_bonus += 10
        if has_study: feature_bonus += 5
        
        return min(100, proportion_score * 0.8 + feature_bonus)
    
    def _score_nbc_compliance(self, variant: Dict) -> float:
        """Score NBC compliance (0-100)"""
        
        # Check if all rooms meet NBC standards
        floors = variant['3_floor_layouts']
        
        compliant_rooms = 0
        total_rooms = 0
        
        nbc_minimums = {
            'Bedroom': 100,  # sqft
            'Living': 150,
            'Kitchen': 75,
            'Bathroom': 24
        }
        
        for floor in floors:
            for room in floor['rooms']:
                for room_type, min_area in nbc_minimums.items():
                    if room_type in room['name']:
                        if room['area'] >= min_area:
                            compliant_rooms += 1
                        total_rooms += 1
                        break
        
        if total_rooms == 0:
            return 90
        
        compliance_ratio = compliant_rooms / total_rooms
        
        return compliance_ratio * 100
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C+'
        elif score >= 55: return 'C'
        else: return 'C-'
    
    def _generate_variant_recommendation(self, variant: Dict, base_params: Dict) -> str:
        """Generate AI recommendation for variant using Granite LLM"""
        
        prompt = f"""Analyze this architectural layout variant and provide a brief professional recommendation.

Variant: {variant['generation_mode'].upper()}
Overall Score: {variant['overall_score']}/100 (Grade: {variant['grade']})

Scores:
- Space Efficiency: {variant['scores']['space_efficiency']:.1f}/100
- Structural Feasibility: {variant['scores']['structural_feasibility']:.1f}/100
- Cost Effectiveness: {variant['scores']['cost_effectiveness']:.1f}/100
- Comfort & Livability: {variant['scores']['comfort_livability']:.1f}/100
- Aesthetic Appeal: {variant['scores']['aesthetic_appeal']:.1f}/100
- NBC Compliance: {variant['scores']['nbc_compliance']:.1f}/100

Provide a 2-3 sentence professional recommendation about this variant's strengths and ideal use case."""

        try:
            payload = {
                "model": self.granite_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
        
        except Exception as e:
            print(f"Granite recommendation error: {str(e)}")
        
        # Fallback recommendation
        mode = variant['generation_mode']
        score = variant['overall_score']
        
        if mode == 'conservative':
            return f"Space-efficient design (Score: {score}/100). Best for budget-conscious projects prioritizing functionality over luxury."
        elif mode == 'balanced':
            return f"Well-balanced design (Score: {score}/100). Ideal for most residential projects with good space, cost, and comfort balance."
        elif mode == 'creative':
            return f"Aesthetically focused design (Score: {score}/100). Perfect for clients seeking unique layouts with premium features."
        elif mode == 'cost_optimized':
            return f"Cost-effective design (Score: {score}/100). Optimal for budget projects without compromising essential standards."
        else:  # luxury
            return f"Premium design (Score: {score}/100). Ideal for high-end projects with spacious rooms and luxury features."
    
    def _params_to_prompt(self, params: Dict) -> str:
        """Convert parameters back to prompt format"""
        
        prompt_parts = []
        
        prompt_parts.append(f"{params['plot_width']}ft × {params['plot_length']}ft plot")
        prompt_parts.append(f"{params['bedrooms']}BHK")
        
        if params['floors'] > 1:
            prompt_parts.append(f"G+{params['floors']-1}")
        
        if params.get('parking'):
            prompt_parts.append("parking")
        
        if params.get('pooja'):
            prompt_parts.append("pooja room")
        
        if params.get('office'):
            prompt_parts.append("office")
        
        if params.get('duplex'):
            prompt_parts.append("duplex")
        
        prompt_parts.append("good ventilation")
        
        return ", ".join(prompt_parts)
