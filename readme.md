# Coding Assignment for Abstrakt Marketing Group

#### Brief:
Create a FastAPI app with an embedded VueJS frontend. Upload a single column of domain names and search a Salesforce organization for up to 5 contacts whose email addresses match the domain names in the uploaded list. Compile the results into a JSON object and upload to an AWS S3 bucket.

#### Running the app:
1. Once you've pulled the project into your IDE of choice, update all variables in the project (ie. saleforce credentials, AWS credentials). Additionally, you may need to update the column names and table name in the Salesforce Org query to match your column and table names.
2. Activate python virtual environment
`source venv/Scripts/activate` 
3. Install python libraries
`pip install -r requirements.txt`
4. Run app
`uvicorn main:app --reload`
5. Upload your CSV and verfiy your results