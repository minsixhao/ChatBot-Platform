from fastapi import APIRouter, HTTPException
from app.services.prompt_validator_service import validate_prompt, PromptValidation
from pydantic import BaseModel

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/validate", response_model=PromptValidation)
async def validate_prompt_route(request: PromptRequest):
    try:
        result = await validate_prompt(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证提示时发生错误：{str(e)}")