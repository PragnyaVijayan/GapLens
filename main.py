#!/usr/bin/env python3
"""
Main entry point for GapLens - Skill Gap Management System.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import SkillGapOrchestrator
from src.agents import (
    ProjectIntakeAgent, SkillExtractionAgent, WorkforceDataAgent,
    GapAnalysisAgent, RecommendationAgent
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_workflow():
    """Run the complete skill gap management workflow."""
    try:
        logger.info("Starting GapLens workflow...")
        
        orchestrator = SkillGapOrchestrator()
        results = await orchestrator.run_workflow()
        
        if results["success"]:
            logger.info("✅ Workflow completed successfully!")
            
            summary = results.get("summary", {})
            if summary:
                logger.info("📊 Workflow Summary:")
                logger.info(f"   Projects analyzed: {summary.get('final_results', {}).get('projects_analyzed', 0)}")
                logger.info(f"   Skills extracted: {summary.get('final_results', {}).get('skills_extracted', 0)}")
                logger.info(f"   Gaps identified: {summary.get('final_results', {}).get('gaps_identified', 0)}")
                logger.info(f"   Decisions created: {summary.get('final_results', {}).get('decisions_created', 0)}")
        else:
            logger.error("❌ Workflow failed!")
            if results.get("errors"):
                for error in results["errors"]:
                    logger.error(f"   Error: {error}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error running workflow: {e}")
        return {"success": False, "error": str(e)}


async def test_agents():
    """Test individual agents."""
    try:
        logger.info("🧪 Testing individual agents...")
        
        # Test each agent
        agents = [
            ("Project Intake Agent", ProjectIntakeAgent()),
            ("Skill Extraction Agent", SkillExtractionAgent()),
            ("Workforce Data Agent", WorkforceDataAgent()),
            ("Gap Analysis Agent", GapAnalysisAgent()),
            ("Recommendation Agent", RecommendationAgent())
        ]
        
        for name, agent in agents:
            logger.info(f"Testing {name}...")
            try:
                # Test agent info
                info = await agent._get_agent_info({})
                logger.info(f"   ✅ {name} is working: {info.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ {name} failed: {e}")
        
        logger.info("✅ Agent testing completed!")
        
    except Exception as e:
        logger.error(f"❌ Error testing agents: {e}")


def run_fastapi():
    """Run the FastAPI server."""
    try:
        logger.info("🚀 Starting FastAPI server...")
        
        import uvicorn
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting FastAPI server: {e}")


def run_streamlit():
    """Run the Streamlit UI."""
    try:
        logger.info("🎨 Starting Streamlit UI...")
        
        import subprocess
        import sys
        
        cmd = [sys.executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py"]
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"❌ Error starting Streamlit UI: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GapLens - Skill Gap Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py workflow          # Run complete workflow
  python main.py test-agents      # Test individual agents
  python main.py api              # Start FastAPI server
  python main.py ui               # Start Streamlit UI
  python main.py demo             # Run workflow and show results
        """
    )
    
    parser.add_argument(
        "command",
        choices=["workflow", "test-agents", "api", "ui", "demo"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🔍 GapLens - Skill Gap Management System")
    logger.info("=" * 50)
    
    try:
        if args.command == "workflow":
            asyncio.run(run_workflow())
            
        elif args.command == "test-agents":
            asyncio.run(test_agents())
            
        elif args.command == "api":
            run_fastapi()
            
        elif args.command == "ui":
            run_streamlit()
            
        elif args.command == "demo":
            logger.info("🎯 Running demo workflow...")
            results = asyncio.run(run_workflow())
            
            if results["success"]:
                logger.info("🎉 Demo completed successfully!")
                logger.info("💡 Next steps:")
                logger.info("   1. Start the API server: python main.py api")
                logger.info("   2. Start the UI: python main.py ui")
                logger.info("   3. Open http://localhost:8000/docs for API docs")
                logger.info("   4. Open http://localhost:8501 for Streamlit UI")
            else:
                logger.error("❌ Demo failed!")
                
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 