import os
import json
import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, List, Union
import re
from collections import defaultdict


class VAERSParser:
    def __init__(self, data_folder: Union[str, Path]):
        self.data_folder = Path(data_folder)
        if not self.data_folder.exists():
            raise ValueError(f"Data folder not found: {self.data_folder}")

    def find_vaers_files(self) -> Dict[int, Dict[str, Path]]:
        """Find VAERS files grouped by year, only keeping complete sets"""
        all_files = list(self.data_folder.glob("*VAERS*.csv"))
        
        # Group files by year
        years = {}
        for file_path in all_files:
            # Extract year from filename
            year_match = re.search(r'(\d{4})', file_path.name)
            if not year_match:
                continue
            year = int(year_match.group(1))
            
            if year not in years:
                years[year] = {}
            
            # Categorize file type
            if 'VAERSDATA' in file_path.name:
                years[year]['data'] = file_path
            elif 'VAERSVAX' in file_path.name:
                years[year]['vax'] = file_path
            elif 'VAERSSYMPTOMS' in file_path.name:
                years[year]['symptoms'] = file_path
        
        # Only keep years with complete sets (data, vax, symptoms)
        complete_years = {}
        for year, files in years.items():
            if all(key in files for key in ['data', 'vax', 'symptoms']):
                complete_years[year] = files
                print(f"Year {year}: Complete set found")
                for file_type, file_path in files.items():
                    print(f"  {file_type}: {file_path.name}")
            else:
                missing = [key for key in ['data', 'vax', 'symptoms'] if key not in files]
                print(f"Year {year}: Incomplete set, missing: {missing}")
        
        return complete_years

    def load_vaers_data_with_duckdb(self, complete_years: Dict[int, Dict[str, Path]]) -> duckdb.DuckDBPyConnection:
        """Load VAERS data using DuckDB"""
        conn = duckdb.connect(':memory:')
        
        for year, files in complete_years.items():
            print(f"Loading {year} data into DuckDB...")
            
            # Load each file type for this year
            for file_type, file_path in files.items():
                table_name = f"{file_type}_{year}"
                try:
                    # Try different encodings
                    for encoding in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            conn.execute(f"""
                                CREATE TABLE {table_name} AS 
                                SELECT *, '{file_path.name}' as source_file
                                FROM read_csv_auto('{file_path}', encoding='{encoding}', ignore_errors=true)
                            """)
                            print(f"  {file_type}: {conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]} records")
                            break
                        except Exception as e:
                            if encoding == 'cp1252':  # Last encoding
                                print(f"  Error loading {file_path}: {e}")
                            continue
                except Exception as e:
                    print(f"  Failed to load {file_path}: {e}")
        
        return conn

    def transform_symptoms_wide_to_long(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Transform symptoms from wide format to long format using DuckDB"""
        print("Transforming symptoms from wide to long format...")
        
        # Get all symptoms tables
        tables = conn.execute("SHOW TABLES").fetchall()
        symptoms_tables = [table[0] for table in tables if table[0].startswith('symptoms_')]
        
        if not symptoms_tables:
            print("No symptoms tables found")
            return
        
        # Create unified long symptoms table
        conn.execute("DROP TABLE IF EXISTS symptoms_long")
        
        union_queries = []
        for table_name in symptoms_tables:
            # Create UNPIVOT query for each symptoms table
            query = f"""
            SELECT 
                VAERS_ID,
                symptom_num,
                SYMPTOM,
                source_file
            FROM (
                SELECT 
                    VAERS_ID,
                    source_file,
                    1 as symptom_num, SYMPTOM1 as SYMPTOM FROM {table_name} WHERE SYMPTOM1 IS NOT NULL AND SYMPTOM1 != ''
                UNION ALL
                SELECT 
                    VAERS_ID,
                    source_file,
                    2 as symptom_num, SYMPTOM2 as SYMPTOM FROM {table_name} WHERE SYMPTOM2 IS NOT NULL AND SYMPTOM2 != ''
                UNION ALL
                SELECT 
                    VAERS_ID,
                    source_file,
                    3 as symptom_num, SYMPTOM3 as SYMPTOM FROM {table_name} WHERE SYMPTOM3 IS NOT NULL AND SYMPTOM3 != ''
                UNION ALL
                SELECT 
                    VAERS_ID,
                    source_file,
                    4 as symptom_num, SYMPTOM4 as SYMPTOM FROM {table_name} WHERE SYMPTOM4 IS NOT NULL AND SYMPTOM4 != ''
                UNION ALL
                SELECT 
                    VAERS_ID,
                    source_file,
                    5 as symptom_num, SYMPTOM5 as SYMPTOM FROM {table_name} WHERE SYMPTOM5 IS NOT NULL AND SYMPTOM5 != ''
            )
            """
            union_queries.append(f"({query})")
        
        # Combine all years
        final_query = f"""
        CREATE TABLE symptoms_long AS
        SELECT VAERS_ID, SYMPTOM, COUNT(*) as symptom_count, source_file
        FROM (
            {' UNION ALL '.join(union_queries)}
        )
        GROUP BY VAERS_ID, SYMPTOM, source_file
        """
        
        conn.execute(final_query)
        
        count = conn.execute("SELECT COUNT(*) FROM symptoms_long").fetchone()[0]
        unique_symptoms = conn.execute("SELECT COUNT(DISTINCT SYMPTOM) FROM symptoms_long").fetchone()[0]
        print(f"Created {count} symptom records with {unique_symptoms} unique symptoms")


    def create_final_merged_table(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Create final merged table with all VAERS data"""
        print("Creating final merged dataset...")
        
        # Get all table names
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        # Find data and vax tables
        data_tables = [t for t in table_names if t.startswith('data_')]
        vax_tables = [t for t in table_names if t.startswith('vax_')]
        
        # Union all data tables
        if data_tables:
            data_union = ' UNION ALL '.join([f'SELECT * FROM {t}' for t in data_tables])
            conn.execute(f"CREATE TABLE all_data AS ({data_union})")
        
        # Union all vax tables  
        if vax_tables:
            vax_union = ' UNION ALL '.join([f'SELECT * FROM {t}' for t in vax_tables])
            conn.execute(f"CREATE TABLE all_vax AS ({vax_union})")
        
        # Create final merged table with symptoms as rows, not columns
        merge_query = """
        CREATE TABLE final_merged AS
        SELECT 
            v.VAERS_ID,
            v.VAX_TYPE, v.VAX_MANU, v.VAX_LOT, v.VAX_DOSE_SERIES, 
            v.VAX_ROUTE, v.VAX_SITE, v.VAX_NAME, v.ORDER as VAX_ORDER,
            d.RECVDATE, d.STATE, d.AGE_YRS, d.SEX, d.SYMPTOM_TEXT,
            d.DIED, d.L_THREAT, d.ER_VISIT, d.HOSPITAL, d.DISABLE,
            d.OTHER_MEDS, d.CUR_ILL, d.HISTORY,
            s.SYMPTOM, s.symptom_count
        FROM all_vax v
        LEFT JOIN all_data d ON v.VAERS_ID = d.VAERS_ID
        LEFT JOIN symptoms_long s ON v.VAERS_ID = s.VAERS_ID
        """
        
        conn.execute(merge_query)
        
        count = conn.execute("SELECT COUNT(*) FROM final_merged").fetchone()[0]
        print(f"Final merged table created with {count} records (including symptom rows)")

    def export_to_duckdb(self, conn: duckdb.DuckDBPyConnection, output_file: str = "../intermediate_results/vaers_database.duckdb"):
        """Export merged data to DuckDB database file"""
        print("Exporting data to DuckDB database...")
        
        # Get summary statistics
        summary_stats = conn.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT VAERS_ID) as unique_vaers_ids,
            COUNT(DISTINCT VAX_NAME) as unique_vaccines
        FROM final_merged
        """).fetchone()
        
        # Create persistent database
        persistent_conn = duckdb.connect(output_file)
        
        # Copy all tables to the persistent database
        tables_to_copy = ['final_merged', 'symptoms_long', 'all_data', 'all_vax']
        
        for table in tables_to_copy:
            try:
                # Check if table exists in memory database
                result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if result[0] > 0:
                    # Export table to persistent database
                    df = conn.execute(f"SELECT * FROM {table}").fetchdf()
                    persistent_conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
                    print(f"  Exported {table}: {len(df)} records")
            except Exception as e:
                print(f"  Skipped {table}: {e}")
        
        # Create summary table
        summary_data = pd.DataFrame([{
            "total_records": int(summary_stats[0]),
            "unique_vaers_ids": int(summary_stats[1]),
            "unique_vaccines": int(summary_stats[2]),
            "processing_date": str(pd.Timestamp.now())
        }])
        persistent_conn.execute("CREATE TABLE processing_summary AS SELECT * FROM summary_data")
        
        persistent_conn.close()
        
        summary = {
            "total_records": int(summary_stats[0]),
            "unique_vaers_ids": int(summary_stats[1]),
            "unique_vaccines": int(summary_stats[2]),
            "processing_date": str(pd.Timestamp.now())
        }
        
        print(f"Database exported to: {output_file}")
        print(f"Summary: {summary}")
        
        return output_file

    def process_all_vaers_data(self, output_file: str = "../intermediate_results/vaers_database.duckdb"):
        """Complete processing pipeline using DuckDB"""
        conn = None
        try:
            # Find complete year sets
            complete_years = self.find_vaers_files()
            
            if not complete_years:
                raise ValueError("No complete VAERS year sets found in data folder")
            
            # Load data into DuckDB
            conn = self.load_vaers_data_with_duckdb(complete_years)
            
            # Transform symptoms to long format
            self.transform_symptoms_wide_to_long(conn)
            
            # Create final merged table
            self.create_final_merged_table(conn)
            
            # Export to DuckDB database
            output_file = self.export_to_duckdb(conn, output_file)
            
            return output_file
            
        except Exception as e:
            print(f"Error processing VAERS data: {e}")
            raise
        finally:
            if conn:
                conn.close()


def main():
    try:
        parser = VAERSParser("../vaers_data/vaers_data")
        output_file = parser.process_all_vaers_data()
        print(f"\n✓ VAERS data processing complete!")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()