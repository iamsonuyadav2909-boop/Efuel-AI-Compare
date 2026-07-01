"""
BOM (Bill of Materials) Builder Engine - generates a full engineering bill of materials
from a natural-language requirement (e.g. "30kW EV Charger").
"""
import logging
from typing import Dict

from integrations.llm_client import generate_json

logger = logging.getLogger(__name__)

BOM_SYSTEM_MESSAGE = (
    "You are a senior EV-charging and solar systems engineer preparing a Bill of Materials (BOM) "
    "for a procurement team. You have deep knowledge of real components, real manufacturers, and "
    "typical industrial system designs. Always respond with strict, valid, parseable JSON only."
)


def _build_bom_prompt(requirement: str) -> str:
    return f"""Generate a complete engineering Bill of Materials (BOM) for this requirement: "{requirement}"

Think through what a real EV charging or solar installation of this specification would require: 
protection devices (MCB/MCCB/RCD/SPD), contactors/relays, energy meters, DC/AC isolators, 
connectors/cables (MC4, EV connector), enclosures, communication modules (Modbus/RS485), power 
supplies (SMPS), cooling fans, terminal blocks, etc. Only include components actually relevant to 
this specific requirement, with realistic quantities.

For EACH required component/category provide:
- category (e.g. "MCCB", "SPD Type 2", "EV Connector Type 2")
- quantity (integer)
- recommended_brand (real manufacturer)
- recommended_model (real model/series if known, else representative series name)
- specification_requirement (key spec needed, e.g. "63A, 3P, 10kA, IEC 60947-2")
- estimated_unit_cost (approx string, e.g. "$45")
- estimated_total_cost (unit cost x quantity, approx string, e.g. "$135")
- engineering_notes (1 sentence rationale)
- alternatives (list of 1-2 alternative brands/models)

Also provide:
- estimated_total_cost (sum across ALL components, approx string e.g. "$2,400 - $3,100")
- engineering_notes (overall system design rationale, 2-3 sentences)

Return ONLY valid JSON with EXACTLY this structure:
{{
  "components": [
    {{"category":"string","quantity":1,"recommended_brand":"string","recommended_model":"string",
      "specification_requirement":"string","estimated_unit_cost":"string","estimated_total_cost":"string",
      "engineering_notes":"string","alternatives":["string"]}}
  ],
  "estimated_total_cost": "string",
  "engineering_notes": "string"
}}"""


async def generate_bom(requirement: str) -> Dict:
    prompt = _build_bom_prompt(requirement)
    parsed = await generate_json(BOM_SYSTEM_MESSAGE, prompt)
    if not parsed:
        raise RuntimeError('AI BOM generation failed to produce a valid result. Please try again.')
    return parsed
