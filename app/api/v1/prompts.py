"""Prompt endpoint routing to agents."""
import logging

from fastapi import APIRouter, HTTPException

from app.agents.prompt_router import prompt_router
from app.agents.summarize_graph import summarize_agent
from app.agents.task_graph import task_agent
from app.api.deps import DatabaseSession, UserID

router = APIRouter(prefix="/prompts", tags=["prompts"])
logger = logging.getLogger(__name__)


@router.post("")
async def handle_prompt(
    payload: dict,
    db: DatabaseSession,
    user_id: UserID,
):
    """Main prompt entrypoint."""
    prompt_text = payload.get("prompt", "")
    context = payload.get("context", {})
    sources = context.get("sources")
    try:
        intent = await prompt_router.classify_intent(prompt_text)
    except Exception as exc:
        logger.error("Intent classification failed", extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail="Intent classification failed")

    if intent == "summarize":
        try:
            result = await summarize_agent.summarize(
                db, user_id=user_id, prompt=prompt_text, hours=2, sources=sources
            )
            return {"intent": "summarize", "response": result}
        except Exception as exc:
            logger.error("Summarize agent failed", extra={"error": str(exc)})
            raise HTTPException(status_code=500, detail="Summarization failed")
    if intent == "task":
        try:
            result = await task_agent.detect_tasks(
                db, user_id=user_id, prompt=prompt_text, sources=sources
            )
            return {"intent": "task", "response": result}
        except Exception as exc:
            logger.error("Task agent failed", extra={"error": str(exc)})
            raise HTTPException(status_code=500, detail="Task detection failed")

    raise HTTPException(status_code=400, detail="Unable to classify prompt intent")

