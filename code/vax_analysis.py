#!/usr/bin/env python3
import pandas as pd
import os
from fuzzywuzzy import fuzz, process

def get_unique_vax_combinations(file_path):
    """
    Get all unique combinations of VAX_TYPE, VAX_MANU, VAX_NAME from a VAERS CSV file.
    
    Args:
        file_path (str): Path to the VAERS VAX CSV file
        
    Returns:
        DataFrame: Unique combinations of VAX_TYPE, VAX_MANU, VAX_NAME or None if error.
    """
    encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            print(f"Trying to read VAERS data with {encoding} encoding...")
            df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip',
                             usecols=['VAX_TYPE', 'VAX_MANU', 'VAX_NAME'], low_memory=False)
            unique_combinations = df[['VAX_TYPE', 'VAX_MANU', 'VAX_NAME']].drop_duplicates().reset_index(drop=True)
            print(f"Successfully read VAERS data with {encoding} encoding.")
            return unique_combinations
        except Exception as e:
            print(f"Error reading VAERS data with {encoding} encoding: {str(e)}")
    print("Could not read the VAERS data file with any of the attempted encodings.")
    return None

def add_fda_matching_file(input_csv_path, fda_dir_path, output_csv_path, cutoff_score=40):
    """
    Adds a column with the closest matching FDA document filename to the input CSV.
    Args:
        input_csv_path (str): Path to the input CSV file (e.g., unique_vax_combinations.csv).
        fda_dir_path (str): Path to the directory containing FDA PDF documents.
        output_csv_path (str): Path to save the updated CSV file.
        cutoff_score (int): Minimum score threshold for considering a match valid.
    """
    try:
        df = pd.read_csv(input_csv_path)
        print(f"\nSuccessfully read {input_csv_path}")
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {input_csv_path}")
        return

    try:
        fda_files = [f for f in os.listdir(fda_dir_path) 
                       if os.path.isfile(os.path.join(fda_dir_path, f)) and f.lower().endswith('.pdf')]
        print(f"Found {len(fda_files)} PDF files in {fda_dir_path}")
    except FileNotFoundError:
        print(f"Error: FDA directory not found at {fda_dir_path}")
        return

    if not fda_files:
        print(f"No PDF files found in {fda_dir_path}. Adding empty FDA_MATCHING_FILE column.")
        df['FDA_MATCHING_FILE'] = None
        df.to_csv(output_csv_path, index=False)
        print(f"Output saved to {output_csv_path}")
        return

    # Prepare to log match scores
    log_dir = os.path.dirname(output_csv_path)
    log_path = os.path.join(log_dir, "vaccine_match_scores.log")
    with open(log_path, 'w') as log_file:
        log_file.write(f"VACCINE MATCHING SCORES (Cutoff = {cutoff_score})\n")
        log_file.write("-" * 80 + "\n\n")
        
        matches = []
        scores = []
        matched_count = 0
        
        print("Matching vaccine combinations to FDA document filenames...")
        for index, row in df.iterrows():
            vax_type = str(row['VAX_TYPE']) if pd.notna(row['VAX_TYPE']) else ""
            vax_manu = str(row['VAX_MANU']) if pd.notna(row['VAX_MANU']) else ""
            vax_name = str(row['VAX_NAME']) if pd.notna(row['VAX_NAME']) else ""
            
            vax_manu_cleaned = vax_manu.replace('\\', ' ').replace('/', ' ')
            
            search_string = f"{vax_type} {vax_manu_cleaned} {vax_name}".strip().lower()
            search_string_simple = f"{vax_manu_cleaned} {vax_name}".strip().lower()

            # First, try with the cutoff to get a match that meets our threshold
            best_match_with_cutoff = process.extractOne(search_string, fda_files, 
                                                    scorer=fuzz.token_set_ratio, 
                                                    score_cutoff=cutoff_score)
            
            if not best_match_with_cutoff:
                best_match_with_cutoff = process.extractOne(search_string_simple, fda_files, 
                                                        scorer=fuzz.token_set_ratio, 
                                                        score_cutoff=cutoff_score)
            
            # Now get the actual best match regardless of cutoff for logging
            best_match_no_cutoff = process.extractOne(search_string, fda_files, 
                                                   scorer=fuzz.token_set_ratio)
            
            if not best_match_no_cutoff or (best_match_with_cutoff and best_match_with_cutoff[1] > best_match_no_cutoff[1]):
                best_match_no_cutoff = best_match_with_cutoff
            
            # Determine if we have a valid match to save to CSV
            if best_match_with_cutoff:
                match_file = best_match_with_cutoff[0]
                match_score = best_match_with_cutoff[1]
                matched_count += 1
                log_file.write(f"✓ [{match_score}] {vax_type} | {vax_manu} | {vax_name}\n")
                log_file.write(f"  └─ MATCHED: {match_file}\n\n")
            else:
                match_file = None
                match_score = best_match_no_cutoff[1] if best_match_no_cutoff else 0
                best_file = best_match_no_cutoff[0] if best_match_no_cutoff else "None"
                log_file.write(f"✗ [{match_score}] {vax_type} | {vax_manu} | {vax_name}\n")
                log_file.write(f"  └─ BEST MATCH (below cutoff): {best_file}\n\n")
            
            matches.append(match_file)
            scores.append(match_score)
        
        # Add summary to log
        log_file.write("\n" + "-" * 80 + "\n")
        log_file.write(f"SUMMARY:\n")
        log_file.write(f"Total vaccine combinations: {len(df)}\n")
        log_file.write(f"Matched with score >= {cutoff_score}: {matched_count} ({matched_count/len(df)*100:.1f}%)\n")
        log_file.write(f"Unmatched (below cutoff): {len(df) - matched_count} ({(len(df) - matched_count)/len(df)*100:.1f}%)\n")
        
        # Calculate and log score distribution
        score_bins = [0, 20, 40, 50, 60, 70, 80, 90, 100]
        bin_counts = [sum(1 for s in scores if low <= s < high) for low, high in zip(score_bins, score_bins[1:] + [101])]
        
        log_file.write("\nScore distribution:\n")
        for i, (low, high) in enumerate(zip(score_bins, score_bins[1:] + [101])):
            log_file.write(f"  {low}-{high-1}: {bin_counts[i]} items\n")
    
    # Add the matching files to the dataframe
    df['FDA_MATCHING_FILE'] = matches
    df['MATCH_SCORE'] = scores
    df.to_csv(output_csv_path, index=False)
    
    print(f"\nFDA matching files added. Results saved to {output_csv_path}")
    print(f"Match score details saved to {log_path}")
    print(f"Matched {matched_count} out of {len(df)} entries ({matched_count/len(df)*100:.1f}%) with score >= {cutoff_score}")
    
    return matched_count, len(df)

