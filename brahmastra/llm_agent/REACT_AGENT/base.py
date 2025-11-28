"""
ReAct Agent (Reasoning + Acting)

An advanced AI agent that combines reasoning and tool execution in an iterative loop.
This agent thinks through problems step-by-step while taking actions using tools.

Based on the ReAct (Reasoning + Acting) paradigm from "ReAct: Synergizing Reasoning and Acting in Language Models"
"""

import re
import json
from typing import Optional
from .prompt import PREFIX_PROMPT, LOGIC_PROMPT, SUFFIX_PROMPT
from brahmastra.utils.tool_executor import Tool_Executor
from brahmastra.utils.logger import AgentLogger


class Create_ReAct_Agent:
    """
    ReAct Agent that combines reasoning and tool execution.
    
    The agent accepts an LLM object that must have a generate_response(prompt) method.
    It iteratively thinks about the problem, takes actions using tools, observes results,
    and continues until reaching a final answer.
    """
    
    def __init__(
        self, 
        llm,
        verbose: bool = False,
        prompt: Optional[str] = None,
        max_iterations: int = 15,
        memory = None,
    ) -> None:
        """
        Initialize ReAct Agent with an LLM object.
        
        Args:
            llm: LLM object with a generate_response(prompt) method.
                 Use llm from the llm folder (google_llm, openai_llm, anthropic_llm, groq_llm, ollama_llm)
            verbose: Enable verbose logging
            prompt: Custom agent introduction (optional). Should ONLY contain agent personality/role description.
                   ⚠️ WARNING: The custom prompt should ONLY be the agent introduction.
                   Do NOT include reasoning/action instructions or response format - these are added automatically.
                   If not provided, uses default agent introduction.
            max_iterations: Maximum number of think-act cycles (default: 15)
            memory: Optional memory object (ConversationalBufferMemory, ConversationalWindowMemory, etc.)
                   from the memory module. If provided, conversation history will be maintained.
        
        Example:
            # Without custom prompt (uses default)
            agent = Create_ReAct_Agent(llm=my_llm, verbose=True)
            
            # With custom agent introduction
            custom_intro = "You are a research assistant specializing in data analysis."
            agent = Create_ReAct_Agent(llm=my_llm, prompt=custom_intro, verbose=True)
            
            # With memory
            from memory import ConversationalWindowMemory
            memory = ConversationalWindowMemory(window_size=10)
            agent = Create_ReAct_Agent(llm=my_llm, memory=memory, verbose=True)
        """
        self.tools = {}
        self.llm = llm
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.memory = memory
        self.logger = AgentLogger(verbose=verbose, agent_name="ReAct Agent")
        
        # If user provides custom prompt (agent introduction), use it instead of PREFIX
        # Otherwise use default PREFIX_PROMPT
        # LOGIC_PROMPT and SUFFIX_PROMPT are always added automatically
        if prompt is not None:
            self.logger.info("Using custom agent introduction")
            self.prompt_template = prompt + "\n\n" + LOGIC_PROMPT + SUFFIX_PROMPT
        else:
            self.prompt_template = PREFIX_PROMPT + LOGIC_PROMPT + SUFFIX_PROMPT
    
    def _parser(self, response):
        """
        Parse the LLM response to extract thought, action, action input, and final answer.
        
        Args:
            response: Raw response string from LLM containing JSON block
            
        Returns:
            tuple: (thought, action, action_input, final_answer)
        """
        # Extract JSON block with ```json or '''json markers
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if not json_match:
            json_match = re.search(r"'''json\s*(\{.*?\})\s*'''", response, re.DOTALL)
        
        if not json_match:
            raise ValueError(f"Invalid response format: No JSON block found in response: {response[:200]}")
        
        # Parse the single JSON object containing all four keys
        parsed_json = json.loads(json_match.group(1))
        
        thought = parsed_json.get("Thought", "None")
        action = parsed_json.get("Action", "None")
        action_input = parsed_json.get("Action Input", "None")
        final_answer = parsed_json.get("Final Answer", "None")
        
        return thought, action, action_input, final_answer
    
    def add_llm(self, llm):
        """
        Set or update the LLM instance.
        
        Args:
            llm: LLM object with a generate_response(prompt) method
        """
        self.llm = llm
    
    def add_memory(self, memory):
        """
        Set or update the memory instance.
        
        Args:
            memory: Memory object from memory module (ConversationalBufferMemory, etc.)
        """
        self.memory = memory
    
    def clear_memory(self):
        """Clear the conversation memory if it exists."""
        if self.memory is not None:
            self.memory.clear()
            self._log("Memory cleared", "success")
    
    def get_memory_history(self):
        """
        Get the conversation history from memory.
        
        Returns:
            List of message dicts if memory exists, empty list otherwise
        """
        if self.memory is not None:
            return self.memory.get_history()
        return []
    
    def add_tool(self, name, description, function, parameters=None):
        """
        Add a tool that the agent can use.
        
        Args:
            name: Tool name
            description: Description of what the tool does
            function: Callable function to execute
            parameters: Optional dictionary defining parameter schema.
                       Format: {"param_name": {"type": "str|int|float|bool", "description": "...", "required": True}}
        
        Example:
            agent.add_tool(
                name="calculator",
                description="Performs mathematical calculations",
                function=calculator_func,
                parameters={
                    "expression": {"type": "str", "description": "Math expression to evaluate", "required": True}
                }
            )
        """
        self.tools[name] = {
            "description": description,
            "function": function,
            "parameters": parameters or {}
        }
    
    def add_tools(self, *tools):
        """
        Add one or more tools to this agent (supports @tool decorator and Tool objects).
        
        Args:
            *tools: Variable number of Tool objects or decorated functions
        
        Example:
            # Using @tool decorator
            @tool
            def calculator(expression: str):
                return eval(expression)
            
            agent.add_tools(calculator)
            
            # Or Tool objects
            agent.add_tools(tool1, tool2, tool3)
        """
        from brahmastra.core import Tool, tool as tool_decorator
        
        added_count = 0
        
        for item in tools:
            if isinstance(item, Tool):
                # Add Tool object directly
                self.tools[item.name] = item.to_dict()
                added_count += 1
                self._log(f"Added tool '{item.name}'", "info")
            
            elif hasattr(item, '__iter__') and not isinstance(item, (str, bytes, type)):
                # Handle iterable tool wrappers (like YouTubeSearchTool, WikipediaSearchTool)
                # Check this BEFORE callable check since wrappers may have __call__ method
                try:
                    sub_tools = list(item)
                    if sub_tools and isinstance(sub_tools[0], Tool):
                        for sub_tool in sub_tools:
                            if isinstance(sub_tool, Tool):
                                self.tools[sub_tool.name] = sub_tool.to_dict()
                                added_count += 1
                                self._log(f"Added tool '{sub_tool.name}' from wrapper", "info")
                        continue
                except (TypeError, StopIteration):
                    # Not actually iterable in the way we need, fall through to other checks
                    pass
            
            if callable(item) and not isinstance(item, (type, Tool)):
                # It's a function (might be decorated or plain)
                # Call the decorator which will return a Tool object
                tool_obj = tool_decorator()(item) if not isinstance(item, Tool) else item
                
                # If it's still callable (not converted), it means it's already a Tool
                if isinstance(tool_obj, Tool):
                    self.tools[tool_obj.name] = tool_obj.to_dict()
                    added_count += 1
                    self._log(f"Added tool '{tool_obj.name}' from function", "info")
                else:
                    self._log(f"Warning: Could not convert function to Tool", "warning")
            else:
                self._log(f"Warning: Skipping invalid item (must be Tool object, function, or iterable wrapper)", "warning")
        
        self._log(f"Successfully added {added_count} tool(s)", "success")
        return added_count
    
    def _log(self, message, level="info"):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            if level == "info":
                self.logger.info(message)
            elif level == "success":
                self.logger.info(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.info(message)
            elif level == "thought":
                self.logger.thought(message)
    
    def invoke(self, query):
        """
        Execute the agent with a user query.
        
        Args:
            query: User's question or request
            
        Returns:
            Final answer from the agent
        """
        if self.llm is None:
            raise ValueError("LLM not set. Call add_llm() first")
        
        if not self.tools:
            raise ValueError("No tools added. Call add_tool() or add_tools() at least once")
        
        # Add user query to memory if available
        if self.memory is not None:
            self.memory.add_user_message(query)
            self._log("Added user message to memory", "info")
        
        # Compile prompt with tool information
        tool_list_items = []
        for name, info in self.tools.items():
            tool_desc = f"        - {name}: {info['description']}"
            
            # Add parameter information if available
            if info.get('parameters'):
                params = []
                for param_name, param_info in info['parameters'].items():
                    param_type = param_info.get('type', 'str')
                    required = param_info.get('required', True)
                    req_str = "required" if required else "optional"
                    params.append(f"{param_name} ({param_type}, {req_str})")
                
                if params:
                    tool_desc += f"\n          Parameters: {', '.join(params)}"
            
            tool_list_items.append(tool_desc)
        
        tool_list = "\n".join(tool_list_items)
        compiled_prompt = self.prompt_template.replace("{tool_list}", tool_list)
        
        # Add memory context if available
        memory_context = ""
        if self.memory is not None:
            context = self.memory.get_context()
            if context:
                memory_context = f"\n\n--- Conversation History ---\n{context}\n--- End History ---\n"
                self.logger.memory_action("Including conversation history")
        
        self.logger.agent_start(query)
        
        prompt = compiled_prompt.format(user_input=query) + memory_context
        scratchpad = ""
        iteration = 0
        failed_attempts = {}  # Track failed tool calls to avoid repeated mistakes
        
        while iteration < self.max_iterations:
            iteration += 1
            self.logger.iteration(iteration)
            
            # Get LLM response
            full_prompt = f"{prompt}\n{scratchpad}" if scratchpad else prompt
            response = self.llm.generate_response(full_prompt)
            
            try:
                thought, action, action_input, final_answer = self._parser(response)
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                self._log(error_msg, "error")
                
                # Add helpful guidance to scratchpad
                scratchpad += f"\n\n--- Error ---"
                scratchpad += f"\nResponse parsing failed. Provide valid JSON with: Thought, Action, Action Input, Final Answer."
                scratchpad += f"\nError: {str(e)[:100]}"
                continue
            
            # Display thought
            if thought != "None" and thought:
                self.logger.thought(thought)
            
            # Check if agent wants to provide final answer
            if final_answer != "None" and final_answer:
                # Decode escape sequences in the final answer
                if isinstance(final_answer, str):
                    final_answer = final_answer.replace('\\n', '\n')
                    final_answer = final_answer.replace('\\t', '\t')
                    final_answer = final_answer.replace('\\r', '\r')
                
                # Add AI response to memory if available
                if self.memory is not None:
                    self.memory.add_ai_message(final_answer)
                    self.logger.memory_action("Added AI response to memory")
                
                self.logger.agent_end(final_answer)
                return final_answer
            
            # Execute action if specified
            action_name = action if action != "None" else None
            
            if action_name:
                self.logger.action(action_name, action_input)
                
                # Check if this exact action+input combination failed before
                attempt_key = f"{action_name}:{str(action_input)}"
                if attempt_key in failed_attempts:
                    failed_attempts[attempt_key] += 1
                    if failed_attempts[attempt_key] >= 3:
                        # Give up on this approach after 3 identical failures
                        observation = f"Error: This exact tool call has failed {failed_attempts[attempt_key]} times. Please try a different approach or different parameters."
                        self.logger.observation(observation)
                        
                        scratchpad += f"\n\n--- Step {iteration} (Repeated Failure) ---"
                        scratchpad += f"\nThought: {thought}"
                        scratchpad += f"\nAction: {action_name}"
                        scratchpad += f"\nObservation: {observation}"
                        scratchpad += f"\n\nTry different parameters or a different tool."
                        continue
                
                # Execute tool
                observation = Tool_Executor(action_name, action_input, self.tools)
                
                # Track if this was an error
                if observation.startswith("Error:"):
                    if attempt_key not in failed_attempts:
                        failed_attempts[attempt_key] = 1
                    
                    # Provide helpful guidance for parameter errors
                    if "Parameter mismatch" in observation or "unexpected keyword argument" in observation:
                        # Extract available parameters from tool
                        tool_info = self.tools.get(action_name, {})
                        tool_params = tool_info.get('parameters', {})
                        
                        if tool_params:
                            param_hint = "\n\nAvailable parameters: " + ", ".join(
                                f"{p} ({info.get('type', 'any')})" 
                                for p, info in tool_params.items()
                            )
                            observation += param_hint
                        
                        observation += "\n\nPlease check the parameter names and try again."
                
                self.logger.observation(observation)
                
                # Update scratchpad with observation for next iteration
                scratchpad += f"\n\n--- Step {iteration} ---"
                scratchpad += f"\nThought: {thought}"
                scratchpad += f"\nAction: {action_name}"
                scratchpad += f"\nObservation: {observation}"
            else:
                # No action but also no final answer - agent is just thinking
                if self.verbose:
                    self._log("No action taken, continuing to think...", "info")
                
                scratchpad += f"\n\n--- Thought {iteration} ---"
                scratchpad += f"\n{thought}"
        
        error_msg = f"Error: Maximum iterations ({self.max_iterations}) reached"
        self._log(error_msg, "error")
        return error_msg
