from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import random

# Set up Chrome options
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
# Uncomment the following line to run in headless mode
# options.add_argument("--headless")

# Initialize the WebDriver using WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Output CSV file
csv_file = "ieee_articles_metadata_complete_001.csv"

# Function to save metadata to CSV
def save_to_csv(metadata):
    metadata_values = [metadata[key] for key in metadata if key != 'Document ID']
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([metadata['Document ID']] + metadata_values)

# Initialize the CSV file with headers
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Document ID", "Publisher", "Cited-by-count", "Authors", "Public name", "Year", "Doi", "Affiliations", "Bibliography Count", "Subject Area"])

# Variables for scraping
success_count = 0
current_id = 10000

# Loop to fetch data
while success_count < 1100:
    base_url = f"https://ieeexplore.ieee.org/abstract/document/{current_id}"
    urls = {
        "affiliations": f"{base_url}/authors#authors",
        "references": f"{base_url}/references#references",
        "cited_by": f"{base_url}/citations#citations"
    }

    metadata = {"Document ID": current_id}

    try:
        # Open the base URL and wait for it to load
        driver.get(base_url)
        time.sleep(1)

        # Check for restricted access (subscription/paywall)
        if "Access to this document requires a subscription" in driver.page_source or \
           "Purchase this document" in driver.page_source:
            print(f"Document ID {current_id} requires subscription/payment, skipping...")
            continue

        # Verify if the page is valid
        if "Page Not Found" in driver.page_source or driver.title == "Page Not Found":
            print(f"Document ID {current_id} not found, skipping...")
            continue

        # Extract Publisher Information
        try:
            # Locate the main container for publisher information
            publisher_div = driver.find_element(By.CLASS_NAME, "publisher-title-tooltip")
            
            # Locate the span containing the publisher name (after the "Publisher:" span)
            publisher_name_span = publisher_div.find_element(By.XPATH, ".//span[@class='title']/following-sibling::span")
            
            # Extract the text content of the publisher name
            metadata['Publisher'] = publisher_name_span.text.strip()
        except:
            metadata['Publisher'] = "Not Found"

        # Extract Cited-by Count
        try:
            citation_element = driver.find_element(By.CLASS_NAME, "document-banner-metric-count")
            citation_count = citation_element.text.strip()
            metadata['Cited-by-count'] = int(citation_count) if citation_count.isdigit() else 0
        except:
            metadata['Cited-by-count'] = "Not Found"

        # Extract Authors
        try:
            driver.get(urls["affiliations"])
            time.sleep(1)
            author_divs = driver.find_elements(By.CLASS_NAME, "col-24-24")
            authors_list = []
            for div in author_divs:
                try:
                    author_link = div.find_element(By.TAG_NAME, "a")
                    author_name = author_link.find_element(By.TAG_NAME, "span").text.strip()
                    if author_name:
                        authors_list.append(author_name)
                except:
                    continue
            metadata["Authors"] = " / ".join(authors_list) if authors_list else "Not Found"
        except:
            metadata["Authors"] = "Not Found"

        # Extract Public Name
        try:
            journal_div = driver.find_element(By.CLASS_NAME, "stats-document-abstract-publishedIn")
            journal_name_element = journal_div.find_element(By.TAG_NAME, "a")
            metadata["Public name"] = journal_name_element.text.strip()
        except:
            metadata["Public name"] = "Not Found"

        # Extract Date (Year)
        try:
            # Try locating the element with both possible classes
            pub_date_div = None
            for class_name in ["doc-abstract-pubdate", "doc-abstract-confdate"]:
                try:
                    pub_date_div = driver.find_element(By.CLASS_NAME, class_name)
                    break  # Stop if the element is found
                except:
                    continue  # Try the next class if the element isn't found

            if pub_date_div:
                pub_date_text = pub_date_div.text.strip()
                print(f"Extracted text: {pub_date_text}")  # Debugging output

                # Extract the first 4-digit year
                if ":" in pub_date_text:
                    date_part = pub_date_text.split(":", 1)[1].strip()
                    years = [word for word in date_part.split() if word.isdigit() and len(word) == 4]
                    metadata["Year"] = years[0] if years else "Not Found"
                else:
                    metadata["Year"] = "Not Found"
            else:
                metadata["Year"] = "Not Found"
        except Exception as e:
            print(f"Error extracting year: {e}")
            metadata["Year"] = "Not Found"

        # Extract DOI
        try:
            doi_div = driver.find_element(By.CLASS_NAME, "stats-document-abstract-doi")
            doi_link = doi_div.find_element(By.TAG_NAME, "a")
            metadata["Doi"] = doi_link.text.strip()
        except:
            metadata["Doi"] = "Not Found"

        # Extract Affiliations
        try:
            driver.get(urls["affiliations"])
            time.sleep(1)
            affiliation_divs = driver.find_elements(By.CLASS_NAME, "col-24-24")
            authors_and_affiliations = []
            for div in affiliation_divs:
                try:
                    affiliation_elem = div.find_elements(By.TAG_NAME, "div")[-1]
                    if affiliation_elem:
                        affiliation = affiliation_elem.text.strip()
                        if affiliation:
                            authors_and_affiliations.append(affiliation)
                except:
                    continue
            metadata["Affiliations"] = " / ".join(authors_and_affiliations) if authors_and_affiliations else "Not Found"
        except:
            metadata["Affiliations"] = "Not Found"

        # Extract References Count
        try:
            driver.get(urls["references"])
            time.sleep(1)
            references = driver.find_elements(By.CLASS_NAME, "reference-container")
            metadata['Bibliography Count'] = len(references)
        except:
            metadata['Bibliography Count'] = "Not Found"

        # Add Subject Area
        metadata['Subject Area'] = 'ENG'

        # Save the metadata to CSV
        save_to_csv(metadata)
        success_count += 1
        print(f"Successfully extracted data for Document ID {current_id}")

    except Exception as e:
        print(f"Error processing Document ID {current_id}: {e}")

    finally:
        # Increment the Document ID regardless of success or error
        current_id += 1

# Close the Selenium WebDriver
driver.quit()
print(f"Metadata extraction completed. Total successful extractions: {success_count}")
