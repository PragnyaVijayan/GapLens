"""
Enhanced Memory System - Handles both short-term session memory and long-term persistent memory
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryType(Enum):
    """Types of memory storage."""
    SESSION = "session"
    LONG_TERM = "long_term"
    LOGS = "logs"

class ReasoningPattern(Enum):
    """Reasoning patterns used by agents."""
    REWOO = "rewoo"  # Reason, Evaluate, Work, Observe, Optimize
    REACT = "react"  # Reason, Evaluate, Act, Check, Think
    COT = "cot"      # Chain of Thought
    TOT = "tot"      # Tree of Thoughts
    AGENT = "agent"  # Agent-based reasoning

@dataclass
class MemoryEntry:
    """Individual memory entry with metadata."""
    id: str
    timestamp: str
    agent: str
    content: Any
    reasoning_pattern: ReasoningPattern
    reasoning_steps: List[str]
    confidence: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['reasoning_pattern'] = self.reasoning_pattern.value
        return data

class SessionMemory:
    """Short-term memory for active sessions."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.entries: List[MemoryEntry] = []
        self.session_data: Dict[str, Any] = {
            "intent": None,
            "entities": [],
            "normalized_question": None,
            "research_facts": [],
            "analysis": None,
            "decision": None,
            "current_step": None
        }
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def add_entry(self, agent: str, content: Any, reasoning_pattern: ReasoningPattern, 
                  reasoning_steps: List[str], confidence: float = 0.8, metadata: Dict[str, Any] = None):
        """Add a new memory entry."""
        entry = MemoryEntry(
            id=f"{agent}_{len(self.entries)}_{datetime.now().strftime('%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            agent=agent,
            content=content,
            reasoning_pattern=reasoning_pattern,
            reasoning_steps=reasoning_steps or [],
            confidence=confidence,
            metadata=metadata or {}
        )
        self.entries.append(entry)
        self.last_updated = datetime.now().isoformat()
        return entry
    
    def update_session_data(self, key: str, value: Any):
        """Update session data."""
        if key in self.session_data:
            self.session_data[key] = value
            self.last_updated = datetime.now().isoformat()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from session data with optional default."""
        return self.session_data.get(key, default)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "total_entries": len(self.entries),
            "agents_used": list(set(entry.agent for entry in self.entries)),
            "reasoning_patterns": list(set(entry.reasoning_pattern.value for entry in self.entries)),
            "session_data": self.session_data.copy()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "entries": [entry.to_dict() for entry in self.entries],
            "session_data": self.session_data.copy()
        }

class LongTermMemory:
    """Long-term memory for persistent storage and learning."""
    
    def __init__(self, storage_dir: str = "infrastructure/memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir = self.storage_dir / "sessions"
        self.long_term_dir = self.storage_dir / "long_term"
        self.logs_dir = self.storage_dir / "logs"
        
        # Create directories
        for dir_path in [self.sessions_dir, self.long_term_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: SessionMemory) -> Optional[str]:
        """Save a session to the sessions directory."""
        try:
            filename = f"{session.session_id}.json"
            filepath = self.sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            return str(filepath)
        except Exception as e:
            print(f"❌ Error saving session: {e}")
            return None
    
    def load_session(self, session_id: str) -> Optional[SessionMemory]:
        """Load a session from the sessions directory."""
        try:
            filepath = self.sessions_dir / f"{session_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct session
            session = SessionMemory(data["session_id"])
            session.created_at = data["created_at"]
            session.last_updated = data["last_updated"]
            session.session_data = data["session_data"]
            
            # Reconstruct entries
            for entry_data in data["entries"]:
                entry = MemoryEntry(
                    id=entry_data["id"],
                    timestamp=entry_data["timestamp"],
                    agent=entry_data["agent"],
                    content=entry_data["content"],
                    reasoning_pattern=ReasoningPattern(entry_data["reasoning_pattern"]),
                    reasoning_steps=entry_data["reasoning_steps"],
                    confidence=entry_data["confidence"],
                    metadata=entry_data["metadata"]
                )
                session.entries.append(entry)
            
            return session
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None

class MemoryLogger:
    """Handles logging for the memory system."""
    
    def __init__(self, logs_dir: str = "infrastructure/memory/logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration."""
        log_file = self.logs_dir / f"memory_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("GapLensMemory")
    
    def log_memory_operation(self, operation: str, details: Dict[str, Any]):
        """Log memory operations."""
        self.logger.info(f"Memory Operation: {operation} - {details}")
    
    def log_agent_reasoning(self, agent: str, reasoning_pattern: ReasoningPattern, steps: List[str]):
        """Log agent reasoning steps."""
        self.logger.info(f"Agent {agent} used {reasoning_pattern.value} reasoning:")
        for i, step in enumerate(steps, 1):
            self.logger.info(f"  Step {i}: {step}")

# Global instances
long_term_memory = LongTermMemory()
memory_logger = MemoryLogger()

def get_memory_system():
    """Get the global memory system instances."""
    return long_term_memory, memory_logger
