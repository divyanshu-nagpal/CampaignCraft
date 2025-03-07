import os
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
from pydantic import BaseModel
import json
from prompt_templates import TAGLINE_CAMPAIGN_PROMPT

app = FastAPI(title="Marketing Tagline & Campaign Generator")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration for Open-WebUI API
WEBUI_ENABLED = True
WEBUI_BASE_URL = "https://chat.ivislabs.in/api"
API_KEY = "sk-5cbca7054e344701a3ed67e944396a35"  # Replace with the actual API key
DEFAULT_MODEL = "gemma2:2b"  # Update based on available models

# Fallback to local Ollama API if needed
OLLAMA_ENABLED = True
OLLAMA_HOST = "localhost"
OLLAMA_PORT = "11434"
OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api"

class GenerationRequest(BaseModel):
    product_name: str
    product_category: str
    target_audience: str
    product_features: str
    num_ideas: int = 3
    tone: Optional[str] = "creative"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_taglines(
    product_name: str = Form(...),
    product_category: str = Form(...),
    target_audience: str = Form(...),
    product_features: str = Form(...),
    num_ideas: int = Form(3),
    tone: str = Form("creative"),
    model: str = Form(DEFAULT_MODEL)
):
    try:
        # Build the prompt using the template
        prompt = TAGLINE_CAMPAIGN_PROMPT.format(
            product_name=product_name,
            product_category=product_category,
            target_audience=target_audience,
            product_features=product_features,
            num_ideas=num_ideas,
            tone=tone
        )
        
        # Try using the WebUI API first
        if WEBUI_ENABLED:
            try:
                messages = [{"role": "user", "content": prompt}]
                request_payload = {"model": model, "messages": messages}
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{WEBUI_BASE_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json=request_payload,
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if generated_text:
                            return {"generated_ideas": generated_text}
            except Exception as e:
                print(f"Open-WebUI API attempt failed: {str(e)}")
        
        # Fallback to Ollama API if enabled
        if OLLAMA_ENABLED:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{OLLAMA_API_URL}/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "")
                    return {"generated_ideas": generated_text}
                
        raise HTTPException(status_code=500, detail="Failed to generate content from any available LLM API")
    
    except Exception as e:
        print(f"Error generating taglines: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating taglines: {str(e)}")

@app.get("/models")
async def get_models():
    try:
        if WEBUI_ENABLED:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{WEBUI_BASE_URL}/models",
                        headers={"Authorization": f"Bearer {API_KEY}"}
                    )
                    if response.status_code == 200:
                        models_data = response.json()
                        if "data" in models_data and isinstance(models_data["data"], list):
                            model_names = [model.get("id") for model in models_data["data"] if "id" in model]
                            if model_names:
                                return {"models": model_names}
            except Exception as e:
                print(f"Error fetching models from WebUI API: {str(e)}")
        
        if OLLAMA_ENABLED:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{OLLAMA_API_URL}/tags")
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        model_names = [model.get("name") for model in models]
                        return {"models": model_names}
            except Exception as e:
                print(f"Error fetching models from Ollama API: {str(e)}")
        
        return {"models": [DEFAULT_MODEL, "gemma2:2b", "qwen2.5:0.5b", "deepseek-r1:1.5b", "deepseek-coder:latest"]}
    
    except Exception as e:
        print(f"Unexpected error in get_models: {str(e)}")
        return {"models": [DEFAULT_MODEL]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
