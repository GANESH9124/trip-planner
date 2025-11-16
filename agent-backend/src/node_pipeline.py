from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from tavily import TavilyClient

from dotenv import load_dotenv
import os

load_dotenv()

# Model Factory - supports multiple free models
from src.model_factory import ModelFactory

# import prompt templates
from utils.prompts import (
    VACATION_PLANNER_PROMPT,
    VACATION_PLANNING_SUPERVISOR_PROMPT,
    PLANNER_ASSISTANT_PROMPT,
    PLANNER_CRITIQUE_PROMPT,
    PLANNER_CRITIQUE_ASSISTANT_PROMPT,
)

from src.agent_state import AgentState, Queries


class NodePipeline:
    """
    Pipeline using Tavily + Gemini through LangChain (Service Account Version)
    """

    def __init__(self):
        super().__init__()

        self.memory = MemorySaver()

        # --- Load Chat Model (supports multiple free providers) ---
        try:
            self.model = ModelFactory.create_model()
        except Exception as e:
            raise ValueError(
                f"Failed to initialize chat model: {str(e)}\n\n"
                "Available options:\n"
                "  1. Ollama (free, local): MODEL_TYPE=ollama\n"
                "  2. Groq (free tier): MODEL_TYPE=groq, GROQ_API_KEY=...\n"
                "  3. Hugging Face (free tier): MODEL_TYPE=huggingface, HUGGINGFACE_API_KEY=...\n"
                "  4. Together AI (free tier): MODEL_TYPE=together, TOGETHER_API_KEY=...\n"
                "  5. Google Gemini: MODEL_TYPE=google, GOOGLE_API_KEY=...\n"
                "\nSee FREE_MODELS.md for setup instructions."
            )

        # --- Initialize Tavily client ---
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set")
        
        try:
            self.tavily = TavilyClient(api_key=tavily_api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Tavily client: {str(e)}")

    def plan_node(self, state: AgentState):
        try:
            task = state.get("task", "")
            if not task:
                raise ValueError("Task is required for planning")

            print(f"  [plan_node] Processing task: {task[:50]}...")
            
            msgs = [
                SystemMessage(content=VACATION_PLANNING_SUPERVISOR_PROMPT),
                HumanMessage(content=task),
            ]

            print(f"  [plan_node] Invoking model...")
            resp = self.model.invoke(msgs)
            print(f"  [plan_node] Model response received")
            
            if not resp or not hasattr(resp, 'content'):
                raise ValueError("Failed to generate plan from model - response has no content")
            
            plan_content = resp.content
            if not plan_content:
                raise ValueError("Model returned empty plan content")
            
            print(f"  [plan_node] Plan generated ({len(plan_content)} chars)")
            return {"plan": plan_content}
        except Exception as e:
            error_msg = f"Plan node failed: {str(e)}"
            print(f"  [plan_node] ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            raise Exception(error_msg)

    def research_plan_node(self, state: AgentState):
        try:
            past_queries = state.get("queries") or []
            answers = state.get("answers") or []
            
            plan = state.get("plan", "")
            if not plan:
                raise ValueError("Plan is required for research")

            queries = self.model.with_structured_output(Queries).invoke([
                SystemMessage(content=PLANNER_ASSISTANT_PROMPT),
                HumanMessage(content=plan)
            ])

            if not queries or not hasattr(queries, 'queries'):
                raise ValueError("Failed to generate research queries")

            for q in queries.queries:
                try:
                    resp = self.tavily.search(query=q, max_results=3)
                    if resp and "results" in resp:
                        for r in resp["results"]:
                            if "content" in r:
                                answers.append(r["content"])
                except Exception as e:
                    # Log error but continue with other queries
                    print(f"Error searching for query '{q}': {str(e)}")
                    continue

            past_queries.extend(queries.queries)
            return {
                "answers": answers,
                "queries": past_queries,
                "lnode": "research_plan",
                "count": 1,
            }
        except Exception as e:
            raise Exception(f"Research plan node failed: {str(e)}")

    def generation_node(self, state: AgentState):
        try:
            task = state.get("task", "")
            plan = state.get("plan", "")
            
            if not task:
                raise ValueError("Task is required for generation")
            if not plan:
                raise ValueError("Plan is required for generation")
            
            answers = "\n------\n".join(state.get("answers", [])) if state.get("answers") else "No research data available."
            user_message = HumanMessage(
                content=f"{task}\n\nHere is my plan:\n\n{plan}"
            )

            msgs = [
                SystemMessage(content=VACATION_PLANNER_PROMPT.format(answers=answers)),
                user_message,
            ]

            resp = self.model.invoke(msgs)
            if not resp or not hasattr(resp, 'content'):
                raise ValueError("Failed to generate draft from model")
                
            return {
                "draft": resp.content,
                "revision_number": state.get("revision_number", 0) + 1,
                "lnode": "generate",
                "count": 1,
            }
        except Exception as e:
            raise Exception(f"Generation node failed: {str(e)}")

    def reflection_node(self, state: AgentState):
        try:
            draft = state.get("draft", "")
            if not draft:
                raise ValueError("Draft is required for critique")

            msgs = [
                SystemMessage(content=PLANNER_CRITIQUE_PROMPT),
                HumanMessage(content=draft),
            ]

            resp = self.model.invoke(msgs)
            if not resp or not hasattr(resp, 'content'):
                raise ValueError("Failed to generate critique from model")
                
            return {
                "critique": resp.content,
                "lnode": "reflect",
                "count": 1,
            }
        except Exception as e:
            raise Exception(f"Reflection node failed: {str(e)}")

    def research_critique_node(self, state: AgentState):
        try:
            past_queries = state.get("queries") or []
            answers = state.get("answers") or []
            critique = state.get("critique", "")
            
            if not critique:
                raise ValueError("Critique is required for research")

            queries = self.model.with_structured_output(Queries).invoke([
                SystemMessage(content=PLANNER_CRITIQUE_ASSISTANT_PROMPT.format(
                    queries=past_queries,
                    answers=answers
                )),
                HumanMessage(content=critique)
            ])

            if not queries or not hasattr(queries, 'queries'):
                raise ValueError("Failed to generate research queries from critique")

            for q in queries.queries:
                past_queries.append(q)
                try:
                    resp = self.tavily.search(query=q, max_results=3)
                    if resp and "results" in resp:
                        for r in resp["results"]:
                            if "content" in r:
                                answers.append(r["content"])
                except Exception as e:
                    # Log error but continue with other queries
                    print(f"Error searching for query '{q}': {str(e)}")
                    continue

            return {
                "queries": past_queries,
                "answers": answers,
                "lnode": "research_critique",
                "count": 1,
            }
        except Exception as e:
            raise Exception(f"Research critique node failed: {str(e)}")

    def should_continue(self, state):
        if state["revision_number"] >= state["max_revisions"]:
            return END

        return "reflect"
