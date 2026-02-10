# 🏭 Industry Classification Tool

An AI-powered tool to classify organizations into industries based on their product portfolios using Google's Gemini API.

## 📋 Features

- **Single Organization Classification**: Test individual organizations with instant results
- **Batch Processing**: Process multiple organizations from JSON files
- **Multi-Industry Detection**: Identifies if organizations operate in multiple distinct industries
- **Confidence Scoring**: AI-powered confidence assessment for each classification
- **Interactive UI**: Beautiful Streamlit interface for easy testing and visualization
- **Results Analysis**: Charts and insights from batch processing results
- **Export Capability**: Download results as JSON files

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the files
# Navigate to the project directory

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Set up API Key

**Option A: Environment Variable (Recommended)**
```bash
# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set GEMINI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"
```

**Option B: Enter in UI**
- Launch the UI and paste your API key in the sidebar

### 4. Run the Application

**Start the Streamlit UI:**
```bash
streamlit run ui.py
```

The app will open in your browser at `http://localhost:8501`

**Or use the Python script directly:**
```python
from prompt import IndustryClassifier

# Initialize classifier
classifier = IndustryClassifier(api_key="your-api-key")

# Classify single organization
org_data = {
    "_id": "001",
    "orgName": "Sample Co.",
    "countryCode": "US",
    "product_names": [
        {"productName": "Product A", "unit": "kg"}
    ]
}

result = classifier.classify_organization(org_data)
print(result)

# Or process from file
classifier.classify_from_file(
    input_file='product5oData.json',
    output_file='results.json',
    max_items=10  # Optional: limit for testing
)
```

## 📁 Project Structure

```
.
├── prompt.py                              # Core classification logic
├── ui.py                                  # Streamlit web interface
├── requirements.txt                       # Python dependencies
├── README.md                              # This file
├── industry_classification_prompt.md      # Detailed prompt documentation
├── classification_examples.md             # Example classifications
└── api_integration_prompts.md            # API integration guide
```

## 🎯 Using the UI

### Single Classification Tab

1. Click "Initialize Classifier" in the sidebar (after entering API key)
2. Go to "Single Classification" tab
3. Click "Load Sample Data" or paste your own JSON
4. Click "Classify Organization"
5. View results with industry breakdown, confidence score, and reasoning

### Batch Processing Tab

1. Upload your JSON file in the sidebar
2. Go to "Batch Processing" tab
3. Select number of organizations to process
4. Click "Start Batch Classification"
5. Download results as JSON when complete

### Results Analysis Tab

1. After batch processing, go to "Results Analysis"
2. View charts showing:
   - Industry distribution
   - Business type breakdown
   - Confidence score distribution
   - Top industries with organization details

## 📊 Input Data Format

Your JSON file should contain an array of organization objects:

```json
[
  {
    "_id": "93649",
    "orgName": "Company Name",
    "businessId": "",
    "countryCode": "US",
    "product_names": [
      {
        "productName": "Product Name",
        "categoryName": "",
        "unit": "Kg",
        "productCode": "",
        "typeOfCommodity": 0,
        "discription": "Description"
      }
    ]
  }
]
```

## 📤 Output Format

```json
{
  "_id": "93649",
  "orgName": "Company Name",
  "countryCode": "US",
  "classification": {
    "isMultiIndustry": false,
    "industries": [
      {
        "industry": "Manufacturing",
        "subCategory": "Printing Inks & Supplies",
        "percentage": 100,
        "sampleProducts": ["Product 1", "Product 2", "Product 3"]
      }
    ],
    "primaryIndustry": "Manufacturing",
    "businessType": "Wholesaler",
    "confidenceScore": 0.95,
    "reasoning": "Explanation of classification logic..."
  }
}
```

## 🔧 Configuration

### Gemini Model Settings

In `prompt.py`, you can adjust the model configuration:

```python
generation_config={
    'temperature': 0.2,      # Lower = more consistent
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 2048,
}
```

### Model Selection

Current model: `gemini-2.0-flash-exp`

Alternative models you can use:
- `gemini-1.5-pro` - More capable but slower
- `gemini-1.5-flash` - Balance of speed and capability

## 💡 Tips for Best Results

1. **Clear Product Names**: More descriptive product names lead to better classifications
2. **Consistent Units**: Helps determine business type (bulk vs. retail)
3. **Product Descriptions**: Use the description field when available
4. **Batch Size**: Start with small batches (5-10) to test before processing large datasets
5. **API Limits**: Be aware of Gemini API rate limits for large batch processing

## 🐛 Troubleshooting

### API Key Issues
- Error: "API key not provided"
  - Solution: Set `GEMINI_API_KEY` environment variable or enter in UI

### JSON Parsing Errors
- Error: "Failed to parse response"
  - Solution: Check if the model is returning valid JSON
  - Try lowering temperature in generation_config

### UI Not Loading
- Error: Module not found
  - Solution: Run `pip install -r requirements.txt`

### Slow Processing
- Issue: Batch processing is slow
  - Solution: Use `gemini-2.0-flash-exp` model (already default)
  - Reduce batch size for testing

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

## 🔗 Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- Prompt templates included in `industry_classification_prompt.md`

## ❓ FAQ

**Q: Can I use other LLM APIs besides Gemini?**
A: Yes, you can modify `prompt.py` to use OpenAI, Anthropic Claude, or other APIs. See `api_integration_prompts.md` for examples.

**Q: How accurate is the classification?**
A: Accuracy depends on product data quality. Clear, descriptive product names yield 90%+ accuracy. The confidence score indicates the model's certainty.

**Q: Can I customize industry categories?**
A: Yes, modify the prompt in `prompt.py` to include your specific industry taxonomy.

**Q: Is my data stored anywhere?**
A: No. Data is only sent to Google's Gemini API for classification and returned to you. See Google's privacy policy for API data handling.

**Q: Can I process thousands of organizations?**
A: Yes, but be aware of API rate limits. Consider implementing batching with delays for very large datasets.

---

Made with ❤️ using Google Gemini AI and Streamlit