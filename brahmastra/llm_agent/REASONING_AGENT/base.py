"""
Reasoning Agent

An advanced AI agent designed for complex reasoning tasks that require step-by-step thinking.
Optimized for reasoning models like OpenAI o1, o3, DeepSeek-R1, etc.

This agent breaks down complex problems and shows its reasoning process transparently.
"""

import re
import json
from typing import Optional
from .prompt import PREFIX_PROMPT, LOGIC_PROMPT, SUFFIX_PROMPT
from ...utils.logger import AgentLogger


class Create_Reasoning_Agent:
    """
    Reasoning Agent that solves complex problems through step-by-step thinking.
    
    The agent accepts an LLM object that must have a generate_response(prompt) method.
    Best used with reasoning models like OpenAI o1, o3, DeepSeek-R1.
    
    Note: This agent does NOT support tool calling. For tool usage, use TOOL_CALLING_AGENT.
    """
    
    def __init__(
        self, 
        llm,
        verbose: bool = False,
        prompt: Optional[str] = None,
        max_reasoning_steps: int = 10,
        show_reasoning: bool = True
    ) -> None:
        """
        Initialize Reasoning Agent with an LLM object.
        
        Args:
            llm: LLM object with a generate_response(prompt) method.
                 Use llm from the llm folder (google_llm, openai_llm, anthropic_llm, groq_llm, ollama_llm)
            verbose: Enable verbose logging
            prompt: Custom agent introduction (optional). Should ONLY contain agent personality/role description.
                   ⚠️ WARNING: The custom prompt should ONLY be the agent introduction.
                   Do NOT include reasoning instructions or response format - these are added automatically.
                   If not provided, uses default agent introduction.
            max_reasoning_steps: Maximum number of reasoning iterations before providing final answer (default: 10)
            show_reasoning: Whether to display reasoning steps in output (default: True)
        
        Example:
            # Without custom prompt (uses default)
            agent = Create_Reasoning_Agent(llm=my_llm, verbose=True)
            
            # With custom agent introduction
            custom_intro = "You are a brilliant mathematics professor specializing in complex problem solving."
            agent = Create_Reasoning_Agent(llm=my_llm, prompt=custom_intro, verbose=True)
            
            # Configure reasoning behavior
            agent = Create_Reasoning_Agent(
                llm=my_llm, 
                max_reasoning_steps=15,  # More steps for complex problems
                show_reasoning=True,     # Display thinking process
                verbose=True
            )
        """
        self.llm = llm
        self.verbose = verbose
        self.max_reasoning_steps = max_reasoning_steps
        self.show_reasoning = show_reasoning
        self.logger = AgentLogger(verbose=verbose, agent_name="Reasoning Agent")
        
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
        Parse the LLM response to extract reasoning steps and final answer.
        
        Args:
            response: Raw response string from LLM containing JSON block
            
        Returns:
            tuple: (reasoning_steps, final_answer)
        """
        # Extract JSON block with ```json or '''json markers
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if not json_match:
            json_match = re.search(r"'''json\s*(\{.*?\})\s*'''", response, re.DOTALL)
        
        if not json_match:
            raise ValueError(f"Invalid response format: No JSON block found in response: {response[:200]}")
        
        # Parse the single JSON object containing both keys
        parsed_json = json.loads(json_match.group(1))
        
        reasoning_steps = parsed_json.get("Reasoning Steps", "None")
        final_answer = parsed_json.get("Final Answer", "None")
        
        return reasoning_steps, final_answer
    
    def add_llm(self, llm):
        """
        Set or update the LLM instance.
        
        Args:
            llm: LLM object with a generate_response(prompt) method
        """
        self.llm = llm
    
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
            elif level == "reasoning":
                self.logger.thought(message)
    
    def invoke(self, query):
        """
        Execute the agent with a user query.
        
        Args:
            query: User's question or problem to solve
            
        Returns:
            Final answer from the agent (string if show_reasoning=False, dict if show_reasoning=True)
        """
        if self.llm is None:
            raise ValueError("LLM not set. Call add_llm() first")
        
        self.logger.agent_start(query)
        
        # Compile prompt
        prompt = self.prompt_template.format(user_input=query)
        
        all_reasoning_steps = []
        scratchpad = ""
        iteration = 0
        
        while iteration < self.max_reasoning_steps:
            iteration += 1
            self.logger.iteration(iteration)
            
            # Get LLM response
            full_prompt = f"{prompt}\n{scratchpad}" if scratchpad else prompt
            response = self.llm.generate_response(full_prompt)
            
            try:
                reasoning_steps, final_answer = self._parser(response)
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                self._log(error_msg, "error")
                return error_msg
            
            # Process reasoning steps
            if reasoning_steps != "None" and reasoning_steps:
                if isinstance(reasoning_steps, list):
                    for step in reasoning_steps:
                        all_reasoning_steps.append(step)
                        if self.verbose:
                            self._log(f"Step {len(all_reasoning_steps)}: {step}", "reasoning")
                else:
                    all_reasoning_steps.append(str(reasoning_steps))
                    if self.verbose:
                        self._log(f"Step {len(all_reasoning_steps)}: {reasoning_steps}", "reasoning")
            
            # Check if agent has final answer
            if final_answer != "None" and final_answer:
                self.logger.agent_end(final_answer)
                
                # Return based on show_reasoning preference
                if self.show_reasoning:
                    return {
                        "reasoning_steps": all_reasoning_steps,
                        "final_answer": final_answer,
                        "iterations": iteration
                    }
                else:
                    return final_answer
            
            # Update scratchpad for next iteration
            if reasoning_steps != "None" and reasoning_steps:
                scratchpad += f"\n\n--- Previous Reasoning ---\n"
                scratchpad += f"Steps completed: {len(all_reasoning_steps)}\n"
                scratchpad += f"Continue reasoning and provide the final answer when ready."
        
        # Max iterations reached without final answer
        error_msg = f"Maximum reasoning steps ({self.max_reasoning_steps}) reached without final answer"
        self._log(error_msg, "warning")
        
        if self.show_reasoning:
            return {
                "reasoning_steps": all_reasoning_steps,
                "final_answer": "Unable to reach conclusion within iteration limit",
                "iterations": iteration,
                "status": "incomplete"
            }
        else:
            return "Unable to reach conclusion within iteration limit"
