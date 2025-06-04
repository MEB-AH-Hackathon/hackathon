#!/usr/bin/env python3
"""
Extract all unique vaccine names from VAERS VAX files.
"""

import pandas as pd
import os
from pathlib import Path
import json
from collections import Counter

def extract_vaccine_names():
    """Extract all unique vaccine names from VAERS VAX CSV files."""
    
    vaers_dir = Path("/Users/abigailhaddad/Documents/repos/hackathon/vaers_data/vaers_data")
    
    all_vaccine_names = set()
    vaccine_counts = Counter()
    files_processed = []
    
    # Process all VAERSVAX.csv files
    for file_path in sorted(vaers_dir.glob("*VAERSVAX.csv")):
        print(f"Processing {file_path.name}...")
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path, encoding='latin-1', low_memory=False)
            
            # Check if VAX_NAME column exists
            if 'VAX_NAME' in df.columns:
                # Get unique vaccine names from this file
                vaccine_names = df['VAX_NAME'].dropna().unique()
                
                # Add to our sets
                all_vaccine_names.update(vaccine_names)
                
                # Count occurrences
                vaccine_counts.update(df['VAX_NAME'].dropna().tolist())
                
                files_processed.append(file_path.name)
                print(f"  Found {len(vaccine_names)} unique vaccines in {file_path.name}")
            else:
                print(f"  WARNING: No VAX_NAME column found in {file_path.name}")
                
        except Exception as e:
            print(f"  ERROR processing {file_path.name}: {e}")
    
    # Sort vaccine names alphabetically
    sorted_vaccines = sorted(all_vaccine_names)
    
    # Create output directory
    output_dir = Path("/Users/abigailhaddad/Documents/repos/hackathon/intermediate_results")
    output_dir.mkdir(exist_ok=True)
    
    # Save results
    results = {
        "total_unique_vaccines": len(sorted_vaccines),
        "files_processed": files_processed,
        "vaccine_names": sorted_vaccines,
        "vaccine_counts": dict(vaccine_counts.most_common())
    }
    
    output_path = output_dir / "vaers_vaccine_names.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSummary:")
    print(f"Total unique vaccine names found: {len(sorted_vaccines)}")
    print(f"Files processed: {len(files_processed)}")
    print(f"Results saved to: {output_path}")
    
    # Print top 20 most common vaccines
    print("\nTop 20 most common vaccines:")
    for vaccine, count in vaccine_counts.most_common(20):
        print(f"  {vaccine}: {count:,} occurrences")
    
    # Print all unique vaccine names
    print("\nAll unique vaccine names (alphabetically sorted):")
    for vaccine in sorted_vaccines:
        print(f"  - {vaccine}")

if __name__ == "__main__":
    extract_vaccine_names()