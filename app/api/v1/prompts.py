"""Prompt endpoint routing to agents with orchestration."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.agents.orchestrator import AgentOrchestrator
from app.agents.prompt_router import PromptRouterAgent
from app.agents.query_graph import QueryAgent
from app.agents.source_extractor import SourceExtractor
from app.agents.summarize_graph import SummarizeAgent
from app.agents.task_graph import TaskAgent
from app.agents.time_extractor import TimeRangeExtractor
from app.api.deps import DatabaseSession, UserID
from app.api.v1.common_helpers import handle_operation
from app.schemas.prompt import (
    PromptClarificationRequest,
    PromptRequest,
    PromptResponse,
)
from app.utils.validation import needs_clarification

router = APIRouter(prefix="/prompts", tags=["prompts"])
logger = logging.getLogger(__name__)


@router.post("", response_model=PromptResponse)
async def handle_prompt(
    payload: PromptRequest,
    db: DatabaseSession,
    user_id: UserID,
) -> PromptResponse:
    """
    Main prompt entrypoint with orchestration.
    
    Handles three intent types:
    - summarize: Pull-based SummarizeAgent (only on explicit request)
    - task: TaskAgent (neither push nor pull - performs tasks)
    - query: QueryAgent uses context bank for fine-grained search
    
    Validates source applications and time ranges.
    Prompts user for clarification if missing.
    """

    async def _operation():
        prompt_text = payload.prompt
        context = payload.context or {}

        # Create orchestrator for this request
        orchestrator = AgentOrchestrator(db, user_id)

        # Extract sources and time range from prompt
        source_extractor = SourceExtractor(orchestrator=orchestrator)
        time_extractor = TimeRangeExtractor(orchestrator=orchestrator)

        source_result = await source_extractor.extract_sources(prompt_text)
        time_result = await time_extractor.extract_time_range(prompt_text)

        # Use extracted values or fall back to context
        sources = source_result.get("sources") or context.get("sources")
        start_time = time_result.get("start_time")
        end_time = time_result.get("end_time")

        # Check if clarification is needed
        clarify_needed, missing, clarify_message = needs_clarification(
            sources=sources,
            start_time=start_time,
            end_time=end_time,
        )

        if clarify_needed:
            return PromptResponse(
                intent="clarification",
                response={},
                clarification_needed=PromptClarificationRequest(
                    missing_fields=missing,
                    message=clarify_message,
                    prompt=prompt_text,
                ),
            )

        # Classify intent
        prompt_router = PromptRouterAgent(orchestrator=orchestrator)
        intent = await orchestrator.execute_agent(
            "prompt_router",
            prompt_router.classify_intent,
            prompt_text,
            intent="classify",
            input_prompt=prompt_text,
            input_params={},
        )

        # Route to appropriate agent
        if intent == "summarize":
            # Pull-based: SummarizeAgent only executes on explicit user request
            summarize_agent = SummarizeAgent(orchestrator=orchestrator)
            result = await orchestrator.execute_agent(
                "summarize",
                summarize_agent.summarize,
                db,
                user_id=user_id,
                prompt=prompt_text,
                time_start=start_time,
                time_end=end_time,
                sources=sources,
                intent="summarize",
                input_prompt=prompt_text,
                input_params={
                    "sources": sources,
                    "time_start": start_time.isoformat() if start_time else None,
                    "time_end": end_time.isoformat() if end_time else None,
                },
            )
            return PromptResponse(
                intent="summarize",
                response=result,
                execution_id=str(orchestrator.current_session_id),
            )

        if intent == "task":
            # Neither push nor pull: TaskAgent performs tasks
            task_agent = TaskAgent(orchestrator=orchestrator)
            result = await orchestrator.execute_agent(
                "task",
                task_agent.detect_tasks,
                db,
                user_id=user_id,
                prompt=prompt_text,
                time_start=start_time,
                time_end=end_time,
                sources=sources,
                intent="task",
                input_prompt=prompt_text,
                input_params={
                    "sources": sources,
                    "time_start": start_time.isoformat() if start_time else None,
                    "time_end": end_time.isoformat() if end_time else None,
                },
            )
            return PromptResponse(
                intent="task",
                response=result,
                execution_id=str(orchestrator.current_session_id),
            )

        if intent == "query":
            # QueryAgent uses context bank for fine-grained search
            query_agent = QueryAgent(orchestrator=orchestrator)
            result = await orchestrator.execute_agent(
                "query",
                query_agent.answer_query_with_context,
                db,
                user_id=user_id,
                prompt=prompt_text,
                sources=sources,
                time_start=start_time,
                time_end=end_time,
                intent="query",
                input_prompt=prompt_text,
                input_params={
                    "sources": sources,
                    "time_start": start_time.isoformat() if start_time else None,
                    "time_end": end_time.isoformat() if end_time else None,
                },
            )
            return PromptResponse(
                intent="query",
                response=result,
                execution_id=str(orchestrator.current_session_id),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown intent: {intent}",
        )

    return await handle_operation(
        db=db,
        operation=_operation,
        success_message="Handled prompt",
        error_message="Prompt handling failed",
        user_id=user_id,
        operation_name="prompts_handle",
        commit_on_success=True,
    )
