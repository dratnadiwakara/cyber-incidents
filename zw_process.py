from config import api_key
import os
import re
import time
from openai import OpenAI
import pandas as pd
os.environ["OPENAI_API_KEY"] = api_key

client = OpenAI()

system_prompt = (
    "You are a research assistant helping identify and summarize cyber incidents. "
    "For each incident, you will be given partial details and an approximate date it occurred. "
    "Your task is to identify the most likely first date the incident was made public, "
    "such as through news reports, regulatory disclosures, or press releases. "
    "You should also provide a one-sentence summary of the severity, based on available information "
    "(e.g., data stolen, operational impact, number of customers affected, or regulatory consequences). "
    "Be precise, factual, and cite the approximate source type (e.g., 'first reported by news', 'disclosed in SEC filing'). "
    "Output in the format:\nDate: <YYYY-MM-DD>\nSeverity: <short description>"
)

# incidents = [
#     "Issue001: Capital One data breach affecting customer accounts, occurred around March 2019",
#     "Issue002: SolarWinds supply chain attack on U.S. government systems, occurred around December 2020",
#     "Issue003: Equifax data breach exposing personal data, occurred around July 2017"
# ]

df = pd.read_csv("top100_zw_cyber_incidents.csv")
incidents = []
for _, row in df.iterrows():
    issue_id = f"MSCAD_ID_{row['MSCAD_ID']}"
    description = str(row['CASE_DESCRIPTION']).strip().replace('\n', ' ')
    date = str(row['ACCIDENT_DATE'])
    content = f"{issue_id}: {description}, occurred around {date}"
    incidents.append((issue_id, content))

output_rows = []



for issue_id, content in incidents:
    print(f"Processing: {issue_id}")
    try:
        # Extract issue ID (e.g., "Issue001")
        # Build message
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        # Call API
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0
        )

        reply = response.choices[0].message.content.strip()

        # Extract Date and Severity
        date_line = next((line for line in reply.split('\n') if line.lower().startswith('date:')), '')
        severity_line = next((line for line in reply.split('\n') if line.lower().startswith('severity:')), '')
        date = date_line.replace('Date:', '').strip()
        severity = severity_line.replace('Severity:', '').strip()

        output_rows.append({
            "issue_id": issue_id,
            "estimated_date": date,
            "estimated_severity": severity
        })

        time.sleep(1)  # to avoid hitting rate limits

    except Exception as e:
        print(f"Error processing {content}: {e}")
        output_rows.append({
            "issue_id": issue_id,
            "estimated_date": "ERROR",
            "estimated_severity": str(e)
        })