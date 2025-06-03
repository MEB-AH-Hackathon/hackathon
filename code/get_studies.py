import requests

nct_id = "NCT03655694"
url = f"https://clinicaltrials.gov/api/query/study_fields?expr={nct_id}&fields=LargeDocFilename&fmt=json"

response = requests.get(url)
data = response.json()

# Check if LargeDocFilename is present
doc_info = data['StudyFieldsResponse']['StudyFields'][0].get('LargeDocFilename', [])
if doc_info:
    print(f"Document available: {doc_info[0]}")
else:
    print("No document available for this study.")
