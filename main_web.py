import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from meta_agent import MetaAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("AssetHealthSystem.WebServer")

app = FastAPI(
    title="ARES - Agentic Ecosystem Sentinel",
    description="Level 5 Managed Multi-Agent System Dashboard",
    version="1.0.0"
)

# Mount the static directory for CSS and JS files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize the MetaAgent (Root Overseer)
logger.info("Initializing MetaAgent backend for Web Server...")
meta_agent = MetaAgent()

class IntentRequest(BaseModel):
    intent: str

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """
    Serves the premium glassmorphic dashboard homepage.
    """
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        logger.error("index.html not found in static folder.")
        raise HTTPException(status_code=404, detail="Dashboard UI not found.")
    
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/run-simulation")
async def run_simulation(request: IntentRequest):
    """
    Triggers the Meta-Agent's intent recomposition and FCoT reasoning loop,
    returning the full optimization history as JSON.
    """
    logger.info(f"Web client triggered simulation with intent: '{request.intent}'")
    try:
        # Run the full Meta-Agent pipeline
        result_bundle = meta_agent.handle_goal(request.intent)
        
        # Serialize the FCoT history into a clean JSON structure
        serializable_iterations = []
        for it in result_bundle["fcot_iterations"]:
            state = it["proposed_state"]
            serializable_iterations.append({
                "iteration": it["iteration"],
                "phase": it["phase"],
                "thought": it["thought"],
                "action": it["action"],
                "observation": it["observation"],
                "proposed_state": {
                    "asset_id": state.asset_id,
                    "operating_load_pct": state.operating_load_pct,
                    "vibration_rms": state.vibration_rms,
                    "bearing_temp": state.bearing_temp,
                    "redundancy_active": state.redundancy_active,
                    "production_mw": state.production_mw,
                    "maintenance_delay_hours": state.maintenance_delay_hours,
                    "description": state.description
                },
                "metrics": it["metrics"],
                "reflection": it["reflection"]
            })
            
        rec_state = result_bundle["recommended_state"]
        
        response_data = {
            "original_intent": result_bundle["parsed_intent"]["original_intent"],
            "target_asset": result_bundle["parsed_intent"]["target_asset"],
            "assembled_team": result_bundle["assembled_team"],
            "fcot_iterations": serializable_iterations,
            "recommended_state": {
                "asset_id": rec_state.asset_id,
                "operating_load_pct": rec_state.operating_load_pct,
                "vibration_rms": rec_state.vibration_rms,
                "bearing_temp": rec_state.bearing_temp,
                "redundancy_active": rec_state.redundancy_active,
                "production_mw": rec_state.production_mw,
                "maintenance_delay_hours": rec_state.maintenance_delay_hours,
                "description": rec_state.description
            },
            "recommended_metrics": result_bundle["recommended_metrics"]
        }
        
        logger.info("Simulation completed successfully. Returning results to web client.")
        return response_data
        
    except Exception as e:
        logger.exception("An error occurred during web simulation run:")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Serve locally on port 8000
    logger.info("Starting Uvicorn server on http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
