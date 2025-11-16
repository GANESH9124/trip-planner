from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import time
import threading
from dotenv import load_dotenv
from src.builder import builder

load_dotenv()

app = Flask(__name__)
CORS(app)

# Build graph
try:
    agent_builder = builder()
    graph = agent_builder.build_graph()
except Exception as e:
    print(f"ERROR: Failed to initialize graph: {str(e)}")
    print("Please check your environment variables:")
    print("  - GOOGLE_APPLICATION_CREDENTIALS")
    print("  - TAVILY_API_KEY")
    raise

# simple in-memory thread id generator
_threads_lock = threading.Lock()
_next_thread_id = 0


def new_thread_config():
    """
    Creates a new unique thread_id + timestamp (thread_ts)
    used by LangGraph checkpointer.
    """
    global _next_thread_id
    with _threads_lock:
        tid = _next_thread_id
        _next_thread_id += 1

    return {"configurable": {"thread_id": str(tid), "thread_ts": str(time.time())}}, tid


def build_config(thread_id, thread_ts=None):
    """
    Consistent config builder for LangGraph.
    """
    cfg = {"configurable": {"thread_id": str(thread_id)}}
    if thread_ts:
        cfg["configurable"]["thread_ts"] = str(thread_ts)
    return cfg


def run_agent_stream(graph, task, stop_after, start, max_iterations):
    """
    Handles multi-step streaming execution across graph.
    """

    # new conversation (new thread)
    if start:
        config, thread_id = new_thread_config()
        thread_ts = config["configurable"]["thread_ts"]
        input_payload = {"task": task}

    # continuing old conversation
    else:
        thread_id = str(task["thread_id"])
        thread_ts = task.get("thread_ts")
        config = build_config(thread_id, thread_ts)
        input_payload = {"task": task.get("task", "")}

    partial = ""

    for _ in range(max_iterations):
        try:
            response = graph.invoke(input_payload, config=config)
        except Exception as e:
            yield {"error": str(e)}
            return

        partial += str(response) + "\n------------------\n\n"

        # extract runtime state
        try:
            state = graph.get_state(config)
            lnode = state.values.get("lnode")
            nnode = state.next
            rev = state.values.get("revision_number")
            count = state.values.get("count")
        except Exception:
            lnode = None
            nnode = None
            rev = None
            count = None

        yield {
            "partial": partial,
            "thread_id": thread_id,
            "thread_ts": thread_ts,
            "lnode": lnode,
            "nnode": nnode,
            "revision_number": rev,
            "count": count,
        }

        # next steps send empty input
        input_payload = {}

        if not nnode or (stop_after and lnode in stop_after):
            return


@app.route("/api/stream-run", methods=["POST"])
def stream_run():
    try:
        if not request.json:
            return jsonify({"error": "Request body is required"}), 400
        
        data = request.json or {}
        task = data.get("task", "")
        stop_after = data.get("stop_after", [])
        start = data.get("start", True)
        
        try:
            max_iterations = int(data.get("max_iterations", 2))
        except (ValueError, TypeError):
            max_iterations = 2

        generator = run_agent_stream(
            graph,
            task,
            stop_after,
            start,
            max_iterations
        )

        def stream():
            try:
                for item in generator:
                    yield json.dumps(item) + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return Response(stream(), mimetype="application/x-ndjson")
    except Exception as e:
        return jsonify({"error": f"Failed to start stream: {str(e)}"}), 500


