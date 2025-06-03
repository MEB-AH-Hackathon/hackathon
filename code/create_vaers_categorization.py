#!/usr/bin/env python3
"""
Categorize each VAERS ID based on the mapping status of its symptoms.
Creates a JSON file with categorization for each report.
"""

import duckdb
import json
from collections import defaultdict

def categorize_vaers_reports():
    # Connect to the database
    conn = duckdb.connect('duckdb/vaers_analysis.db')
    
    print("Categorizing VAERS reports by symptom mapping status...")
    
    # Get all VAERS reports with their symptom statuses
    results = conn.execute("""
        WITH symptom_status AS (
            SELECT 
                v.VAERS_ID,
                v.vax_name as vaccine,
                v.symptom,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM symptom_mappings sm 
                        INNER JOIN fda_reports f ON f.adverse_event = sm.fda_adverse_event
                        WHERE sm.vaers_symptom = v.symptom 
                        AND f.vaccine_name = v.vax_name
                    ) THEN 'fully_matched'
                    WHEN EXISTS (
                        SELECT 1 FROM symptom_mappings sm 
                        WHERE sm.vaers_symptom = v.symptom
                    ) THEN 'mapped_not_matched'
                    ELSE 'not_mapped'
                END as status
            FROM vaers_subset v
        )
        SELECT 
            VAERS_ID,
            vaccine,
            COUNT(DISTINCT symptom) as total_symptoms,
            COUNT(DISTINCT CASE WHEN status = 'fully_matched' THEN symptom END) as fully_matched,
            COUNT(DISTINCT CASE WHEN status = 'mapped_not_matched' THEN symptom END) as mapped_not_matched,
            COUNT(DISTINCT CASE WHEN status = 'not_mapped' THEN symptom END) as not_mapped
        FROM symptom_status
        GROUP BY VAERS_ID, vaccine
        ORDER BY VAERS_ID
    """).fetchall()
    
    # Process results into categorized structure
    categorized_reports = []
    
    # Count reports by category
    category_counts = defaultdict(int)
    
    for vaers_id, vaccine, total, fully_matched, mapped_not_matched, not_mapped in results:
        # Determine the category
        categories = []
        if fully_matched > 0:
            categories.append("fully_matched")
        if mapped_not_matched > 0:
            categories.append("mapped_not_matched")
        if not_mapped > 0:
            categories.append("not_mapped")
        
        # Create category string
        if len(categories) == 1:
            category = categories[0]
        else:
            category = "_and_".join(categories)
        
        category_counts[category] += 1
        
        # Calculate percentages
        fully_matched_pct = (fully_matched / total * 100) if total > 0 else 0
        mapped_not_matched_pct = (mapped_not_matched / total * 100) if total > 0 else 0
        not_mapped_pct = (not_mapped / total * 100) if total > 0 else 0
        
        report = {
            "VAERS_ID": vaers_id,
            "vaccine": vaccine,
            "category": category,
            "total_symptoms": total,
            "symptom_breakdown": {
                "fully_matched": fully_matched,
                "mapped_not_matched": mapped_not_matched,
                "not_mapped": not_mapped
            },
            "symptom_percentages": {
                "fully_matched_pct": round(fully_matched_pct, 1),
                "mapped_not_matched_pct": round(mapped_not_matched_pct, 1),
                "not_mapped_pct": round(not_mapped_pct, 1)
            }
        }
        
        categorized_reports.append(report)
    
    # Create summary statistics
    summary = {
        "total_reports": len(categorized_reports),
        "category_counts": dict(category_counts),
        "category_percentages": {}
    }
    
    # Calculate category percentages
    total_reports = summary["total_reports"]
    for category, count in category_counts.items():
        summary["category_percentages"][category] = round(count / total_reports * 100, 2)
    
    # Create the final output structure
    output = {
        "metadata": {
            "description": "Categorization of VAERS reports based on symptom mapping status",
            "categories": {
                "fully_matched": "All symptoms are documented in FDA package insert for the vaccine",
                "mapped_not_matched": "All symptoms are mapped but not in FDA list for the vaccine",
                "not_mapped": "All symptoms have not been mapped yet",
                "fully_matched_and_mapped_not_matched": "Mix of FDA-documented and mapped-but-not-matched symptoms",
                "fully_matched_and_not_mapped": "Mix of FDA-documented and unmapped symptoms",
                "mapped_not_matched_and_not_mapped": "Mix of mapped-but-not-matched and unmapped symptoms",
                "fully_matched_and_mapped_not_matched_and_not_mapped": "Mix of all three types"
            },
            "generated_date": "2025-06-03"
        },
        "summary": summary,
        "reports": categorized_reports
    }
    
    # Save to JSON
    with open('json_data/vaers_categorization.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"\nTotal reports categorized: {total_reports:,}")
    print("\nCategory breakdown:")
    for category in sorted(category_counts.keys()):
        count = category_counts[category]
        pct = summary["category_percentages"][category]
        print(f"  {category}: {count:,} ({pct}%)")
    
    print("\nCategorization saved to json_data/vaers_categorization.json")
    
    # Also create a smaller sample file for inspection
    sample_output = {
        "metadata": output["metadata"],
        "summary": output["summary"],
        "sample_reports": categorized_reports[:100]  # First 100 reports
    }
    
    with open('json_data/vaers_categorization_sample.json', 'w') as f:
        json.dump(sample_output, f, indent=2)
    
    print("Sample (first 100 reports) saved to json_data/vaers_categorization_sample.json")
    
    conn.close()

if __name__ == "__main__":
    categorize_vaers_reports()