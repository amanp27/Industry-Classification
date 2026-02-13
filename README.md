# Industry Classification System

AI-powered classification system that analyzes product portfolios and categorizes organizations into industry segments.

## Overview

This tool uses OpenAI's GPT models to automatically classify organizations based on their product listings. It identifies primary and secondary industries, determines business type (Manufacturer, Wholesaler, Retailer), and detects multi-industry operations.

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Alternatively, you can enter it manually in the application interface.

## Usage

### Web Interface

Launch the Streamlit application:

```bash
streamlit run app.py
```

The application provides three main features:

1. **Single Classification** - Classify individual organizations by pasting JSON data
2. **Batch Processing** - Upload and process multiple organizations from a JSON file
3. **Results Analysis** - View statistics and visualizations of classification results

### Python API

```python
from prompt import IndustryClassifier

# Initialize classifier
classifier = IndustryClassifier(api_key="your-api-key")

# Classify single organization
result = classifier.classify_organization(organization_data)

# Batch process from file
classifier.classify_from_file(
    input_file='input.json',
    output_file='output.json'
)
```

## Input Format

```json
{
  "_id": "unique-identifier",
  "orgName": "Organization Name",
  "countryCode": "US",
  "product_names": [
    {
      "productName": "Product Name",
      "unit": "unit of measurement",
      "discription": "optional description"
    }
  ]
}
```

## Output Format

```json
{
  "_id": "unique-identifier",
  "orgName": "Organization Name",
  "countryCode": "US",
  "classification": {
    "isMultiIndustry": false,
    "industries": [
      {
        "industry": "Industry Name",
        "subCategory": "Subcategory",
        "percentage": 100,
        "sampleProducts": ["Product 1", "Product 2"]
      }
    ],
    "primaryIndustry": "Industry Name",
    "businessType": "Retailer",
    "confidenceScore": 0.95,
    "reasoning": "Classification rationale"
  }
}
```

## Classification Methodology

### Industry Taxonomy

The system classifies organizations into 14 primary industries:

- Health & Medical
- Fitness & Sports
- Beauty & Personal Care
- Home Appliances
- Home & Living
- Electronics & Tech
- Food & Beverage
- Tobacco & Vaping
- Stationery & Office
- Automotive
- Fashion & Apparel
- Manufacturing Supplies
- Wholesale/Distribution
- General Retail

### Multi-Industry Detection

Organizations are flagged as multi-industry when their products span two or more distinct industry categories. Products within subcategories of the same industry are classified as single-industry.

### Business Type Classification

- **Manufacturer** - Produces goods, handles raw materials
- **Wholesaler** - Distributes in bulk quantities
- **Retailer** - Sells to end consumers
- **Distributor** - Intermediary in supply chain
- **Mixed** - Multiple business models

### Confidence Scoring

Confidence scores (0.0-1.0) reflect classification certainty based on product name clarity, industry mapping obviousness, and data completeness.

## Project Structure

```
├── app.py                                 # Streamlit web interface
├── prompt.py                              # Classification engine and API integration
├── requirements.txt                       # Python dependencies
├── industry_classification.md             # Detailed prompt documentation
├── classification_examples.md             # Example classifications
└── README.md                              # Documentation
```

## Model Configuration

The system supports two OpenAI models:

- **gpt-4o-mini** (default) - Optimized for speed and cost-efficiency
- **gpt-4o** - Higher accuracy for complex classifications

Model selection can be changed in the web interface.

## Cost Estimation

Approximate costs using gpt-4o-mini:
- Single classification: $0.001 - $0.003
- 100 organizations: $0.10 - $0.30
- 1,000 organizations: $1.00 - $3.00

Actual costs vary based on product count and description length.

## Performance

- Single classification: 2-4 seconds
- Batch processing (100 orgs): 4-5 minutes

## Troubleshooting

**API Key Issues**
Ensure the `OPENAI_API_KEY` environment variable is set correctly.

**Installation Errors**
Verify Python version (3.8+) and install dependencies with pip.

**UI Display Issues**
Clear browser cache and perform a hard refresh (Ctrl+Shift+R).

## Technical Support

For issues related to:
- Classification accuracy - Review input data format and product descriptions
- Performance - Consider using gpt-4o-mini model and processing smaller batches
- API costs - Monitor usage through OpenAI dashboard

---


## 📝 Classification Logic

### Multi-Industry Detection
- `isMultiIndustry: true` → 2+ distinct industries (e.g., Food + Electronics)
- `isMultiIndustry: false` → Single industry with subcategories (e.g., different printing supplies)

### Business Type Detection
- **Manufacturer**: Raw materials, production equipment
- **Wholesaler**: Bulk quantities (Kg, L), variety of finished products
- **Retailer**: Consumer units, small quantities
- **Distributor**: Wide variety, branded products
- **Mixed**: Combination of above

### Confidence Scoring
- **0.95-1.0**: Very clear patterns, well-described products
- **0.85-0.94**: Clear classification, minor ambiguities
- **0.70-0.84**: Reasonable classification, some unclear products
- **0.50-0.69**: Uncertain, limited information
- **<0.50**: Insufficient data or highly ambiguous

## 🤝 Contributing

Suggestions and improvements are welcome! Common areas for enhancement:
- Additional industry categories
- Improved multi-language support
- Custom industry taxonomies
- Integration with other LLM APIs

## 📄 License

This tool is provided as-is for classification purposes. Ensure compliance with Google's Gemini API terms of service.