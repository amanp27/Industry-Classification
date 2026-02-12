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
INDUSTRY TAXONOMY  (use EXACTLY these names)
════════════════════════════════════════
Each of the following is a DISTINCT top-level industry. Products belonging to different industries here ALWAYS make isMultiIndustry = true:

1.  Health & Medical        — bandages, pain relief, BP monitors, surgical items, first aid, knee/ankle/wrist supports, kinesiology tape, elastic bandages, pain patches, compression gear, medical devices
2.  Fitness & Sports        — gym gloves, resistance bands, ab wheels, skipping ropes, yoga mats, pushup stands, hand grips, massage guns, cooling towels, workout equipment, sports accessories
3.  Beauty & Personal Care  — derma rollers, beard oil, wax beans, hair straighteners, curling irons, facial hair removers, nail clippers, bath brushes, skin care, hair care tools
4.  Home Appliances         — vacuum cleaners, air coolers, fans, humidifiers, dryer blowers, home electrical appliances
5.  Home & Living           — air fresheners, essential oils, diffusers, insect sprays, lint removers, lint rollers, drain powders, memory foam, fire extinguishers, home accessories
6.  Electronics & Tech      — phone holders, tablet holders, wireless mice, TV remotes, data cables, LED lights, keychain lights, table lamp holders, consumer electronics accessories
7.  Food & Beverage         — teas, edible products, food items, beverages, cooking ingredients
8.  Tobacco & Vaping        — vapes, e-cigarettes, puff bars, vaping accessories, lighters, hip flasks, smoking accessories
9.  Stationery & Office     — maths sets, geometry sets, rulers, triangles, office supplies, desk organizers, cash boxes
10. Automotive              — car phone holders, car accessories, car care products
11. Fashion & Apparel       — clothing, shoes, corsets, shapewear wraps, insoles, textiles
12. Manufacturing Supplies  — industrial inks, chemicals, raw materials, printing supplies, varnishes
13. Wholesale/Distribution  — when ONLY bulk commodities with no clear end-use category
14. General Retail          — ONLY use this when a store's product mix is so diverse it defies categorisation into specific industries above

════════════════════════════════════════
isMultiIndustry RULES  — READ CAREFULLY
════════════════════════════════════════
Set isMultiIndustry = TRUE when products span 2 or more DISTINCT industries from the taxonomy above.

CRITICAL: Do NOT collapse different industries into one just because they are all "consumer goods" or all "retail products".
- Fitness equipment + Health/Medical products = MULTI-INDUSTRY (Fitness & Sports + Health & Medical)
- Home Appliances + Beauty tools = MULTI-INDUSTRY (Home Appliances + Beauty & Personal Care)
- Vapes + First Aid kits = MULTI-INDUSTRY (Tobacco & Vaping + Health & Medical)
- UV inks + flexo inks + varnish = SINGLE INDUSTRY (all Manufacturing Supplies)
- Resistance bands + gym gloves + yoga mat = SINGLE INDUSTRY (all Fitness & Sports)

Rule of thumb: if you find yourself needing 3+ industry names from the taxonomy to describe the products, isMultiIndustry is definitely true.

════════════════════════════════════════
PERCENTAGE CALCULATION
════════════════════════════════════════
Count the number of products belonging to each industry, divide by total products, round to nearest 5%.
All percentages must sum to exactly 100.
List industries from highest to lowest percentage.
Only include industries with at least 5% share.

════════════════════════════════════════
BUSINESS TYPE
════════════════════════════════════════
- Retailer: consumer-ready individual products (no bulk units), diverse product mix for end-users
- Wholesaler: bulk quantities (Kg, L, large unit counts), B2B focus
- Manufacturer: raw materials, production inputs, industrial quantities
- Distributor: branded goods in moderate quantities for resale
- Mixed: combination of the above

════════════════════════════════════════
CONFIDENCE SCORE
════════════════════════════════════════
This is a SINGLE score (0.0–1.0) reflecting your overall certainty about the ENTIRE classification output.
It does NOT measure how "single" or "multi" the industry is — it measures how confident you are in your analysis.

Ask yourself:
- Are the product names clear and descriptive? (high confidence)
- Is the industry mapping obvious? (high confidence)
- Are there ambiguous products that could belong to multiple industries? (lower confidence)
- Are descriptions missing or vague? (lower confidence)
- Is the business type determination uncertain? (lower confidence)

Scoring guide:
- 0.92–1.0:  Crystal clear products, zero ambiguity, every product maps perfectly to an industry
- 0.80–0.91: Mostly clear, a few products are generic (e.g. "Axe", "Triangles") but overall classification is solid
- 0.65–0.79: Meaningful ambiguity — several vague product names, or business type is hard to determine
- 0.50–0.64: High uncertainty — many products are unclear, or product mix defies standard industry categories
- below 0.50: Insufficient data or completely ambiguous product list

Example 1: "UV Cyan Ink, Offset Magenta, Flexo Varnish" → 0.98 confidence (printing supplies, very clear)
Example 2: "Pushup Stand, Vacuum Cleaner, Beard Oil, Vape, First Aid Kit" → 0.83 confidence (multi-industry is obvious, but some products like "Axe" are ambiguous without context)
Example 3: "Item A, Product B, Thing C" → 0.45 confidence (no idea what these are)"""

    USER_PROMPT_TEMPLATE = """Classify the organization below. Return ONLY a valid JSON object, no other text.

Required schema:
{{
  "_id": "<original id>",
  "orgName": "<original name>",
  "countryCode": "<original country or null>",
  "classification": {{
    "isMultiIndustry": <true|false>,
    "industries": [
      {{
        "industry": "<name from taxonomy>",
        "subCategory": "<specific subcategory e.g. Pain Relief Products>",
        "percentage": <integer, multiples of 5, sums to 100>,
        "sampleProducts": ["<product>", "<product>", "<product>"]
      }}
    ],
    "primaryIndustry": "<industry with highest percentage>",
    "businessType": "<Manufacturer|Wholesaler|Distributor|Retailer|Mixed>",
    "confidenceScore": <float 0.0-1.0, reflects certainty across ALL decisions>,
    "reasoning": "<2-3 sentences: list the distinct industry categories found, explain why isMultiIndustry is true/false, note business type signals>"
  }}
}}

Step-by-step instructions:
1. Read every product name carefully.
2. Map each product to an industry from the taxonomy.
3. If products map to 2+ distinct taxonomy industries → isMultiIndustry = true.
4. Count products per industry → calculate percentages.
5. Fill the schema. Do not invent extra keys.

Organization data:
{organization_data}"""

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
                temperature=0.2,
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