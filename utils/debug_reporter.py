"""
Comprehensive debug reporting system for CDP Runbooker.

This module generates detailed diagnostic reports to help troubleshoot
user environment issues, import problems, and runtime errors.
"""

import os
import sys
import json
import platform
import traceback
import subprocess
import importlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DebugReporter:
    """
    Generates comprehensive debug reports for troubleshooting.
    """
    
    def __init__(self):
        """Initialize the debug reporter."""
        self.report_data = {}
        self.session_id = self._generate_session_id()
        self.timestamp = datetime.now(timezone.utc)
        
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for this debug session."""
        import hashlib
        import time
        
        # Create a unique identifier based on timestamp and process info
        identifier = f"{time.time()}-{os.getpid()}-{platform.node()}"
        return hashlib.md5(identifier.encode()).hexdigest()[:8]
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information."""
        info = {
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'node': platform.node()
            },
            'python': {
                'version': sys.version,
                'version_info': list(sys.version_info),
                'executable': sys.executable,
                'prefix': sys.prefix,
                'path': sys.path.copy()
            },
            'environment': {
                'shell': os.environ.get('SHELL', 'unknown'),
                'user': os.environ.get('USER', 'unknown'),
                'home': str(Path.home()),
                'cwd': os.getcwd(),
                'cdp_debug': os.environ.get('CDP_DEBUG', 'not set')
            }
        }
        
        # Add relevant environment variables (sanitized)
        relevant_env_vars = [
            'PATH', 'PYTHONPATH', 'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV',
            'SHELL', 'TERM', 'LANG', 'LC_ALL'
        ]
        
        info['environment']['variables'] = {}
        for var in relevant_env_vars:
            value = os.environ.get(var)
            if value:
                # Sanitize paths that might contain sensitive info
                if var in ['PATH', 'PYTHONPATH']:
                    # Replace home directory with ~
                    home_str = str(Path.home())
                    value = value.replace(home_str, '~')
                info['environment']['variables'][var] = value
        
        return info
    
    def collect_execution_context(self) -> Dict[str, Any]:
        """Collect information about how the script is being executed."""
        context = {
            'command_line': sys.argv.copy(),
            'script_path': None,
            'execution_method': 'unknown',
            'main_module': None,
            'package_context': None
        }
        
        # Get main module info
        main_module = sys.modules.get('__main__')
        if main_module:
            if hasattr(main_module, '__file__') and main_module.__file__:
                context['script_path'] = main_module.__file__
                context['main_module'] = main_module.__name__
                
                # Determine execution method
                script_name = Path(main_module.__file__).name
                if script_name == 'cdpRunbooker.py':
                    context['execution_method'] = 'direct_script'
                elif '-m' in sys.argv:
                    context['execution_method'] = 'module_execution'
                else:
                    context['execution_method'] = 'script_execution'
        
        # Package context
        if __package__:
            context['package_context'] = __package__
        
        return context
    
    def collect_file_structure(self) -> Dict[str, Any]:
        """Collect information about the CDP Runbooker file structure."""
        structure = {
            'project_root': None,
            'files_found': {},
            'files_missing': {},
            'permissions': {}
        }
        
        # Try to find project root
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent  # Go up from utils/
        
        if project_root.name == 'CDP-Quip-Runbooker':
            structure['project_root'] = str(project_root)
            
            # Check for expected files
            expected_files = [
                'cdpRunbooker.py',
                '__init__.py',
                'core/__init__.py',
                'core/secure_token_manager.py',
                'core/models.py',
                'utils/__init__.py',
                'utils/user_interface.py',
                'utils/validators.py',
                'utils/csv_handler.py',
                'requirements.txt',
                'README.md'
            ]
            
            for file_path in expected_files:
                full_path = project_root / file_path
                if full_path.exists():
                    structure['files_found'][file_path] = {
                        'exists': True,
                        'size': full_path.stat().st_size,
                        'readable': os.access(full_path, os.R_OK),
                        'writable': os.access(full_path, os.W_OK)
                    }
                else:
                    structure['files_missing'][file_path] = 'File not found'
        
        return structure
    
    def collect_import_analysis(self, error_context: Optional[Exception] = None) -> Dict[str, Any]:
        """Collect detailed import analysis and attempt resolution."""
        analysis = {
            'python_path': sys.path.copy(),
            'import_attempts': [],
            'module_discovery': {},
            'error_context': None
        }
        
        if error_context:
            analysis['error_context'] = {
                'type': type(error_context).__name__,
                'message': str(error_context),
                'traceback': ''.join(traceback.format_exception(type(error_context), error_context, error_context.__traceback__))
            }
        
        # Test common import scenarios
        import_tests = [
            ('utils.user_interface', 'Absolute import of user_interface'),
            ('core.secure_token_manager', 'Absolute import of secure_token_manager'),
            ('CDP-Quip-Runbooker.utils.user_interface', 'Package-style import'),
        ]
        
        for module_name, description in import_tests:
            attempt = {
                'module': module_name,
                'description': description,
                'status': 'unknown',
                'error': None,
                'path': None
            }
            
            try:
                module = importlib.import_module(module_name)
                attempt['status'] = 'success'
                if hasattr(module, '__file__'):
                    attempt['path'] = module.__file__
            except ImportError as e:
                attempt['status'] = 'failed'
                attempt['error'] = str(e)
            except Exception as e:
                attempt['status'] = 'error'
                attempt['error'] = f"{type(e).__name__}: {str(e)}"
            
            analysis['import_attempts'].append(attempt)
        
        # Module discovery
        try:
            import pkgutil
            current_path = Path(__file__).parent.parent
            for importer, modname, ispkg in pkgutil.iter_modules([str(current_path)]):
                analysis['module_discovery'][modname] = {
                    'is_package': ispkg,
                    'importer': str(type(importer))
                }
        except Exception as e:
            analysis['module_discovery']['error'] = str(e)
        
        return analysis
    
    def collect_dependency_info(self) -> Dict[str, Any]:
        """Collect information about Python dependencies."""
        deps = {
            'required_packages': {},
            'optional_packages': {},
            'pip_list': None
        }
        
        # Check required packages
        required = [
            'requests', 'cryptography', 'pathlib'
        ]
        
        for package in required:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                deps['required_packages'][package] = {
                    'status': 'available',
                    'version': version,
                    'path': getattr(module, '__file__', 'unknown')
                }
            except ImportError as e:
                deps['required_packages'][package] = {
                    'status': 'missing',
                    'error': str(e)
                }
        
        # Check optional packages
        optional = [
            'amazoncerts', 'quip', 'quipclient'
        ]
        
        for package in optional:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                deps['optional_packages'][package] = {
                    'status': 'available',
                    'version': version
                }
            except ImportError:
                deps['optional_packages'][package] = {
                    'status': 'not_available'
                }
        
        # Try to get pip list
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                deps['pip_list'] = result.stdout
        except Exception as e:
            deps['pip_list'] = f"Error getting pip list: {str(e)}"
        
        return deps
    
    def collect_error_details(self, error: Optional[Exception] = None) -> Dict[str, Any]:
        """Collect detailed error information."""
        if not error:
            return {'error': 'No error provided'}
        
        # Extract context information safely
        context_file = 'unknown'
        context_line = 'unknown'
        
        if hasattr(error, '__traceback__') and error.__traceback__:
            tb = error.__traceback__
            if hasattr(tb, 'tb_frame') and hasattr(tb.tb_frame, 'f_code'):
                context_file = tb.tb_frame.f_code.co_filename
            if hasattr(tb, 'tb_lineno'):
                context_line = tb.tb_lineno
        
        return {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__)),
            'context': {
                'file': context_file,
                'line': context_line
            }
        }
    
    def generate_recommendations(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on the collected data."""
        recommendations = []
        
        # Check for missing __init__.py
        if 'file_structure' in report_data:
            missing_files = report_data['file_structure'].get('files_missing', {})
            if '__init__.py' in missing_files:
                recommendations.append("Add __init__.py to the root directory to enable package imports")
        
        # Check for import issues
        if 'import_analysis' in report_data:
            failed_imports = [
                attempt for attempt in report_data['import_analysis'].get('import_attempts', [])
                if attempt['status'] == 'failed'
            ]
            if failed_imports:
                recommendations.append("Consider using absolute imports for direct script execution")
                recommendations.append("Ensure all required files are present and accessible")
        
        # Check for missing dependencies
        if 'dependencies' in report_data:
            missing_deps = [
                pkg for pkg, info in report_data['dependencies'].get('required_packages', {}).items()
                if info.get('status') == 'missing'
            ]
            if missing_deps:
                recommendations.append(f"Install missing dependencies: {', '.join(missing_deps)}")
        
        # Check execution context
        if 'execution_context' in report_data:
            if report_data['execution_context'].get('execution_method') == 'direct_script':
                recommendations.append("For direct script execution, ensure all imports use absolute paths")
        
        return recommendations
    
    def generate_full_report(self, error: Optional[Exception] = None, 
                           include_error_context: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive debug report."""
        report = {
            'metadata': {
                'generated_at': self.timestamp.isoformat(),
                'session_id': self.session_id,
                'cdp_runbooker_version': '2.0.0',  # Should be dynamic
                'report_version': '1.0'
            }
        }
        
        # Collect all diagnostic information
        try:
            report['system_info'] = self.collect_system_info()
        except Exception as e:
            report['system_info'] = {'error': str(e)}
        
        try:
            report['execution_context'] = self.collect_execution_context()
        except Exception as e:
            report['execution_context'] = {'error': str(e)}
        
        try:
            report['file_structure'] = self.collect_file_structure()
        except Exception as e:
            report['file_structure'] = {'error': str(e)}
        
        try:
            report['import_analysis'] = self.collect_import_analysis(error if include_error_context else None)
        except Exception as e:
            report['import_analysis'] = {'error': str(e)}
        
        try:
            report['dependencies'] = self.collect_dependency_info()
        except Exception as e:
            report['dependencies'] = {'error': str(e)}
        
        if error:
            try:
                report['error_details'] = self.collect_error_details(error)
            except Exception as e:
                report['error_details'] = {'error': str(e)}
        
        # Generate recommendations
        try:
            report['recommendations'] = self.generate_recommendations(report)
        except Exception as e:
            report['recommendations'] = [f"Error generating recommendations: {str(e)}"]
        
        return report
    
    def format_report_as_markdown(self, report_data: Dict[str, Any]) -> str:
        """Format the debug report as a readable markdown document."""
        md_lines = []
        
        # Header
        md_lines.extend([
            "# CDP-Runbooker Debug Report",
            "",
            f"**Generated:** {report_data['metadata']['generated_at']}  ",
            f"**Session ID:** {report_data['metadata']['session_id']}  ",
            f"**CDP-Runbooker Version:** {report_data['metadata']['cdp_runbooker_version']}  ",
            "",
            "---",
            ""
        ])
        
        # System Information
        if 'system_info' in report_data:
            md_lines.extend([
                "## System Information",
                "",
                f"- **OS:** {report_data['system_info'].get('platform', {}).get('system', 'unknown')} {report_data['system_info'].get('platform', {}).get('release', '')}",
                f"- **Python:** {report_data['system_info'].get('python', {}).get('version', 'unknown').split()[0]} ({report_data['system_info'].get('python', {}).get('executable', 'unknown')})",
                f"- **Shell:** {report_data['system_info'].get('environment', {}).get('shell', 'unknown')}",
                f"- **Working Directory:** {report_data['system_info'].get('environment', {}).get('cwd', 'unknown')}",
                ""
            ])
        
        # Execution Context
        if 'execution_context' in report_data:
            md_lines.extend([
                "## Execution Context",
                "",
                f"- **Script Path:** {report_data['execution_context'].get('script_path', 'unknown')}",
                f"- **Execution Method:** {report_data['execution_context'].get('execution_method', 'unknown')}",
                f"- **Command Line:** `{' '.join(report_data['execution_context'].get('command_line', []))}`",
                ""
            ])
        
        # Import Analysis
        if 'import_analysis' in report_data:
            md_lines.extend([
                "## Import Analysis",
                "",
                "### Import Attempts",
                ""
            ])
            
            for attempt in report_data['import_analysis'].get('import_attempts', []):
                status_emoji = "✅" if attempt['status'] == 'success' else "❌"
                md_lines.append(f"{status_emoji} **{attempt['module']}** - {attempt['description']}")
                if attempt['status'] != 'success':
                    md_lines.append(f"   - Error: {attempt.get('error', 'unknown')}")
                elif attempt.get('path'):
                    md_lines.append(f"   - Path: {attempt['path']}")
                md_lines.append("")
        
        # File Structure
        if 'file_structure' in report_data:
            md_lines.extend([
                "## File Structure Validation",
                ""
            ])
            
            for file_path, info in report_data['file_structure'].get('files_found', {}).items():
                md_lines.append(f"✅ {file_path}")
            
            for file_path, error in report_data['file_structure'].get('files_missing', {}).items():
                md_lines.append(f"❌ {file_path} - {error}")
            
            md_lines.append("")
        
        # Dependencies
        if 'dependencies' in report_data:
            md_lines.extend([
                "## Dependencies",
                ""
            ])
            
            for pkg, info in report_data['dependencies'].get('required_packages', {}).items():
                status_emoji = "✅" if info['status'] == 'available' else "❌"
                version = f" (version {info.get('version', 'unknown')})" if info.get('version') != 'unknown' else ""
                md_lines.append(f"{status_emoji} **{pkg}**{version}")
                if info['status'] != 'available':
                    md_lines.append(f"   - Error: {info.get('error', 'not available')}")
            
            md_lines.append("")
        
        # Error Details
        if 'error_details' in report_data:
            md_lines.extend([
                "## Error Details",
                "",
                f"**Type:** {report_data['error_details']['type']}  ",
                f"**Message:** {report_data['error_details']['message']}  ",
                "",
                "**Traceback:**",
                "```",
                report_data['error_details']['traceback'],
                "```",
                ""
            ])
        
        # Recommendations
        if 'recommendations' in report_data:
            md_lines.extend([
                "## Recommendations",
                ""
            ])
            
            for i, rec in enumerate(report_data['recommendations'], 1):
                md_lines.append(f"{i}. {rec}")
            
            md_lines.append("")
        
        # Footer
        md_lines.extend([
            "---",
            "",
            "**Note:** This report contains diagnostic information to help troubleshoot CDP-Runbooker issues.",
            "Personal information has been sanitized, but please review before sharing.",
            ""
        ])
        
        return "\n".join(md_lines)
    
    def save_report(self, report_data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        """Save the debug report to a file."""
        if output_dir is None:
            output_dir = os.getcwd()
        
        # Generate filename
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"cdp-runbooker-debug-{timestamp_str}-{self.session_id}.md"
        filepath = Path(output_dir) / filename
        
        # Format and save
        markdown_content = self.format_report_as_markdown(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)


def generate_debug_report(error: Optional[Exception] = None, 
                         save_to_file: bool = True,
                         output_dir: Optional[str] = None) -> str:
    """
    Generate a comprehensive debug report.
    
    Args:
        error: Optional exception to include in the report
        save_to_file: Whether to save the report to a file
        output_dir: Directory to save the report (defaults to current directory)
        
    Returns:
        Path to the saved report file, or the markdown content if not saved
    """
    reporter = DebugReporter()
    report_data = reporter.generate_full_report(error=error)
    
    if save_to_file:
        return reporter.save_report(report_data, output_dir)
    else:
        return reporter.format_report_as_markdown(report_data)
