from fastapi import FastAPI
from pydantic import BaseModel

from rag import ask_patient

app = FastAPI()


class Query(BaseModel):

    question: str


@app.post("/chat")
def chat(data: Query):

    answer = ask_patient(
        data.question
    )

    return {
        "answer": answer
    }