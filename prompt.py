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

Electronics & Tech: chokes, switches, plugs, sockets, wiring, circuit breakers, transformers, ballasts, LED bulbs, spotlights, tube lights, lamps, fixtures, phones, tablets, TVs, remotes, cables, adapters, chargers, phone holders, wireless mice, keyboards, USB devices, batteries (AA, AAA, C, D cell, 9V), zero watt bulbs, energy saving bulbs, CFL, tape (electrical/insulation: black tape, white tape, red tape, osaka tape), scotch tape, power banks

Fashion & Apparel: shirting fabric, linen, cotton, silk, polyester fabric, dress materials, shirts, pants, dresses, jackets, uniforms, shoes, sandals, boots, insoles, belts, ties, scarves, shapewear

Home Appliances: vacuum cleaners, air coolers, fans, humidifiers, heaters, dryers, washing machines, refrigerators

Home & Living: air fresheners, diffusers, organizers, storage, decor, detergents, sprays, wipes, drain cleaners, insect killers, fire extinguishers, disposable cups/glasses/plates, tissue paper, napkins

Health & Medical: bandages, gauze, surgical items, first aid kits, BP monitors, thermometers, glucose meters, pain patches, compression supports, braces, tapes (medical), medical devices, sani plast, band-aid, plasters, ispaghol (psyllium husk), johar joshanda, herbal health sachets, digestive powders, rose patel (ayurvedic), khama cream, irani cream, herbal remedies, OTC medicines, supplements, cotton swabs, wipes (medical/hygiene context)

Fitness & Sports: weights, resistance bands, ab wheels, pushup stands, yoga mats, skipping ropes, hand grips, massage guns, gym gloves, sports accessories

