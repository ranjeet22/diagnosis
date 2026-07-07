#!/usr/bin/env python3
"""
Development environment setup script for Diagnōsis.
Ensures local log and storage folders exist and copies environment variables.
"""
import os
import shutil

def main():
    print("Setting up development environment for Diagnōsis...")
    
    # 1. Create logs directory
    os.makedirs("logs", exist_ok=True)
    print("✔ Logs directory validated.")

    # 2. Create storage uploads directory
    os.makedirs("storage/uploads", exist_ok=True)
    print("✔ Storage uploads directory validated.")

    # 3. Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✔ Copied .env.example to .env")
        else:
            print("❌ .env.example not found! Cannot copy default settings.")
    else:
        print("✔ .env file already exists.")

    print("\nSetup complete! You can now run 'make run' or 'poetry run uvicorn app.main:app --reload'")

if __name__ == "__main__":
    main()
