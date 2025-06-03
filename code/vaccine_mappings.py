# Hard-coded vaccine mappings between VAERS and PDF data
# Based on actual matches between VAERS data and PDF vaccine names

VACCINE_MAPPINGS = [
    {
        "vaers_vaccine": "COVID19 (COVID19 (PFIZER-BIONTECH))",
        "pdf_vaccine": "COVID19 (COVID19 (MNEXSPIKE))",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "ZOSTER (SHINGRIX)",
        "pdf_vaccine": "SHINGRIX (ZOSTER VACCINE RECOMBINANT, ADJUVANTED)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "HPV (GARDASIL)",
        "pdf_vaccine": "HUMAN PAPILLOMAVIRUS QUADRIVALENT (TYPES 6, 11, 16, AND 18) VACCINE, RECOMBINANT (GARDASIL)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "ZOSTER LIVE (ZOSTAVAX)",
        "pdf_vaccine": "ZOSTER VACCINE LIVE (ZOSTAVAX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "TDAP (ADACEL)",
        "pdf_vaccine": "TETANUS TOXOID, REDUCED DIPHTHERIA TOXOID AND ACELLULAR PERTUSSIS VACCINE ADSORBED (ADACEL)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "HEP A (HAVRIX)",
        "pdf_vaccine": "HEPATITIS A (HAVRIX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "DTAP (INFANRIX)",
        "pdf_vaccine": "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS (INFANRIX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "ROTAVIRUS (ROTARIX)",
        "pdf_vaccine": "ROTARIX (ROTAVIRUS VACCINE, LIVE, ORAL)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "DTAP (DAPTACEL)",
        "pdf_vaccine": "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS VACCINE ADSORBED (DAPTACEL)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "DTAP + HEPB + IPV (PEDIARIX)",
        "pdf_vaccine": "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, HEPATITIS B (RECOMBINANT) AND INACTIVATED POLIOVIRUS VACCINE (PEDIARIX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "DTAP + IPV (KINRIX)",
        "pdf_vaccine": "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED AND INACTIVATED POLIOVIRUS VACCINE (KINRIX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "DTAP + IPV + HIB (PENTACEL)",
        "pdf_vaccine": "DIPHTHERIA AND TETANUS TOXOIDS AND ACELLULAR PERTUSSIS ADSORBED, INACTIVATED POLIOVIRUS AND HAEMOPHILUS B CONJUGATE (TETANUS TOXOID CONJUGATE) VACCINE (PENTACEL)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "YELLOW FEVER (YF-VAX)",
        "pdf_vaccine": "YELLOW FEVER (YF-VAX)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
    {
        "vaers_vaccine": "TYPHOID VI POLYSACCHARIDE (TYPHIM VI)",
        "pdf_vaccine": "TYPHOID VI POLYSACCHARIDE VACCINE (TYPHIM VI)",
        "confidence": 1.0,
        "match_type": "exact_brand_match"
    },
]

def get_pdf_vaccine_for_vaers(vaers_vaccine_name):
    """Get the corresponding PDF vaccine name for a VAERS vaccine"""
    for mapping in VACCINE_MAPPINGS:
        if mapping["vaers_vaccine"] == vaers_vaccine_name:
            return mapping["pdf_vaccine"]
    return None

def get_vaers_vaccine_for_pdf(pdf_vaccine_name):
    """Get the corresponding VAERS vaccine name for a PDF vaccine"""
    for mapping in VACCINE_MAPPINGS:
        if mapping["pdf_vaccine"] == pdf_vaccine_name:
            return mapping["vaers_vaccine"]
    return None

def get_all_mapped_vaers_vaccines():
    """Get all VAERS vaccine names that have PDF mappings"""
    return [mapping["vaers_vaccine"] for mapping in VACCINE_MAPPINGS]

def get_all_mapped_pdf_vaccines():
    """Get all PDF vaccine names that have VAERS mappings"""
    return [mapping["pdf_vaccine"] for mapping in VACCINE_MAPPINGS]

if __name__ == "__main__":
    print(f"Total vaccine mappings: {len(VACCINE_MAPPINGS)}")
    print("\nMapped vaccines:")
    for i, mapping in enumerate(VACCINE_MAPPINGS, 1):
        print(f"{i:2d}. {mapping['vaers_vaccine']}")
        print(f"    ↔ {mapping['pdf_vaccine']}")
        print()