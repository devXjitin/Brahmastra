"""
Simple and clean logging utility for Brahmastra agents.
Inspired by LangChain's clean verbose output style.
"""

from typing import Optional, Any
import json
import sys
import os


class AgentLogger:
    """
    Clean, minimal logger for agent operations.
    Provides a LangChain-style verbose output with color support.
    """
    
    # ANSI colors for terminal (vibrant, professional palette)
    GRAY = '\033[90m'           # Dim text for labels
    GREEN = '\033[92m'          # Bright green for success
    BLUE = '\033[94m'           # Bright blue for thoughts
    YELLOW = '\033[93m'         # Bright yellow for warnings/actions
    CYAN = '\033[96m'           # Bright cyan for execution
    MAGENTA = '\033[95m'        # Bright magenta for special events
    RED = '\033[91m'            # Bright red for errors
    BOLD = '\033[1m'            # Bold text
    DIM = '\033[2m'             # Dim text
    RESET = '\033[0m'           # Reset all formatting
    
    def __init__(self, verbose: bool = False, agent_name: str = "Agent"):
        """
        Initialize logger.
        
        Args:
            verbose: Enable logging output
            agent_name: Name of the agent for context
        """
        self.verbose = verbose
        self.agent_name = agent_name
        self.colors_enabled = self._check_color_support()
    
    def _check_color_support(self) -> bool:
        """
        Check if terminal supports colors.
        Returns True if colors should be enabled.
        """
        # Check if running in a terminal
        if not sys.stdout.isatty():
            return False
        
        # Windows: Enable ANSI escape sequences
        if sys.platform == "win32":
            try:
                # Enable ANSI colors in Windows Console
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                # Fallback: Check if running in Windows Terminal or VS Code
                return bool(os.environ.get('WT_SESSION') or os.environ.get('TERM_PROGRAM') == 'vscode')
        
        # Unix/Linux/Mac: Check TERM variable
        return os.environ.get('TERM', 'dumb') != 'dumb'
    
    def _print(self, message: str, prefix: str = "", color: str = ""):
        """Internal print with optional color and prefix."""
        if self.verbose:
            if color and self.colors_enabled:
                print(f"{color}{prefix}{message}{self.RESET}")
            else:
                print(f"{prefix}{message}")
    
    def agent_start(self, query: str):
        """Log agent starting with user query."""
        if self.verbose:
            if self.colors_enabled:
                print(f"\n{self.BOLD}{self.CYAN}> Entering {self.agent_name}{self.RESET}")
                print(f"  {self.GRAY}Input:{self.RESET} {query}")
            else:
                print(f"\n> Entering {self.agent_name}")
                print(f"  Input: {query}")
    
    def agent_end(self, output: str):
        """Log agent completion with final output."""
        if self.verbose:
            if self.colors_enabled:
                print(f"\n{self.BOLD}{self.GREEN}> Finished {self.agent_name}{self.RESET}")
                print(f"  {self.GRAY}Output:{self.RESET} {output}")
            else:
                print(f"\n> Finished {self.agent_name}")
                print(f"  Output: {output}")
    
    def iteration(self, num: int):
        """Log iteration number."""
        if self.verbose:
            if self.colors_enabled:
                print(f"\n{self.GRAY}[{num}] Iteration{self.RESET}")
            else:
                print(f"\n[{num}] Iteration")
    
    def thought(self, thought: str):
        """Log agent's thought process."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.BLUE}Thought:{self.RESET} {thought}")
            else:
                print(f"  Thought: {thought}")
    
    def action(self, tool_name: str, tool_input: Any = None):
        """Log tool execution."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.YELLOW}Action:{self.RESET} {tool_name}")
            else:
                print(f"  Action: {tool_name}")
            
            if tool_input:
                # Clean input display
                if isinstance(tool_input, dict):
                    input_str = json.dumps(tool_input, ensure_ascii=False)
                else:
                    input_str = str(tool_input)
                
                if self.colors_enabled:
                    print(f"  {self.GRAY}Input:{self.RESET} {input_str}")
                else:
                    print(f"  Input: {input_str}")
    
    def observation(self, result: Any):
        """Log tool execution result."""
        if self.verbose:
            if isinstance(result, dict):
                result_str = json.dumps(result, ensure_ascii=False, indent=2)
            else:
                result_str = str(result)
            
            # Truncate long tool results for readability
            if len(result_str) > 500:
                result_str = result_str[:500] + "..."
            
            if self.colors_enabled:
                print(f"  {self.GREEN}Observation:{self.RESET} {result_str}")
            else:
                print(f"  Observation: {result_str}")
    
    def parallel_start(self, count: int, tool_names = None):
        """Log start of execution (parallel, batch, or mixed)."""
        if self.verbose:
            message = ""
            if count == 1:
                message = "Executing tool..."
            else:
                # Analyze tool distribution
                if tool_names:
                    from collections import Counter
                    tool_counts = Counter(tool_names)
                    unique_tools = len(tool_counts)
                    
                    if unique_tools == 1:
                        # All same tool - pure batch
                        message = f"Parallel batch: {tool_names[0]} ({count} calls simultaneously)..."
                    else:
                        # Mixed execution - some tools sequential, some batch
                        batch_tools = [name for name, cnt in tool_counts.items() if cnt > 1]
                        sequential_tools = [name for name, cnt in tool_counts.items() if cnt == 1]
                        
                        if batch_tools and sequential_tools:
                            # Mixed: some batch, some sequential
                            batch_desc = ", ".join([f"{name} (×{tool_counts[name]})" for name in batch_tools])
                            seq_desc = ", ".join(sequential_tools)
                            message = f"Mixed execution: Batch [{batch_desc}] + Sequential [{seq_desc}]..."
                        elif batch_tools:
                            # Multiple different tools, all batched
                            batch_desc = ", ".join([f"{name} (×{tool_counts[name]})" for name in batch_tools])
                            message = f"Parallel batch: {batch_desc}..."
                        else:
                            # All different tools, once each
                            message = f"Parallel execution: {count} different tools simultaneously..."
                else:
                    message = f"Parallel execution: {count} tools simultaneously..."
            
            if self.colors_enabled:
                print(f"  {self.CYAN}{message}{self.RESET}")
            else:
                print(f"  {message}")
    
    def parallel_result(self, tool_name: str, success: bool, result: str):
        """Log individual parallel execution result."""
        if self.verbose:
            # Truncate long results
            if len(result) > 150:
                result = result[:150] + "..."
            
            if self.colors_enabled:
                status = f"{self.GREEN}✓{self.RESET}" if success else f"{self.YELLOW}✗{self.RESET}"
                print(f"    {status} {tool_name}: {result}")
            else:
                status = "✓" if success else "✗"
                print(f"    {status} {tool_name}: {result}")
    
    def error(self, message: str):
        """Log error message."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.RED}Error:{self.RESET} {message}")
            else:
                print(f"  Error: {message}")
    
    def info(self, message: str):
        """Log informational message."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.GRAY}{message}{self.RESET}")
            else:
                print(f"  {message}")
    
    def final_answer(self, answer: str):
        """Log final answer."""
        if self.verbose:
            if self.colors_enabled:
                print(f"\n{self.BOLD}{self.GREEN}Final Answer:{self.RESET}")
            else:
                print(f"\nFinal Answer:")
            
            if len(answer) > 1000:
                print(f"{answer[:1000]}...")
            else:
                print(answer)
    
    def memory_action(self, action: str):
        """Log memory-related actions."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.MAGENTA}[Memory]{self.RESET} {action}")
            else:
                print(f"  [Memory] {action}")
    
    def tool_added(self, tool_name: str):
        """Log tool addition."""
        if self.verbose:
            if self.colors_enabled:
                print(f"  {self.GREEN}✓{self.RESET} Added tool: {tool_name}")
            else:
                print(f"  ✓ Added tool: {tool_name}")
