"""
Parses test results from Gradle builds (JUnit XML format).
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FailureDetail:
    """Represents a single test failure."""
    name: str
    classname: str
    message: str
    stacktrace: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"FailureDetail({self.classname}.{self.name}: {self.message})"


@dataclass
class ExecutionSummary:
    """Summary of all tests in a build."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failures: List[FailureDetail] = field(default_factory=list)
    errors: List[str] = field(default_factory=list) # Parsing errors
    
    def add_suite(self, total: int, failures: int, skipped: int, errors: int):
        """Add counts from a test suite."""
        self.total += total
        self.failed += failures + errors # Treat errors as failures for simplicity
        self.skipped += skipped
        # Passed is calculated: total - failed - skipped
        self.passed += (total - (failures + errors) - skipped)


class TestResultParser:
    """Parses JUnit XML test reports."""
    
    def parse_results(self, project_path: Path) -> ExecutionSummary:
        """
        Parse test results from the project's build directory.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            ExecutionSummary object
        """
        project_path = Path(project_path)
        # Standard Gradle JUnit report location
        report_dir = project_path / 'build' / 'test-results' / 'test'
        
        summary = ExecutionSummary()
        
        if not report_dir.exists():
            summary.errors.append(f"Test report directory not found: {report_dir}")
            return summary
        
        # Find all XML files
        xml_files = list(report_dir.glob('**/*.xml'))
        
        if not xml_files:
            summary.errors.append("No test report XML files found")
            return summary
            
        for xml_file in xml_files:
            try:
                self._parse_xml_file(xml_file, summary)
            except Exception as e:
                summary.errors.append(f"Error parsing {xml_file.name}: {str(e)}")
                
        return summary
    
    def _parse_xml_file(self, xml_file: Path, summary: ExecutionSummary) -> None:
        """
        Parse a single JUnit XML file and update the summary.
        
        Args:
            xml_file: Path to XML file
            summary: ExecutionSummary object to update
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Handle both <testsuite> root and <testsuites> root with children
        if root.tag == 'testsuites':
            suites = root.findall('testsuite')
        else:
            suites = [root]
            
        for suite in suites:
            # Get suite stats
            # Attributes are usually strings, need to parse safely
            tests = int(suite.get('tests', 0))
            failures = int(suite.get('failures', 0))
            errors = int(suite.get('errors', 0))
            skipped = int(suite.get('skipped', 0))
            
            summary.add_suite(tests, failures, skipped, errors)
            
            # Extract failure details
            for testcase in suite.findall('testcase'):
                failure_node = testcase.find('failure')
                error_node = testcase.find('error')
                
                fault_node = failure_node if failure_node is not None else error_node
                
                if fault_node is not None:
                    name = testcase.get('name', 'unknown')
                    classname = testcase.get('classname', 'unknown')
                    message = fault_node.get('message', '')
                    stacktrace = fault_node.text
                    
                    failure = FailureDetail(
                        name=name,
                        classname=classname,
                        message=message,
                        stacktrace=stacktrace
                    )
                    summary.failures.append(failure)
