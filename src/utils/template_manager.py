"""Template management for email templates.

This module provides functionality to load and render email templates
with variable substitution for candidate-specific information.
"""

import os
import re
from typing import Dict


class TemplateManager:
    """Manages email template loading and rendering.
    
    Attributes:
        template_dir: Directory path where template files are stored
    """
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize TemplateManager with template directory.
        
        Args:
            template_dir: Path to directory containing template files
        """
        self.template_dir = template_dir
    
    def load_template(self, template_name: str) -> str:
        """Load email template from file.
        
        Args:
            template_name: Name of template file (without .txt extension)
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = os.path.join(self.template_dir, f"{template_name}.txt")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Template file not found: {template_path}"
            )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_content: str, variables: Dict[str, str]) -> str:
        """Render template by replacing variables with actual values.
        
        Args:
            template_content: Template string with {variable} placeholders
            variables: Dictionary of variable names to values
            
        Returns:
            Rendered template string
            
        Raises:
            KeyError: If required variable is missing from variables dict
        """
        # Extract all variable names from template
        required_vars = set(re.findall(r'\{(\w+)\}', template_content))
        
        # Check for missing variables
        missing_vars = required_vars - set(variables.keys())
        if missing_vars:
            raise KeyError(
                f"Missing required template variables: {', '.join(sorted(missing_vars))}"
            )
        
        # Render template by replacing all variables
        rendered = template_content
        for var_name, var_value in variables.items():
            rendered = rendered.replace(f"{{{var_name}}}", str(var_value))
        
        return rendered
