"""Prompt endpoint routing to agents."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.agents.prompt_router import prompt_router
from app.agents.summarize_graph import summarize_agent
from app.agents.task_graph import task_agent
from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.schemas.prompt import PromptRequest, PromptResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])
logger = logging.getLogger(__name__)


@router.post("", response_model=PromptResponse)
async def handle_prompt(
    payload: PromptRequest,
    db: DatabaseSession,
    user_id: UserID,
) -> PromptResponse:
    """Main prompt entrypoint."""
    async def _operation():
        prompt_text = payload.prompt
        context = payload.context or {}
        sources = context.get("sources")

        intent = await prompt_router.classify_intent(prompt_text)

        if intent == "summarize":
            result = await summarize_agent.summarize(
                db, user_id=user_id, prompt=prompt_text, hours=2, sources=sources
            )
            return PromptResponse(intent="summarize", response=result)

        if intent == "task":
            result = await task_agent.detect_tasks(
                db, user_id=user_id, prompt=prompt_text, sources=sources
            )
            return PromptResponse(intent="task", response=result)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to classify prompt intent",
        )

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Handled prompt",
        error_message="Prompt handling failed",
        user_id=user_id,
        operation_name="prompts_handle",
        commit_on_success=False,
    )