Beauty & Personal Care: straighteners, curling irons, hair dryers, hair brushes, derma rollers, wax, facial tools, beard oil, nail clippers, bath brushes, skincare products, cosmetics, razors (trim razor, hygiene razor, universal razor, 7 o'clock blade, treat blade, platinum blade, shaving blades), shaving cream, wipes (personal care), rocket wipes, hair wax, pomade, grooming products

Food & Beverage: teas (isb tea, green tea, black tea sachets), spices, snacks, drinks, cooking ingredients, edible products, candies (kish candy, local candy, caramel toffee, gold coin, choco beans, cc stick, imli teeka, lolypop, bigtop lolypop, doremon lolypop, lolypop 5), chocolates (ramtin chocolate, nani chocolate, dream caramel chocolate, spark), gum (trigum, tridegum, cat bubble, panda), juices (smiley juice), bubble gum jar, lawa shak, till patti

Tobacco & Vaping: vapes, e-cigarettes, lighters (simple lighter, gerari lighter, heater lighter, pine light, any brand lighter), smoking accessories, hip flasks, matchboxes, disposable lighters

Tobacco & Pan Products: supari (raseeli supari, bombay sapari), paan masala, gutka, khaini, chewing tobacco, mouth freshener pouches, elaichi (cardamom pouches sold as mouth freshener), tulsi (paan/mouth freshener brand), shahi meewa, sultan (pan masala brand), ratan, delhi/dehli (pan masala), host (pan masala), josh black, knight rider, sathi, mond blue, mond red, milano, olivia (mouth freshener/supari brand), touch blue, touch green, gemsa elfi, platinum blue, qm55, ramtin irani, clay (chewing product), paan products — NOTE: Tulsi, Shahi Meewa, Sultan, Ratan, Delhi, Host, Josh Black, Knight Rider, Sathi, Mond, Milano, Olivia, Touch are South Asian pan masala / supari brands, NOT food

Stationery & Office: pens, paper, rulers, geometry sets, calculators, desk organizers, notebooks, agendas

Automotive: car parts, car accessories, car care products, tyres, batteries, oils

Manufacturing Supplies: inks, chemicals, adhesives, solvents, printing supplies, raw industrial materials, dyes

General Trade & Wholesale: mixed small goods traders who sell a broad combination of unrelated everyday consumer items — including pan masala, lighters, blades/razors, candies, batteries, bulbs, tapes, health sachets, and other fast-moving consumer goods (FMCG) in one portfolio. Use this when an org sells 4 or more distinct industry categories together with no clear dominant industry above 60%.

== STEP 2: COUNT DISTINCT INDUSTRIES ==
1. Count unique industries found
2. unique_industries >= 2 → isMultiIndustry = TRUE
3. unique_industries == 1 → isMultiIndustry = FALSE
NO EXCEPTIONS. This is a count, not a judgment call.

== STEP 3: PERCENTAGE CALCULATION ==
percentage = (products_in_industry / total_products) * 100
Round to nearest 5%. All must sum to 100. Exclude industries below 5%.

IMPORTANT for South Asian wholesale traders: Be very careful to correctly split:
- Pan masala/supari brands (Tulsi, Olivia, Mond, Milano, Touch, Sultan, Knight Rider, Josh, Sathi etc.) → Tobacco & Pan Products
- Lighters → Tobacco & Vaping
- Blades/Razors → Beauty & Personal Care
- Batteries/Bulbs/Electrical tape → Electronics & Tech
- Candies/Chocolates/Gum/Juices → Food & Beverage
- Herbal medicine sachets (Ispaghol, Johar Joshanda) → Health & Medical

== STEP 4: OPERATION TYPE (9 CLASSES ONLY) ==
Pick EXACTLY ONE from this fixed list. No other values allowed.

1. "Seller"
   WHO: Org that ONLY sells products, no evidence of services or maintenance
   SIGNALS: Product catalogue only, no service language, no repair/installation signals
   EXAMPLES: retail store, wholesale dealer, online shop, trading company, depot, home depot, general store

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

7. "Seller, Service and Maintenance"
   WHO: Org that sells physical products AND also provides services OR maintenance/installation
   SIGNALS: Physical products for sale + any combination of: consulting, advice, support, repair, installation, maintenance
   EXAMPLES: electronics shop that sells + provides IT support, hardware store that sells + installs, auto parts dealer + repair shop
   NOTE: Do NOT use this for orgs that only provide services without selling physical goods

8. "Service"
   WHO: Org that ONLY provides services — no physical product sales
   SIGNALS: All revenue from services: accommodation (hotels, villas), laundry/dry cleaning, consulting, catering, event services
   EXAMPLES: hotel, villa, laundry service, dry cleaner, event planner, catering service, consulting firm
   NOTE: Includes Hotels & Villa (accommodation) and Laundry & Services (dry cleaning) as primary industries

9. "Mixed"
   WHO: Org whose operation type doesn't clearly fit any single class above
   SIGNALS: Genuinely ambiguous — cannot determine primary mode of operation from available data

DECISION RULES (in order — stop at first match):
- Org name contains "MART", "SUPERMARKET", "HYPERMARKET", "MINIMART", "SUPERSTORE" → "Supermarket"
- Org name contains "LAUNDRY", "LAUNDROMAT", "DRY CLEAN", "LAVANDERÍA", "LAVANDERIA", "DRYCLEANING" → "Service" (primary industry: Laundry & Services)
- Org name contains "HOTEL", "VILLA", "MOTEL", "INN", "RESORT", "LODGE", "HOSTAL", "HOSPEDAJE" → "Service" (primary industry: Hotels & Villa)
- Org name has "APARTA-HOTEL" + "LAVANDERÍA" together → "Service" (primary industry: Laundry & Services)
- Raw materials / production inputs → "Manufacturer"
- Org name has "CLINIC", "HOSPITAL", "DR.", "DOCTOR", "DENTAL", "LAW", "CONSULT", "ENGINEER" → "Professional Service"
- Org name has "RESTAURANT", "BAKERY", "CATERING", "CAFE", "KITCHEN" → "Food Service"
- ALL products are pure services (accommodation, laundry, consulting, events) with NO physical goods → "Service"
- Evidence of selling physical goods + (services OR maintenance OR both) → "Seller, Service and Maintenance"
- Org name has "DEPOT", "STORE", "SHOP", "TRADING", "SUPPLIERS", "WHOLESALER", "DISTRIBUTOR", "IMPORTER", "EXPORTER", "TRADERS", "TRADER", "ENTERPRISE", "GENERAL STORE" → "Seller"
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
- "Lavar", "Planchar", "Planchado", "Lavado", "Lavandería", "Washing", "Ironing", "Dry Clean" → ALWAYS Laundry & Services (laundry service products)
- "Renta de Habitaciones", "Room Rental", "Alquiler", "Accommodation", "Accomodation" → ALWAYS Hotels & Villa (accommodation products)
- "CHOKE", "SPOTLIGHT", "LED", "Switch", "Plug", "Bulb", "Battery", "AAA", "AA", "Zero watt" → ALWAYS Electronics & Tech
- "Electrical tape", "Insulation tape", "Black tape", "White tape", "Red tape", "Osaka tape" → ALWAYS Electronics & Tech (NOT Stationery)
- "Scotch tape", "Cello tape" used in general stationery context → Stationery & Office
- "Supari", "Pan masala", "Tulsi", "Shahi Meewa", "Sultan", "Ratan", "Delhi", "Dehli", "Host", "Josh Black", "Knight Rider", "Sathi", "Mond", "Milano", "Olivia", "Touch Blue", "Touch Green", "Bombay Sapari", "Raseeli Supari", "Elaichi (pouch)" → ALWAYS Tobacco & Pan Products
- "Lighter", "Gerari lighter", "Simple lighter", "Heater lighter", "Pine light" → ALWAYS Tobacco & Vaping
- "Razor", "Blade", "Rezor", "Shaving" (Trim, Universal, Hygiene, 7 O'Clock, Treat, Platinum, Kangi) → ALWAYS Beauty & Personal Care
- "Ispaghol", "Johar Joshanda", "Sani plast", "Saniplast", "Rose patel", "Khama cream", "Irani cream" → ALWAYS Health & Medical
- "Candy", "Chocolate", "Gum", "Lolypop", "Lollipop", "Toffee", "Juice", "Snack", "Tea sachet", "Shak", "Till patti" → ALWAYS Food & Beverage
- "Wipes" in grooming/personal hygiene context (Rocket wipes) → Beauty & Personal Care
- "Wipes" in household cleaning context → Home & Living
- "MART", "SUPERMARKET", "MINIMART" in org name → operationType = "Supermarket"
- "DEPOT", "STORE", "SHOP", "TRADING", "TRADERS", "TRADER", "ENTERPRISE" in org name → operationType = "Seller"
- "LAUNDRY", "LAVANDERÍA", "LAUNDROMAT", "DRY CLEAN" in org name → operationType = "Service", primaryIndustry = "Laundry & Services"
- "HOTEL", "VILLA", "MOTEL", "RESORT" in org name → operationType = "Service", primaryIndustry = "Hotels & Villa"
- If count >= 2 → isMultiIndustry = TRUE (no exceptions)
- If 4+ distinct industries found → consider primaryIndustry = "General Trade & Wholesale" and list all industries in breakdown

== SOUTH ASIAN WHOLESALE TRADER RECOGNITION ==
When an org name contains "TRADERS", "ENTERPRISE", "GENERAL STORE", "STORE", "SHOP" AND the product list contains a mix of:
pan masala brands + lighters + blades/razors + candies/sweets + batteries/bulbs + health sachets
→ This is a GENERAL TRADE / WHOLESALE organization
→ primaryIndustry = whichever single industry has the highest % OR "General Trade & Wholesale" if no industry exceeds 35%
→ operationType = "Seller"
→ isMultiIndustry = TRUE (guaranteed, as these always span multiple industries)
→ List ALL individual industries in the breakdown with accurate percentages

KNOWN SOUTH ASIAN BRAND CLASSIFICATION REFERENCE:
Pan Masala / Mouth Freshener / Supari brands → Tobacco & Pan Products:
Tulsi, Shahi Meewa, Sultan, Ratan, Delhi/Dehli, Host, Josh Black, Knight Rider, Sathi, Mond Blue, Mond Red, Touch Blue, Touch Green, Milano, Olivia (all variants: 1-12), Gemsa Elfi, Platinum Blue, Qm55, Bombay Sapari, Raseeli Supari, Elaichi (pouch form), Clay, Pine Light (paan brand), Ramtin Irani, Panda, Cat Bubble

Lighter brands → Tobacco & Vaping:
Simple Lighter, Gerari Lighter, Heater Lighter, Pine Light (lighter variant)

Blade/Razor brands → Beauty & Personal Care:
Trim Razor/Rezor, Universal Razor, Hygiene Razor/Rezor, 7 O'Clock Blade, Treat Blade, Platinum Blade, Universal Razor Kangi

Candy/Confectionery brands → Food & Beverage:
Kish Candy, Local Candy, Caramel Toffee, Gold Coin, Choco Beans, CC Stick, Imli Teeka, Trigum Bubble Jar, Tridegum, Lolypop 5, Bigtop Lolypop, Doremon Lolypop, Ramtin Chocolate, Nani Chocolate, Dream Caramel Chocolate, Spark, Smiley Juice, Lawa Shak, Till Patti

Health/Herbal brands → Health & Medical:
Johar Joshanda, Ispaghol (Sashy/Box), Sani Plast, Rose Patel, Khama Irani Cream, Rocket Wipes (medical wipes)

Electronics brands → Electronics & Tech:
Power Plus AA/AAA/D, 777D (battery), Bulb Osaka B22/E27, Bulb Tuff B22/E27, Zero Watt 2 Pin, White Tape Osaka, Osaka Red Tape, Osaka Black Tape, Scotch Tape

== MULTILINGUAL PRODUCT SIGNALS (Spanish/French/Arabic/Portuguese) ==
Laundry services (→ Laundry & Services): Lavar, Lavado, Planchar, Planchado, Planchando, Lavandería, Secado, Doblado, Hamper, Dry Clean, Press, Fold, Wash
Hotel/accommodation (→ Hotels & Villa): Renta de Habitaciones, Alquiler, Habitacion, Hostal, Accommodation, Accomodation, Room Rental, Lodging
Linens/bedding (→ Home & Living): Sabana, Corcha, Funda, Colchon, Frisa, Toalla, Mantel, Servilleta, Cortina, Almohada
Clothing items being serviced (→ Laundry & Services, NOT Fashion): Vestido Lavar, Poloche Lavar, Pantalon Lavar, Native, Gown, Uniform with "wash/press/fold" context — these are laundry items, not clothing for sale"""

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
  "operationType": "<Seller|Seller, Service and Maintenance|Service|Manufacturer|Maintenance & Installation|Professional Service|Food Service|Supermarket|Mixed>",
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