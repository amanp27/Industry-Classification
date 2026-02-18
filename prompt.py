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

Maintenance & Installation (as industry): laundry services (lavar, planchar, lavado), dry cleaning, repair services, cleaning services, installation work

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
   WHO: Org that ONLY sells products, no evidence of services or maintenance
   SIGNALS: Product catalogue only, no service language, no repair/installation signals
   EXAMPLES: retail store, wholesale dealer, online shop, trading company, depot, home depot, general store

2. "Seller and Services"
   WHO: Org that sells products AND also provides some form of professional/general services
   SIGNALS: Products for sale + service language, consulting, advice, or support mentioned
   EXAMPLES: electronics shop that also offers IT support, hardware store that also consults

3. "Manufacturer"
   WHO: Org that produces/makes goods
   SIGNALS: Raw materials, production inputs, industrial equipment, factory supplies, bulk chemicals, inks, dyes
   EXAMPLES: factory, production company, industrial supplier, printing press, food processor

4. "Maintenance & Installation"
   WHO: Org that repairs, installs, or maintains equipment/property
   SIGNALS: Service-oriented, tools for repair, maintenance contracts, installation services
   EXAMPLES: electrician, plumber, HVAC company, IT support, equipment repair shop, contractor

5. "Professional Service"
   WHO: Licensed professionals or specialist knowledge-based services
   SIGNALS: Professional title in org name, certifications, specialized services
   EXAMPLES: doctor, dentist, lawyer, engineer, architect, accountant, consultant, clinic, law firm

6. "Food Service"
   WHO: Org in food preparation, cooking, or catering
   SIGNALS: Cooking equipment, food ingredients, restaurant supplies, catering services
   EXAMPLES: restaurant, hotel kitchen, catering company, bakery, food stall, cafe

7. "Supermarket"
   WHO: General merchandise store selling a wide mix of everyday consumer products under one roof
   SIGNALS: Org name contains MART, SUPERMARKET, HYPERMARKET, MINIMART, or sells a very broad mix (food + household + personal care + electronics together)
   EXAMPLES: Easy Mart, Quick Mart, SuperMart, FreshMart, any store with "MART" in the name

8. "Seller, Service and Maintenance"
   WHO: Org that sells physical products AND provides services AND does repairs/maintenance/installation
   SIGNALS: Physical products for sale + professional services + maintenance/repair/installation work
   EXAMPLES: electrical shop that sells goods, consults, and installs; hardware company that sells, advises, and repairs
   NOTE: Do NOT use this for orgs that only provide services (laundry, hotel) without selling physical goods

9. "Service and Maintenance"
   WHO: Org that ONLY provides services and/or maintenance — no physical product sales
   SIGNALS: All "products" are actually services (laundry, ironing, room rental, cleaning, repair)
   EXAMPLES: laundry shop, dry cleaner, apartment hotel, cleaning company, repair-only workshop

10. "Mixed"
   WHO: Org whose operation type doesn't clearly fit any single class above
   SIGNALS: Genuinely ambiguous — cannot determine primary mode of operation from available data

DECISION RULES (in order — stop at first match):
- Org name contains "MART", "SUPERMARKET", "HYPERMARKET", "MINIMART", "SUPERSTORE" → "Supermarket"
- Raw materials / production inputs → "Manufacturer"
- Org name has "CLINIC", "HOSPITAL", "DR.", "DOCTOR", "DENTAL", "LAW", "CONSULT", "ENGINEER" → "Professional Service"
- Org name has "RESTAURANT", "HOTEL", "BAKERY", "CATERING", "CAFE", "KITCHEN" → "Food Service"
- Org name has "LAVANDERÍA", "LAUNDRY", "LAVANDERIA", "DRY CLEAN", "APARTA-HOTEL", "HOSTAL" → start with service base
- ALL products are services (laundry, ironing, room rental, cleaning) with NO physical goods for sale → "Service and Maintenance"
- Evidence of selling physical goods + services + maintenance/installation → "Seller, Service and Maintenance"
- Evidence of selling physical goods + services (no maintenance) → "Seller and Services"
- Org name has "DEPOT", "STORE", "SHOP", "TRADING", "SUPPLIERS", "WHOLESALER", "DISTRIBUTOR", "IMPORTER", "EXPORTER" → "Seller"
- Products only, no service signals → "Seller"
- Cannot clearly determine → "Mixed"

== STEP 5: CONFIDENCE SCORE ==
Start at 1.0, subtract penalties:
- Missing descriptions for >50% products: -0.10
- Vague/codified product names (e.g. "ITEM-A", "SKU123"): -0.05 per vague product (max -0.20)
- Missing units when units would help: -0.05
- Ambiguous industry assignment: -0.10
Clamp final score to [0.50, 1.0].

