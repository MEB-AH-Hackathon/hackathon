import json
from pathlib import Path

def normalize(s):
    return s.lower().strip().replace("\\", "/")

# File paths
vaers_path = Path("../json_data/vaers_subset.json")
fda_path = Path("../json_data/fda_reports_cleaned.json")

# Hardcoded pairs that SHOULD match (from your verified overlap list)
expected_matches = {
    ("DENGUE TETRAVALENT (DENGVAXIA)", "SANOFI PASTEUR"),
    ("DTAP (DAPTACEL)", "SANOFI PASTEUR"),
    ("DTAP (INFANRIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("DTAP + HEPB + IPV (PEDIARIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("DTAP + IPV (KINRIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("DTAP + IPV (QUADRACEL)", "SANOFI PASTEUR"),
    ("DTAP + IPV + HIB (PENTACEL)", "SANOFI PASTEUR"),
    ("DTAP+IPV+HIB+HEPB (VAXELIS)", "MSP VACCINE COMPANY"),
    ("HEP A (HAVRIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("HPV (GARDASIL)", "MERCK & CO. INC."),
    ("JAPANESE ENCEPHALITIS (IXIARO)", "VALNEVA USA, INC."),
    ("ROTAVIRUS (ROTARIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("TD ADSORBED (TDVAX)", "MASS. PUB HLTH BIOL LAB"),
    ("TDAP (ADACEL)", "SANOFI PASTEUR"),
    ("TICK-BORNE ENCEPH (TICOVAC)", "PFIZER/WYETH"),
    ("TYPHOID VI POLYSACCHARIDE (TYPHIM VI)", "SANOFI PASTEUR"),
    ("YELLOW FEVER (YF-VAX)", "SANOFI PASTEUR"),
    ("ZOSTER (SHINGRIX)", "GLAXOSMITHKLINE BIOLOGICALS"),
    ("ZOSTER LIVE (ZOSTAVAX)", "MERCK & CO. INC.")
}

# Normalize the expected pairs for comparison
expected_normalized = {(normalize(v), normalize(m)) for v, m in expected_matches}

# Load VAERS pairs
vaers_norm_set = set()
with vaers_path.open("r", encoding="utf-8") as f:
    for row in json.load(f):
        vax = row.get("VAX_NAME_list", [])
        manu = row.get("VAX_MANU_list", [])
        if len(vax) == 1 and len(manu) == 1:
            vaers_norm_set.add((normalize(vax[0]), normalize(manu[0])))

# Load FDA pairs
fda_norm_set = set()
with fda_path.open("r", encoding="utf-8") as f:
    for row in json.load(f):
        name = row.get("vax_name")
        manu = row.get("vax_manu")
        if name and manu:
            fda_norm_set.add((normalize(name), normalize(manu)))

# Check if expected matches are missing from the intersection
print("\n=== Expected Matches NOT Found ===")
missing = expected_normalized - (vaers_norm_set & fda_norm_set)
for name, manu in sorted(missing):
    print(f"{name} | {manu}")
