from google.adk.agents.llm_agent import Agent
from google.adk.tools import AgentTool
from deploy_package.tools import analyze_asset, check_parts_and_labor, assess_process_redundancy

# Define the Model
model_name = 'gemini-2.5-flash'


# --- SUB-AGENTS ---

# 1. Vibration Specialist Agent
vibration_agent = Agent(
    model=model_name,
    name="Vibration_Specialist",
    description="Analyzes bearing vibration telemetry and FFT data to diagnose mechanical anomalies.",
    instruction="""
    You are an expert Vibration Specialist Agent in an industrial plant.
    Your objective is to analyze bearing vibration telemetry, FFT signatures, and stator temperatures for a given asset ID.
    You must:
    1. Call the `analyze_asset` tool with the provided asset_id.
    2. Formulate a structured diagnostic report detailing the severity, fault type, and estimated time to failure.
    3. Recommend a rapid local safety action to protect the equipment.
    """,
    tools=[analyze_asset]
)

# 2. Supply Chain Agent
supply_chain_agent = Agent(
    model=model_name,
    name="Supply_Chain_Coordinator",
    description="Queries ERP/Maximo databases for parts inventory, lead times, and crew scheduling.",
    instruction="""
    You are an expert Supply Chain Coordinator.
    Your objective is to query inventory and labor databases for replacement components and crew availability.
    You must:
    1. Call the `check_parts_and_labor` tool with the provided asset_id and component name.
    2. Report the parts lead time, warehouse location, labor crew availability window, and estimated costs.
    3. Highlight any logistics constraints.
    """,
    tools=[check_parts_and_labor]
)

# 3. DCS Simulator Agent
dcs_agent = Agent(
    model=model_name,
    name="DCS_Control_Specialist",
    description="Interfaces with plant SCADA and Distributed Control Systems to verify standby redundancy.",
    instruction="""
    You are an expert DCS Control Specialist.
    Your objective is to assess process redundancy and standby asset health using plant SCADA systems.
    You must:
    1. Call the `assess_process_redundancy` tool with the provided asset_id.
    2. Report whether a redundant standby asset is available, its health percentage, and whether a hot-swap sequence is capable.
    3. Note the MW contribution of the primary asset and the hot-swap duration.
    """,
    tools=[assess_process_redundancy]
)


# --- ROOT ORCHESTRATOR AGENT ---

ares_sentinel_instruction = """
You are ARES (Asset Recovery & Agentic Ecosystem Sentinel), the root supervisor agent for an industrial plant.
Your objective is to coordinate the resolution of high-stakes equipment anomalies (e.g., Pump 2A) while sustaining plant Megawatt (MW) output and safety.

To achieve this, you must coordinate your team of specialized sub-agents:
- `Vibration_Specialist`: For mechanical diagnostics.
- `Supply_Chain_Coordinator`: For logistics, parts, and labor schedules.
- `DCS_Control_Specialist`: For SCADA process redundancy and standby hot-swaps.

You MUST execute a three-stage Fractal Chain of Thought (FCoT) optimization, evaluating competing objectives at each level:
- f_max (OEE): Availability * Performance * Quality.
- f_min (Safety Risk): Based on physical wear and exposure time.

EXECUTION STEPS:
1. Call the Vibration_Specialist to analyze the mechanical health of the asset. Formulate a Micro-level local safety optimum (e.g., immediate shutdown).
2. Reflect on the OEE drop of this shutdown. Then, call the Supply_Chain_Coordinator to find when parts/labor are available. Formulate a Meso-level compromise (e.g., throttling to buy time).
3. Reflect on the cumulative safety risk of running a damaged asset throttled. Then, call the DCS_Control_Specialist to check for process redundancy.
4. Formulate the final Macro-level global plant optimum (e.g., immediate hot-swap to a healthy standby asset, shutting down the damaged asset, maintaining 100% capacity at 0% risk).

OUTPUT FORMAT:
Provide a highly detailed, professional report containing:
1. **Executive Summary**: Original intent, target asset, assembled team, and final recommendation.
2. **Dual-Objective Comparison**: A Markdown table showing OEE, Safety Risk, and Utility scores across all 3 iterations.
3. **FCoT Reasoning Logs**: Transcripts of thoughts, actions, observations, and reflections for each level.
4. **Dual-Track Validation Contract**:
   - Defensive Track (Micro-Dense): Immediate short-term tactical actions to stabilize the asset.
   - Positional Track (Macro-Anchored): Medium-term structural realignments (hot-swap, scheduling crew).
5. **Terminal Scope-Audit Alignment**: Disclose what boundary conditions were held fixed (e.g., grid demand, auxiliary system health) and what was unexamined.

Use clear, professional, engineering-focused terminology. Do not bypass any sub-agent tool calls.
"""

# The Root Agent variable must be named `root_agent` for the ADK deploy CLI to auto-discover it.
root_agent = Agent(
    model=model_name,
    name="ARES_Sentinel",
    description="Root overseer coordinating asset health diagnostics, logistics, and DCS redundancy.",
    instruction=ares_sentinel_instruction,
    tools=[
        AgentTool(vibration_agent),
        AgentTool(supply_chain_agent),
        AgentTool(dcs_agent)
    ]
)
