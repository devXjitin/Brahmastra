"""
Multi Tool Agent Implementation

This agent executes multiple tools simultaneously for efficiency.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from brahmastra.core import Tool, tool as tool_decorator
from brahmastra.utils.logger import AgentLogger
from .prompt import AGENT_SYSTEM_PROMPT, HISTORY_TEMPLATE, USER_REQUEST_TEMPLATE


class Create_MultiToolAgent:
    """
    Agent that executes multiple tools simultaneously for efficiency.
    
    Features:
    - Parallel execution of independent tools
    - Batch execution with multiple parameters
    - Sequential execution when dependencies exist
    - Error handling per tool call
    
    Args:
        llm: Language model instance with invoke() or generate_response() method
        tools: Optional list of Tool objects or decorated functions
        max_workers: Maximum number of parallel tool executions (default: 5)
        max_iterations: Maximum thinking iterations (default: 10)
        verbose: Enable detailed logging (default: False)
        agent_introduction: Custom introduction prompt
    """
    
    def __init__(
        self,
        llm,
        tools: Optional[List[Union[Tool, Callable]]] = None,
        max_workers: int = 50,
        max_iterations: int = 10,
        verbose: bool = False,
        agent_introduction: str = ""
    ):
        self.llm = llm
        self.tools: List[Tool] = []
        self.max_workers = max_workers
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.agent_introduction = agent_introduction
        self.logger = AgentLogger(verbose=verbose, agent_name="Multi Tool Agent")
        
        if tools:
            self.add_tools(*tools)
    
    def add_tools(self, *tools) -> None:
        """Add tools to the agent. Accepts Tool objects, decorated functions, or iterable tool wrappers."""
        for item in tools:
            if isinstance(item, Tool):
                self.tools.append(item)
                continue
            
            # Check __iter__ BEFORE callable (wrappers may have both __iter__ and __call__)
            if hasattr(item, '__iter__') and not isinstance(item, (str, bytes, type)):
                # Handle iterable tool wrappers (like WikipediaSearchTool, YouTubeSearchTool)
                try:
                    sub_tools = list(item)
                    if sub_tools and isinstance(sub_tools[0], Tool):
                        for sub_tool in sub_tools:
                            if isinstance(sub_tool, Tool):
                                self.tools.append(sub_tool)
                            else:
                                raise ValueError(f"Iterable contained non-Tool item: {type(sub_tool)}")
                        continue
                except (TypeError, StopIteration):
                    pass
            
            if callable(item) and not isinstance(item, (type, Tool)):
                # Try to convert function to Tool using decorator
                tool_obj = tool_decorator()(item)
                if isinstance(tool_obj, Tool):
                    self.tools.append(tool_obj)
                else:
                    raise ValueError(f"Could not convert {item} to Tool")
            else:
                raise ValueError(f"Invalid tool type: {type(item)}")
    
    def _build_tools_description(self) -> str:
        """Build formatted tool descriptions for the prompt."""
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for tool in self.tools:
            params = tool.parameters if hasattr(tool, 'parameters') else {}
            param_desc = []
            
            for param_name, param_info in params.items():
                param_type = param_info.get('type', 'str')
                required = param_info.get('required', True)
                req_str = "required" if required else "optional"
                param_desc.append(f"  - {param_name} ({param_type}, {req_str})")
            
            param_str = "\n".join(param_desc) if param_desc else "  No parameters"
            descriptions.append(f"• {tool.name}: {tool.description}\n{param_str}")
        
        return "\n\n".join(descriptions)
    
    def _build_prompt(self, user_input: str, history: List[Dict]) -> str:
        """Build the agent prompt with multi-tool instructions."""
        tools_desc = self._build_tools_description()
        
        # Build history text
        history_text = ""
        if history:
            for idx, entry in enumerate(history, 1):
                history_text += HISTORY_TEMPLATE.format(
                    round_number=idx,
                    thought=entry['thought'],
                    execution_mode=entry.get('execution_mode', 'unknown'),
                    actions=json.dumps(entry['actions'], indent=2),
                    results=json.dumps(entry['results'], indent=2)
                )
        
        # Build complete prompt
        system_prompt = AGENT_SYSTEM_PROMPT.format(
            agent_introduction=self.agent_introduction,
            tools_description=tools_desc
        )
        
        user_request = USER_REQUEST_TEMPLATE.format(user_input=user_input)
        
        prompt = system_prompt + history_text + user_request
        
        return prompt
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response to extract structured data."""
        response = response.strip()
        
        # Try to extract JSON from code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'```\s*(\{.*?\})\s*```', response, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try parsing the whole response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Fallback: create a finish response
        return {
            "thought": "Response parsing failed",
            "final_answer": response[:1000] if response else "Unable to parse response",
            "finish": True
        }
    
    def _execute_single_tool(self, action: Dict) -> Dict:
        """Execute a single tool directly (optimized, no parallel overhead)."""
        tool_name = action.get("tool")
        parameters = action.get("parameters", {})
        
        # Find the tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            # Provide helpful suggestions
            available_tools = [t.name for t in self.tools]
            # Find similar tool names (simple matching)
            suggestions = []
            if tool_name:
                suggestions = [t for t in available_tools if tool_name.lower() in t.lower() or t.lower() in tool_name.lower()]
            
            error_msg = f"Tool '{tool_name}' not found"
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions)}?"
            else:
                error_msg += f". Available tools: {', '.join(available_tools)}"
            
            return {
                "tool": tool_name,
                "status": "error",
                "result": error_msg
            }
        
        try:
            # Execute the tool
            result = tool.function(**parameters)
            return {
                "tool": tool_name,
                "status": "success",
                "result": result,
                "parameters": parameters
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "status": "error",
                "result": f"Error: {str(e)}",
                "parameters": parameters
            }
    
    def _execute_tools_parallel(self, actions: List[Dict]) -> List[Dict]:
        """Execute multiple tool calls in parallel."""
        results = []
        
        # Execute in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_action = {executor.submit(self._execute_single_tool, action): action for action in actions}
            
            for future in as_completed(future_to_action):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    action = future_to_action[future]
                    results.append({
                        "tool": action.get("tool", "unknown"),
                        "status": "error",
                        "result": f"Execution error: {str(e)}"
                    })
        
        return results
    
    def invoke(self, user_input: str) -> str:
        """
        Execute the agent with multi-tool capabilities.
        
        Args:
            user_input: User's request
            
        Returns:
            String containing the final answer
        """
        self.logger.agent_start(user_input)
        history = []
        
        for iteration in range(self.max_iterations):
            self.logger.iteration(iteration + 1)
            
            # Build prompt
            prompt = self._build_prompt(user_input, history)
            
            # Get LLM response
            if hasattr(self.llm, 'invoke'):
                response = self.llm.invoke(prompt)
            elif hasattr(self.llm, 'generate_response'):
                response = self.llm.generate_response(prompt)
            else:
                raise ValueError("LLM must have invoke() or generate_response() method")
            
            # Parse response
            parsed = self._parse_response(response)
            
            # Log thought if present
            if parsed.get("thought"):
                self.logger.thought(parsed["thought"])
            
            # Check if finished
            if parsed.get("finish", False):
                final_answer = parsed.get("final_answer", parsed.get("thought", "Task completed"))
                
                # Decode escape sequences in the final answer
                if isinstance(final_answer, str):
                    # Replace common escape sequences (but preserve actual content)
                    final_answer = final_answer.replace('\\n', '\n')
                    final_answer = final_answer.replace('\\t', '\t')
                    final_answer = final_answer.replace('\\r', '\r')
                
                self.logger.agent_end(final_answer)
                
                return final_answer
            
            # Execute actions
            actions = parsed.get("actions", [])
            if not actions:
                # No actions but not finished - force completion
                final_answer = parsed.get("final_answer") or parsed.get("thought") or "Task completed"
                final_answer = final_answer.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
                self.logger.agent_end(final_answer)
                return final_answer
            
            # Extract tool names for better logging
            tool_names = [action.get("tool") for action in actions]
            self.logger.parallel_start(len(actions), tool_names)
            
            # Optimize: Use direct execution for single tool (avoid parallel overhead)
            if len(actions) == 1:
                results = [self._execute_single_tool(actions[0])]
            else:
                results = self._execute_tools_parallel(actions)
            
            # Log results
            for result in results:
                success = result["status"] == "success"
                self.logger.parallel_result(
                    result['tool'], 
                    success, 
                    result['result']
                )
            
            # Add to history
            history.append({
                "thought": parsed.get("thought", ""),
                "execution_mode": parsed.get("execution_mode", "parallel"),
                "actions": actions,
                "results": results
            })
        
        # Max iterations reached
        error_msg = "Maximum iterations reached without completion"
        self.logger.error(error_msg)
        return error_msg
