"""
Robust import resolution utilities for CDP Runbooker.

This module provides utilities to handle imports across different execution contexts:
- Direct script execution (python3 cdpRunbooker.py)
- Module execution (python3 -m CDP-Quip-Runbooker.cdpRunbooker)
- Package imports (from CDP-Quip-Runbooker import ...)
- Installed package usage
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Any, Optional, List, Dict

logger = logging.getLogger(__name__)

class ImportResolver:
    """
    Handles robust import resolution across different execution contexts.
    """
    
    @staticmethod
    def resolve_import(module_paths: List[str], fallback_paths: Optional[List[str]] = None) -> Any:
        """
        Attempt to import a module using multiple strategies.
        
        Args:
            module_paths: List of module paths to try (e.g., ['..utils.user_interface', 'utils.user_interface'])
            fallback_paths: Optional list of additional paths to add to sys.path
            
        Returns:
            The imported module
            
        Raises:
            ImportError: If all import attempts fail
        """
        import_errors = []
        
        # Strategy 1: Try each module path as-is
        for module_path in module_paths:
            try:
                if module_path.startswith('.'):
                    # Relative import
                    module = importlib.import_module(module_path, package=__package__)
                else:
                    # Absolute import
                    module = importlib.import_module(module_path)
                return module
            except ImportError as e:
                import_errors.append(f"{module_path}: {str(e)}")
                continue
        
        # Strategy 2: Try with path manipulation
        if fallback_paths:
            original_path = sys.path.copy()
            try:
                for path in fallback_paths:
                    if path not in sys.path:
                        sys.path.insert(0, path)
                
                for module_path in module_paths:
                    try:
                        # Only try absolute imports with path manipulation
                        if not module_path.startswith('.'):
                            module = importlib.import_module(module_path)
                            return module
                    except ImportError as e:
                        import_errors.append(f"{module_path} (with path): {str(e)}")
                        continue
            finally:
                sys.path = original_path
        
        # Strategy 3: Try to construct path based on current file location
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # Go up from utils/ to project root
        
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            
            for module_path in module_paths:
                try:
                    if not module_path.startswith('.'):
                        module = importlib.import_module(module_path)
                        return module
                except ImportError as e:
                    import_errors.append(f"{module_path} (with project root): {str(e)}")
                    continue
        
        # All strategies failed
        error_msg = "Failed to import module using all strategies:\n" + "\n".join(import_errors)
        raise ImportError(error_msg)
    
    @staticmethod
    def get_execution_context() -> Dict[str, Any]:
        """
        Determine how the script is being executed.
        
        Returns:
            Dictionary with execution context information
        """
        context = {
            'execution_method': 'unknown',
            'script_path': None,
            'package_name': None,
            'is_main': False,
            'python_path': sys.path.copy(),
            'working_directory': os.getcwd()
        }
        
        # Check if we're the main module
        main_module = sys.modules.get('__main__')
        if main_module:
            context['is_main'] = hasattr(main_module, '__file__')
            if hasattr(main_module, '__file__') and main_module.__file__:
                context['script_path'] = main_module.__file__
                
                # Determine execution method
                if main_module.__file__.endswith('cdpRunbooker.py'):
                    context['execution_method'] = 'direct_script'
                elif '-m' in sys.argv:
                    context['execution_method'] = 'module_execution'
                else:
                    context['execution_method'] = 'script_execution'
        
        # Check for package context
        if __package__:
            context['package_name'] = __package__
            context['execution_method'] = 'package_import'
        
        return context
    
    @staticmethod
    def setup_import_paths() -> List[str]:
        """
        Set up import paths for the current execution context.
        
        Returns:
            List of paths that were added to sys.path
        """
        added_paths = []
        current_file = Path(__file__).resolve()
        
        # Add project root (parent of utils directory)
        project_root = current_file.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            added_paths.append(str(project_root))
        
        # Add utils directory itself
        utils_dir = current_file.parent
        if str(utils_dir) not in sys.path:
            sys.path.insert(0, str(utils_dir))
            added_paths.append(str(utils_dir))
        
        # Add core directory
        core_dir = project_root / 'core'
        if core_dir.exists() and str(core_dir) not in sys.path:
            sys.path.insert(0, str(core_dir))
            added_paths.append(str(core_dir))
        
        return added_paths


def safe_import_user_interface():
    """
    Safely import the user_interface module using multiple strategies.
    
    Returns:
        The user_interface module
        
    Raises:
        ImportError: If import fails with all strategies
    """
    resolver = ImportResolver()
    
    # Set up paths
    fallback_paths = resolver.setup_import_paths()
    
    # Try different import paths
    module_paths = [
        '..utils.user_interface',  # Relative import (package context)
        'utils.user_interface',    # Absolute import
        'user_interface'           # Direct import (if in path)
    ]
    
    try:
        module = resolver.resolve_import(module_paths, fallback_paths)
        return module
    except ImportError as e:
        # Log the context for debugging
        context = resolver.get_execution_context()
        logger.error(f"Failed to import user_interface. Context: {context}")
        logger.error(f"Import error: {str(e)}")
        raise


def safe_import_from_user_interface(*names):
    """
    Safely import specific items from user_interface module.
    
    Args:
        *names: Names to import from the module
        
    Returns:
        Tuple of imported items (or single item if only one name)
        
    Raises:
        ImportError: If import fails
    """
    module = safe_import_user_interface()
    
    if len(names) == 1:
        return getattr(module, names[0])
    else:
        return tuple(getattr(module, name) for name in names)
