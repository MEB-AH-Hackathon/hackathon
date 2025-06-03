#!/usr/bin/env python3
"""
Fix vaccine mappings between FDA reports and VAERS data.
Maps FDA vaccine names to their VAERS equivalents.
"""

import json
import pandas as pd
from pathlib import Path

# Define the mappings from FDA names to VAERS names
FDA_TO_VAERS_MAPPINGS = {
    # COVID vaccines
    "COVID19 (COVID19 (MNEXSPIKE))": ["COVID19 (COVID19 (MODERNA))", "COVID19 (COVID19 (MODERNA BIVALENT))"],
    
    # Zoster vaccines
    "SHINGRIX (ZOSTER VACCINE RECOMBINANT, ADJUVANTED)": ["ZOSTER (SHINGRIX)"],
    "ZOSTER VACCINE LIVE (ZOSTAVAX)": ["ZOSTER LIVE (ZOSTAVAX)"],
    "ZOSTER LIVE (ZOSTAVAX)": ["ZOSTER LIVE (ZOSTAVAX)"],
    "ZOSTER (SHINGRIX)": ["ZOSTER (SHINGRIX)"],
    
    # HPV vaccines  
    "HUMAN PAPILLOMAVIRUS QUADRIVALENT (TYPES 6, 11, 16, AND 18) VACCINE, RECOMBINANT (GARDASIL)": ["HPV (GARDASIL)"],
    "HUMAN PAPILLOMAVIRUS QUADRIVALENT (GARDASIL)": ["HPV (GARDASIL)"],
    
    # DTaP vaccines
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS (INFANRIX)": ["DTAP (INFANRIX)"],
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS VACCINE ADSORBED (DAPTACEL)": ["DTAP (DAPTACEL)"],
    
    # TDaP vaccines
    "TETANUS TOXOID, REDUCED DIPHTHERIA TOXOID AND ACELLULAR PERTUSSIS VACCINE ADSORBED (ADACEL)": ["TDAP (ADACEL)"],
    
    # Combination vaccines
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, HEPATITIS B (RECOMBINANT) AND INACTIVATED POLIOVIRUS VACCINE (PEDIARIX)": ["DTAP + HEPB + IPV (PEDIARIX)"],
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED AND INACTIVATED POLIOVIRUS VACCINE (KINRIX)": ["DTAP + IPV (KINRIX)"],
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, INACTIVATED POLIOVIRUS AND HAEMOPHILUS B CONJUGATE (TETANUS TOXOID CONJUGATE) VACCINE (PENTACEL)": ["DTAP + IPV + HIB (PENTACEL)"],
    "PENTACEL (DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, INACTIVATED POLIOVIRUS AND HAEMOPHILUS B CONJUGATE (TETANUS TOXOID CONJUGATE) VACCINE)": ["DTAP + IPV + HIB (PENTACEL)"],
    "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED AND INACTIVATED POLIOVIRUS VACCINE (QUADRACEL)": ["DTAP + IPV (QUADRACEL)"],
    "VAXELIS (DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS, INACTIVATED POLIOVIRUS, HAEMOPHILUS B CONJUGATE AND HEPATITIS B VACCINE)": ["DTAP+IPV+HIB+HEPB (VAXELIS)"],
    
    # Hepatitis A
    "HEPATITIS A (HAVRIX)": ["HEP A (HAVRIX)"],
    
    # Rotavirus
    "ROTARIX (ROTAVIRUS VACCINE, LIVE, ORAL)": ["ROTAVIRUS (ROTARIX)"],
    
    # Yellow fever
    "YELLOW FEVER (YF-VAX)": ["YELLOW FEVER (YF-VAX)"],
    
    # Typhoid
    "TYPHOID VI POLYSACCHARIDE VACCINE (TYPHIM VI)": ["TYPHOID VI POLYSACCHARIDE (TYPHIM VI)"],
    
    # BCG
    "BCG LIVE (TICE® BCG)": ["BCG (NO BRAND NAME)"],
    "BCG VACCINE (TICE® STRAIN)": ["BCG (NO BRAND NAME)"],
    
    # Adenovirus
    "ADENOVIRUS TYPE 4 AND TYPE 7 VACCINE, LIVE, ORAL": ["ADENOVIRUS TYPES 4 & 7, LIVE, ORAL (NO BRAND NAME)"],
    
    # Japanese Encephalitis
    "JAPANESE ENCEPHALITIS VACCINE, INACTIVATED, ADSORBED (IXIARO)": ["JEV (IXIARO)"],
    
    # Tetanus/Diphtheria
    "TETANUS AND DIPHTHERIA TOXOIDS ADSORBED (TDVAX)": ["TD (TDVAX)"],
    
    # Tick-borne encephalitis
    "TICOVAC (TICK-BORNE ENCEPHALITIS VACCINE)": ["TBE (TICOVAC)"],
    
    # Dengue
    "DENGUE TETRAVALENT (DENGVAXIA)": ["DENGUE (DENGVAXIA)"],
    "DENGUE (DENGVAXIA)": ["DENGUE (DENGVAXIA)"],
    
    # Anthrax
    "UNKNOWN": ["ANTHRAX (CYFENDUS)"]  # For CYFENDUS which shows as UNKNOWN in FDA
}

def main():
    # Load FDA reports
    with open('json_data/fda_reports.json', 'r') as f:
        fda_reports = json.load(f)
    
    # Load VAERS vaccine names
    with open('intermediate_results/vaers_vaccine_names.json', 'r') as f:
        vaers_data = json.load(f)
        vaers_vaccines = vaers_data['vaccine_names']
    
    # Update FDA reports with VAERS vaccine names
    updated_reports = []
    matched_count = 0
    
    for report in fda_reports:
        fda_name = report['vax_name']
        
        # Find VAERS equivalent
        vaers_names = FDA_TO_VAERS_MAPPINGS.get(fda_name, [])
        
        if vaers_names:
            # Update the report with VAERS name(s)
            report['vaers_vaccine_names'] = vaers_names
            report['vaccine_name'] = vaers_names[0]  # Primary VAERS name
            matched_count += 1
            print(f"✓ Matched: {fda_name} -> {vaers_names}")
        else:
            print(f"✗ No match found for: {fda_name}")
            report['vaers_vaccine_names'] = []
            report['vaccine_name'] = fda_name  # Keep original
        
        updated_reports.append(report)
    
    # Save updated FDA reports
    with open('json_data/fda_reports.json', 'w') as f:
        json.dump(updated_reports, f, indent=2)
    
    print(f"\nTotal vaccines: {len(fda_reports)}")
    print(f"Matched to VAERS: {matched_count}")
    
    # Create a simple mapping file for reference
    simple_mappings = []
    for report in updated_reports:
        if report.get('vaers_vaccine_names'):
            simple_mappings.append({
                'fda_name': report['vax_name'],
                'vaers_names': report['vaers_vaccine_names'],
                'manufacturer': report['vax_manu'],
                'adverse_events': report['adverse_events']
            })
    
    with open('intermediate_results/vaccine_mappings.json', 'w') as f:
        json.dump(simple_mappings, f, indent=2)
    
    print(f"\nSaved {len(simple_mappings)} vaccine mappings to intermediate_results/vaccine_mappings.json")

if __name__ == "__main__":
    main()