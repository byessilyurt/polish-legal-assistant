#!/usr/bin/env python3
"""
Setup verification script for Polish Legal Assistant Backend.

This script checks if all required dependencies are installed and
configuration is properly set up.
"""

import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 11):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (requires 3.11+)")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")

    required = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "openai": "OpenAI",
        "pinecone": "Pinecone",
        "langchain": "LangChain",
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
    }

    all_installed = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (not installed)")
            all_installed = False

    return all_installed


def check_env_file():
    """Check if .env file exists."""
    print("\nChecking environment configuration...", end=" ")
    env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        print("✓ .env file found")
        return True
    else:
        print("✗ .env file not found")
        print("  → Copy .env.example to .env and add your API keys")
        return False


def check_configuration():
    """Check if configuration can be loaded."""
    print("\nChecking configuration loading...", end=" ")
    try:
        from app.config import settings

        print("✓ Configuration loaded")

        print("\nConfiguration status:")
        print(f"  OpenAI configured: {'✓' if settings.openai_configured else '✗'}")
        print(f"  Pinecone configured: {'✓' if settings.pinecone_configured else '✗'}")

        if settings.is_configured:
            print("\n✓ All services configured!")
            return True
        else:
            print("\n✗ Some services not configured")
            print("  → Please set API keys in .env file")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def check_file_structure():
    """Check if all required files exist."""
    print("\nChecking file structure...")

    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/models/schemas.py",
        "app/services/llm_service.py",
        "app/services/retrieval_service.py",
        "app/services/rag_service.py",
        "app/api/chat.py",
        "tests/test_rag.py",
        "requirements.txt",
        "Dockerfile",
    ]

    base_path = Path(__file__).parent
    all_exist = True

    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (missing)")
            all_exist = False

    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Polish Legal Assistant Backend - Setup Verification")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_file_structure(),
        check_dependencies(),
        check_env_file(),
        check_configuration(),
    ]

    print("\n" + "=" * 60)

    if all(checks):
        print("✓ All checks passed! You're ready to run the backend.")
        print("\nNext steps:")
        print("  1. Ensure your API keys are set in .env")
        print("  2. Run: ./run.sh (or: uvicorn app.main:app --reload)")
        print("  3. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nFor help, see: README.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
