from fastapi import FastAPI
from pydantic import BaseModel

from support_assistant.graph import graph, FinalAnswer


# ============================================================
# Request Model
# ============================================================

class AskRequest(BaseModel):
    query: str


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Zepto Support Assistant",
    description="LangGraph-based Zepto policy support assistant",
    version="1.0.0",
)


# ============================================================
# POST /ask
# ============================================================

@app.post("/ask", response_model=FinalAnswer)
def ask(request: AskRequest) -> FinalAnswer:

    result = graph.invoke({
        "query": request.query
    })

    # Convert graph output back into the validated
    # Pydantic response model.
    return FinalAnswer.model_validate(result["answer"])
