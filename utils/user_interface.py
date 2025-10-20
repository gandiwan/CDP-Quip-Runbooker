"""
User interface utilities for CDP Runbooker.
"""

import os
import sys
import time
from enum import Enum


class MessageType(Enum):
    """Enumeration for different types of user messages."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    PROMPT = "prompt"
    HEADER = "header"
    STEP = "step"


class UserMessenger:
    """Centralized messaging system for consistent user communication."""
    
    # ANSI color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'gray': '\033[90m'
    }
    
    # Message symbols and formatting
    SYMBOLS = {
        MessageType.SUCCESS: "✅",
        MessageType.WARNING: "⚠️",
        MessageType.ERROR: "❌",
        MessageType.INFO: "ℹ️",
        MessageType.PROMPT: "🔄",
        MessageType.HEADER: "🎯",
        MessageType.STEP: "▶️"
    }
    
    @classmethod
    def _colorize(cls, text: str, color: str) -> str:
        """Apply color formatting to text if terminal supports it."""
        try:
            if os.getenv('NO_COLOR') or not os.isatty(sys.stdout.fileno()):
                return text
            return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['reset']}"
        except (AttributeError, OSError):
            return text
    
    @classmethod
    def print_message(cls, message: str, msg_type: MessageType = MessageType.INFO, 
                     prefix: str = "", bold: bool = False) -> None:
        """Print a formatted message to the user."""
        symbol = cls.SYMBOLS.get(msg_type, "")
        
        # Choose color based on message type
        color_map = {
            MessageType.SUCCESS: 'green',
            MessageType.WARNING: 'yellow', 
            MessageType.ERROR: 'red',
            MessageType.INFO: 'blue',
            MessageType.PROMPT: 'cyan',
            MessageType.HEADER: 'magenta',
            MessageType.STEP: 'cyan'
        }
        
        color = color_map.get(msg_type, 'reset')
        formatted_text = f"{symbol} {prefix}{message}" if symbol else f"{prefix}{message}"
        
        if bold:
            formatted_text = cls._colorize(formatted_text, 'bold')
        else:
            formatted_text = cls._colorize(formatted_text, color)
            
        print(formatted_text)
    
    @classmethod
    def print_header(cls, title: str) -> None:
        """Print a formatted header."""
        cls.print_message(f"\n{title}", MessageType.HEADER, bold=True)
    
    @classmethod
    def print_step(cls, step_num: int, description: str) -> None:
        """Print a formatted step message."""
        cls.print_message(f" Step {step_num}: {description}", MessageType.STEP)
    
    @classmethod
    def print_success(cls, message: str) -> None:
        """Print a success message."""
        cls.print_message(message, MessageType.SUCCESS)
    
    @classmethod
    def print_warning(cls, message: str) -> None:
        """Print a warning message."""
        cls.print_message(message, MessageType.WARNING)
    
    @classmethod
    def print_error(cls, message: str) -> None:
        """Print an error message."""
        cls.print_message(message, MessageType.ERROR)
    
    @classmethod
    def print_info(cls, message: str) -> None:
        """Print an informational message."""
        cls.print_message(message, MessageType.INFO)
    
    @classmethod
    def get_user_input(cls, prompt: str, required: bool = True) -> str:
        """Get user input with consistent formatting."""
        formatted_prompt = cls._colorize(f"🔄 {prompt}: ", 'cyan')
        while True:
            try:
                value = input(formatted_prompt).strip()
                if value or not required:
                    return value
                cls.print_warning("This field is required. Please enter a value.")
            except KeyboardInterrupt:
                cls.print_error("\nOperation cancelled by user.")
                sys.exit(1)
    
    @classmethod
    def get_user_choice(cls, prompt: str, choices: list, default: str = None) -> str:
        """Get user choice from a list of options."""
        choices_str = "/".join(choices)
        if default:
            full_prompt = f"{prompt} ({choices_str}) [{default}]"
        else:
            full_prompt = f"{prompt} ({choices_str})"
            
        while True:
            response = cls.get_user_input(full_prompt, required=not bool(default)).lower()
            if not response and default:
                return default.lower()
            if response in [choice.lower() for choice in choices]:
                return response
            cls.print_warning(f" Please enter one of: {choices_str}")
    
    @classmethod
    def print_summary(cls, title: str, items: dict) -> None:
        """Print a formatted summary with items."""
        cls.print_header(title)
        for key, value in items.items():
            print(f"  {key}: {value}")


class ProgressBar:
    """Simple progress bar for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items to process
            description: Description of the operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.bar_width = 40
    
    def update(self, current: int, status: str = ""):
        """
        Update progress bar display.
        
        Args:
            current: Current progress count
            status: Optional status message
        """
        self.current = current
        
        # Calculate progress percentage
        if self.total > 0:
            progress = min(current / self.total, 1.0)
        else:
            progress = 1.0
        
        # Create progress bar
        filled_width = int(self.bar_width * progress)
        bar = '█' * filled_width + '░' * (self.bar_width - filled_width)
        percentage = int(progress * 100)
        
        # Format status message
        status_msg = f" {status}" if status else ""
        
        # Print progress bar (overwrite previous line)
        print(f"\r[{bar}] {percentage}% {self.description}{status_msg}", end='', flush=True)
    
    def complete(self, final_message: str = "Complete!"):
        """
        Show completion status and move to next line.
        
        Args:
            final_message: Final completion message
        """
        # Show 100% completion
        bar = '█' * self.bar_width
        print(f"\r[{bar}] 100% {final_message}")
    
    def increment(self, step: int = 1, status: str = ""):
        """
        Increment progress by step amount.
        
        Args:
            step: Amount to increment by
            status: Optional status message
        """
        self.update(self.current + step, status)


