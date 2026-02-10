# Industry Classification - Prompt & Gemini Integration Details

## 1. THE PROMPT TEMPLATE (Multi-Industry Support)

```text
You are an industry classification expert. Analyze the organization data below and classify it into appropriate industries.

Organization Name: {orgName}
Country: {countryCode}

Products/Services offered (typeOfCommodity: 0=undefined, 1=product, 2=service):
{productsList}

Based on the product names, descriptions, units, and commodity types, classify this organization.

IMPORTANT: 
- If products/services span MULTIPLE industries, list ALL relevant industries with their percentage share.
- The percentages should sum to 100.
- Consider the diversity of products when classifying.

Respond ONLY with a valid JSON object in this exact format (no markdown, no code blocks):
{
    "isMultiIndustry": true,
    "industries": [
        {
            "industry": "Main industry category",
            "subCategory": "Specific sub-category",
            "percentage": 60,
            "sampleProducts": ["Product A", "Product B"]
        },
        {
            "industry": "Second industry if applicable",
            "subCategory": "Specific sub-category",
            "percentage": 40,
            "sampleProducts": ["Product C", "Product D"]
        }
    ],
    "primaryIndustry": "The dominant industry (highest percentage)",
    "businessType": "Manufacturer | Wholesaler | Retailer | Service Provider | Distributor | Hybrid",
    "confidenceScore": 0.85,
    "reasoning": "Brief explanation of the classification and why multiple industries if applicable"
}
```

---

## 2. MULTI-INDUSTRY EXAMPLES

### Example A: Single Industry Organization
```json
{
    "isMultiIndustry": false,
    "industries": [
        {
            "industry": "Manufacturing",
            "subCategory": "Printing & Packaging Supplies",
            "percentage": 100,
            "sampleProducts": ["Supra UV cyan", "Xtrime magenta", "Tir will UV varnish"]
        }
    ],
    "primaryIndustry": "Manufacturing",
    "businessType": "Wholesaler",
    "confidenceScore": 0.95,
    "reasoning": "All products are UV inks, varnishes, and printing supplies for the printing industry."
}
```

### Example B: Multi-Industry Organization
```json
{
    "isMultiIndustry": true,
    "industries": [
        {
            "industry": "Electronics",
            "subCategory": "Consumer Electronics Retail",
            "percentage": 45,
            "sampleProducts": ["iPhone 15", "Samsung TV", "Laptop"]
        },
        {
            "industry": "Healthcare",
            "subCategory": "Medical Supplies",
            "percentage": 30,
            "sampleProducts": ["Blood Pressure Monitor", "Surgical Masks", "First Aid Kit"]
        },
        {
            "industry": "Food & Beverage",
            "subCategory": "Grocery Retail",
            "percentage": 25,
            "sampleProducts": ["Rice", "Cooking Oil", "Canned Foods"]
        }
    ],
    "primaryIndustry": "Electronics",
    "businessType": "Retailer",
    "confidenceScore": 0.88,
    "reasoning": "This appears to be a general store/supermarket with diverse product categories. Electronics has the highest share followed by medical supplies and groceries."
}
```

### Example C: Product + Service Hybrid
```json
{
    "isMultiIndustry": true,
    "industries": [
        {
            "industry": "Technology",
            "subCategory": "Software Products",
            "percentage": 60,
            "sampleProducts": ["CRM License", "ERP Module", "Mobile App"]
        },
        {
            "industry": "Professional Services",
            "subCategory": "IT Consulting",
            "percentage": 40,
            "sampleProducts": ["Implementation Service", "Training", "Support Contract"]
        }
    ],
    "primaryIndustry": "Technology",
    "businessType": "Hybrid",
    "confidenceScore": 0.92,
    "reasoning": "Organization sells software products (typeOfCommodity=1) and provides related services (typeOfCommodity=2)."
}
```

---

## 3. BUSINESS TYPE CLASSIFICATION

