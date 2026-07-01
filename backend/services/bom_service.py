"""
BOM (Bill of Materials) Builder Engine - generates a full engineering bill of materials
from a natural-language requirement (e.g. "30kW EV Charger").
"""
import logging
from typing import Dict

from integrations.llm_client import generate_json

logger = logging.getLogger(__name__)

BOM_SYSTEM_MESSAGE = (
    "You are a senior EV-charging and solar systems engineer in India preparing a Bill of Materials "
    "(BOM) for a procurement team based in India. You have deep knowledge of real components, real "
    "manufacturers available in India (Havells, Polycab, RR Kabel, L&T, Crompton, CG Power, HPL, Indo "
    "Asian, Anchor, Exicom, Waaree, Vikram Solar and global brands sold in India like ABB, Siemens, "
    "Schneider Electric, Chint), and typical Indian industrial system designs. All costs MUST be given "
    "in Indian Rupees (₹/INR). Always respond with strict, valid, parseable JSON only."
)


def _build_bom_prompt(requirement: str) -> str:
    return f"""Generate a complete engineering Bill of Materials (BOM) for this requirement: "{requirement}"
for an installation in India. Only recommend brands/models genuinely available for purchase in India.

Think through what a real EV charging or solar installation of this specification would require: 
protection devices (MCB/MCCB/RCD/SPD), contactors/relays, energy meters, DC/AC isolators, 
connectors/cables (MC4, EV connector), enclosures, communication modules (Modbus/RS485), power 
supplies (SMPS), cooling fans, terminal blocks, etc. Only include components actually relevant to 
this specific requirement, with realistic quantities.

For EACH required component/category provide:
- category (e.g. "MCCB", "SPD Type 2", "EV Connector Type 2")
- quantity (integer)
- recommended_brand (real manufacturer available in India)
- recommended_model (real model/series if known, else representative series name)
- specification_requirement (key spec needed, e.g. "63A, 3P, 10kA, IEC 60947-2, BIS certified")
- estimated_unit_cost (in Indian Rupees, e.g. "₹3,500")
- estimated_total_cost (unit cost x quantity, in Indian Rupees, e.g. "₹10,500")
- engineering_notes (1 sentence rationale)
- alternatives (list of 1-2 alternative brands/models available in India)

Also provide:
- estimated_total_cost (sum across ALL components, in Indian Rupees, e.g. "₹1,85,000 - ₹2,20,000")
- engineering_notes (overall system design rationale, 2-3 sentences)

Return ONLY valid JSON with EXACTLY this structure:
{{
  "components": [
    {{"category":"string","quantity":1,"recommended_brand":"string","recommended_model":"string",
      "specification_requirement":"string","estimated_unit_cost":"₹3,500","estimated_total_cost":"₹10,500",
      "engineering_notes":"string","alternatives":["string"]}}
  ],
  "estimated_total_cost": "₹1,85,000 - ₹2,20,000",
  "engineering_notes": "string"
}}"""


async def generate_bom(requirement: str) -> Dict:
    prompt = _build_bom_prompt(requirement)
    parsed = await generate_json(BOM_SYSTEM_MESSAGE, prompt)
    if not parsed:
        raise RuntimeError('AI BOM generation failed to produce a valid result. Please try again.')
    return parsed
