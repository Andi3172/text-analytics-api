from fastapi import FastAPI, Depends, Security, Response, HTTPException
from fastapi.security import APIKeyCookie
from pydantic import BaseModel
from transformers import pipeline
import os
import spacy
import torch
from starlette.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

#to run locally: uvicorn main:app --reload
#to de

app = FastAPI(
    title="Text Analytics API",
    description="API for sentiment analysis and NER. Go to /login to get your auth cookie."
)

#security cookie
API_KEY = os.getenv("API_KEY", "BASIC_API_KEY")
COOKIE_NAME = "access_token"

api_key_cookie_scheme = APIKeyCookie(name=COOKIE_NAME)

async def get_api_key(api_key: str= Security(api_key_cookie_scheme)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code = HTTP_403_FORBIDDEN,
            detail = "Cannot validate credentials"
        )



print("Loading sentiment analysis model")

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print("Sentiment analysis model loaded")

print("Loading spaCy NER model")
ner_pipeline = spacy.load("en_core_web_sm")
print("spaCy NER model loaded")

print("Loading Zero-Shot model")
zero_shot_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Zero-Shot model loaded")


class TextIn(BaseModel):
    text: str

class SentimentOut(BaseModel):
    label: str
    score: float
    
class EntityOut(BaseModel):
    text: str
    label: str

class AnalysisOut(BaseModel):
    sentiment: SentimentOut
    entities: list[EntityOut]

class LoginRequest(BaseModel):
    password: str
    
class ZeroShotRequest(BaseModel):
    text: str
    labels: list[str]

class ZeroShotScore(BaseModel):
    label: str
    score: float

class ZeroShotOut(BaseModel):
    sequence: str
    scores: list[ZeroShotScore]
    
# Api endpoints

@app.post("/login")
def login(request: LoginRequest, response: Response):
    """
    Simple login to get auth cookie.
    Use the password BASIC_API_KEY to get the cookie for this demo.
    """
    if request.password == API_KEY:
        response.set_cookie(
            key=COOKIE_NAME,
            value=API_KEY,
            httponly=True,
            max_age=1800,
            samesite="lax",
        )
        return {
            "message": "Login successful. Cookie set."
        }
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
        

@app.post("/analyze", response_model=AnalysisOut)
def analyze_text(req: TextIn, api_key: str = Depends(get_api_key)):
    #sent analysis
    sentiment_result = sentiment_pipeline(req.text)[0]
    
    #entity recognition
    doc = ner_pipeline(req.text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    
    #json response
    return{
        "sentiment": sentiment_result,
        "entities": entities
    }
    
@app.post("/classify", response_model=ZeroShotOut)
def classify_text(request: ZeroShotRequest, api_key: str = Depends(get_api_key)):
    result = zero_shot_pipeline(
        request.text,
        candidate_labels=request.labels
    )
    
    return{
        "sequence": result["sequence"],
        "scores": [
            {"label": label, "score": score}
            for label, score in zip(result["labels"], result["scores"])
        ]
    }

@app.get("/")
def root():
    return {"message": "Text Analytics API is running. Go to /docs for more."}

print("App startup complete")
    