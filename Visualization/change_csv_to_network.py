import pandas as pd

# Base file paths
input_base_path = r'C:\Users\USER\Downloads/'
output_base_path = r'C:\Users\USER\Downloads/'

# Loop through years 2018 to 2023
for year in range(2018, 2024):  # Loop from 2018 to 2023
    input_file = f'{input_base_path}{year}_combined_info.csv'  # Adjust input file name for each year
    output_file = f'{output_base_path}full_df_for_network_{year}_doi.csv'  # Adjust output file name for each year
    
    try:
        # Load the CSV file for the current year
        df = pd.read_csv(input_file)

        # Replace '|' with ',' in the 'ref_doi' column
        df['ref_doi'] = df['ref_doi'].str.split('|')

        # Explode the 'ref_doi' column to create a new row for each value
        df = df.explode('ref_doi')

        # Select only the 'doi' and 'ref_doi' columns
        df = df[['doi', 'ref_doi']]

        # Remove whitespace in 'ref_doi' column (leading, trailing, and internal)
        df['ref_doi'] = df['ref_doi'].apply(lambda x: str(x).strip().replace(' ', '') if isinstance(x, str) else x)

        # Replace '-' with '_' only in rows where 'ref_doi' contains '-'
        df['ref_doi'] = df['ref_doi'].apply(lambda x: x.replace('-', '_') if '-' in str(x) else x)

        # Drop rows where either 'doi' or 'ref_doi' is null
        filtered_df = df.dropna(subset=['doi', 'ref_doi'], how='any')

        # Save the filtered DataFrame to a new CSV
        filtered_df.to_csv(output_file, index=False)

        print(f"Filtered file for {year} saved to {output_file}")

    except Exception as e:
        print(f"An error occurred while processing {year}: {str(e)}")
