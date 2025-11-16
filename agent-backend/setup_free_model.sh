#!/bin/bash
# Quick setup script for free models

echo "=========================================="
echo "Free Chat Model Setup"
echo "=========================================="
echo ""

echo "Which model would you like to use?"
echo "1. Ollama (Free, Local - Recommended)"
echo "2. Groq (Free Tier, Very Fast)"
echo "3. Hugging Face (Free Tier)"
echo "4. Together AI (Free Tier)"
echo "5. Google Gemini (API Key)"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Setting up Ollama..."
        echo "1. Install Ollama from: https://ollama.com"
        echo "2. Run: ollama pull llama3.2"
        echo "3. Add to .env:"
        echo "   MODEL_TYPE=ollama"
        echo "   OLLAMA_MODEL=llama3.2"
        echo ""
        echo "Then install Python package:"
        echo "   pip install langchain-ollama"
        ;;
    2)
        echo ""
        echo "Setting up Groq..."
        echo "1. Get API key from: https://console.groq.com"
        echo "2. Add to .env:"
        echo "   MODEL_TYPE=groq"
        echo "   GROQ_API_KEY=your_key_here"
        echo "   GROQ_MODEL=llama-3.1-8b-instant"
        echo ""
        echo "Then install Python package:"
        echo "   pip install langchain-groq"
        ;;
    3)
        echo ""
        echo "Setting up Hugging Face..."
        echo "1. Get API key from: https://huggingface.co/settings/tokens"
        echo "2. Add to .env:"
        echo "   MODEL_TYPE=huggingface"
        echo "   HUGGINGFACE_API_KEY=your_key_here"
        echo "   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2"
        echo ""
        echo "Then install Python package:"
        echo "   pip install langchain-huggingface"
        ;;
    4)
        echo ""
        echo "Setting up Together AI..."
        echo "1. Get API key from: https://api.together.xyz"
        echo "2. Add to .env:"
        echo "   MODEL_TYPE=together"
        echo "   TOGETHER_API_KEY=your_key_here"
        echo "   TOGETHER_MODEL=meta-llama/Llama-2-7b-chat-hf"
        echo ""
        echo "Then install Python package:"
        echo "   pip install langchain-together"
        ;;
    5)
        echo ""
        echo "Setting up Google Gemini..."
        echo "1. Get API key from: https://makersuite.google.com/app/apikey"
        echo "2. Add to .env:"
        echo "   MODEL_TYPE=google"
        echo "   GOOGLE_API_KEY=your_key_here"
        echo ""
        echo "Then install Python package:"
        echo "   pip install langchain-google-genai"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

echo ""
echo "See FREE_MODELS.md for more details!"

