"""
BuildWise AI Construction Assistant
Hybrid: Python formula engine for calculations (instant) + Llama streaming for open questions
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import Generator

OLLAMA_URL = "http://localhost:11434/api/generate"

# Model selection based on available hardware:
# CPU only (your current laptop)  → llama3.2:1b  (1.3GB, ~40s response)
# 6GB GPU (RTX 3060/4060 etc.)    → llama3:8b    (4.7GB, ~3s response)
# 4GB GPU                         → llama3.2:3b  (2.0GB, ~5s response)
MODEL = "llama3.2:1b"  # change to "llama3:8b" on 6GB GPU machine

# ─── Construction formula engine ──────────────────────────────────────────────

THUMB_RULES = {
    "steel_kg_per_sqft": 4.0,
    "cement_bags_per_1000sqft": 425,
    "sand_cft_per_sqft": 1.8,
    "aggregate_cft_per_sqft": 2.7,
    "bricks_per_sqft": 55,
    "sqft_per_day": 45,
    "sqft_per_worker": 450,
}

CONSTRUCTION_KEYWORDS = [
    "steel", "cement", "sand", "aggregate", "brick", "bricks", "concrete",
    "slab", "beam", "column", "pillar", "foundation", "footing", "wall",
    "floor", "roof", "plinth", "rcc", "pcc", "shuttering", "curing",
    "plastering", "plaster", "waterproof", "dpc", "boq", "bill of quantities",
    "rate analysis", "labour", "labor", "worker", "workers", "manpower",
    "sqft", "square feet", "construction", "building", "residential",
    "excavation", "brickwork", "masonry", "estimate", "estimation",
    "cost", "budget", "timeline", "schedule", "is code", "nbc",
    "m20", "m25", "opc", "ppc", "tmt", "fe500", "carpet area",
    "built-up", "built up", "super built", "floor height", "beam size",
]


def _extract_area(text: str) -> int | None:
    """Extract sqft value from text."""
    m = re.search(r"(\d[\d,]*)\s*(?:sqft|sq\.?\s*ft|square\s*feet?)", text, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def _is_construction_question(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in CONSTRUCTION_KEYWORDS)


def _try_formula_engine(message: str) -> str | None:
    """
    Handle common calculation questions with instant Python formulas.
    Returns formatted answer string or None if not matched.
    """
    msg = message.lower()
    area = _extract_area(message)

    # ── Steel ──────────────────────────────────────────────────────────────
    if any(w in msg for w in ["steel", "tmt", "reinforcement", "rebar"]):
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "how"]):
            kg = area * THUMB_RULES["steel_kg_per_sqft"]
            tons = kg / 1000
            return f"""Given Data: Built-up area = {area:,} sqft

Formula: Steel = Area × 4 kg/sqft (thumb rule, RCC residential)

Calculation:
  Steel = {area:,} × 4 = {kg:,.0f} kg = {tons:.2f} tons

Final Answer: {tons:.2f} tons ({kg:,.0f} kg) of TMT steel

Assumptions:
  - RCC residential structure (G+1 or G+2)
  - Includes foundation, columns, beams, and slabs
  - Fe 500 grade TMT bars

Recommendations:
  - Add 5–10% wastage allowance → order {tons * 1.08:.2f} tons
  - Use Fe 500 or Fe 550 TMT bars (IS 1786)
  - Get structural engineer design for exact bar schedule"""

    # ── Cement ─────────────────────────────────────────────────────────────
    if any(w in msg for w in ["cement", "bags"]):
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "how"]):
            bags = (area / 1000) * THUMB_RULES["cement_bags_per_1000sqft"]
            return f"""Given Data: Built-up area = {area:,} sqft

Formula: Cement = (Area ÷ 1000) × 425 bags

Calculation:
  Cement = ({area:,} ÷ 1000) × 425 = {bags:.0f} bags (50 kg each)

Final Answer: {bags:.0f} cement bags = {bags * 50 / 1000:.1f} MT

Assumptions:
  - RCC residential structure
  - Includes all concrete work + masonry + plastering
  - OPC 43 or 53 grade

Recommendations:
  - Add 3% wastage → order {bags * 1.03:.0f} bags
  - Use OPC 53 for structural work, PPC for plastering
  - Store in dry place, use within 3 months of manufacture"""

    # ── Sand ───────────────────────────────────────────────────────────────
    if "sand" in msg:
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "how"]):
            cft = area * THUMB_RULES["sand_cft_per_sqft"]
            brass = cft / 100
            return f"""Given Data: Built-up area = {area:,} sqft

Formula: Sand = Area × 1.8 cft/sqft

Calculation:
  Sand = {area:,} × 1.8 = {cft:,.0f} cft
  In brass: {cft:,.0f} ÷ 100 = {brass:.1f} brass

