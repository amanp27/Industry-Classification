"""
Example usage of the Industry Classifier
This script demonstrates how to use the classifier in different scenarios
"""

import json
from prompt import IndustryClassifier


def example_1_single_classification():
    """Example 1: Classify a single organization"""
    print("=" * 80)
    print("EXAMPLE 1: Single Organization Classification")
    print("=" * 80)
    
    # Initialize classifier (make sure GEMINI_API_KEY is set)
    classifier = IndustryClassifier()
    
    # Sample organization data
    org_data = {
        "_id": "sample_001",
        "orgName": "ABC Printing Supplies",
        "countryCode": "US",
        "product_names": [
            {
                "productName": "UV Cyan Ink",
                "categoryName": "",
                "unit": "Kg",
                "productCode": "UV-CY-001",
                "typeOfCommodity": 0,
                "discription": "Cyan UV ink for offset printing"
            },
            {
                "productName": "Offset Magenta Ink",
                "categoryName": "",
                "unit": "Kg",
                "productCode": "OF-MG-002",
                "typeOfCommodity": 0,
                "discription": "Magenta ink for offset printing"
            },
            {
                "productName": "UV Varnish",
                "categoryName": "",
                "unit": "L",
                "productCode": "UV-VN-003",
                "typeOfCommodity": 0,
                "discription": "UV coating varnish"
            },
            {
                "productName": "Flexo Black Ink",
                "categoryName": "",
                "unit": "Kg",
                "productCode": "FL-BK-004",
                "typeOfCommodity": 0,
                "discription": "Black ink for flexographic printing"
            }
        ]
    }
    
    # Classify
    print("\nClassifying organization...")
    result = classifier.classify_organization(org_data)
    
    # Display result
    print("\nRESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Extract key information
    classification = result.get('classification', {})
    print("\n" + "=" * 80)
    print("KEY INSIGHTS:")
    print(f"Organization: {result.get('orgName')}")
    print(f"Multi-Industry: {'Yes' if classification.get('isMultiIndustry') else 'No'}")
    print(f"Primary Industry: {classification.get('primaryIndustry')}")
    print(f"Business Type: {classification.get('businessType')}")
    print(f"Confidence: {classification.get('confidenceScore', 0):.1%}")
    print("=" * 80)


def example_2_batch_classification():
    """Example 2: Batch classify multiple organizations"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Batch Classification")
    print("=" * 80)
    
    # Initialize classifier
    classifier = IndustryClassifier()
    
    # Sample organizations
    organizations = [
        {
            "_id": "001",
            "orgName": "Tech Components Ltd",
            "countryCode": "CN",
            "product_names": [
                {"productName": "USB-C Cable", "unit": "1000 pcs"},
                {"productName": "HDMI Cable", "unit": "500 pcs"},
                {"productName": "Power Adapter", "unit": "200 pcs"}
            ]
        },
        {
            "_id": "002",
            "orgName": "Fresh Foods Market",
            "countryCode": "US",
            "product_names": [
                {"productName": "Organic Apples", "unit": "kg"},
                {"productName": "Fresh Milk", "unit": "L"},
                {"productName": "Whole Wheat Bread", "unit": "loaf"}
            ]
        },
        {
            "_id": "003",
            "orgName": "MultiTrade Co",
            "countryCode": "AE",
            "product_names": [
                {"productName": "Laptop Charger", "unit": "50 pcs"},
                {"productName": "Office Chair", "unit": "20 pcs"},
                {"productName": "Desk Lamp", "unit": "100 pcs"}
            ]
        }
    ]
    
    # Batch classify
    print(f"\nClassifying {len(organizations)} organizations...")
    results = classifier.classify_batch(organizations)
    
    # Display summary
    print("\n" + "=" * 80)
    print("BATCH RESULTS SUMMARY:")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        classification = result.get('classification', {})
        print(f"\n{i}. {result.get('orgName')}")
        print(f"   Primary Industry: {classification.get('primaryIndustry', 'N/A')}")
        print(f"   Business Type: {classification.get('businessType', 'N/A')}")
        print(f"   Multi-Industry: {'Yes' if classification.get('isMultiIndustry') else 'No'}")
        print(f"   Confidence: {classification.get('confidenceScore', 0):.1%}")
    
    # Save results
    output_file = 'example_batch_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    print("=" * 80)


def example_3_from_file():
    """Example 3: Process from JSON file"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Process from File")
    print("=" * 80)
    
    # Initialize classifier
    classifier = IndustryClassifier()
    
    # Check if the main data file exists
    input_file = 'product5oData.json'
    
    try:
        print(f"\nAttempting to process first 3 organizations from {input_file}...")
        
        results = classifier.classify_from_file(
            input_file=input_file,
            output_file='file_classification_results.json',
            max_items=3  # Process only first 3 for demo
        )
        
        print("\n✅ Processing complete!")
        print(f"   Results saved to: file_classification_results.json")
        
    except FileNotFoundError:
        print(f"\n⚠️  File '{input_file}' not found in current directory")
        print("   This example requires the main data file to be present")
        print("   Skip this example or place the file in the same directory")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("=" * 80)