| Business Type      | Description                                        | Indicators                                    |
|--------------------|----------------------------------------------------|--------------------------------------------- |
| Manufacturer       | Produces goods from raw materials                  | Units: Kg, L, meters; industrial products     |
| Wholesaler         | Sells in bulk to other businesses                  | Large quantities, B2B products                |
| Retailer           | Sells directly to consumers                        | Mixed products, consumer goods                |
| Service Provider   | Offers services (typeOfCommodity=2)                | Consulting, repairs, maintenance              |
| Distributor        | Distributes products from manufacturers            | Branded products, import/export               |
| Hybrid             | Combination of products + services                 | Both type 1 and type 2 commodities            |

---

## 4. PRODUCT DATA FORMAT

Each product is formatted as:
```
- {productName} | Unit: {unit} | Type: {typeOfCommodity} | Desc: {description}
```

### TypeOfCommodity Values:
| Value | Meaning     | Example                          |
|-------|-------------|----------------------------------|
| 0     | Not defined | Legacy data, unknown type        |
| 1     | Product     | Physical goods, inventory items  |
| 2     | Service     | Consulting, maintenance, support |

---

## 5. EXAMPLE - ACTUAL PROMPT SENT TO GEMINI

For the first organization in your data:

```text
You are an industry classification expert. Analyze the organization data below and classify it into an appropriate industry.

Organization Name: الفريده للإستيراد
Country: EG

Products/Services offered (typeOfCommodity: 0=undefined, 1=product, 2=service):
- Supra Uv opeque white | Unit: K.g | Type: 0 | Desc: ابيض زنك عادي ليتربرس
- Supra Uv red032 | Unit: K.g | Type: 0 | Desc: احمر ٠٢٣ ليتربس
- Supra Uv purpur | Unit: K.g | Type: 0 | Desc: بربل ليتربس
- Supra Uv vilot | Unit: Kg | Type: 0 | Desc: فيلوت ليتربرس
- Supra Uv reflex blue | Unit: K.g | Type: 0 | Desc: ازرق ريفلكس ليتربرس
- Supra Uv orange | Unit: K.g | Type: 0 | Desc: برتقالي ليتربرس
- Xtrime magenta | Unit: K.g | Type: 0 | Desc: اوفسيت احمر
- Xtrime cyan | Unit: K.g | Type: 0 | Desc: اوفسيت ازرق
- Tir will Uv تقيل | Unit: L | Type: 0 | Desc: ورنيش تقيل
- بلانكت | Unit: متر | Type: 0 | Desc: N/A
... and 47 more products

Based on the product names, descriptions, units, and commodity types, classify this organization.

Respond ONLY with a valid JSON object in this exact format (no markdown, no code blocks):
{
    "primaryIndustry": "Main industry category (e.g., Manufacturing, Retail, Healthcare, Technology, Food & Beverage, etc.)",
    "subCategory": "Specific sub-category (e.g., Printing & Packaging, Electronics Retail, Cosmetics & Skincare)",
    "confidenceScore": 0.85,
    "reasoning": "Brief explanation of why this classification was chosen",
    "relatedIndustries": ["Other possible industry 1", "Other possible industry 2"]
}
```

---

## 6. GEMINI API REQUEST STRUCTURE

### Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}
```

### Request Body (JSON)
```json
{
    "contents": [
        {
            "parts": [
                {
                    "text": "Your prompt text here..."
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 1024
    }
}
```

### Generation Config Explained:
| Parameter       | Value | Why                                              |
|-----------------|-------|--------------------------------------------------|
| temperature     | 0.3   | Low = more consistent, deterministic responses   |
| maxOutputTokens | 1024  | Enough for JSON response, prevents runaway output|

---

## 7. GEMINI API RESPONSE STRUCTURE

### Raw Response from Gemini:
```json
{
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": "{\n    \"primaryIndustry\": \"Manufacturing\",\n    \"subCategory\": \"Printing & Packaging Supplies\",\n    \"confidenceScore\": 0.92,\n    \"reasoning\": \"The organization deals primarily in UV inks, varnishes, and printing supplies including offset inks (CMYK colors), flexographic inks, and UV coatings. Product names like Supra UV, Xtrime, and Tir will indicate professional printing industry supplies.\",\n    \"relatedIndustries\": [\"Chemical Manufacturing\", \"Industrial Supplies\", \"Wholesale Trade\"]\n}"
                    }
                ],
                "role": "model"
            },
            "finishReason": "STOP"
        }
    ],
    "usageMetadata": {
        "promptTokenCount": 450,
        "candidatesTokenCount": 120,
        "totalTokenCount": 570
    }
}
```

### Extracted & Parsed Response:
```json
{
    "primaryIndustry": "Manufacturing",
    "subCategory": "Printing & Packaging Supplies",
    "confidenceScore": 0.92,
    "reasoning": "The organization deals primarily in UV inks, varnishes, and printing supplies including offset inks (CMYK colors), flexographic inks, and UV coatings.",
    "relatedIndustries": ["Chemical Manufacturing", "Industrial Supplies", "Wholesale Trade"]
}
```

---

## 8. FINAL OUTPUT FORMAT

The classified organization returned by the API:

### Single Industry Example:
```json
{
    "_id": "93649",
    "orgName": "الفريده للإستيراد",
    "businessId": "",
    "countryCode": "EG",
    "product_names": [
        {
            "productName": "Supra Uv opeque white",
            "categoryName": "",
            "unit": "K.g",
            "productCode": "",
            "typeOfCommodity": 0,
            "discription": "ابيض زنك عادي ليتربرس"
        }
    ],
    "classification": {
        "isMultiIndustry": false,
        "industries": [
            {
                "industry": "Manufacturing",
                "subCategory": "Printing & Packaging Supplies",
                "percentage": 100,
                "sampleProducts": ["Supra UV cyan", "Xtrime magenta", "Tir will UV varnish"]
            }
        ],
        "primaryIndustry": "Manufacturing",
        "businessType": "Wholesaler",
        "confidenceScore": 0.92,
        "reasoning": "Organization deals in UV inks, varnishes, and printing supplies..."
    }
}
```

### Multi-Industry Example:
```json
{
    "_id": "12345",
    "orgName": "General Trading Co",
    "countryCode": "AE",
    "product_names": [...],
    "classification": {
        "isMultiIndustry": true,
        "industries": [
            {
                "industry": "Electronics",
                "subCategory": "Consumer Electronics",
                "percentage": 50,
                "sampleProducts": ["TV", "Mobile Phone", "Laptop"]
            },
            {
                "industry": "Home & Garden",
                "subCategory": "Home Appliances",
                "percentage": 30,
                "sampleProducts": ["Washing Machine", "Refrigerator"]
            },
            {
                "industry": "Food & Beverage",
                "subCategory": "Grocery",
                "percentage": 20,
                "sampleProducts": ["Rice", "Sugar", "Oil"]
            }
        ],
        "primaryIndustry": "Electronics",
        "businessType": "Retailer",
        "confidenceScore": 0.85,
        "reasoning": "Diversified trading company with products across multiple categories..."
    }
}
```

---

## 9. INDUSTRY CATEGORIES (EXPECTED VALUES)

The LLM may return these primary industries:

| Primary Industry          | Example Sub-Categories                                    |
|---------------------------|-----------------------------------------------------------|
| Manufacturing             | Printing & Packaging, Chemical, Textile, Electronics      |
| Retail                    | Electronics Retail, Fashion Retail, Grocery               |
| Wholesale Trade           | Industrial Supplies, Food Distribution, Building Materials|
| Healthcare                | Medical Supplies, Pharmaceuticals, Cosmetics & Skincare   |
| Technology                | Software, IT Services, Telecommunications                 |
| Food & Beverage           | Beverages, Food Processing, Restaurants                   |
| Construction              | Building Materials, Hardware, Civil Engineering           |
| Agriculture               | Farming, Livestock, Agricultural Supplies                 |
| Transportation & Logistics| Freight, Warehousing, Courier Services                    |
| Professional Services     | Consulting, Legal, Accounting                             |

---

## 10. PROMPT CUSTOMIZATION OPTIONS

### Option A: Add Industry List Constraint
If you want to limit to specific industries:

```text
Classify into ONE of these industries only:
- Manufacturing
- Retail  
- Wholesale Trade
- Healthcare
- Technology
- Food & Beverage
- Construction
- Agriculture
- Transportation & Logistics
- Professional Services
- Other
```

### Option B: Add More Context Fields
```text
Organization Name: {orgName}
Country: {countryCode}
Business ID: {businessId}
Total Products: {productCount}
Products (Type 1): {productTypeCount}
Services (Type 2): {serviceTypeCount}
```

### Option C: Structured Output (Gemini 1.5+)
Use JSON schema for guaranteed format:

```json
{
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "object",
            "properties": {
                "primaryIndustry": {"type": "string"},
                "subCategory": {"type": "string"},
                "confidenceScore": {"type": "number"},
                "reasoning": {"type": "string"},
                "relatedIndustries": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["primaryIndustry", "subCategory", "confidenceScore"]
        }
    }
}
```

---

## 11. TOKEN MANAGEMENT

### Current Limits:
- **Products per request**: 50 (to stay under token limits)
- **Estimated tokens per org**: ~500-800 tokens
- **Gemini Flash limit**: 1M tokens context window

### To Process More Products:
1. Increase limit in `buildProductsSummary()` method
2. Or summarize products by category first
3. Or use product sampling (random 50)

---

## 12. ERROR HANDLING

### Common Errors & Solutions:

| Error                    | Cause                          | Solution                         |
|--------------------------|--------------------------------|----------------------------------|
| 400 Bad Request          | Invalid JSON in request        | Check request body format        |
| 401 Unauthorized         | Invalid/missing API key        | Verify GEMINI_API_KEY            |
| 429 Too Many Requests    | Rate limit exceeded            | Increase delayMs parameter       |
| 500 Internal Error       | Gemini service issue           | Retry with exponential backoff   |
| JSON Parse Error         | LLM returned markdown/text     | Response cleaning handles this   |

---

## 13. TESTING THE PROMPT

### Quick Test with cURL:

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "You are an industry classification expert. Analyze the organization data below and classify it into an appropriate industry.\n\nOrganization Name: Test Electronics Shop\nCountry: US\n\nProducts/Services offered (typeOfCommodity: 0=undefined, 1=product, 2=service):\n- iPhone 15 Pro | Unit: piece | Type: 1 | Desc: Apple smartphone\n- Samsung TV 55inch | Unit: piece | Type: 1 | Desc: Smart TV\n- Laptop Repair | Unit: service | Type: 2 | Desc: Computer repair service\n\nRespond ONLY with a valid JSON object in this exact format (no markdown, no code blocks):\n{\"primaryIndustry\": \"...\", \"subCategory\": \"...\", \"confidenceScore\": 0.0, \"reasoning\": \"...\", \"relatedIndustries\": []}"
      }]
    }],
    "generationConfig": {
      "temperature": 0.3,
      "maxOutputTokens": 1024
    }
  }'
```

---

## 14. COST ESTIMATION

### Gemini 1.5 Flash Pricing (as of 2024):
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

### For Your Data (50 organizations):
- ~500 tokens input per org × 50 = 25,000 input tokens
- ~150 tokens output per org × 50 = 7,500 output tokens
- **Estimated cost: < $0.01**

---

## Summary

The prompt works by:
1. Providing organization context (name, country)
2. Listing products with type indicators (product/service)
3. Asking for structured JSON classification
4. Using low temperature for consistent results

The response includes industry classification with confidence scores and reasoning for transparency.