Final Answer: {cft:,.0f} cft ({brass:.1f} brass) of sand

Assumptions:
  - Includes concrete + masonry + plastering work
  - River sand or M-sand

Recommendations:
  - Add 20% wastage → order {cft * 1.2:,.0f} cft ({brass * 1.2:.1f} brass)
  - Check silt content < 5% (IS 383)
  - M-sand is a good alternative to river sand"""

    # ── Aggregate ──────────────────────────────────────────────────────────
    if any(w in msg for w in ["aggregate", "coarse", "20mm", "10mm", "jelly"]):
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "how"]):
            total = area * THUMB_RULES["aggregate_cft_per_sqft"]
            a20 = total * 0.6
            a10 = total * 0.4
            return f"""Given Data: Built-up area = {area:,} sqft

Formula: Aggregate = Area × 2.7 cft/sqft (60% 20mm + 40% 10mm)

Calculation:
  Total aggregate = {area:,} × 2.7 = {total:,.0f} cft
  20mm aggregate  = {total:,.0f} × 60% = {a20:,.0f} cft
  10mm aggregate  = {total:,.0f} × 40% = {a10:,.0f} cft

Final Answer: {total:,.0f} cft total ({a20:,.0f} cft 20mm + {a10:,.0f} cft 10mm)

Assumptions:
  - Crushed stone aggregate (IS 383)
  - Includes all RCC work

Recommendations:
  - Add 5% wastage allowance
  - Check flakiness index < 25% (IS 2386)"""

    # ── Bricks ─────────────────────────────────────────────────────────────
    if any(w in msg for w in ["brick", "bricks"]):
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "wall", "how"]):
            bricks = area * THUMB_RULES["bricks_per_sqft"]
            return f"""Given Data: Wall area = {area:,} sqft (9-inch wall)

Formula: Bricks = Area × 55 nos/sqft

Calculation:
  Bricks = {area:,} × 55 = {bricks:,.0f} nos

