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

== STEP 1: PRODUCT-TO-INDUSTRY MAPPING ==
Map EVERY product to EXACTLY ONE industry:

Electronics & Tech: chokes, switches, plugs, sockets, wiring, circuit breakers, transformers, ballasts, LED bulbs, spotlights, tube lights, lamps, fixtures, phones, tablets, TVs, remotes, cables, adapters, chargers, phone holders, wireless mice, keyboards, USB devices

Fashion & Apparel: shirting fabric, linen, cotton, silk, polyester fabric, dress materials, shirts, pants, dresses, jackets, uniforms, shoes, sandals, boots, insoles, belts, ties, scarves, shapewear

Home Appliances: vacuum cleaners, air coolers, fans, humidifiers, heaters, dryers, washing machines, refrigerators

Home & Living: air fresheners, diffusers, organizers, storage, decor, detergents, sprays, wipes, drain cleaners, insect killers, fire extinguishers

Health & Medical: bandages, gauze, surgical items, first aid kits, BP monitors, thermometers, glucose meters, pain patches, compression supports, braces, tapes, medical devices

Fitness & Sports: weights, resistance bands, ab wheels, pushup stands, yoga mats, skipping ropes, hand grips, massage guns, gym gloves, sports accessories

Beauty & Personal Care: straighteners, curling irons, dryers, hair brushes, derma rollers, wax, facial tools, beard oil, nail clippers, bath brushes, skincare products, cosmetics

Food & Beverage: teas, spices, snacks, drinks, cooking ingredients, edible products

Tobacco & Vaping: vapes, e-cigarettes, lighters, smoking accessories, hip flasks

Stationery & Office: pens, paper, rulers, geometry sets, calculators, desk organizers, notebooks, agendas

Automotive: car parts, car accessories, car care products, tyres, batteries, oils

Manufacturing Supplies: inks, chemicals, adhesives, solvents, printing supplies, raw industrial materials, dyes

== STEP 2: COUNT DISTINCT INDUSTRIES ==
1. Count unique industries found
2. unique_industries >= 2 → isMultiIndustry = TRUE
3. unique_industries == 1 → isMultiIndustry = FALSE
NO EXCEPTIONS. This is a count, not a judgment call.

== STEP 3: PERCENTAGE CALCULATION ==
percentage = (products_in_industry / total_products) * 100
Round to nearest 5%. All must sum to 100. Exclude industries below 5%.

== STEP 4: OPERATION TYPE (6 CLASSES ONLY) ==
Pick EXACTLY ONE from this fixed list. No other values allowed.

1. "Seller"
   WHO: Any org selling products — whether retail shop, wholesale dealer, distributor, importer, e-commerce
   SIGNALS: Sells finished goods to buyers (B2C or B2B), diverse product catalogue, no service offerings
   EXAMPLES: retail store, wholesale dealer, online shop, trading company, depot, home depot, general store, export/import company

2. "Manufacturer"
   WHO: Org that produces/makes goods
   SIGNALS: Raw materials, production inputs, industrial equipment, factory supplies, bulk chemicals, inks, dyes
   EXAMPLES: factory, production company, industrial supplier, printing press, food processor

3. "Maintenance & Installation"
   WHO: Org that repairs, installs, or maintains equipment/property
   SIGNALS: Service-oriented, tools for repair, maintenance contracts, installation services
   EXAMPLES: electrician, plumber, HVAC company, IT support, equipment repair shop, contractor

4. "Professional Service"
   WHO: Licensed professionals or specialist knowledge-based services
   SIGNALS: Professional title in org name, certifications, specialized services
   EXAMPLES: doctor, dentist, lawyer, engineer, architect, accountant, consultant, clinic, law firm

5. "Food Service"
   WHO: Org in food preparation, cooking, or catering
   SIGNALS: Cooking equipment, food ingredients, restaurant supplies, catering services
   EXAMPLES: restaurant, hotel kitchen, catering company, bakery, food stall, cafe

6. "Supermarket"
   WHO: General merchandise store selling a wide mix of everyday consumer products under one roof
   SIGNALS: Org name contains MART, SUPERMARKET, HYPERMARKET, MINIMART, or sells a very broad mix (food + household + personal care + electronics together)
   EXAMPLES: Easy Mart, Quick Mart, SuperMart, FreshMart, any store with "MART" in the name

7. "Mixed"
   WHO: Org clearly operating in BOTH product sales AND services simultaneously
   SIGNALS: Evidence of both selling products AND providing services
   EXAMPLES: hardware shop that also does installation, clinic that also sells medical supplies

DECISION RULES (in order — stop at first match):
- Org name contains "MART", "SUPERMARKET", "HYPERMARKET", "MINIMART", "SUPERSTORE" → "Supermarket"
- Raw materials / production inputs → "Manufacturer"
- Org name has "DEPOT", "STORE", "SHOP", "TRADING", "SUPPLIERS", "WHOLESALER", "DISTRIBUTOR", "IMPORTER", "EXPORTER" → "Seller"
- Org name has "CLINIC", "HOSPITAL", "DR.", "DOCTOR", "DENTAL", "LAW", "CONSULT", "ENGINEER" → "Professional Service"
- Org name has "RESTAURANT", "HOTEL", "BAKERY", "CATERING", "CAFE", "KITCHEN" → "Food Service"
- Org name has "REPAIR", "MAINTENANCE", "INSTALLATION", "SERVICES", "CONTRACTORS" → "Maintenance & Installation"
- Products only, no service signals → "Seller"
- Cannot clearly decide → "Mixed"

== STEP 5: CONFIDENCE SCORE ==
Start at 1.0, subtract penalties:
- Missing descriptions for >50% products: -0.10
- Vague/codified product names (e.g. "ITEM-A", "SKU123"): -0.05 per vague product (max -0.20)
- Missing units when units would help: -0.05
- Ambiguous industry assignment: -0.10
Clamp final score to [0.50, 1.0].

== CONSISTENCY RULES ==
- "Shirting", "Linen", "Fabric", "Cloth" → ALWAYS Fashion & Apparel
- "CHOKE", "SPOTLIGHT", "LED", "Switch", "Plug" → ALWAYS Electronics & Tech
- "MART", "SUPERMARKET", "MINIMART" in org name → operationType = "Supermarket"
- "DEPOT", "HOME DEPOT", "TRADING" in org name → operationType = "Seller"
- If count >= 2 → isMultiIndustry = TRUE (no exceptions)"""

    USER_PROMPT_TEMPLATE = """Classify the organization below. Follow every step in the system prompt strictly.

MANDATORY STEPS:
1. Map each product to an industry
2. Count distinct industries → set isMultiIndustry
3. Calculate percentages
4. Determine operationType from the 6 fixed classes
5. Calculate confidence score

Return ONLY this exact JSON (no extra keys, no markdown):
{{
  "orgName": "<original name>",
  "classification": {{
    "isMultiIndustry": <true|false>,
    "industries": [
      {{
        "industry": "<industry name>",
        "subCategory": "<specific subcategory>",
        "percentage": <integer, multiple of 5, sum=100>,
        "sampleProducts": ["<product>", "<product>", "<product>"]
      }}
    ],
    "primaryIndustry": "<industry with highest percentage>",
    "operationType": "<Seller|Manufacturer|Maintenance & Installation|Professional Service|Food Service|Supermarket|Mixed>",
    "confidenceScore": <float 0.5-1.0>,
    "reasoning": "<2 sentences max: (1) list industries found with product counts, (2) explain operationType choice>"
  }}
}}

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
            "orgName": org.get("orgName", "unknown"),
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