def example_4_multi_industry_detection():
    """Example 4: Demonstrate multi-industry detection"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: Multi-Industry Detection")
    print("=" * 80)
    
    classifier = IndustryClassifier()
    
    # Organization with products from multiple industries
    multi_industry_org = {
        "_id": "multi_001",
        "orgName": "Global Traders Inc",
        "countryCode": "UK",
        "product_names": [
            {"productName": "Laptop Computer", "unit": "10 pcs"},
            {"productName": "Office Desk", "unit": "5 pcs"},
            {"productName": "Organic Honey", "unit": "50 jars"},
            {"productName": "Vitamin C Tablets", "unit": "100 bottles"},
            {"productName": "USB Flash Drive", "unit": "200 pcs"},
            {"productName": "Ergonomic Chair", "unit": "8 pcs"}
        ]
    }
    
    # Organization with products from single industry
    single_industry_org = {
        "_id": "single_001",
        "orgName": "Printing Solutions Pro",
        "countryCode": "DE",
        "product_names": [
            {"productName": "Cyan Ink", "unit": "Kg"},
            {"productName": "Magenta Ink", "unit": "Kg"},
            {"productName": "Yellow Ink", "unit": "Kg"},
            {"productName": "Black Ink", "unit": "Kg"},
            {"productName": "UV Varnish", "unit": "L"},
            {"productName": "Printing Blanket", "unit": "m"}
        ]
    }
    
    print("\nTest Case 1: Multi-Industry Organization")
    print("-" * 80)
    result1 = classifier.classify_organization(multi_industry_org)
    classification1 = result1.get('classification', {})
    
    print(f"Organization: {result1.get('orgName')}")
    print(f"Is Multi-Industry: {classification1.get('isMultiIndustry')}")
    print(f"Industries Found: {len(classification1.get('industries', []))}")
    
    for ind in classification1.get('industries', []):
        print(f"  - {ind.get('industry')} / {ind.get('subCategory')} ({ind.get('percentage')}%)")
    
    print("\nTest Case 2: Single-Industry Organization")
    print("-" * 80)
    result2 = classifier.classify_organization(single_industry_org)
    classification2 = result2.get('classification', {})
    
    print(f"Organization: {result2.get('orgName')}")
    print(f"Is Multi-Industry: {classification2.get('isMultiIndustry')}")
    print(f"Primary Industry: {classification2.get('primaryIndustry')}")
    print(f"SubCategory: {classification2.get('industries', [{}])[0].get('subCategory')}")
    
    print("\n" + "=" * 80)
    print("COMPARISON:")
    print(f"Multi-Industry Org has {len(classification1.get('industries', []))} industries")
    print(f"Single-Industry Org has {len(classification2.get('industries', []))} industry")
    print("=" * 80)


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "INDUSTRY CLASSIFIER EXAMPLES" + " " * 30 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run examples
        example_1_single_classification()
        example_2_batch_classification()
        example_3_from_file()
        example_4_multi_industry_detection()
        
        print("\n\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 80)
        print("\nGenerated files:")
        print("  - example_batch_results.json")
        print("  - file_classification_results.json (if main file exists)")
        print("\nNext steps:")
        print("  1. Review the generated JSON files")
        print("  2. Try the Streamlit UI: streamlit run ui.py")
        print("  3. Customize the classifier for your needs")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nMake sure:")
        print("  1. GEMINI_API_KEY environment variable is set")
        print("  2. Required packages are installed: pip install -r requirements.txt")


if __name__ == "__main__":
    main()