Final Answer: {bricks:,.0f} bricks (standard size 9"×4.5"×3")

Assumptions:
  - 9-inch (230mm) thick wall
  - 10mm mortar joints
  - Standard clay bricks

Recommendations:
  - Add 8% breakage allowance → order {bricks * 1.08:,.0f} bricks
  - Use First Class bricks for load-bearing walls (IS 1077)
  - Check water absorption < 20%"""

    # ── Labour / Workers ───────────────────────────────────────────────────
    if any(w in msg for w in ["labour", "labor", "worker", "workers", "manpower"]):
        if area and any(w in msg for w in ["sqft", "required", "need", "much", "calculate", "estimate", "how", "many"]):
            workers = max(1, round(area / THUMB_RULES["sqft_per_worker"]))
            days = round(area / THUMB_RULES["sqft_per_day"])
            return f"""Given Data: Built-up area = {area:,} sqft

Formula:
  Workers = Area ÷ 450 sqft/worker
  Duration = Area ÷ 45 sqft/day

Calculation:
  Workers  = {area:,} ÷ 450 = {workers} workers
  Duration = {area:,} ÷ 45  = {days} working days (~{days // 30} months)

Final Answer: {workers} workers for approximately {days} days

Labour Cost Breakdown (India, 2024):
  Mason  : ₹600–800/day
  Helper : ₹400–500/day
  Total labour cost ≈ ₹80–100/sqft

Recommendations:
  - Add 15% buffer for weather/holiday delays
  - Hire experienced masons for structural work
  - Provide safety equipment (IS 3696)"""

    return None  # Not matched — fall through to LLM


# ─── System prompt for LLM (open-ended questions) ─────────────────────────────

LLM_SYSTEM_PROMPT = """You are BuildWise AI, a professional construction planning assistant for India.

RULES:
- Only answer construction-related questions (materials, structure, cost, planning, IS codes, NBC India).
- For non-construction questions reply: "I'm BuildWise AI, specialized in construction planning. Please ask construction-related questions."
- Use Indian units: sqft, kg, cft, brass, ₹
- Be concise and professional. No emojis.
- For definitions/concepts: give a clear structured explanation.
- For calculations: show Given Data → Formula → Calculation → Final Answer → Recommendations.

THUMB RULES (India):
Steel 4 kg/sqft | Cement 425 bags/1000sqft | Sand 1.8 cft/sqft | Aggregate 2.7 cft/sqft
Bricks 55/sqft (9-inch wall) | Labour 1 worker/450sqft | Speed 45 sqft/day
Slab min 5 inches | Column spacing 10-15ft | Beam min 9"×12" | Floor height 10ft std
External wall 9" | Internal wall 4.5" | M20 concrete for residential RCC"""


# ─── Main assistant class ──────────────────────────────────────────────────────

class ConstructionAIAssistant:
    def __init__(self):
        self.ollama_url = OLLAMA_URL
        self.model = MODEL

    def chat(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Returns response dict. Formula engine answers instantly (~0s).
        LLM fallback streams and returns full text.
        """
        # 1. Non-construction → instant refusal
        if not _is_construction_question(user_message):
            return {
                "response": "I'm BuildWise AI, specialized in construction planning. I can only help with construction-related questions like material estimation, structural design, cost planning, and project scheduling.",
                "timestamp": datetime.now().isoformat(),
                "model": "formula_engine",
                "success": True,
                "source": "validation"
            }

        # 2. Formula engine → instant calculation
        formula_result = _try_formula_engine(user_message)
        if formula_result:
            return {
                "response": formula_result,
                "timestamp": datetime.now().isoformat(),
                "model": "formula_engine",
                "success": True,
                "source": "formula_engine"
            }

        # 3. LLM fallback for open-ended questions (BOQ, types, concepts, etc.)
        return self._llm_response(user_message, conversation_history)

    def chat_stream(self, user_message: str, conversation_history: list = None) -> Generator[str, None, None]:
        """
        Streaming version — yields tokens as they arrive.
        Formula engine yields the full answer at once (instant).
        """
        if not _is_construction_question(user_message):
            yield "I'm BuildWise AI, specialized in construction planning. I can only help with construction-related questions like material estimation, structural design, cost planning, and project scheduling."
            return

        formula_result = _try_formula_engine(user_message)
        if formula_result:
            yield formula_result
            return

        # Stream from LLM
        yield from self._llm_stream(user_message, conversation_history)

    def _llm_response(self, user_message: str, conversation_history: list = None) -> dict:
        """Non-streaming LLM call."""
        try:
            prompt = self._build_prompt(user_message, conversation_history)
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 2048,    # GPU can handle large context easily
                    "num_predict": 600,
                    "top_k": 20,
                    "top_p": 0.85,
                    "repeat_penalty": 1.1,
                    "num_thread": 12,
                }
            }
            r = requests.post(self.ollama_url, json=payload, timeout=120)
            if r.status_code == 200:
                text = r.json().get("response", "").strip()
                if not text:
                    text = "I could not generate a response. Please rephrase your question."
                return {
                    "response": text,
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model,
                    "success": True,
                    "source": "llm"
                }
            return self._error_response(f"HTTP {r.status_code}")
        except requests.exceptions.Timeout:
            return self._error_response("LLM timed out. Please try a simpler question or ask about specific materials/quantities.")
        except requests.exceptions.ConnectionError:
            return self._error_response("Cannot connect to Ollama. Run: ollama serve")
        except Exception as e:
            return self._error_response(str(e))

    def _llm_stream(self, user_message: str, conversation_history: list = None) -> Generator[str, None, None]:
        """Streaming LLM call — yields tokens."""
        try:
            prompt = self._build_prompt(user_message, conversation_history)
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 2048,
                    "num_predict": 600,
                    "top_k": 20,
                    "top_p": 0.85,
                    "repeat_penalty": 1.1,
                    "num_thread": 12,
                }
            }
            with requests.post(self.ollama_url, json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done"):
                            break
        except Exception as e:
            yield f"Error: {e}"

    def _build_prompt(self, user_message: str, conversation_history: list = None) -> str:
        prompt = LLM_SYSTEM_PROMPT + "\n\n"
        if conversation_history:
            for msg in conversation_history[-4:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:200]
                prompt += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
            prompt += "\n"
        prompt += f"User: {user_message}\nAssistant:"
        return prompt

    def _error_response(self, error: str) -> dict:
        return {
            "response": f"Error: {error}",
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "success": False,
            "error": error
        }

    def get_quick_estimate(self, area_sqft: float, floors: int) -> str:
        total = area_sqft * floors
        steel_kg = total * 4
        cement_bags = (total / 1000) * 425
        sand_cft = total * 1.8
        agg_cft = total * 2.7
        workers = max(1, round(total / 450))
        days = round(total / 45)

        return f"""Quick Thumb Rule Estimate

Given Data:
  Area per floor : {area_sqft:,.0f} sqft
  Floors         : {floors}
  Total area     : {total:,.0f} sqft

Material Estimates:
  Steel     : {steel_kg:,.0f} kg ({steel_kg/1000:.2f} tons)
  Cement    : {cement_bags:.0f} bags (50 kg each)
  Sand      : {sand_cft:,.0f} cft ({sand_cft/100:.1f} brass)
  Aggregate : {agg_cft:,.0f} cft ({agg_cft*0.6:,.0f} cft 20mm + {agg_cft*0.4:,.0f} cft 10mm)

Labour & Timeline:
  Workers   : {workers} workers
  Duration  : ~{days} working days (~{days//30} months)

Note: Preliminary thumb rule estimate. Add 5–10% wastage. Consult structural engineer for detailed BOQ."""
