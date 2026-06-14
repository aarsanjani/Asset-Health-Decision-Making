import os
import json
import logging
from typing import Dict, Any, List
from google import genai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

# Configure logging
logger = logging.getLogger("AssetHealthSystem.Registry")

# Initialize Gemini model using Google ADK wrappers
project = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger.info(f"Initializing GenAI Client (Project: {project}, Location: {location})...")
client = genai.Client(vertexai=True, project=project, location=location)
model_instance = Gemini(model_name="gemini-2.5-flash", client=client)


# --- Simulated Industrial Tools ---

def analyze_asset(asset_id: str) -> str:
    """
    Analyzes bearing vibration telemetry, FFT signatures, and stator temperatures for a given asset ID.
    
    Args:
        asset_id: The unique identifier of the industrial asset (e.g., 'Pump 2A').
        
    Returns:
        A JSON string containing severe bearing failure diagnostics, severity level, and time to failure.
    """
    logger.info(f"[Tool: analyze_asset] Executing vibration telemetry and FFT analysis for {asset_id}...")
    telemetry = {
        "asset_id": asset_id,
        "vibration_rms_mms": 12.8,  # Critical threshold is > 7.1 mm/s
        "vibration_peak_g": 4.2,
        "fft_dominant_frequency_hz": 120.0,
        "bearing_temperature_c": 87.5,  # Alarm limit is > 80C
        "anomaly_detected": True,
        "fault_type": "Outer Race Bearing Defect (Stage 4)",
        "severity_level": "CRITICAL",
        "estimated_time_to_catastrophic_failure_hours": 36.0,
        "recommended_local_action": "Immediate Emergency Shutdown or Throttle to < 30% load"
    }
    return json.dumps(telemetry)


def check_parts_and_labor(asset_id: str, component_needed: str) -> str:
    """
    Checks ERP, Maximo, and logistics databases for replacement parts inventory, lead times, and labor crew availability.
    
    Args:
        asset_id: The unique identifier of the industrial asset (e.g., 'Pump 2A').
        component_needed: The name of the replacement component (e.g., 'Replacement Bearing Set').
        
    Returns:
        A JSON string containing warehouse availability, shipping lead time, labor crew schedule, and costs.
    """
    logger.info(f"[Tool: check_parts_and_labor] Querying ERP/Maximo for {asset_id} replacement part: {component_needed}...")
    logistics = {
        "asset_id": asset_id,
        "component_needed": component_needed,
        "part_in_local_warehouse": False,
        "part_in_regional_warehouse": True,
        "part_sku": "BRG-22322-E1D1",
        "shipping_lead_time_hours": 24.0,
        "expedited_shipping_cost_usd": 1200.0,
        "maintenance_crew_available": True,
        "next_available_window_hours": 36.0,  # Crew available in 36 hours for morning shift
        "standard_labor_hours_required": 6.0,
        "total_repair_cost_estimate_usd": 7800.0,
        "constraints": ["Requires asset cooldown of 4 hours prior to repair start"]
    }
    return json.dumps(logistics)


def assess_process_redundancy(asset_id: str) -> str:
    """
    Assesses Distributed Control System (DCS) status, process flow bypasses, and standby operational redundancy.
    
    Args:
        asset_id: The unique identifier of the primary asset facing anomaly (e.g., 'Pump 2A').
        
    Returns:
        A JSON string detailing standby asset ID, standby health, hot-swap capability, and process MW demand.
    """
    logger.info(f"[Tool: assess_process_redundancy] Querying DCS SCADA for redundancy options for {asset_id}...")
    redundancy_state = {
        "primary_asset_id": asset_id,
        "redundant_pair_id": "Pump 2B",
        "redundant_pair_status": "STANDBY_READY",
        "redundant_pair_health_pct": 98.5,
        "current_plant_mw_demand": 500.0,
        "current_plant_mw_actual": 500.0,
        "asset_mw_contribution": 250.0,  # Pump 2A contributes to 250MW of steam generation
        "hot_swap_capable": True,
        "hot_swap_duration_minutes": 30.0,
        "throttle_capability": {
            "allowed": True,
            "mw_drop_per_10_percent_throttle": 25.0
        },
        "bypass_valve_status": "NORMAL_CLOSED"
    }
    return json.dumps(redundancy_state)


# --- Google ADK Agent Instantiations ---

# 1. Vibration Specialist Agent
vibration_agent_instruction = """
You are an expert Vibration Specialist Agent in an industrial plant.
Your objective is to analyze bearing vibration telemetry, FFT signatures, and stator temperatures for a given asset ID.
You must:
1. Call the `analyze_asset` tool with the provided asset_id.
2. Formulate a structured diagnostic report detailing the severity, fault type, and estimated time to failure.
3. Recommend a rapid local safety action to protect the equipment.
"""

vibration_agent = LlmAgent(
    model=model_instance,
    name="Vibration_Specialist",
    description="Analyzes bearing vibration telemetry and FFT data to diagnose mechanical anomalies.",
    instruction=vibration_agent_instruction,
    tools=[analyze_asset]
)


# 2. Supply Chain Agent
supply_chain_agent_instruction = """
You are an expert Supply Chain Coordinator.
Your objective is to query inventory and labor databases for replacement components and crew availability.
You must:
1. Call the `check_parts_and_labor` tool with the provided asset_id and component name.
2. Report the parts lead time, warehouse location, labor crew availability window, and estimated costs.
3. Highlight any logistics constraints.
"""

supply_chain_agent = LlmAgent(
    model=model_instance,
    name="Supply_Chain_Coordinator",
    description="Queries ERP/Maximo databases for parts inventory, lead times, and crew scheduling.",
    instruction=supply_chain_agent_instruction,
    tools=[check_parts_and_labor]
)


# 3. DCS Simulator Agent
dcs_agent_instruction = """
You are an expert DCS Control Specialist.
Your objective is to assess process redundancy and standby asset health using plant SCADA systems.
You must:
1. Call the `assess_process_redundancy` tool with the provided asset_id.
2. Report whether a redundant standby asset is available, its health percentage, and whether a hot-swap sequence is capable.
3. Note the MW contribution of the primary asset and the hot-swap duration.
"""

dcs_agent = LlmAgent(
    model=model_instance,
    name="DCS_Control_Specialist",
    description="Interfaces with plant SCADA and Distributed Control Systems to verify standby redundancy.",
    instruction=dcs_agent_instruction,
    tools=[assess_process_redundancy]
)


# Capability Registry Class to manage these agents
class AgentRegistry:
    """
    A capability-based registry managing Google ADK agents.
    """
    def __init__(self):
        self._agents = {
            "Vibration Specialist": vibration_agent,
            "Supply Chain Coordinator": supply_chain_agent,
            "DCS Control Specialist": dcs_agent
        }

    def get_agent_by_role(self, role: str) -> LlmAgent:
        if role not in self._agents:
            raise ValueError(f"No agent registered for role: {role}")
        return self._agents[role]

    def discover_agents_for_capabilities(self, required_caps: List[str]) -> List[str]:
        # Simple rule-based discovery matching roles to capabilities
        roles = []
        for cap in required_caps:
            if "vibration" in cap or "thermal" in cap:
                roles.append("Vibration Specialist")
            elif "parts" in cap or "labor" in cap or "scheduling" in cap:
                roles.append("Supply Chain Coordinator")
            elif "redundancy" in cap or "load" in cap:
                roles.append("DCS Control Specialist")
        return list(set(roles))
