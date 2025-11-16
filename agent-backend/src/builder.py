from src.node_pipeline import NodePipeline
from src.agent_state import AgentState
from langgraph.graph import StateGraph, END


class builder(NodePipeline):
    def __init__(self):
        super().__init__()
        self.builder = StateGraph(AgentState)

    def build_graph(self):

        self.builder.add_node("planner", self.plan_node)
        self.builder.add_node("research_plan", self.research_plan_node)
        self.builder.add_node("generate", self.generation_node)
        self.builder.add_node("reflect", self.reflection_node)
        self.builder.add_node("research_critique", self.research_critique_node)
        self.builder.set_entry_point("planner")
        self.builder.add_conditional_edges(
            "generate", 
            self.should_continue, 
            {END: END, "reflect": "reflect"}
        )
        self.builder.add_edge("planner", "research_plan")
        self.builder.add_edge("research_plan", "generate")
        self.builder.add_edge("reflect", "research_critique")
        self.builder.add_edge("research_critique", "generate")

        self.graph = self.builder.compile(
            checkpointer=self.memory,
        )

        return self.graph

