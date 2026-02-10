#!/bin/bash

# Industry Classification Tool - Quick Start Script

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Industry Classification Tool - Quick Start             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 is installed"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✅ pip is installed"

# Install requirements
echo ""
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Check for API key
echo ""
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY environment variable is not set"
    echo ""
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or you can enter it in the UI after launching."
    echo ""
else
    echo "✅ GEMINI_API_KEY is set"
fi

# Offer to launch UI
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Setup complete! Choose an option:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  1) Launch Streamlit UI (recommended)"
echo "  2) Run example script"
echo "  3) Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Streamlit UI..."
        streamlit run ui.py
        ;;
    2)
        echo ""
        echo "🚀 Running example script..."
        python3 example.py
        ;;
    3)
        echo ""
        echo "👋 Goodbye!"
        ;;
    *)
        echo ""
        echo "❌ Invalid choice"
        ;;
esac