import logging
import os
from meta_agent import MetaAgent
from governance_gateway import GovernanceGateway

def setup_logging():
    # Configure logging to show timestamps, logger names, levels, and messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    setup_logging()
    
    logger = logging.getLogger("AssetHealthSystem.Main")
    logger.info("Starting Level 5 Managed Multi-Agent System Simulation...")

    # Initialize the Meta-Agent (Root Overseer)
    meta_agent = MetaAgent()
    
    # High-level operational goal from the plant manager
    goal_intent = "Mitigate Pump 2A anomaly while sustaining MW output"
    
    # Execute the intent-driven recomposition and reasoning loop
    try:
        result_bundle = meta_agent.handle_goal(goal_intent)
        
        # Pass the results through the Governance Gateway
        gateway = GovernanceGateway()
        markdown_report = gateway.generate_markdown_report(result_bundle)
        json_report = gateway.generate_json_report(result_bundle)
        
        # Write reports to the workspace
        workspace_dir = os.path.dirname(os.path.abspath(__file__))
        md_file_path = os.path.join(workspace_dir, "autonomous_recommendation_report.md")
        json_file_path = os.path.join(workspace_dir, "autonomous_recommendation_report.json")
        
        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_report)
            
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(json_report)
            
        logger.info(f"Successfully wrote Markdown report to: {md_file_path}")
        logger.info(f"Successfully wrote JSON report to: {json_file_path}")
        
        # Print the Markdown report to the console for the operator to view
        print("\n" + "="*80)
        print("                   GENERATED OPERATOR GOVERNANCE REPORT")
        print("="*80)
        print(markdown_report)
        print("="*80 + "\n")
        
    except Exception as e:
        logger.exception("An error occurred during simulation execution:")

if __name__ == "__main__":
    main()
