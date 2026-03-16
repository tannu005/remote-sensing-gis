"""
Main Orchestration Script - Run Complete Analysis Pipeline
"""
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("\n" + "="*80)
    print("SCHOOL SITE SUITABILITY ANALYSIS - COMPLETE PIPELINE".center(80))
    print("Location: Chennai, Tamil Nadu, India".center(80))
    print("="*80 + "\n")
    
    # Step 1: Data Generation
    print("\n[STEP 1] Generating Synthetic Spatial Data...")
    print("-"*80)
    try:
        from scripts.data_generation import generate_all_data
        generate_all_data()
    except Exception as e:
        print(f"✗ Data generation failed: {e}")
        return
    
    # Step 2: GIS Analysis
    print("\n[STEP 2] Performing GIS Multi-Criteria Analysis...")
    print("-"*80)
    try:
        from scripts.gis_analysis import SuitabilityAnalysis
        analysis = SuitabilityAnalysis()
        suitability_map, classified_map = analysis.run_full_analysis()
    except Exception as e:
        print(f"✗ GIS analysis failed: {e}")
        return
    
    # Final Summary
    print("\n" + "="*80)
    print("PIPELINE EXECUTION COMPLETE".center(80))
    print("="*80)
    
    print("\n✓ All outputs saved to:")
    print(f"  - Data: {PROJECT_ROOT / 'data' / 'processed'}")
    print(f"  - Results: {PROJECT_ROOT / 'outputs'}")
    print(f"  - Reports: {PROJECT_ROOT / 'reports'}")
    
    print("\n✓ Next Steps:")
    print("  1. Review results in 'outputs' directory")
    print("  2. Open Jupyter notebook: notebooks/01_School_Suitability_Analysis.ipynb")
    print("  3. Run Streamlit app: streamlit run app/streamlit_app.py")
    print("  4. Analyze suitability maps and reports")
    print("  5. Validate findings through field surveys")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
