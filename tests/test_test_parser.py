"""
Tests for TestResultParser.
"""

import pytest
from pathlib import Path
from gradeit.test_parser import TestResultParser, ExecutionSummary, FailureDetail


@pytest.fixture
def parser():
    return TestResultParser()


def test_missing_report_dir(parser, tmp_path):
    """Test handling of missing report directory."""
    summary = parser.parse_results(tmp_path)
    
    assert summary.total == 0
    assert len(summary.errors) > 0
    assert "not found" in summary.errors[0]


def test_no_xml_files(parser, tmp_path):
    """Test handling of empty report directory."""
    report_dir = tmp_path / 'build' / 'test-results' / 'test'
    report_dir.mkdir(parents=True)
    
    summary = parser.parse_results(tmp_path)
    
    assert summary.total == 0
    assert len(summary.errors) > 0
    assert "No test report XML files" in summary.errors[0]


def test_parse_success(parser, tmp_path):
    """Test parsing a successful test suite."""
    report_dir = tmp_path / 'build' / 'test-results' / 'test'
    report_dir.mkdir(parents=True)
    
    xml_content = """
    <testsuite name="com.example.Test" tests="2" failures="0" errors="0" skipped="0">
        <testcase name="testOne" classname="com.example.Test"/>
        <testcase name="testTwo" classname="com.example.Test"/>
    </testsuite>
    """
    
    (report_dir / "TEST-com.example.Test.xml").write_text(xml_content.strip())
    
    summary = parser.parse_results(tmp_path)
    
    assert summary.total == 2
    assert summary.passed == 2
    assert summary.failed == 0
    assert len(summary.failures) == 0
    assert len(summary.errors) == 0


def test_parse_failure(parser, tmp_path):
    """Test parsing a failed test suite."""
    report_dir = tmp_path / 'build' / 'test-results' / 'test'
    report_dir.mkdir(parents=True)
    
    xml_content = """
    <testsuite name="com.example.Test" tests="2" failures="1" errors="0" skipped="0">
        <testcase name="testPass" classname="com.example.Test"/>
        <testcase name="testFail" classname="com.example.Test">
            <failure message="Expected 1 but got 2">Stacktrace goes here...</failure>
        </testcase>
    </testsuite>
    """
    
    (report_dir / "TEST-com.example.Test.xml").write_text(xml_content.strip())
    
    summary = parser.parse_results(tmp_path)
    
    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert len(summary.failures) == 1
    
    failure = summary.failures[0]
    assert failure.name == "testFail"
    assert failure.message == "Expected 1 but got 2"
    assert "Stacktrace" in failure.stacktrace


def test_multiple_suites(parser, tmp_path):
    """Test aggregation of multiple test suites."""
    report_dir = tmp_path / 'build' / 'test-results' / 'test'
    report_dir.mkdir(parents=True)
    
    xml1 = '<testsuite name="T1" tests="1" failures="0" errors="0" skipped="0"></testsuite>'
    xml2 = '<testsuite name="T2" tests="1" failures="1" errors="0" skipped="0"><testcase><failure/></testcase></testsuite>'
    
    (report_dir / "TEST-1.xml").write_text(xml1)
    (report_dir / "TEST-2.xml").write_text(xml2)
    
    summary = parser.parse_results(tmp_path)
    
    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert len(summary.failures) == 1
