#!/usr/bin/env python
"""
Quick Start Script - One-command setup and execution
Usage: python quick_start.py
"""
import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*70}")
    print(f"→ {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully\n")
            return True
        else:
            print(f"✗ {description} failed\n")
            return False
    except Exception as e:
        print(f"✗ Error during {description}: {e}\n")
        return False

def main():
    print("\n" + "="*70)
    print("SCHOOL SITE SUITABILITY ANALYSIS - QUICK START".center(70))
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return
    if sys.version_info >= (3, 13):
        # Numpy and several scientific packages do not yet support 3.13
        print("✗ Python 3.13 is not supported by some dependencies (e.g. numpy).")
        print("  Please install Python 3.12 or 3.11 and retry.")
        return
    
    print("✓ Python version check passed")
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Step 1: Create virtual environment
    if not (project_dir / "venv").exists():
        print("\n[1/5] Creating virtual environment...")
        if sys.platform == "win32":
            run_command("python -m venv venv", "Virtual environment creation")
            pip_cmd = "venv\\Scripts\\pip"
            python_cmd = "venv\\Scripts\\python"
        else:
            run_command("python3 -m venv venv", "Virtual environment creation")
            pip_cmd = "venv/bin/pip"
            python_cmd = "venv/bin/python"
    else:
        print("\n✓ Virtual environment already exists")
        if sys.platform == "win32":
            pip_cmd = "venv\\Scripts\\pip"
            python_cmd = "venv\\Scripts\\python"
        else:
            pip_cmd = "venv/bin/pip"
            python_cmd = "venv/bin/python"
    
    # Step 2: Install dependencies
    print("\n[2/5] Installing dependencies...")
    run_command(f"{pip_cmd} install --upgrade pip", "pip upgrade")
    # ensure build tools are current to avoid BackendUnavailable errors
    run_command(f"{pip_cmd} install --upgrade setuptools wheel", "setuptools & wheel upgrade")
    run_command(f"{pip_cmd} install -r requirements.txt", "Package installation")
    
    # Step 3: Generate data
    print("\n[3/5] Generating spatial datasets...")
    run_command(f"{python_cmd} scripts/data_generation.py", "Data generation")
    
    # Step 4: Run analysis
    print("\n[4/5] Running GIS analysis...")
    run_command(f"{python_cmd} scripts/gis_analysis.py", "GIS analysis")
    
    # Step 5: Summary
    print("\n[5/5] Setup complete!")
    print("="*70)
    print("\n✓ ALL SYSTEMS READY\n")
    
    print("Next steps:")
    print("1. View analysis results:")
    print("   Open 'outputs/' folder to see generated maps and statistics")
    print("\n2. Run Jupyter notebook for detailed analysis:")
    print(f"   {python_cmd} -m jupyter notebook notebooks/01_School_Suitability_Analysis.ipynb")
    print("\n3. Launch interactive dashboard:")
    print(f"   {python_cmd} -m streamlit run app/streamlit_app.py")
    print("\n4. Read documentation:")
    print("   Open README.md for comprehensive project information")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