== CONSISTENCY RULES ==
- "Shirting", "Linen", "Fabric", "Cloth", "Sabana", "Corcha", "Funda", "Colchon", "Frisa", "Toalla", "Mantel", "Cortina" → ALWAYS Home & Living (hotel/laundry linens, NOT fashion)
- "Lavar", "Planchar", "Planchado", "Lavado", "Lavandería", "Washing", "Ironing", "Dry Clean" → ALWAYS Maintenance & Installation (laundry service)
- "Renta de Habitaciones", "Room Rental", "Alquiler" → ALWAYS Professional Service (accommodation)
- "CHOKE", "SPOTLIGHT", "LED", "Switch", "Plug" → ALWAYS Electronics & Tech
- "MART", "SUPERMARKET", "MINIMART" in org name → operationType = "Supermarket"
- "DEPOT", "STORE", "SHOP", "TRADING" in org name → operationType = "Seller"
- "APARTA-HOTEL", "HOSTAL", "HOSPEDAJE", "POSADA" in org name alone → operationType = "Professional Service"
- "LAVANDERÍA" + "HOTEL/APARTA-HOTEL" in org name together → operationType = "Service and Maintenance"
- "LAVANDERÍA", "LAUNDRY", "LAVANDERIA", "DRY CLEAN" in org name → includes laundry service
- If org name has HOTEL + LAVANDERÍA → operationType = "Seller, Service and Maintenance"
- If count >= 2 → isMultiIndustry = TRUE (no exceptions)

== MULTILINGUAL PRODUCT SIGNALS (Spanish/French/Arabic/Portuguese) ==
Laundry services (→ Maintenance & Installation): Lavar, Lavado, Planchar, Planchado, Planchando, Lavandería, Secado, Doblado, Hamper
Hotel/accommodation (→ Professional Service): Renta de Habitaciones, Alquiler, Habitacion, Hostal
Linens/bedding (→ Home & Living): Sabana, Corcha, Funda, Colchon, Frisa, Toalla, Mantel, Servilleta, Cortina, Almohada
Clothing items being serviced (→ Maintenance & Installation, NOT Fashion): Vestido Lavar, Poloche Lavar, Pantalon Lavar — these are laundry items, not clothing for sale"""

    USER_PROMPT_TEMPLATE = """Classify the organization below. Follow every step in the system prompt strictly.

MANDATORY STEPS:
1. Map each product to an industry
2. Count distinct industries → set isMultiIndustry
3. Calculate percentages
4. Determine operationType from the fixed classes
5. Calculate confidence score

Return ONLY this exact JSON (no extra keys, no markdown):
{{
  "orgName": "<original name>",
  "productCount": null,
  "primaryIndustry": "<industry with highest percentage>",
  "operationType": "<Seller|Seller and Services|Seller, Service and Maintenance|Service and Maintenance|Manufacturer|Maintenance & Installation|Professional Service|Food Service|Supermarket|Mixed>",
  "confidenceScore": <float 0.5-1.0>,
  "AIreasoning": "<2 sentences max: (1) list industries found (DO NOT state any product counts or numbers — only industry names and percentages), (2) explain operationType choice based on org name and product signals>",
  "classification": {{
    "isMultiIndustry": <true|false>,
    "industries": [
      {{
        "industry": "<industry name>",
        "subCategory": "<specific subcategory>",
        "percentage": <integer, multiple of 5, sum=100>,
        "sampleProducts": ["<product>", "<product>", "<product>"]
      }}
    ]
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
        # Count products in Python — never trust LLM to count accurately
        actual_product_count = len(organization_data.get("product_names", []))

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
            result = json.loads(raw)

            # ── Always overwrite productCount with true Python-computed value ──
            result["productCount"] = actual_product_count

            # ── Rebuild AIreasoning with accurate numbers (LLM often hallucinates counts) ──
            industries = result.get("classification", {}).get("industries", [])
            total = actual_product_count
            industry_parts = []
            for ind in industries:
                pct = ind.get("percentage", 0)
                real_count = round((pct / 100) * total)
                industry_parts.append(
                    f"{ind.get('industry', '?')} ({pct}% ≈ {real_count} products)"
                )
            op_type = result.get("operationType", "—")
            industries_str = ", ".join(industry_parts) if industry_parts else "—"
            result["AIreasoning"] = (
                f"Industries found: {industries_str}. "
                f"Total products: {total}. "
                f"Operation type '{op_type}' determined from org name signals and product nature."
            )

            return result

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
            "orgName":        org.get("orgName", "unknown"),
            "productCount":   len(org.get("product_names", [])),
            "primaryIndustry": None,
            "operationType":  None,
            "confidenceScore": None,
            "AIreasoning":    None,
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