if __name__ == "__main__":
    vaers_csv_path = "/Users/nicholaswagner/Downloads/2025VAERSData/2025VAERSVAX.csv"
    # Output path for unique combinations, now in the project's data directory
    project_data_dir = "/Users/nicholaswagner/Projects/hackathon/data"
    unique_combos_csv_path = os.path.join(project_data_dir, "unique_vax_combinations.csv")
    fda_docs_dir_path = os.path.join(project_data_dir, "fda_vaccine_info")

    # Ensure the project data directory exists
    os.makedirs(project_data_dir, exist_ok=True)

    try:
        print("Step 1: Generating unique vaccine combinations...")
        unique_vax_combos_df = get_unique_vax_combinations(vaers_csv_path)
        
        if unique_vax_combos_df is not None:
            print(f"\nFound {len(unique_vax_combos_df)} unique VAX_TYPE, VAX_MANU, VAX_NAME combinations.")
            unique_vax_combos_df.to_csv(unique_combos_csv_path, index=False)
            print(f"Unique combinations saved to {unique_combos_csv_path}")
            
            print("\nStep 2: Adding FDA matching file information...")
            add_fda_matching_file(unique_combos_csv_path, fda_docs_dir_path, unique_combos_csv_path)
        else:
            print("Skipping FDA matching step due to error in generating unique combinations.")
            
    except Exception as e:
        print(f"An overall error occurred in the script: {str(e)}")
