"""
Multi-Agent Cognitive Architecture - Main Entry Point
"""

import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from core import make_all_agent_llms
from core.workflow import MultiAgentWorkflow

from config import DEFAULT_DISPLAY_LIMIT, FULL_OUTPUT_DISPLAY_LIMIT

def main():
    """Main entry point for the multi-agent system."""
    parser = argparse.ArgumentParser(description="Multi-Agent Cognitive Architecture")
    parser.add_argument("--question", help="User query to process")
    parser.add_argument("--backend", choices=["anthropic", "groq", "fake"], 
                       default=os.getenv("BACKEND", "anthropic"),
                       help="LLM backend to use")

    parser.add_argument("--test", action="store_true", 
                       help="Run built-in tests with FakeLLM")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--full-output", action="store_true",
                       help="Show full content without truncation")
    
    args = parser.parse_args()
    
    # Reasoning patterns are built into each agent    
    if args.test:
        print("🧪 Running tests with FakeLLM backend...")
        run_tests()
        return
    
    if args.interactive:
        run_interactive(args.backend, args.full_output)
        return
    
    if not args.question:
        print("❌ Please provide a question with --question or use --interactive mode")
        parser.print_help()
        return
    
    # Run the workflow
    run_workflow(args.question, args.backend, args.full_output)

def run_workflow(question: str, backend: str, full_output: bool = False):
    """Run the multi-agent workflow for a given question."""
    try:
        print(f"🚀 Starting Multi-Agent Workflow with {backend} backend...")
        print("🧠 Each agent uses its specialized reasoning pattern:")
        print("   - Perception: Chain of Thought (COT) - Extracts intent and entities")
        print("   - Research: REWOO - Gathers project and team data")
        print("   - Analysis: REACT - Analyzes skill gaps")
        print("   - Decision: Tree of Thoughts (TOT) - Makes final recommendations")
        print("   - Orchestrator: Multi-agent reasoning - Coordinates workflow")
        print("   - Data Client: MCP pattern - Accesses server-side data sources")
        
        # Create specialized LLMs for each agent
        agent_llms = make_all_agent_llms(backend)
        
        # Create and run workflow with appropriate display limit
        display_limit = FULL_OUTPUT_DISPLAY_LIMIT if full_output else DEFAULT_DISPLAY_LIMIT
        workflow = MultiAgentWorkflow(
            agent_llms["perception"],
            agent_llms["research"], 
            agent_llms["analysis"],
            agent_llms["decision"],
            agent_llms["orchestrator"],
            display_limit
        )
        result = workflow.run(question)
        
        # Display final results
        print("\n" + "=" * 60)
        print("🎯 FINAL RECOMMENDATION")
        print("=" * 60)
        decision = result.get("decision", "No decision produced.")
        if full_output or len(decision) <= FULL_OUTPUT_DISPLAY_LIMIT:
            print(decision)
        else:
            print(f"{decision[:FULL_OUTPUT_DISPLAY_LIMIT]}...")
            print(f"\n... (truncated, full length: {len(decision)} chars)")
            print("Use --full-output to see complete content")
        
        print("\n" + "=" * 60)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Intent: {result.get('intent', 'Unknown')}")
        print(f"Entities: {', '.join(result.get('entities', []))}")
        print(f"Normalized Question: {result.get('normalized_question', 'Not available')}")
        print(f"Analysis: {'✓' if result.get('analysis') else '✗'}")
        print(f"Decision: {'✓' if result.get('decision') else '✗'}")
        print("Reasoning Patterns: Built into each agent")
        
        # Show full content if requested
        if full_output:
            print("\n" + "=" * 60)
            print("📋 FULL CONTENT")
            print("=" * 60)
            
            print("\n🔍 PERCEPTION:")
            print(f"Intent: {result.get('intent')}")
            print(f"Entities: {result.get('entities')}")
            print(f"Normalized Question: {result.get('normalized_question')}")
            print(f"Context: {result.get('context', 'No context available')}")
            
            print("\n🧠 ANALYSIS:")
            print(result.get('analysis', 'No analysis available'))
            
            print("\n🎯 DECISION:")
            print(result.get('decision', 'No decision available'))
        
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        print("\n💡 Troubleshooting tips:")
        if backend == "groq":
            print("   - Make sure GROQ_API_KEY is set in .env file")
            print("   - Check your Groq API key is valid")
            print("   - Verify you have sufficient Groq credits")

def run_interactive(backend: str, full_output: bool = False):
    """Run the system in interactive mode."""
    try:
        print(f"🤖 Multi-Agent System Interactive Mode ({backend} backend)")
        print("🧠 Each agent uses its specialized reasoning pattern")
        print("Type 'quit' or 'exit' to stop")
        if full_output:
            print("📋 Full output mode enabled")
        print("=" * 50)
        
        # Create specialized LLMs for each agent
        agent_llms = make_all_agent_llms(backend)
        display_limit = FULL_OUTPUT_DISPLAY_LIMIT if full_output else DEFAULT_DISPLAY_LIMIT
        workflow = MultiAgentWorkflow(
            agent_llms["perception"],
            agent_llms["research"], 
            agent_llms["analysis"],
            agent_llms["decision"],
            agent_llms["orchestrator"],
            display_limit
        )
        
        while True:
            try:
                question = input("\n🤔 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                # Run workflow
                workflow.run(question)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start interactive mode: {e}")

def run_tests():
    """Run basic tests to verify the system works."""
    try:
        print("🧪 Creating test workflow...")
        print("🧠 Each agent uses its specialized reasoning pattern")
        
        # Use fake backend for tests
        agent_llms = make_all_agent_llms("fake")
        workflow = MultiAgentWorkflow(
            agent_llms["perception"],
            agent_llms["research"], 
            agent_llms["analysis"],
            agent_llms["decision"],
            agent_llms["orchestrator"]
        )
        
        # Test questions
        test_questions = [
            "Compare MacBook Air vs Pro for development",
            "What are the best Python web frameworks?",
            "How should I choose between different programming languages?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🧪 Test {i}: {question}")
            try:
                result = workflow.run(question, verbose=False)
                
                # Verify outputs - updated to match cleaned agents
                assert result.get("intent"), "Intent missing"
                assert result.get("entities"), "Entities missing"
                assert result.get("normalized_question"), "Normalized question missing"
                assert result.get("analysis"), "Analysis missing"
                assert result.get("decision"), "Decision missing"
                
                print(f"   ✅ Test {i} passed")
                
            except Exception as e:
                print(f"   ❌ Test {i} failed: {e}")
                return
        
        print("\n🎉 All tests passed! The multi-agent system is working correctly.")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")

if __name__ == "__main__":
    main() 