import os
import re
import json

# SETTINGS 
# Change and adjust the input_dir accordingly
input_dir = r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\ocr_textfiles"

# Final JSON output will be saved here
output_file = r"C:\Users\jonhe\OneDrive\Documents\SpotCheck\parsed_output.json"

# Adjust according to the directory being parsed through
directory_name = "Minneapolis 1900"

# UTILITY FUNCTIONS

#Removes weird quotation marks and whitespace from a line
def clean_line(line):

    return re.sub(r'[“”‘’"]', '', line).strip()

#This function fixes common OCR mistakes (like '1th' → '11th').
def normalize_text(text):
    
    replacements = {
        '\u00a2': 'c',
        'Unt- versity': 'University',
        'Uni- versity': 'University',
        '1th': '11th',
        'av n:': 'av n',
        '- ': '',
        '.': '',
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text.strip()


#Skips junk lines that are actually business names or ads
# This helps keep resident names clean of junk
def looks_like_ad(entry):
    
    bad_last_names = {"store", "goods", "co", "line", "creamery"}
    if not entry["LastName"]:
        return True
    if entry["LastName"].lower() in bad_last_names:
        return True
    return False

#  MAIN PARSING LOGIC 
# This function parses a single block of text into a structured resident entry
def parse_entry(raw_text, page_number):
    
    raw_text = normalize_text(clean_line(raw_text))

    # Template for a resident's data
    entry = {
        "FirstName": None,
        "LastName": None,
        "Spouse": None,
        "Occupation": None,
        "CompanyName": None,
        "HomeAddress": {
            "StreetNumber": None,
            "StreetName": None,
            "ApartmentOrUnit": None,
            "ResidenceIndicator": None
        },
        "WorkAddress": None,
        "Telephone": None,
        "DirectoryName": directory_name,
        "PageNumber": page_number
    }

    # Try to find a widow reference like (wid Rasmus)
    spouse_match = re.search(r'\(wid(?:ow)?\.?\s+([A-Z][a-z]+)', raw_text)
    if spouse_match:
        entry["Spouse"] = spouse_match.group(1)

    # Match names at the beginning of the line
    name_match = re.match(r'^([A-Z][a-zA-Z]+)\s+([A-Z][\w\-\.]*)', raw_text)
    if name_match:
        entry["FirstName"] = name_match.group(1)
        entry["LastName"] = name_match.group(2)

    # Skip this entry if it looks like an ad or not a real person
    if looks_like_ad(entry):
        return None

    # Try to grab occupation and possibly the company
    occ_match = re.search(r',\s*([a-zA-Z ]+?)(?:\s+[A-Z][a-zA-Z&]+.*?,)?\s+(r|b|rms)\b', raw_text)
    if occ_match:
        occupation = occ_match.group(1).strip()
        if 'see also' not in occupation.lower():
            entry["Occupation"] = occupation

        # Try to find a company name after the occupation
        # This assumes the company name follows the occupation and is separated by a comma
        company_match = re.search(rf'{occupation},\s+(.+?),\s+(r|b|rms)', raw_text)
        if company_match:
            possible_company = company_match.group(1).strip()
            if not re.search(r'\d{3,5}', possible_company):  # avoid mistaking address for company
                entry["CompanyName"] = possible_company

    # Address parsing: try to find things like "r 2103 Bryant av S"
    addr_match = re.search(r'\b(r|b|rms)\.?,?\s+(\d{3,5})\s+([^\.,\n]+)', raw_text)
    if addr_match:
        entry["HomeAddress"]["ResidenceIndicator"] = addr_match.group(1)
        entry["HomeAddress"]["StreetNumber"] = addr_match.group(2)

        # Clean up the street name
        street_name = normalize_text(addr_match.group(3))

        # Stop at likely false starts (like names, "Store", etc.)
        street_name = re.split(r'(?=\s[A-Z][a-z]+[\s:,]| [A-Z]{2,})', street_name)[0]
        entry["HomeAddress"]["StreetName"] = street_name.strip()

    return entry


# OCR LINE PROCESSING 
#Combines broken lines into full entries based on name pattern.
def load_and_stitch_lines(filepath):
    
    with open(filepath, "r", encoding="utf-8") as f:
        raw_lines = [clean_line(line) for line in f if line.strip()]

    stitched_entries = []
    buffer = ''
    for line in raw_lines:
        # Start a new entry when a line begins with a capitalized name
        if re.match(r'^["‘“]?[A-Z][a-z]+\s+[A-Z]', line):
            if buffer:
                stitched_entries.append(buffer.strip())
            buffer = line
        else:
            buffer += ' ' + line

    # If there's any remaining buffer, add it as the last entry
    if buffer:
        stitched_entries.append(buffer.strip())

    return stitched_entries

# MAIN FUNCTION TO PARSE ALL PAGES
#Goes through each page and parses all entries into structured JSON.
def parse_all_pages(input_dir):
    
    all_entries = []

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".txt"):
        
            # Try to grab the page number from the filename
            page_number = int(re.search(r"\d+", filename).group())
            filepath = os.path.join(input_dir, filename)

            stitched_lines = load_and_stitch_lines(filepath)

            for raw_entry in stitched_lines:
                parsed = parse_entry(raw_entry, page_number)

                # Only save entries with at least a name or address
                if parsed and any([
                    parsed["FirstName"],
                    parsed["LastName"],
                    parsed["HomeAddress"]["StreetNumber"]
                ]):
                    all_entries.append(parsed)

    return all_entries

# RUN SCRIPT

if __name__ == "__main__":
    final_data = parse_all_pages(input_dir)

    # Save results to JSON file
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(final_data, out, indent=2)

    print(f"Parsed and saved {len(final_data)} entries to:")
    print(output_file)
