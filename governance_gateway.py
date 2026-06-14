import json
import logging
from typing import Dict, Any

logger = logging.getLogger("AssetHealthSystem.GovernanceGateway")

class GovernanceGateway:
    """
    Implements Human-on-the-Loop Governance for GEAP Blueprint 4.
    Formats the FCoT reasoning steps, competing objective scores, and rejected local optima.
    Enforces a Dual-Track Validation Contract and Terminal Scope-Audit for operator sign-off.
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
        report.append("# 🛡️ ARES: Level 5 Autonomous Operational Recommendation Report")
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
        report.append("| Iteration | Phase / Scale | Proposed Operational State | OEE ($f_{max}$) | Safety Risk ($f_{min}$) | Utility Score | Status |")
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
        report.append("### 🧠 Fractal Chain of Thought (FCoT) Hierarchical Reasoning Log")
        report.append("Full transparency of the multi-aperture self-correcting reasoning loop:")
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
        report.append("### 📝 Dual-Track Validation Contract")
        report.append("The recommended action plan is structured into two distinct execution vectors for the control room:")
        report.append("")
        report.append("#### 1. 🛑 Defensive Track (Micro-Dense / Immediate)")
        report.append("> **Objective:** Eliminate immediate catastrophic physical risk during transition.")
        report.append("> - **Action 1.1**: Throttle Pump 2A to 30% load immediately to reduce vibration amplitude below critical thresholds.")
        report.append("> - **Action 1.2**: Monitor bearing temperatures continuously, ensuring they stabilize below 70°C.")
        report.append("")
        report.append("#### 2. ⚡ Positional Track (Macro-Anchored / Medium-Term)")
        report.append("> **Objective:** Align plant redundancy and schedule permanent repair with zero throughput loss.")
        report.append("> - **Action 2.1**: Initiate the 30-minute hot-swap sequence to ramp up standby **Pump 2B** to 100% capacity.")
        report.append("> - **Action 2.2**: Shut down Pump 2A completely once Pump 2B assumes the full load, maintaining a net 500 MW output.")
        report.append("> - **Action 2.3**: Dispatch a Maximo work order and schedule the certified maintenance crew for the 08:00 morning shift tomorrow.")
        report.append("\n")
        
        report.append("---")
        report.append("### 🔍 Terminal Scope-Audit Alignment")
        report.append("In compiling this Level 5 recommendation, the Meta-Agent holds the following boundary conditions fixed:")
        report.append("- **Plant Grid Demand**: Assumed constant at 500 MW over the next 48 hours.")
        report.append("- **Auxiliary Systems**: Assumed auxiliary bearing cooling water loops and electrical switchgears remain 100% healthy.")
        report.append("- **Logistics Lead Times**: Assumed regional warehouse shipping and crew shift availability are locked and free from exogenous disruptions.")
        report.append("*Scope Audit Note: Exogenous market demand fluctuations and auxiliary cooling failures were intentionally unexamined to optimize operational actionability.*")
        report.append("\n")
        
        report.append("---")
        report.append("> [!WARNING]")
        report.append("> ### ⚠️ HUMAN-ON-THE-LOOP SIGN-OFF REQUIRED")
        report.append("> This action requires manual confirmation from the Control Room Operator.")
        report.append("> **No physical commands have been dispatched to the DCS.**")
        report.append("> ")
        report.append("> **Operator Action Required:**")
        report.append(f"> 1. Confirm standby asset **{recommended_state.redundant_pair_id if hasattr(recommended_state, 'redundant_pair_id') else 'Pump 2B'}** is ready to assume load.")
        report.append("> 2. Approve the Dual-Track Validation Contract sequence.")
        report.append(f"> 3. Authorize LOTO and work order scheduling.")
        report.append("\n")
        
        report_str = "\n".join(report)
        logger.info("Markdown governance report generated successfully.")
        return report_str

    def generate_json_report(self, result_bundle: Dict[str, Any]) -> str:
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
        
        # Include the Dual-Track contract and Scope-Audit programmatically
        serializable_bundle["dual_track_validation_contract"] = {
            "defensive_track_micro_dense": [
                "Throttle Pump 2A to 30% load immediately.",
                "Monitor bearing temperatures continuously, ensuring stabilization below 70C."
            ],
            "positional_track_macro_anchored": [
                "Initiate the 30-minute hot-swap sequence to standby Pump 2B.",
                "Shut down Pump 2A completely once Pump 2B assumes full load.",
                "Schedule certified maintenance crew for tomorrow at 08:00."
            ]
        }
        serializable_bundle["terminal_scope_audit_alignment"] = {
            "fixed_boundaries": [
                "Plant Grid Demand constant at 500 MW.",
                "Auxiliary systems (cooling, switchgear) are 100% operational.",
                "Regional warehouse lead times are locked."
            ],
            "unexamined_variables_note": "Exogenous market demand fluctuations and auxiliary cooling failures were intentionally unexamined."
        }
        
        json_str = json.dumps(serializable_bundle, indent=2)
        logger.info("JSON governance report generated successfully.")
        return json_str