class MenuSystem:
    """Enhanced menu system with consistent styling."""
    
    @staticmethod
    def display_boxed_menu(title: str, options: list, current_step: int = None, total_steps: int = None):
        """
        Display a consistently formatted menu box.
        
        Args:
            title: Menu title
            options: List of menu options (strings)
            current_step: Current step number (optional)
            total_steps: Total number of steps (optional)
        """
        # Calculate box width based on content
        title_width = len(title) if title else 0
        options_width = max(len(opt) for opt in options) if options else 0
        max_width = max(title_width, options_width)
        box_width = min(max(max_width + 4, 50), 70)  # Min 50, max 70 characters
        
        # Create title with step info if provided
        if current_step and total_steps:
            step_info = f" - Step {current_step}/{total_steps}"
            display_title = title + step_info
        else:
            display_title = title
        
        # Top border
        print(f"┌─ {display_title} {'─' * (box_width - len(display_title) - 3)}┐")
        
        # Empty line for spacing
        print(f"│{' ' * (box_width - 1)}│")
        
        # Options
        for i, option in enumerate(options, 1):
            print(f"│  {i}. {option}{' ' * (box_width - len(option) - 6)}│")
        
        # Empty line before bottom
        print(f"│{' ' * (box_width - 1)}│")
        
        # Navigation options
        nav_line = "  [B]ack  [E]xit"
        print(f"│{nav_line}{' ' * (box_width - len(nav_line) - 1)}│")
        
        # Bottom border
        print(f"└{'─' * (box_width - 1)}┘")
    
    @staticmethod
    def display_breadcrumb(steps: list, current_index: int):
        """
        Display breadcrumb navigation.
        
        Args:
            steps: List of step names
            current_index: Current step index (0-based)
        """
        breadcrumb_parts = []
        for i, step in enumerate(steps):
            if i == current_index:
                breadcrumb_parts.append(f"► {step}")
            elif i < current_index:
                breadcrumb_parts.append(f"✓ {step}")
            else:
                breadcrumb_parts.append(f"  {step}")
        
        print(UserMessenger._colorize("Navigation: " + " → ".join(breadcrumb_parts), 'gray'))
        print()
    
    @staticmethod
    def get_navigation_choice(valid_numbers: list, allow_back: bool = True, allow_exit: bool = True) -> str:
        """
        Get user navigation choice with back/exit options.
        
        Args:
            valid_numbers: List of valid numeric choices
            allow_back: Whether to allow back navigation
            allow_exit: Whether to allow exit
            
        Returns:
            User choice ('back', 'exit', or the selected number as string)
        """
        valid_choices = [str(n) for n in valid_numbers]
        if allow_back:
            valid_choices.extend(['b', 'back'])
        if allow_exit:
            valid_choices.extend(['e', 'exit'])
        
        while True:
            choice = msg.get_user_input("Enter your choice", required=True).lower().strip()
            
            if choice in valid_choices:
                if choice in ['b', 'back']:
                    return 'back'
                elif choice in ['e', 'exit']:
                    return 'exit'
                else:
                    return choice
            
            # Build help message
            help_parts = [f"1-{max(valid_numbers)}"]
            if allow_back:
                help_parts.append("B(ack)")
            if allow_exit:
                help_parts.append("E(xit)")
            
            msg.print_warning(f" Please enter one of: {', '.join(help_parts)}")


# Create global instances for easy access
msg = UserMessenger()
menu = MenuSystem()
