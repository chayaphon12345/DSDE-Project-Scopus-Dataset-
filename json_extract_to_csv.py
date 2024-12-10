
import os
import pandas as pd
import json
def extract_combined_info(data):
    """
    Extract funding, reference, affiliation, core data, subject areas, and additional fields from JSON data.

    Args:
        data (dict): JSON data parsed into a Python dictionary.

    Returns:
        dict: A dictionary with the extracted fields.
    """
    extracted = {
        "doi": None,
        "title": None,
        "cover_date": None,
        "subject_areas": None,
        "src_type": None,
        "publication_name": None,
        "publisher": None,
        "author": None,
        "affil_name": None,
        "affil_city": None,
        "affil_country": None,
        "citedby_count": None,
        "ref_count": None,
        "ref_doi": None,
        "ref_fid": None,
        "ref_sgr": None,
        "ref_title": None,
        "ref_author": None,
        "open_access": None,
        "funding_agency": None,
        "funding_country": None,
    }

    try:
        extracted["doi"] = data["abstracts-retrieval-response"]["coredata"]["prism:doi"]
    except:
        pass

    try:
        extracted["title"] = data["abstracts-retrieval-response"]["coredata"]["dc:title"]
    except:
        pass

    try:
        extracted["cover_date"] = data["abstracts-retrieval-response"]["coredata"]["prism:coverDate"]
    except:
        pass

    try:
        subject_areas = data["abstracts-retrieval-response"]["subject-areas"]["subject-area"]
        subject_list = []

        for subject in subject_areas:
            try:
                subject_list.append(subject["@abbrev"])
            except:
                pass

        extracted["subject_areas"] = "|".join(subject_list)
    except:
        pass

    try:
        extracted["src_type"] = data["abstracts-retrieval-response"]["coredata"]["srctype"]
    except:
        pass    

    try:
        extracted["publication_name"] = data["abstracts-retrieval-response"]["coredata"]["prism:publicationName"]
    except:
        pass

    try:
        extracted["publisher"] = data["abstracts-retrieval-response"]["coredata"]["dc:publisher"]
    except:
        pass

    try:
        authors = data["abstracts-retrieval-response"]["authors"]["author"]
        author_list = []

        for author in authors:
            try:
                author_list.append(author["ce:indexed-name"])
            except:
                pass

        extracted["author"] = "|".join(author_list)
    except:
        pass

    try:
        affiliations = data["abstracts-retrieval-response"]["affiliation"]
        affil_name_list = []
        affil_city_list = []
        affil_country_list = []

        for affil in affiliations:
            try:
                affil_name_list.append(affil["affilname"])
            except:
                pass

            try:
                affil_city_list.append(affil["affiliation-city"])
            except:
                pass

            try:
                affil_country_list.append(affil["affiliation-country"])
            except:
                pass

        extracted["affil_name"] = "|".join(affil_name_list)
        extracted["affil_city"] = "|".join(affil_city_list)
        extracted["affil_country"] = "|".join(affil_country_list)
    except:
        pass

    try:
        extracted["citedby_count"] = data["abstracts-retrieval-response"]["coredata"]["citedby-count"]
    except:
        pass

    try:
        extracted["ref_count"] = data["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"]["bibliography"]["@refcount"]
    except:
        pass

    try:
        references = data["abstracts-retrieval-response"]["item"]["bibrecord"]["tail"]["bibliography"]["reference"]
        ref_doi_list = []
        ref_fid_list = []
        ref_sgr_list = []
        ref_title_list = []
        ref_author_list = []


        for ref in references:
            try:
                ref_item = ref["ref-info"]["refd-itemidlist"]["itemid"]
                for id in ref_item:
                    if id["@idtype"] == "DOI":
                        ref_doi_list.append(id["$"])
                    elif id["@idtype"] == "FRAGMENTID":
                        ref_fid_list.append(id["$"])
                    elif id["@idtype"] == "SGR":
                        ref_sgr_list.append(id["$"])
            except:
                pass

            try:
                ref_title_list.append(ref["ref-info"]["ref-title"]["ref-titletext"])
            except:
                pass

            try:
                authors = ref["ref-info"]["ref-authors"]["author"]
                for author in authors:
                    ref_author_list.append(author["ce:indexed-name"])
            except:
                pass

        extracted["ref_doi"] = "|".join(ref_doi_list)
        extracted["ref_fid"] = "|".join(ref_fid_list)
        extracted["ref_sgr"] = "|".join(ref_sgr_list)
        extracted["ref_title"] = "|".join(ref_title_list)
        extracted["ref_author"] = "|".join(ref_author_list)
    except:
        pass

    try:
        extracted["open_access"] = data["abstracts-retrieval-response"]["coredata"]["openaccessFlag"]
    except:
        pass

    try:
        funding_list = data["abstracts-retrieval-response"]["item"]["xocs:meta"]["xocs:funding-list"]["xocs:funding"]
        funding_name_list = []
        funding_country_list = []

        for funding in funding_list:
            try:
                funding_name_list.append(funding["xocs:funding-agency-matched-string"])
            except:
                pass

            try:
                funding_country_list.append(funding["xocs:funding-agency-country"].split('/')[-2])
            except:
                pass

        extracted["funding_agency"] = "|".join(funding_name_list)
        extracted["funding_country"] = "|".join(funding_country_list)
    except:
        pass

    return extracted

def process_files(base_folder, years, output_folder):
    """
    Process files for each year, extract funding, reference, affiliation, core data, subject areas, and additional fields, and save to CSV.

    Args:
        base_folder (str): Path to the base folder containing year subfolders.
        years (list): List of years to loop through (e.g., [2018, 2019, ..., 2023]).
        output_folder (str): Path to the folder where output CSV files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for year in years:
        year_folder = os.path.join(base_folder, str(year))
        if not os.path.exists(year_folder):
            print(f"Folder {year_folder} does not exist. Skipping.")
            continue

        rows = []

        for root, _, files in os.walk(year_folder):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    combined_info = extract_combined_info(data)
                    rows.append(combined_info)

                except json.JSONDecodeError:
                    print(f"Skipping {file_path}: Not valid JSON content.")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        if rows:
            df = pd.DataFrame(rows)
            output_csv_path = os.path.join(output_folder, f"{year}_combined_info.csv")
            df.to_csv(output_csv_path, index=False, encoding='utf-8')
            print(f"Processed files for {year} into {output_csv_path}")
        else:
            print(f"No valid data found for {year}")


base_folder = r"C:\Users\USER\Downloads\Data 2018-2023\Project"
output_folder = r"C:\Users\USER\Documents\Python\dsde_project"
years = list(range(2018, 2024))  

process_files(base_folder, years, output_folder)

