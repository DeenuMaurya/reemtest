import os
import boto3

from dotenv import load_dotenv

from openai import OpenAI
from pinecone import Pinecone

from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Pinecone
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index("ai-patient-data-v2")

# AWS S3
BUCKET = "medical-patient"

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Download PDF from S3
local_file = "CKD.pdf"

s3.download_file(
    BUCKET,
    "CKD.pdf",
    local_file
)

# Read PDF
loader = PyPDFLoader(local_file)

docs = loader.load()

# Upload vectors
for doc in docs:

    text = doc.page_content

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    vector = embedding.data[0].embedding

    index.upsert(
        vectors=[
            {
                "id": f"ckd_{hash(text)}",
                "values": vector,
                "metadata": {
                    "text": text
                }
            }
        ]
    )

print("CKD PDF uploaded successfully")