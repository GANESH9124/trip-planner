"""
Model Factory - Supports multiple free chat model providers
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

class ModelFactory:
    """Factory to create chat models from different providers"""
    
    @staticmethod
    def create_model():
        """
        Create a chat model based on MODEL_TYPE environment variable
        Returns a LangChain-compatible chat model
        """
        model_type = os.getenv("MODEL_TYPE", "ollama").lower()
        
        if model_type == "ollama":
            return ModelFactory._create_ollama_model()
        elif model_type == "huggingface":
            return ModelFactory._create_huggingface_model()
        elif model_type == "groq":
            return ModelFactory._create_groq_model()
        elif model_type == "together":
            return ModelFactory._create_together_model()
        elif model_type == "openrouter":
            return ModelFactory._create_openrouter_model()
        elif model_type == "google" or model_type == "gemini":
            return ModelFactory._create_google_model()
        else:
            # Default to Ollama
            print(f"⚠️  Unknown MODEL_TYPE '{model_type}', defaulting to Ollama")
            return ModelFactory._create_ollama_model()
    
    @staticmethod
    def _create_ollama_model():
        """Create Ollama model (free, local)"""
        try:
            from langchain_ollama import ChatOllama
            
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
            
            # Check if Ollama is accessible
            try:
                import requests
                response = requests.get(f"{base_url}/api/tags", timeout=2)
                if response.status_code != 200:
                    raise ConnectionError("Ollama service not responding")
            except Exception as e:
                raise ConnectionError(
                    f"Cannot connect to Ollama at {base_url}. "
                    f"Make sure Ollama is running: ollama serve\n"
                    f"Error: {str(e)}"
                )
            
            # Check if model is available
            try:
                import requests
                response = requests.get(f"{base_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    # Check if exact match or starts with model name
                    if not any(model_name in name or name.startswith(model_name) for name in model_names):
                        raise ValueError(
                            f"Model '{model_name}' not found in Ollama.\n"
                            f"Available models: {', '.join(model_names) if model_names else 'None'}\n"
                            f"Download it with: ollama pull {model_name}\n"
                            f"Or run: .\\download_model.ps1"
                        )
            except ValueError:
                raise  # Re-raise ValueError
            except Exception:
                # If we can't check, try anyway - might work
                pass
            
            model = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.7,
            )
            print(f"✅ Using Ollama model: {model_name}")
            return model
        except ImportError:
            raise ImportError(
                "langchain-ollama not installed. Install with: pip install langchain-ollama\n"
                "Also make sure Ollama is running: ollama serve"
            )
        except (ValueError, ConnectionError) as e:
            raise  # Re-raise these with our custom messages
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                raise ValueError(
                    f"Model '{model_name}' not found.\n"
                    f"Download it with: ollama pull {model_name}\n"
                    f"Or run: .\\download_model.ps1"
                )
            raise ValueError(f"Failed to create Ollama model: {str(e)}\n"
                           f"Make sure Ollama is running: ollama serve")
    
    @staticmethod
    def _create_huggingface_model():
        """Create Hugging Face model"""
        try:
            from langchain_huggingface import ChatHuggingFace
            from langchain_huggingface.llms import HuggingFaceEndpoint
            
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("HUGGINGFACE_API_KEY not set in .env")
            
            model_name = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
            
            endpoint = HuggingFaceEndpoint(
                repo_id=model_name,
                huggingfacehub_api_token=api_key,
                temperature=0.7,
            )
            
            model = ChatHuggingFace(llm=endpoint)
            print(f"✅ Using Hugging Face model: {model_name}")
            return model
        except ImportError:
            raise ImportError(
                "langchain-huggingface not installed. Install with: pip install langchain-huggingface"
            )
        except Exception as e:
            raise ValueError(f"Failed to create Hugging Face model: {str(e)}")
    
    @staticmethod
    def _create_groq_model():
        """Create Groq model (free tier, very fast)"""
        try:
            from langchain_groq import ChatGroq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in .env. Get it from: https://console.groq.com")
            
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            
            model = ChatGroq(
                model=model_name,
                groq_api_key=api_key,
                temperature=0.7,
            )
            print(f"✅ Using Groq model: {model_name}")
            return model
        except ImportError:
            raise ImportError(
                "langchain-groq not installed. Install with: pip install langchain-groq"
            )
        except Exception as e:
            raise ValueError(f"Failed to create Groq model: {str(e)}")
    
    @staticmethod
    def _create_together_model():
        """Create Together AI model"""
        try:
            from langchain_together import ChatTogether
            
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                raise ValueError("TOGETHER_API_KEY not set in .env. Get it from: https://api.together.xyz")
            
            model_name = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-2-7b-chat-hf")
            
            model = ChatTogether(
                model=model_name,
                together_api_key=api_key,
                temperature=0.7,
            )
            print(f"✅ Using Together AI model: {model_name}")
            return model
        except ImportError:
            raise ImportError(
                "langchain-together not installed. Install with: pip install langchain-together"
            )
        except Exception as e:
            raise ValueError(f"Failed to create Together AI model: {str(e)}")
    
    @staticmethod
    def _create_openrouter_model():
        """Create OpenRouter model"""
        try:
            from langchain_openai import ChatOpenAI
            
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not set in .env. Get it from: https://openrouter.ai")
            
            model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-flash-1.5-8b")
            
            model = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.7,
            )
            print(f"✅ Using OpenRouter model: {model_name}")
            return model
        except ImportError:
            raise ImportError(
                "langchain-openai not installed. Install with: pip install langchain-openai"
            )
        except Exception as e:
            raise ValueError(f"Failed to create OpenRouter model: {str(e)}")
    
    @staticmethod
    def _create_google_model():
        """Create Google Gemini model (original)"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            google_api_key = os.getenv("GOOGLE_API_KEY")
            service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if google_api_key:
                model = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.7,
                    google_api_key=google_api_key,
                )
                print("✅ Using Google Gemini with API key")
                return model
            elif service_account_path:
                path_dir = os.getcwd()
                service_account_path = os.path.join(path_dir, 'src', service_account_path)
                
                creds = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                creds.refresh(Request())
                
                model = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.7,
                    credentials=creds,
                )
                print("✅ Using Google Gemini with service account")
                return model
            else:
                raise ValueError("GOOGLE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS not set")
        except Exception as e:
            raise ValueError(f"Failed to create Google model: {str(e)}")

