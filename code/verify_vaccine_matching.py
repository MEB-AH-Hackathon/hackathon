#!/usr/bin/env python3
"""
Verify that VAERS subset vaccines match FDA reports by vaccine name and manufacturer
"""

import json
from collections import defaultdict

def verify_vaccine_matching():
    """Check if VAERS subset vaccines match FDA reports"""
    
    # Load FDA reports
    print("Loading FDA reports...")
    with open('json_data/fda_reports.json', 'r') as f:
        fda_reports = json.load(f)
    
    # Load VAERS subset
    print("Loading VAERS subset...")
    with open('json_data/vaers_subset.json', 'r') as f:
        vaers_subset = json.load(f)
    
    # Build FDA vaccine lookup
    fda_vaccines = {}
    fda_vaers_names = set()
    
    for report in fda_reports:
        # Store by primary vaccine name
        vaccine_name = report.get('vaccine_name')
        manufacturer = report.get('vax_manu')
        
        if vaccine_name:
            fda_vaccines[vaccine_name] = {
                'manufacturer': manufacturer,
                'fda_name': report.get('vax_name'),
                'vaers_names': report.get('vaers_vaccine_names', [])
            }
            
        # Collect all VAERS names
        if report.get('vaers_vaccine_names'):
            fda_vaers_names.update(report['vaers_vaccine_names'])
    
    print(f"\nFDA Reports Summary:")
    print(f"  Total FDA vaccines: {len(fda_vaccines)}")
    print(f"  Total VAERS names in FDA: {len(fda_vaers_names)}")
    
    # Analyze VAERS subset
    vaers_vaccine_counts = defaultdict(int)
    vaers_manufacturer_counts = defaultdict(int)
    vaers_vaccine_manu_pairs = defaultdict(int)
    unmatched_vaccines = set()
    
    for record in vaers_subset:
        # Check each vaccine in the record
        vax_names = record.get('VAX_NAME_list', [])
        vax_manus = record.get('VAX_MANU_list', [])
        
        # Handle cases where lists might be different lengths
        max_len = max(len(vax_names), len(vax_manus))
        
        for i in range(max_len):
            vax_name = vax_names[i] if i < len(vax_names) else None
            vax_manu = vax_manus[i] if i < len(vax_manus) else None
            
            if vax_name:
                vaers_vaccine_counts[vax_name] += 1
                
                # Check if vaccine is in FDA list
                if vax_name not in fda_vaers_names:
                    unmatched_vaccines.add(vax_name)
                
                if vax_manu:
                    vaers_manufacturer_counts[vax_manu] += 1
                    vaers_vaccine_manu_pairs[(vax_name, vax_manu)] += 1
    
    print(f"\nVAERS Subset Summary:")
    print(f"  Total records: {len(vaers_subset)}")
    print(f"  Unique vaccines found: {len(vaers_vaccine_counts)}")
    print(f"  Unique manufacturers found: {len(vaers_manufacturer_counts)}")
    
    # Show matching statistics
    matched_vaccines = set(vaers_vaccine_counts.keys()) & fda_vaers_names
    print(f"\nMatching Statistics:")
    print(f"  Vaccines in both FDA and VAERS: {len(matched_vaccines)}")
    print(f"  Vaccines in VAERS but not FDA: {len(unmatched_vaccines)}")
    
    if unmatched_vaccines:
        print("\n⚠️  Unmatched vaccines (in VAERS but not FDA):")
        for vax in sorted(unmatched_vaccines):
            count = vaers_vaccine_counts[vax]
            print(f"    - {vax}: {count} reports")
    
    # Show top vaccines by count
    print("\nTop 10 vaccines in VAERS subset:")
    for vax, count in sorted(vaers_vaccine_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        match_status = "✓" if vax in fda_vaers_names else "✗"
        print(f"  {match_status} {vax}: {count:,} reports")
    
    # Show manufacturer distribution
    print("\nTop manufacturers in VAERS subset:")
    for manu, count in sorted(vaers_manufacturer_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {manu}: {count:,} reports")
    
    # Verify vaccine-manufacturer pairs
    print("\nVerifying vaccine-manufacturer pairs:")
    mismatches = []
    
    for (vax_name, vax_manu), count in sorted(vaers_vaccine_manu_pairs.items(), 
                                               key=lambda x: x[1], reverse=True)[:20]:
        # Find FDA info for this vaccine
        fda_info = None
        for fda_vax, info in fda_vaccines.items():
            if vax_name in info['vaers_names']:
                fda_info = info
                break
        
        if fda_info:
            expected_manu = fda_info['manufacturer']
            if vax_manu != expected_manu and expected_manu:
                mismatches.append({
                    'vaccine': vax_name,
                    'vaers_manu': vax_manu,
                    'fda_manu': expected_manu,
                    'count': count
                })
                status = "✗ MISMATCH"
            else:
                status = "✓"
        else:
            status = "? (not in FDA)"
        
        print(f"  {status} {vax_name} | {vax_manu}: {count:,} reports")
    
    if mismatches:
        print("\n⚠️  Manufacturer mismatches found:")
        for m in mismatches:
            print(f"    {m['vaccine']}: VAERS has '{m['vaers_manu']}', FDA has '{m['fda_manu']}' ({m['count']} reports)")
    
    # Summary
    print("\n" + "="*60)
    if unmatched_vaccines:
        print(f"⚠️  WARNING: {len(unmatched_vaccines)} vaccines in VAERS don't match FDA list")
    else:
        print("✓ All vaccines in VAERS subset match FDA list!")
    
    if mismatches:
        print(f"⚠️  WARNING: {len(mismatches)} manufacturer mismatches found")
    else:
        print("✓ All manufacturer names match between VAERS and FDA!")

if __name__ == "__main__":
    verify_vaccine_matching()