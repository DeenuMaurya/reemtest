import os

from dotenv import load_dotenv

from openai import OpenAI
from pinecone import Pinecone

from prompt import build_prompt

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


def ask_patient(question):

    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )

    query_vector = query_embedding.data[0].embedding

    results = index.query(
        vector=query_vector,
        top_k=2,
        include_metadata=True
    )

    matches = results["matches"]

    if not matches:
        return "I am not sure doctor."

    context = "\n".join(
        [
            match["metadata"]["text"]
            for match in matches
        ]
    )

    prompt = build_prompt(
        context,
        question
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content