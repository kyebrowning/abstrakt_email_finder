from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import io
import json
import boto3
from simple_salesforce import Salesforce
import os
from typing import List

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration - replace with your actual credentials
SF_USERNAME = os.getenv("SF_USERNAME", "your_salesforce_username")
SF_PASSWORD = os.getenv("SF_PASSWORD", "your_salesforce_password")
SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN", "your_salesforce_token")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "your_aws_access_key")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "your_aws_secret_key")
S3_BUCKET = "your-s3-bucket-name"

#Model structure for displaying results
class Contact(BaseModel):
    FirstName: str
    LastName: str
    Email: str
    Title: str | None

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/upload-csv/", response_model=List[Contact])
async def upload_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        if len(df.columns) != 1:
            raise HTTPException(status_code=400, detail="All emails must be in one column")

        # Initialize Salesforce connection
        sf = Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_SECURITY_TOKEN
        )

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )

        contacts = []
        for domain in df.iloc[:, 0]:
            query = f"SELECT FirstName, LastName, Email, Title FROM Contact WHERE Email LIKE '%@{domain}'"
            result = sf.query(query)
            
            for record in result['records']:
                contacts.append({
                    "FirstName": record['FirstName'] or "",
                    "LastName": record['LastName'] or "",
                    "Email": record['Email'],
                    "Title": record['Title'] or ""
                })

        json_data = json.dumps(contacts, indent=2)
        
        s3_key = f"contacts_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json_data,
            ContentType='application/json'
        )

        return contacts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))