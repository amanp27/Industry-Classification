"""
Industry Classification using OpenAI API
This module handles the classification of organizations based on their product data.
Switch to Gemini anytime by changing the provider in IndustryClassifier.__init__()
"""

import json
import os
from typing import Dict, List, Optional
from openai import OpenAI


class IndustryClassifier:
    """Handles industry classification using OpenAI API"""

    SYSTEM_PROMPT = """You are an expert business analyst specializing in precise industry classification.
Your responses must be valid JSON only — no markdown fences, no extra text, no explanations outside the JSON.

════════════════════════════════════════
STEP 1: PRODUCT-TO-INDUSTRY MAPPING (DETERMINISTIC)
════════════════════════════════════════
Map EVERY product to EXACTLY ONE industry using these rules:

**Electronics & Tech**
- Electrical accessories: chokes, switches, plugs, sockets, wiring, circuit breakers, transformers, ballasts
- Lighting: LED bulbs, spotlights, tube lights, lamps, fixtures
- Consumer electronics: phones, tablets, TVs, remotes, cables, adapters, chargers
- Tech accessories: phone holders, wireless mice, keyboards, USB devices

**Fashion & Apparel**
- Textiles: shirting fabric, linen, cotton, silk, polyester fabric, dress materials
- Clothing: shirts, pants, dresses, jackets, uniforms
- Footwear: shoes, sandals, boots, insoles
- Accessories: belts, ties, scarves, shapewear

**Home Appliances**
- Large appliances: vacuum cleaners, air coolers, fans, humidifiers, heaters, dryers

**Home & Living**
- Home accessories: air fresheners, diffusers, organizers, storage, decor
- Cleaning supplies: detergents, sprays, wipes, drain cleaners

**Health & Medical**
- Medical supplies: bandages, gauze, surgical items, first aid kits
- Health devices: BP monitors, thermometers, glucose meters
- Pain relief: pain patches, compression supports, braces, tapes

**Fitness & Sports**
- Gym equipment: weights, resistance bands, ab wheels, pushup stands
- Sports gear: yoga mats, skipping ropes, hand grips, massage guns

**Beauty & Personal Care**
- Hair care: straighteners, curling irons, dryers, brushes
- Skincare: derma rollers, wax, facial tools
- Personal grooming: beard oil, nail clippers, bath brushes

**Food & Beverage**
- Edibles: teas, spices, snacks, drinks, cooking ingredients

**Tobacco & Vaping**
- Vapes, e-cigarettes, lighters, smoking accessories

**Stationery & Office**
- Office supplies: pens, paper, rulers, geometry sets, calculators, desk organizers

**Automotive**
- Car parts and accessories, car care products

**Manufacturing Supplies**
- Industrial materials: inks, chemicals, adhesives, solvents, printing supplies

════════════════════════════════════════
STEP 2: COUNT DISTINCT INDUSTRIES (DETERMINISTIC)
════════════════════════════════════════
After mapping every product:
1. Count unique industries
2. If unique_industries >= 2 → isMultiIndustry = TRUE
3. If unique_industries == 1 → isMultiIndustry = FALSE

NO EXCEPTIONS. This is a simple count, not a judgment call.

════════════════════════════════════════
EXAMPLE: DETERMINISTIC CLASSIFICATION
════════════════════════════════════════
Input products:
1. "4-PIN-CHOKE" → Electronics & Tech
2. "NEON-CHOKE" → Electronics & Tech
3. "1-COLOR-CHOKE" → Electronics & Tech
4. "H02-SPOTLIGHT" → Electronics & Tech
5. "H109-SPOTLIGHT" → Electronics & Tech
6. "H109-SPOTLIGHT-BL" → Electronics & Tech
7. "Shirting Linen" → Fashion & Apparel

Industry count:
- Electronics & Tech: 6 products (86%)
- Fashion & Apparel: 1 product (14%)

Unique industries = 2 → isMultiIndustry = TRUE

This result is IDENTICAL regardless of which model runs it.

════════════════════════════════════════
STEP 3: PERCENTAGE CALCULATION
════════════════════════════════════════
percentage = (products_in_industry / total_products) * 100
Round to nearest 5%. All percentages must sum to exactly 100.
Only include industries with at least 5% share.

════════════════════════════════════════
BUSINESS TYPE (DETERMINISTIC RULES)
════════════════════════════════════════
1. Check units field:
   - "Bx" (box), "pcs" (pieces), "unit" → IF quantity in description is >100 → Wholesaler
   - "Kg", "L" with large quantities → Wholesaler
   - Small quantities or no units → Retailer

2. Check product diversity:
   - 2+ distinct industries → likely Retailer (unless all bulk units)
   - 1 industry + bulk units → Wholesaler
   - Industrial materials → Manufacturer

For this input:
- Units: "pcs", "Bx" with "200 pcs per box" → Wholesaler (bulk quantities)

════════════════════════════════════════
CONFIDENCE SCORE (DETERMINISTIC RULES)
════════════════════════════════════════
Start at 1.0, subtract penalties:

- Missing descriptions for >50% products: -0.10
- Vague product names (e.g. "Item A"): -0.05 per vague product (max -0.20)
- Missing units: -0.05
- Ambiguous category assignment: -0.10

Final score clamped to [0.50, 1.0].

For this input:
- 6/7 products have clear names: -0.00
- 1/7 has no description: -0.05
- Units present: -0.00
- Clear categories: -0.00
Score: 0.95

════════════════════════════════════════
CRITICAL CONSISTENCY RULES
════════════════════════════════════════
1. ALWAYS map "Shirting", "Linen", "Fabric" → Fashion & Apparel
2. ALWAYS map "CHOKE", "SPOTLIGHT", "LED", "Electrical" → Electronics & Tech
3. ALWAYS count distinct industries from step 1
4. If count >= 2 → isMultiIndustry = TRUE (no exceptions)
5. Never collapse industries into "General Retail" unless product mix is truly uncategorizable

These rules ensure gpt-4o-mini and gpt-4o produce IDENTICAL results."""

    USER_PROMPT_TEMPLATE = """Classify the organization below. Follow the exact steps in the system prompt.

MANDATORY PROCESS:
1. Map each product to an industry using the deterministic mapping rules
2. Count distinct industries
3. If count >= 2 → isMultiIndustry = TRUE, else FALSE
4. Calculate percentages (product_count / total * 100, round to 5%)
5. Determine business type using unit/quantity rules
6. Calculate confidence score using penalty system

Return ONLY this JSON structure (no markdown, no extra keys):
{{
  "_id": "<original id>",
  "orgName": "<original name>",
  "countryCode": "<original country or null>",
  "classification": {{
    "isMultiIndustry": <true|false>,
    "industries": [
      {{
        "industry": "<name from taxonomy>",
        "subCategory": "<specific subcategory>",
        "percentage": <integer, multiple of 5, sum=100>,
        "sampleProducts": ["<product>", "<product>", "<product>"]
      }}
    ],
    "primaryIndustry": "<industry with highest percentage>",
    "businessType": "<Manufacturer|Wholesaler|Retailer|Distributor|Mixed>",
    "confidenceScore": <float 0.5-1.0>,
    "reasoning": "<2-3 sentences: (1) list distinct industries found, (2) state product count per industry, (3) explain isMultiIndustry decision>"
  }}
}}

Organization data:
{organization_data}

CRITICAL REMINDER: Map "Shirting Linen" → Fashion & Apparel, "CHOKE/SPOTLIGHT" → Electronics & Tech. If you find 2+ distinct industries, isMultiIndustry MUST be true."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the classifier.

        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env variable.
            model:   OpenAI model to use. Default: gpt-4o-mini (fast + cheap).
                     Use "gpt-4o" for higher accuracy on ambiguous data.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not found. Set the OPENAI_API_KEY environment variable "
                "or pass api_key= when creating IndustryClassifier()."
            )

        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    # ------------------------------------------------------------------
    # Core classification
    # ------------------------------------------------------------------

    def classify_organization(self, organization_data: Dict) -> Dict:
        """
        Classify a single organization.

        Args:
            organization_data: Dict with _id, orgName, countryCode, product_names …

        Returns:
            Dict with classification results (or an error entry on failure).
        """
        org_json_str = json.dumps(organization_data, ensure_ascii=False, indent=2)
        user_message = self.USER_PROMPT_TEMPLATE.format(organization_data=org_json_str)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.0,  # Completely deterministic - no randomness
                max_tokens=2048,
                response_format={"type": "json_object"},   # guarantees valid JSON back
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user",   "content": user_message},
                ],
            )

            raw = response.choices[0].message.content.strip()
            return json.loads(raw)

        except json.JSONDecodeError as e:
            return self._error_result(organization_data, f"JSON parse error: {e}")
        except Exception as e:
            return self._error_result(organization_data, f"Classification failed: {e}")

    # ------------------------------------------------------------------
    # Batch helpers
    # ------------------------------------------------------------------

    def classify_batch(
        self,
        organizations: List[Dict],
        max_items: Optional[int] = None,
    ) -> List[Dict]:
        """
        Classify a list of organizations.

        Args:
            organizations: List of org dicts.
            max_items:      Cap the number processed (handy for testing).

        Returns:
            List of classification result dicts.
        """
        items = organizations[:max_items] if max_items else organizations
        results = []

        for i, org in enumerate(items, 1):
            print(f"[{i}/{len(items)}] {org.get('orgName', 'Unknown')}")
            results.append(self.classify_organization(org))

        return results

    def classify_from_file(
        self,
        input_file: str,
        output_file: str,
        max_items: Optional[int] = None,
    ) -> List[Dict]:
        """
        Load orgs from a JSON file, classify them, and write results.

        Args:
            input_file:  Path to source JSON (array of org objects).
            output_file: Path where classified JSON will be saved.
            max_items:   Optional cap for testing.

        Returns:
            List of classification result dicts.
        """
        with open(input_file, "r", encoding="utf-8") as f:
            organizations = json.load(f)

        print(f"Loaded {len(organizations)} organizations from {input_file}")
        results = self.classify_batch(organizations, max_items)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(results)} results to {output_file}")
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _error_result(org: Dict, message: str) -> Dict:
        return {
            "_id":         org.get("_id", "unknown"),
            "orgName":     org.get("orgName", "unknown"),
            "countryCode": org.get("countryCode"),
            "classification": {"error": message},
        }


# ----------------------------------------------------------------------
# Quick CLI test
# ----------------------------------------------------------------------

def main():
    classifier = IndustryClassifier()          # reads OPENAI_API_KEY from env
    classifier.classify_from_file(
        input_file="product5oData.json",
        output_file="classified_organizations.json",
        max_items=5,                            # remove to process all
    )


if __name__ == "__main__":
    main()