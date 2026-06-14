import math
import logging
from dataclasses import dataclass
from typing import Dict, Any

logger = logging.getLogger("AssetHealthSystem.Evaluator")

@dataclass
class PlantState:
    asset_id: str
    operating_load_pct: float     # 0.0 (Shutdown) to 100.0 (Full Load)
    vibration_rms: float          # mm/s RMS
    bearing_temp: float           # °C
    redundancy_active: bool       # Is Pump 2B carrying the load?
    production_mw: float          # Current total plant output (nominal 500 MW)
    maintenance_delay_hours: float # Hours until repair starts
    description: str = ""

class DualObjectiveEvaluator:
    """
    Evaluates plant states against two competing objective functions:
    1. Maximize OEE (Overall Equipment Effectiveness) - f_max
    2. Minimize Safety Risk / Operational Penalty - f_min
    
    Provides a Hill-Climbing utility metric to find the global optimum.
    """
    
    def __init__(self, nominal_mw: float = 500.0):
        self.nominal_mw = nominal_mw
        logger.info("Initializing Dual-Objective Evaluator...")

    def calculate_oee(self, state: PlantState) -> float:
        """
        Calculates f_max(S) = Availability * Performance * Quality.
        Values are scaled between 0.0 and 1.0.
        """
        # 1. Availability (A): Fraction of planned operating time the asset is available.
        # If the asset is shut down and no redundancy is active, availability is reduced.
        # If redundancy is active, availability remains 1.0 because the system is fully operational.
        if state.redundancy_active:
            availability = 1.0
        else:
            # If no redundancy, availability scales with primary asset's operating capacity
            availability = state.operating_load_pct / 100.0
            
        # 2. Performance (P): Actual production vs. design capacity (nominal_mw)
        performance = min(1.0, max(0.0, state.production_mw / self.nominal_mw))
        
        # 3. Quality (Q): Process stability and health index.
        # High vibration and high temperatures degrade quality/stability of the process.
        # If the asset is shut down, its local vibration/temp doesn't impact quality.
        if state.operating_load_pct == 0.0:
            quality = 1.0
        else:
            # Penalty increases with vibration above nominal (2.0 mm/s) and temp above nominal (50C)
            vib_penalty = max(0.0, (state.vibration_rms - 2.0) / 15.0) * 0.4
            temp_penalty = max(0.0, (state.bearing_temp - 50.0) / 50.0) * 0.2
            quality = max(0.1, min(1.0, 1.0 - (vib_penalty + temp_penalty)))
            
        oee = availability * performance * quality
        
        logger.debug(
            f"OEE Calculation -> A: {availability:.2f}, P: {performance:.2f}, Q: {quality:.2f} | Total f_max: {oee:.4f}"
        )
        return oee

    def calculate_safety_risk(self, state: PlantState) -> float:
        """
        Calculates f_min(S) = R_vib * R_temp * R_time * (1 - C_redundancy).
        Values are scaled between 0.0 and 1.0.
        """
        # If the asset is completely shut down, local physical risks drop to near zero
        if state.operating_load_pct == 0.0:
            r_vib = 0.0
            r_temp = 0.0
        else:
            # Vibration Risk: Exponential curve. Significant risk above 7.1 mm/s.
            # RMS of 12.8 mm/s will yield ~0.95 risk.
            r_vib = 1.0 - math.exp(-0.23 * state.vibration_rms)
            
            # Temperature Risk: Bearing temperature risk starts climbing above 60C.
            # 87.5C will yield ~0.90 risk.
            delta_temp = max(0.0, state.bearing_temp - 50.0)
            r_temp = 1.0 - math.exp(-0.06 * delta_temp)
            
        # Time Risk: Cumulative risk of running in an anomalous state before repair.
        # Delay of 36 hours yields ~0.75 risk. Immediate repair (0 hours) yields 0.0 risk.
        r_time = 1.0 - math.exp(-0.04 * state.maintenance_delay_hours)
        
        # Primary Asset Risk
        primary_risk = max(r_vib, r_temp) * (0.3 + 0.7 * r_time) if state.operating_load_pct > 0.0 else 0.0
        
        # Redundancy Discount: If we have a healthy standby running, the plant's overall
        # operational safety risk is significantly lower even if the primary is still idling/cooling.
        if state.redundancy_active:
            # Risk is heavily discounted since the load is carried by a healthy asset
            system_risk = primary_risk * 0.05
        else:
            system_risk = primary_risk
            
        logger.debug(
            f"Risk Calculation -> R_vib: {r_vib:.2f}, R_temp: {r_temp:.2f}, R_time: {r_time:.2f} | Total f_min: {system_risk:.4f}"
        )
        return system_risk

    def evaluate_state(self, state: PlantState) -> Dict[str, float]:
        oee = self.calculate_oee(state)
        risk = self.calculate_safety_risk(state)
        
        # Utility Score (Hill-Climbing metric): We want to maximize OEE and minimize Risk.
        # Max utility is 1.0 (perfect OEE, 0 risk). Min utility is -1.0.
        utility = oee - risk
        
        return {
            "oee": oee,
            "risk": risk,
            "utility": utility
        }

    def log_forced_reflection(self, iteration: int, state: PlantState, metrics: Dict[str, float]):
        """
        Forced reflection trigger. Outputs the exact requested prompt format and logs the evaluation.
        """
        logger.warning(
            f"\n[FORCED REFLECTION - ITERATION {iteration}]\n"
            f"Evaluating proposed state: '{state.description}'\n"
            f"-> Overall Equipment Effectiveness (OEE) [f_max]: {metrics['oee']:.4f}\n"
            f"-> Safety Risk / Penalty Score   [f_min]: {metrics['risk']:.4f}\n"
            f"-> Composite Utility Score               : {metrics['utility']:.4f}\n"
            f"PROMPT: \"What did you miss in this state regarding OEE and Risk?\"\n"
        )
