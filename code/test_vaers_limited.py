import sys
sys.path.append('.')
from vaers_parser import VAERSParser

# Run VAERS parser with limited years for testing
parser = VAERSParser("../vaers_data/vaers_data")

# Find all year sets but limit processing
complete_years = parser.find_vaers_files()
print(f"\nFound {len(complete_years)} complete year sets")

# Process only recent 3 years for testing
limited_years = {}
for year in sorted(complete_years.keys(), reverse=True)[:3]:
    limited_years[year] = complete_years[year]

print(f"\nProcessing only {len(limited_years)} years for testing: {list(limited_years.keys())}")

# Process the limited set
conn = parser.load_vaers_data_with_duckdb(limited_years)
parser.transform_symptoms_wide_to_long(conn)
parser.create_final_merged_table(conn)
output_file = parser.export_to_duckdb(conn, "../intermediate_results/vaers_test.duckdb")

print(f"\n✓ Limited VAERS data processing complete!")
print(f"Output saved to: {output_file}")