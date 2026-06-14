import json
import logging
from typing import Dict, Any

logger = logging.getLogger("AssetHealthSystem.GovernanceGateway")

class GovernanceGateway:
    """
    Implements Human-on-the-Loop Governance for GEAP Blueprint 4.
    Ensures absolute transparency by formatting the FCoT reasoning steps, 
    competing objectives, and rejected local optima into structured reports.
    Prevents automatic command execution without operator sign-off.
    """
    def __init__(self):
        logger.info("Initializing Governance Gateway...")

    def generate_markdown_report(self, result_bundle: Dict[str, Any]) -> str:
        parsed_intent = result_bundle["parsed_intent"]
        assembled_team = result_bundle["assembled_team"]
        fcot_iterations = result_bundle["fcot_iterations"]
        recommended_state = result_bundle["recommended_state"]
        recommended_metrics = result_bundle["recommended_metrics"]
        
        report = []
        report.append("# 🛡️ Level 5 Autonomous Operational Recommendation Report")
        report.append("## GEAP Blueprint 4: Governed Eco-System Gateway\n")
        
        report.append("---")
        report.append("### 📋 Executive Summary")
        report.append(f"**Parsed Business Intent:** *\"{parsed_intent['original_intent']}\"*")
        report.append(f"**Target Asset:** `{parsed_intent['target_asset']}`")
        report.append(f"**Assembled Meso-Agents:** `{', '.join(assembled_team)}`")
        report.append(f"**Final Recommendation:** **{recommended_state.description}**\n")
        
        report.append("---")
        report.append("### 📈 Dual-Objective Optimization Comparison (Hill-Climbing Path)")
        report.append("The system evaluated multiple local optima before reaching the global optimum:")
        report.append("")
        report.append("| Iteration | Phase | Proposed Operational State | OEE ($f_{max}$) | Safety Risk ($f_{min}$) | Utility Score | Status |")
        report.append("| :--- | :--- | :--- | :---: | :---: | :---: | :--- |")
        
        for it in fcot_iterations:
            state = it["proposed_state"]
            metrics = it["metrics"]
            status = "🏆 **RECOMMENDED**" if it["iteration"] == 3 else "❌ REJECTED"
            report.append(
                f"| {it['iteration']} | {it['phase']} | {state.description} | "
                f"{metrics['oee']:.2f} | {metrics['risk']:.2f} | {metrics['utility']:.2f} | {status} |"
            )
        report.append("\n")
        
        report.append("---")
        report.append("### 🧠 Fractal Chain of Thought (FCoT) Reasoning Log")
        report.append("Full transparency of the self-similar reasoning loop:")
        report.append("")
        
        for it in fcot_iterations:
            report.append(f"#### 🔄 Iteration {it['iteration']}: {it['phase']}")
            report.append(f"- **Thought:** {it['thought']}")
            report.append(f"- **Action:** {it['action']}")
            report.append(f"- **Observation:** {it['observation']}")
            report.append(f"- **State Metrics:** OEE = `{it['metrics']['oee']:.3f}`, Safety Risk = `{it['metrics']['risk']:.3f}`")
            report.append(f"- **Reflection & Evaluation:** *{it['reflection']}*")
            report.append("")
            
        report.append("---")
        report.append("> [!WARNING]")
        report.append("> ### ⚠️ HUMAN-ON-THE-LOOP SIGN-OFF REQUIRED")
        report.append("> This action requires manual confirmation from the Control Room Operator.")
        report.append("> **No physical commands have been dispatched to the DCS.**")
        report.append("> ")
        report.append("> **Operator Action Required:**")
        report.append(f"> 1. Confirm standby asset **{recommended_state.redundant_pair_id if hasattr(recommended_state, 'redundant_pair_id') else 'Pump 2B'}** is ready to assume load.")
        report.append("> 2. Approve the 30-minute hot-swap sequence.")
        report.append(f"> 3. Authorize lockout/tagout (LOTO) and work order scheduling for **{parsed_intent['target_asset']}**.")
        report.append("\n")
        
        report_str = "\n".join(report)
        logger.info("Markdown governance report generated successfully.")
        return report_str

    def generate_json_report(self, result_bundle: Dict[str, Any]) -> str:
        # Convert dataclass states to dictionaries for JSON serialization
        serializable_bundle = {
            "parsed_intent": result_bundle["parsed_intent"],
            "assembled_team": result_bundle["assembled_team"],
            "recommended_metrics": result_bundle["recommended_metrics"],
            "fcot_iterations": []
        }
        
        for it in result_bundle["fcot_iterations"]:
            state = it["proposed_state"]
            serializable_bundle["fcot_iterations"].append({
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
            
        # Add recommended state dict
        rec_state = result_bundle["recommended_state"]
        serializable_bundle["recommended_state"] = {
            "asset_id": rec_state.asset_id,
            "operating_load_pct": rec_state.operating_load_pct,
            "vibration_rms": rec_state.vibration_rms,
            "bearing_temp": rec_state.bearing_temp,
            "redundancy_active": rec_state.redundancy_active,
            "production_mw": rec_state.production_mw,
            "maintenance_delay_hours": rec_state.maintenance_delay_hours,
            "description": rec_state.description
        }
        
        json_str = json.dumps(serializable_bundle, indent=2)
        logger.info("JSON governance report generated successfully.")
        return json_str
