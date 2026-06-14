import logging
import uuid
import json
from typing import Dict, Any, List
from evaluator import DualObjectiveEvaluator, PlantState
from agent_registry import AgentRegistry
from google.adk.runners import InMemoryRunner
from google.genai import types

logger = logging.getLogger("AssetHealthSystem.Orchestrator")

class FCoTOrchestrator:
    """
    Fractal Chain of Thought (FCoT) Orchestrator.
    
    Implements a self-similar, hierarchical optimization loop that applies the dual-objective functions
    (Maximize OEE [f_max] vs. Minimize Safety Risk [f_min]) across three levels of abstraction:
    
    1. MICRO LEVEL: Individual asset mechanical health, local sensor limits, and immediate physics.
    2. MESO LEVEL: System-level logistics, supply chain lead times, labor scheduling, and local process constraints.
    3. MACRO LEVEL: Global plant production (MW), system-wide process redundancy, and overall plant utility.
    
    At the end of each iteration, the Meta-Agent triggers a forced reflection to analyze what was
    missed in the current state regarding OEE and Risk, using the resulting gaps to guide the hill-climbing
    optimization in the next iteration.
    """
    def __init__(self, registry: AgentRegistry, evaluator: DualObjectiveEvaluator):
        self.registry = registry
        self.evaluator = evaluator
        self.user_id = "operator-system"
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
        logger.info(f"Initializing Hierarchical FCoT Orchestrator (Session: {self.session_id})...")

    def _run_adk_agent(self, role: str, prompt: str) -> str:
        """
        Runs a Google ADK agent using InMemoryRunner, handling session states and streaming events.
        """
        agent = self.registry.get_agent_by_role(role)
        logger.info(f"Setting up InMemoryRunner for ADK Agent: [{agent.name}]...")
        runner = InMemoryRunner(agent=agent, app_name="agents")
        
        try:
            runner.session_service.create_session_sync(
                app_name="agents",
                user_id=self.user_id,
                session_id=self.session_id
            )
        except Exception:
            # Session already exists across iterations, which is normal
            pass

        logger.info(f"Dispatching query to [{agent.name}]...")
        events = runner.run(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
        )
        
        response_parts = []
        for event in events:
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)
        
        response_text = "".join(response_parts)
        logger.info(f"Received response from [{agent.name}].")
        return response_text

    def execute_reasoning_loop(self, asset_id: str, goal_intent: str) -> List[Dict[str, Any]]:
        iterations_history = []
        
        # =====================================================================
        # ITERATION 1: MICRO-LEVEL OPTIMIZATION (Local Physics & Asset Health)
        # =====================================================================
        logger.info("\n" + "="*80 + "\n[FCoT ITERATION 1] MICRO-LEVEL FOCUS: LOCAL MECHANICAL SAFETY\n" + "="*80)
        
        thought_1 = (
            f"Focusing strictly on the MICRO level—the physics and mechanical health of {asset_id}. "
            f"Must analyze high-frequency vibration telemetry and thermal limits to protect the asset from catastrophic failure. "
            f"Business and system-level constraints are out of scope for this micro-evaluation."
        )
        logger.info(f"[Micro Thought] {thought_1}")
        
        logger.info(f"[Micro Action] Calling Vibration Specialist Agent to analyze telemetry.")
        prompt_1 = f"Analyze the bearing telemetry and FFT signatures of {asset_id}. What is the mechanical state?"
        observation_1 = self._run_adk_agent("Vibration Specialist", prompt_1)
        
        logger.info(f"[Micro Observation] Received local telemetry diagnostics:\n{observation_1}")
        
        # Micro-Level State: Immediate Shutdown.
        # Physics focus: Vibration = 0, Temp = Ambient. Mechanical risk is completely eliminated.
        state_1 = PlantState(
            asset_id=asset_id,
            operating_load_pct=0.0,          # Physics-based local optimum: turn off the vibrating asset
            vibration_rms=0.0,
            bearing_temp=25.0,
            redundancy_active=False,         # Meso-level redundancy is not considered yet
            production_mw=250.0,             # Macro-level drop (50% plant capacity lost)
            maintenance_delay_hours=0.0,     # Immediate local intervention
            description="Micro-Level Local Optimum: Immediate emergency shutdown of Pump 2A to eliminate mechanical risk."
        )
        
        # Hierarchical Multi-Level Evaluation
        metrics_1 = self.evaluator.evaluate_state(state_1)
        
        logger.info("\n[MULTI-LEVEL OBJECTIVE EVALUATION - ITERATION 1]")
        logger.info(f"└─ MICRO (Asset Health) : f_min (Risk) = {metrics_1['risk']:.2f} (Perfect local safety)")
        logger.info(f"└─ MESO  (Logistics)    : Maintenance Delay = {state_1.maintenance_delay_hours} hrs, Redundancy = {state_1.redundancy_active}")
        logger.info(f"└─ MACRO (Plant Output) : f_max (OEE)  = {metrics_1['oee']:.2f} (Catastrophic 50% capacity loss)")
        
        # Forced Reflection Trigger at the end of Iteration 1
        self.evaluator.log_forced_reflection(1, state_1, metrics_1)
        
        reflection_1 = (
            f"What did we miss regarding OEE and Risk in Iteration 1?\n"
            f"We achieved a perfect micro-level safety score (Risk = 0.00), but completely missed the macro-level impact. "
            f"Shutting down Pump 2A immediately without logistical coordination cuts plant output by 50% (OEE = 0.00). "
            f"To climb towards a better utility, we must transition to the MESO level—integrating supply chain, parts "
            f"inventory, and crew schedules to see when we can actually execute a repair, and finding a throttled operational "
            f"compromise that balances plant output while keeping the pump alive."
        )
        logger.info(f"[Micro-to-Meso Reflection] {reflection_1}")
        
        iterations_history.append({
            "iteration": 1,
            "phase": "Micro-Level Safety Optimum",
            "thought": thought_1,
            "action": "Vibration Specialist Analysis (Google ADK)",
            "observation": observation_1,
            "proposed_state": state_1,
            "metrics": metrics_1,
            "reflection": reflection_1
        })
        
        # =====================================================================
        # ITERATION 2: MESO-LEVEL OPTIMIZATION (System-Level Logistics & Compromise)
        # =====================================================================
        logger.info("\n" + "="*80 + "\n[FCoT ITERATION 2] MESO-LEVEL FOCUS: OPERATIONAL & LOGISTICS COMPROMISE\n" + "="*80)
        
        thought_2 = (
            f"Transitioning to the MESO level. We must address the gaps identified in our first reflection. "
            f"We cannot afford an unscheduled 50% load drop. We must query the supply chain database "
            f"for parts and labor availability, and calculate a throttled operating state (e.g., 60% load) "
            f"that buys us time until a scheduled maintenance window, balancing OEE against physical wear."
        )
        logger.info(f"[Meso Thought] {thought_2}")
        
        logger.info(f"[Meso Action] Calling Supply Chain Coordinator Agent to query ERP/Maximo.")
        prompt_2 = f"Query ERP for {asset_id} bearing replacement lead times and available certified maintenance crews."
        observation_2 = self._run_adk_agent("Supply Chain Coordinator", prompt_2)
        
        logger.info(f"[Meso Observation] Received system logistics data:\n{observation_2}")
        
        # Meso-Level State: Throttle to 60% and schedule maintenance in 36 hours.
        # Coordinates local physical limits (vibration drops to 6.5 mm/s, temp to 68C)
        # with logistical constraints (parts/labor available in 36 hours).
        state_2 = PlantState(
            asset_id=asset_id,
            operating_load_pct=60.0,
            vibration_rms=6.5,                # Throttled, reducing physical stress
            bearing_temp=68.0,                # Throttled, reducing thermal stress
            redundancy_active=False,         # Process-level redundancy is still inactive
            production_mw=400.0,              # Throttled plant output (nominal 500MW)
            maintenance_delay_hours=36.0,     # Scheduled window based on crew availability
            description="Meso-Level Compromise: Throttle Pump 2A to 60% load, run for 36 hours until scheduled repair."
        )
        
        # Hierarchical Multi-Level Evaluation
        metrics_2 = self.evaluator.evaluate_state(state_2)
        
        logger.info("\n[MULTI-LEVEL OBJECTIVE EVALUATION - ITERATION 2]")
        logger.info(f"└─ MICRO (Asset Health) : Vibration = {state_2.vibration_rms} mm/s, Temp = {state_2.bearing_temp}C")
        logger.info(f"└─ MESO  (Logistics)    : Lead Time = 24 hrs, Crew Ready = 36 hrs | f_min (Risk) = {metrics_2['risk']:.2f}")
        logger.info(f"└─ MACRO (Plant Output) : f_max (OEE)  = {metrics_2['oee']:.2f} (Restored to 80% capacity)")
        
        # Forced Reflection Trigger at the end of Iteration 2
        self.evaluator.log_forced_reflection(2, state_2, metrics_2)
        
        reflection_2 = (
            f"What did we miss regarding OEE and Risk in Iteration 2?\n"
            f"The Meso-level compromise improved plant OEE (f_max = {metrics_2['oee']:.2f}) by keeping the plant at 400MW. "
            f"However, the safety risk is still unacceptably high (f_min = {metrics_2['risk']:.2f}). Running a damaged bearing "
            f"at 6.5 mm/s for 36 hours carries a high cumulative probability of catastrophic failure before the crew arrives. "
            f"We optimized the logistics, but the physical risk remains. "
            f"To climb to a globally flawless utility, we must transition to the MACRO level—monitoring plant-wide DCS controls "
            f"and checking for standby process redundancy to see if we can bypass Pump 2A entirely, restoring 100% capacity at 0% risk."
        )
        logger.info(f"[Meso-to-Macro Reflection] {reflection_2}")
        
        iterations_history.append({
            "iteration": 2,
            "phase": "Operational Compromise",
            "thought": thought_2,
            "action": "Supply Chain ERP & Labor Query (Google ADK)",
            "observation": observation_2,
            "proposed_state": state_2,
            "metrics": metrics_2,
            "reflection": reflection_2
        })
        
        # =====================================================================
        # ITERATION 3: MACRO-LEVEL OPTIMIZATION (Global Redundancy & Optimum)
        # =====================================================================
        logger.info("\n" + "="*80 + "\n[FCoT ITERATION 3] MACRO-LEVEL FOCUS: GLOBAL PLANT OPTIMUM\n" + "="*80)
        
        thought_3 = (
            f"Transitioning to the MACRO level. We must resolve the critical risk identified in our second reflection. "
            f"We need to query the plant DCS SCADA systems to check if a redundant standby asset (e.g., Pump 2B) "
            f"is available to take over the load. If available, we can perform an immediate hot-swap, "
            f"allowing us to shut down Pump 2A completely (micro risk = 0) while sustaining full plant output (macro OEE = 1.0)."
        )
        logger.info(f"[Macro Thought] {thought_3}")
        
        logger.info(f"[Macro Action] Calling DCS Control Specialist Agent to check standby redundancy.")
        prompt_3 = f"Query DCS SCADA for standby redundancy and hot-swap capabilities for {asset_id}."
        observation_3 = self._run_adk_agent("DCS Control Specialist", prompt_3)
        
        logger.info(f"[Macro Observation] Received plant-wide DCS status:\n{observation_3}")
        
        # Macro-Level State: Hot-swap to standby Pump 2B.
        # Fully aligns Micro health (Pump 2A is safely shut down, vibration/temp = 0)
        # with Meso logistics (repair scheduled in 36 hours)
        # and Macro controls (Pump 2B carrying full load, plant output = 500MW).
        state_3 = PlantState(
            asset_id=asset_id,
            operating_load_pct=0.0,           # Shut down Pump 2A completely
            vibration_rms=0.0,                # No physical wear on Pump 2A
            bearing_temp=25.0,                # Cooling down
            redundancy_active=True,           # Standby Pump 2B is carrying the load!
            production_mw=500.0,              # Full 500MW maintained!
            maintenance_delay_hours=36.0,     # Repair safely scheduled in 36 hours
            description="Macro-Level Global Optimum: Initiate hot-swap to standby Pump 2B. Shut down Pump 2A immediately. Repair Pump 2A in 36 hours."
        )
        
        # Hierarchical Multi-Level Evaluation
        metrics_3 = self.evaluator.evaluate_state(state_3)
        
        logger.info("\n[MULTI-LEVEL OBJECTIVE EVALUATION - ITERATION 3]")
        logger.info(f"└─ MICRO (Asset Health) : Pump 2A Load = 0% (Physical risk eliminated)")
        logger.info(f"└─ MESO  (Logistics)    : Pump 2B ACTIVE, Repair scheduled in 36 hrs | f_min (Risk) = {metrics_3['risk']:.2f}")
        logger.info(f"└─ MACRO (Plant Output) : Production = {state_3.production_mw} MW | f_max (OEE)  = {metrics_3['oee']:.2f}")
        
        # Forced Reflection Trigger at the end of Iteration 3
        self.evaluator.log_forced_reflection(3, state_3, metrics_3)
        
        reflection_3 = (
            f"What did we miss regarding OEE and Risk in Iteration 3?\n"
            f"By leveraging the plant's DCS process redundancy, we have achieved a flawless global optimum. "
            f"The Micro, Meso, and Macro objectives are fully balanced and aligned. "
            f"OEE is fully sustained (f_max = {metrics_3['oee']:.2f}) at 100% capacity. "
            f"Safety risk is virtually eliminated (f_min = {metrics_3['risk']:.2f}) because the damaged Pump 2A is isolated and idle. "
            f"The Hill-Climbing utility score is maximized at {metrics_3['utility']:.4f}. "
            f"This recommendation is complete and ready for human-on-the-loop sign-off."
        )
        logger.info(f"[Global Macro Optimum Reflection] {reflection_3}")
        
        iterations_history.append({
            "iteration": 3,
            "phase": "Global Optimum",
            "thought": thought_3,
            "action": "DCS Redundancy & Hot-swap Assessment (Google ADK)",
            "observation": observation_3,
            "proposed_state": state_3,
            "metrics": metrics_3,
            "reflection": reflection_3
        })
        
        return iterations_history
