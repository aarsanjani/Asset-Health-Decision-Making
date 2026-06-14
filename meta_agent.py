import logging
from typing import Dict, Any, List
from agent_registry import AgentRegistry
from evaluator import DualObjectiveEvaluator
from fcot_orchestrator import FCoTOrchestrator

logger = logging.getLogger("AssetHealthSystem.MetaAgent")

class IntentParser:
    """
    Parses natural language industrial instructions into structured targets, constraints, and capabilities.
    """
    def __init__(self):
        logger.info("Initializing Intent Parser...")

    def parse_intent(self, intent_str: str) -> Dict[str, Any]:
        logger.info(f"Parsing intent: '{intent_str}'")
        
        # Rule-based parser for our industrial domain.
        intent_lower = intent_str.lower()
        
        # Extract target asset
        target_asset = "Unknown"
        if "pump 2a" in intent_lower:
            target_asset = "Pump 2A"
        elif "pump 2b" in intent_lower:
            target_asset = "Pump 2B"
            
        # Extract primary objective and constraints
        sustain_mw = "sustain" in intent_lower or "mw output" in intent_lower or "maintain" in intent_lower
        mitigate_anomaly = "mitigate" in intent_lower or "anomaly" in intent_lower or "vibration" in intent_lower
        
        required_capabilities = []
        if mitigate_anomaly:
            required_capabilities.extend(["vibration_analysis", "thermal_monitoring"])
        if sustain_mw:
            required_capabilities.extend(["process_redundancy_assessment", "load_shedding_simulation"])
        # Always check supply chain for repair logistics
        required_capabilities.extend(["parts_inventory_check", "labor_resource_scheduling"])
        
        parsed = {
            "original_intent": intent_str,
            "target_asset": target_asset,
            "sustain_mw_output": sustain_mw,
            "required_capabilities": list(set(required_capabilities)),
            "constraints": ["Sustain plant Megawatts close to nominal 500MW", "Avoid catastrophic asset destruction"]
        }
        
        logger.info(f"Parsed Intent Details: Target Asset: {parsed['target_asset']}, Capabilities: {parsed['required_capabilities']}")
        return parsed


class MetaAgent:
    """
    The Root Overseer in GEAP Blueprint 4 (The Governed Ecosystem).
    Responsible for:
    1. Parsing high-level business goals.
    2. Dynamic recomposition (discovering and assembling micro-agents).
    3. Delegating execution to the FCoT Orchestrator.
    """
    def __init__(self, registry: AgentRegistry = None):
        self.registry = registry or AgentRegistry()
        self.intent_parser = IntentParser()
        self.evaluator = DualObjectiveEvaluator(nominal_mw=500.0)
        self.orchestrator = FCoTOrchestrator(self.registry, self.evaluator)
        logger.info("Meta-Agent (Root Overseer) fully operational.")

    def handle_goal(self, high_level_goal: str) -> Dict[str, Any]:
        logger.info(f"=== META-AGENT RECEIVED HIGH-LEVEL GOAL: '{high_level_goal}' ===")
        
        # Step 1: Parse the business intent
        parsed_intent = self.intent_parser.parse_intent(high_level_goal)
        asset_id = parsed_intent["target_asset"]
        
        if asset_id == "Unknown":
            logger.error("Failed to parse a valid industrial asset target from intent.")
            raise ValueError("Invalid target asset in goal instruction.")
            
        # Step 2: Dynamic Recomposition (Query registry to ensure we have the capabilities)
        needed_caps = parsed_intent["required_capabilities"]
        matching_roles = self.registry.discover_agents_for_capabilities(needed_caps)
        
        logger.info(f"Dynamic Recomposition: Assembled agent team [{', '.join(matching_roles)}] to address goal.")
        
        # Step 3: Run the Fractal Chain of Thought Reasoning Loop
        f_c_o_t_history = self.orchestrator.execute_reasoning_loop(asset_id, high_level_goal)
        
        # Step 4: Bundle the results
        result_bundle = {
            "parsed_intent": parsed_intent,
            "assembled_team": matching_roles,
            "fcot_iterations": f_c_o_t_history,
            "recommended_state": f_c_o_t_history[-1]["proposed_state"],
            "recommended_metrics": f_c_o_t_history[-1]["metrics"]
        }
        
        logger.info("Meta-Agent successfully finished reasoning and optimization.")
        return result_bundle
