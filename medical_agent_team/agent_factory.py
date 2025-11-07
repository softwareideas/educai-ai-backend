from __future__ import annotations
from typing import Optional, List, Union, Callable, Any, Dict

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import BaseTool
from google.adk.tools.base_toolset import BaseToolset


class AgentCreator:
    def __init__(
        self,
        app_name: Optional[str] = None,
        session_service: Optional[Any] = None,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self.app_name = app_name or "medical-agent-app"
        self.session_service = session_service or InMemorySessionService()
        self.model = model
        self.runner: Optional[Runner] = None

    def _initialize_agent(
        self,
        name: str,
        description: str,
        instruction: str,
        tools: Optional[List[Union[Callable, BaseTool, BaseToolset]]] = None,
        model: Optional[str] = None,
        sub_agents: Optional[List[BaseAgent]] = None,
    ) -> LlmAgent:
        """Correctly initialize an LlmAgent with its own model and tools."""
        agent_model = model or self.model
        return LlmAgent(
            name=name,
            description=description,
            instruction=instruction,
            model=agent_model,
            tools=tools or [],
            sub_agents=sub_agents or [],
        )

    def _check_session_exists(self, user_id: str, session_id: str) -> bool:
        return bool(self.session_service.get_session(app_name=self.app_name, user_id=user_id, session_id=session_id))

    def _initialize_session(self, user_id: str, session_id: str) -> None:
        self.session_service.create_session(app_name=self.app_name, user_id=user_id, session_id=session_id)

    def _initialize_runner(self, root_agent: BaseAgent) -> None:
        self.runner = Runner(app_name=self.app_name, agent=root_agent, session_service=self.session_service)

    async def _agent_invoke(self, user_id: str, session_id: str, user_query: str) -> Dict[str, Any]:
        """Invoke agent asynchronously and stream events."""
        if not self._check_session_exists(user_id=user_id, session_id=session_id):
            self._initialize_session(user_id=user_id, session_id=session_id)

        if self.runner is None:
            raise RuntimeError("Runner not initialized. Call _initialize_runner with a root agent.")

        events: List[Dict[str, Any]] = []
        final_response: Optional[str] = None

        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_query,
        ):
            ev: Dict[str, Any] = {
                "is_final": getattr(event, "turnComplete", False) or getattr(event, "is_final_response", lambda: False)(),
                "type": getattr(event, "__class__", type("E", (), {})).__name__,
                "author": getattr(event, "author", None),
            }
            content = getattr(event, "content", None)
            if content is not None:
                parts = getattr(content, "parts", None) or []
                texts = [getattr(p, "text", "") for p in parts if hasattr(p, "text") and p.text]
                if texts:
                    ev["content"] = "\n".join(texts)
                    if ev["is_final"]:
                        final_response = ev["content"]
            events.append(ev)

        return {"events": events, "final_response": final_response}


def _create_sequential_agent(name: str, description: str, agents: List[BaseAgent]) -> BaseAgent:
    from google.adk.agents import SequentialAgent

    return SequentialAgent(name=name, description=description, sub_agents=agents)


def _create_loop_agent(name: str, description: str, agents: List[BaseAgent]) -> BaseAgent:
    from google.adk.agents import LoopAgent

    return LoopAgent(name=name, description=description, sub_agents=agents, max_iterations=5)


def _create_parallel_agent(name: str, description: str, agents: List[BaseAgent]) -> BaseAgent:
    from google.adk.agents import ParallelAgent

    return ParallelAgent(name=name, description=description, sub_agents=agents)