@app.route("/api/get-state", methods=["GET"])
def get_state():
    try:
        tid = request.args.get("thread_id")
        if not tid:
            return jsonify({"error": "thread_id required"}), 400

        config = build_config(tid)

        state = graph.get_state(config)
        
        return jsonify({
            "values": getattr(state, "values", {}),
            "next": getattr(state, "next", None),
            "metadata": getattr(state, "metadata", {}),
            "config": getattr(state, "config", {}),
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get state: {str(e)}"}), 500


@app.route("/api/get-state-history", methods=["GET"])
def get_state_history():
    try:
        tid = request.args.get("thread_id")
        if not tid:
            return jsonify({"error": "thread_id required"}), 400

        config = build_config(tid)

        history = []
        for s in graph.get_state_history(config):
            history.append({
                "step": s.metadata.get("step"),
                "lnode": s.values.get("lnode"),
                "next": s.next,
                "revision_number": s.values.get("revision_number"),
                "count": s.values.get("count"),
                "thread_ts": s.config.get("configurable", {}).get("thread_ts"),
            })

        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": f"Failed to get state history: {str(e)}"}), 500


# ------------------------------------------------------
# Atomic Step Endpoints (single-node invokes)
# ------------------------------------------------------

@app.route("/api/plan", methods=["POST"])
def plan():
    try:
        if not request.json:
            return jsonify({"error": "Request body is required"}), 400
        
        data = request.json
        task = data.get("task")
        
        if not task or not task.strip():
            return jsonify({"error": "Task is required"}), 400

        config, tid = new_thread_config()
        print(f">> invoking graph with task: {task[:50]}...")
        
        # Initialize state with defaults for TypedDict
        initial_state = {
            "task": task,
            "plan": "",
            "draft": "",
            "critique": "",
            "queries": [],
            "answers": [],
            "revision_number": 0,
            "max_revisions": 3,
            "count": 0
        }
        
        try:
            result = graph.invoke(initial_state, config=config)
            print(">> graph returned successfully")
        except Exception as graph_error:
            print(f">> ERROR in graph.invoke: {str(graph_error)}")
            print(f">> Error type: {type(graph_error).__name__}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "error": f"Graph execution failed: {str(graph_error)}",
                "error_type": type(graph_error).__name__
            }), 500
        
        if not result:
            return jsonify({"error": "Failed to generate plan - graph returned empty result"}), 500
        
        plan_result = result.get("plan", "")
        if not plan_result:
            return jsonify({
                "error": "Plan generation returned empty plan",
                "result_keys": list(result.keys()) if result else "None"
            }), 500
            
        return jsonify({
            "plan": plan_result,
            "thread_id": tid
        })
    except Exception as e:
        import traceback
        print(f">> ERROR in plan endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "error_type": type(e).__name__
        }), 500


@app.route("/api/research", methods=["POST"])
def research():
    try:
        if not request.json:
            return jsonify({"error": "Request body is required"}), 400
        
        data = request.json
        plan = data.get("plan")
        thread_id = data.get("thread_id")
        
        if not plan or not plan.strip():
            return jsonify({"error": "Plan is required"}), 400
        
        if not thread_id:
            return jsonify({"error": "thread_id is required"}), 400

        config = build_config(thread_id)

        result = graph.invoke({"plan": plan}, config=config)
        
        if not result:
            return jsonify({"error": "Failed to research plan"}), 500
            
        return jsonify({
            "queries": result.get("queries", []),
            "answers": result.get("answers", []),
            "thread_id": thread_id
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        if not request.json:
            return jsonify({"error": "Request body is required"}), 400
        
        data = request.json
        thread_id = data.get("thread_id")
        task = data.get("task")
        plan = data.get("plan")
        
        if not thread_id:
            return jsonify({"error": "thread_id is required"}), 400
        
        if not task or not task.strip():
            return jsonify({"error": "Task is required"}), 400
        
        if not plan or not plan.strip():
            return jsonify({"error": "Plan is required"}), 400

        config = build_config(thread_id)

        result = graph.invoke(data, config=config)
        
        if not result:
            return jsonify({"error": "Failed to generate draft"}), 500
            
        return jsonify({
            "draft": result.get("draft", ""),
            "revision_number": result.get("revision_number", 1),
            "thread_id": thread_id
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/critique", methods=["POST"])
def critique():
    try:
        if not request.json:
            return jsonify({"error": "Request body is required"}), 400
        
        data = request.json
        thread_id = data.get("thread_id")
        draft = data.get("draft")
        
        if not thread_id:
            return jsonify({"error": "thread_id is required"}), 400
        
        if not draft or not draft.strip():
            return jsonify({"error": "Draft is required"}), 400

        config = build_config(thread_id)

        result = graph.invoke(data, config=config)
        
        if not result:
            return jsonify({"error": "Failed to critique draft"}), 500
            
        return jsonify({
            "critique": result.get("critique", ""),
            "thread_id": thread_id
        })
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/")
def index():
    return jsonify({"service": "agent-backend", "status": "running"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        threaded=True
    )
