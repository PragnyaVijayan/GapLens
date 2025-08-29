"""
Workflow Orchestration - Manages the multi-agent workflow execution with LangGraph
"""

from typing import Dict, Any
from core.memory_system import SessionMemory, get_memory_system
from core.langgraph_workflow import create_workflow, set_llms, WorkflowState
from config import DEFAULT_DISPLAY_LIMIT, LLM_OUTPUT_SHOW_MEMORY, WORKFLOW_VERBOSE

class MultiAgentWorkflow:
    """Orchestrates the execution of the multi-agent cognitive architecture using LangGraph."""
    
    def __init__(self, perception_llm, reasoner_llm, display_limit: int = None):
        self.perception_llm = perception_llm
        self.reasoner_llm = reasoner_llm
        self.display_limit = display_limit or DEFAULT_DISPLAY_LIMIT
        
        # Set LLMs for the workflow
        set_llms(perception_llm, reasoner_llm)
        
        # Create LangGraph workflow
        self.workflow = create_workflow(perception_llm, reasoner_llm, display_limit)
        
        # Get memory system
        self.long_term_memory, self.memory_logger = get_memory_system()
    
    def run(self, question: str, verbose: bool = None, project_id: str = None, scope: str = "company") -> Dict[str, Any]:
        """Run the complete multi-agent workflow using LangGraph."""
        verbose = verbose if verbose is not None else WORKFLOW_VERBOSE
        
        try:
            if verbose:
                self._print_workflow_start(question)
            
            # Initialize session memory
            session_memory = SessionMemory()
            
            # Store project-specific parameters in session memory
            if project_id:
                session_memory.update_session_data("project_id", project_id)
                session_memory.update_session_data("scope", scope)
                if verbose:
                    print(f"🎯 Project-specific analysis: {project_id} (scope: {scope})")
            
            # Initialize state
            initial_state = WorkflowState(
                question=question,
                memory=session_memory,
                intent="",
                entities=[],
                normalized_question="",
                research_facts=[],
                analysis="",
                decision="",
                step="",
                project_id=project_id,
                scope=scope
            )
            
            if verbose:
                print("🚀 Starting LangGraph workflow...")
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Save session and log completion
            if verbose:
                self._print_workflow_complete()
                self._save_and_display_session(session_memory)
            
            # Log workflow completion
            self._log_workflow_completion(question, session_memory)
            
            return result
            
        except Exception as e:
            print(f"❌ Error running workflow: {e}")
            raise
    
    def _print_workflow_start(self, question: str):
        """Print workflow start information."""
        print(f"🤔 Processing: {question}")
        print("🧠 Memory System: Initializing session...")
    
    def _print_workflow_complete(self):
        """Print workflow completion information."""
        print("✅ Workflow completed successfully")
        print("📊 Results saved to session memory")
    
    def _save_and_display_session(self, session_memory: SessionMemory):
        """Save session and display relevant information."""
        session_file = self.long_term_memory.save_session(session_memory)
        
        if session_file and LLM_OUTPUT_SHOW_MEMORY:
            print(f"✅ Session saved to: {session_file}")
            self._display_memory_statistics(session_memory, session_file)
        elif not LLM_OUTPUT_SHOW_MEMORY:
            print("💾 Session saved to long-term memory (details hidden)")
        else:
            print("❌ Failed to save session to long-term memory")
    
    def _display_memory_statistics(self, session_memory: SessionMemory, session_file: str):
        """Display memory statistics for the session."""
        print(f"📊 Memory Statistics:")
        print(f"   - Session ID: {session_memory.session_id}")
        print(f"   - Total Entries: {len(session_memory.entries)}")
        print(f"   - Agents Used: {', '.join(set(entry.agent for entry in session_memory.entries))}")
        print(f"   - Reasoning Patterns: {', '.join(set(entry.reasoning_pattern.value for entry in session_memory.entries))}")
        
        # Show memory file size
        import os
        if os.path.exists(session_file):
            size = os.path.getsize(session_file)
            print(f"   - File Size: {size} bytes")
    
    def _log_workflow_completion(self, question: str, session_memory: SessionMemory):
        """Log workflow completion to memory system."""
        self.memory_logger.log_memory_operation("workflow_complete", {
            "question": question,
            "session_id": session_memory.session_id,
            "total_entries": len(session_memory.entries)
        })
        print("📝 Workflow completion logged to memory system")