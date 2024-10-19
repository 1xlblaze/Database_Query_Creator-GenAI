import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from google.cloud import storage
import os
import tempfile

# Function to upload a file to Google Cloud Storage
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    return f"gs://{bucket_name}/{destination_blob_name}"

# Function to initialize and generate SQL
def generate_sql(schema_pdf_uri, query_text):
    try:
        # Initialize Vertex AI
        vertexai.init(project="hackathon-pluto-ai", location="asia-south1")
        model = GenerativeModel("gemini-1.5-flash-002")

        # Load the schema document (document1) from GCS URI
        document1 = Part.from_uri(mime_type="application/pdf", uri=schema_pdf_uri)
        
        # Use the provided query input text
        input_text = query_text
        
        # Define document2 with static sample queries
        # document2 = Part.from_uri(
        #     mime_type="application/pdf",
        #     uri="gs://pluto-ai-hackathon-data/db-query-helper/Sample Schema For Automated Query Creator - Sample Queries.pdf",
        # )
        
        # Configuration for generating content
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        }
        prompt = f"""
        Context:
        You are an expert SQL query generation assistant. The schema {schema_pdf_uri} provided defines tables with various relationships, including primary and foreign keys.

        Instruction:
        Based on the schema, generate a SQL query for the following task:
        Task: {query_text}
        Ensure the query is correct and optimized.
        
        """
        # Safety settings
        safety_settings = [
            SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF),
            SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
            SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=SafetySetting.HarmBlockThreshold.OFF),
            SafetySetting(category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF),
        ]
           

        # Generate content from the model
        response = model.generate_content(
            [document1, prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False,
        )

        # Access the text from the response directly (no iteration)
        return response.text
    
    except Exception as e:
        return f"Error occurred: {e}"

# Streamlit GUI
st.title('SQL Query Generator')

# File upload for schema (document1)
schema_pdf = st.file_uploader("Upload Schema PDF (Document 1)", type=["pdf"])

# Query input
query_text = st.text_area("Enter Query Instruction")

# Generate button
if st.button("Generate SQL"):
    if schema_pdf and query_text:
        # Save the uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(schema_pdf.read())
            schema_pdf_path = tmp_file.name

        # Define your GCS bucket and file path
        gcs_bucket_name = "pluto-ai-hackathon-data"  # Replace with your bucket name
        gcs_blob_name = f"schemas/{os.path.basename(schema_pdf_path)}"

        # Upload the file to GCS
        schema_pdf_uri = upload_to_gcs(gcs_bucket_name, schema_pdf_path, gcs_blob_name)
        st.write(f"Schema uploaded to: {schema_pdf_uri}")

        # Generate SQL using the uploaded schema and query text
        result = generate_sql(schema_pdf_uri, query_text)
        
        # Display the generated SQL output
        st.text_area("Generated SQL Output", value=result, height=200)
    else:
        st.error("Please upload a schema PDF and enter query instructions.")