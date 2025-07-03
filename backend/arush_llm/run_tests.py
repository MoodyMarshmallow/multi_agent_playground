#!/usr/bin/env python3
"""
Test Runner for Arush LLM Package
=================================

Comprehensive test runner with performance reporting and coverage analysis.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestRunner:
    """Comprehensive test runner for the arush_llm package."""
    
    def __init__(self):
        self.package_dir = Path(__file__).parent
        self.test_dir = self.package_dir / "tests"
        
    def run_all_tests(self):
        """Run all test suites with detailed reporting."""
        print("🧪 Arush LLM Package Test Suite")
        print("=" * 50)
        print(f"Package directory: {self.package_dir}")
        print(f"Test directory: {self.test_dir}")
        print()
        
        # Check if pytest is available
        try:
            import pytest
            print("✅ pytest is available")
        except ImportError:
            print("❌ pytest not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
            import pytest
        
        # Run unit tests
        print("\n📋 Running Unit Tests...")
        self.run_unit_tests()
        
        # Run performance tests
        print("\n⚡ Running Performance Tests...")
        self.run_performance_tests()
        
        # Run integration tests
        print("\n🔗 Running Integration Tests...")
        self.run_integration_tests()
        
        # Generate summary
        print("\n📊 Test Summary")
        print("-" * 30)
        
    def run_unit_tests(self):
        """Run unit tests with coverage."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "unit",
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.package_dir, capture_output=True, text=True)
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error running unit tests: {e}")
    
    def run_performance_tests(self):
        """Run performance-specific tests."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "performance",
            "-v",
            "-s",  # Don't capture output for performance prints
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.package_dir, capture_output=True, text=True)
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error running performance tests: {e}")
    
    def run_integration_tests(self):
        """Run integration tests."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "integration",
            "-v",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.package_dir, capture_output=True, text=True)
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"Error running integration tests: {e}")
    
    def run_demo(self):
        """Run the performance demonstration."""
        print("\n🚀 Running Performance Demo...")
        print("-" * 30)
        
        demo_script = self.package_dir / "demo" / "performance_showcase.py"
        
        if demo_script.exists():
            try:
                result = subprocess.run([sys.executable, str(demo_script)], 
                                      cwd=self.package_dir, 
                                      capture_output=False)
                print(f"\nDemo completed with exit code: {result.returncode}")
            except Exception as e:
                print(f"Error running demo: {e}")
        else:
            print(f"Demo script not found: {demo_script}")
    
    def check_dependencies(self):
        """Check if all required dependencies are available."""
        print("🔍 Checking Dependencies...")
        print("-" * 30)
        
        required_packages = [
            'pytest',
            'pathlib',
            'json',
            'time',
            're',
            'collections',
            'string',
            'typing'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package}")
                missing.append(package)
        
        if missing:
            print(f"\n❌ Missing packages: {', '.join(missing)}")
            print("Install with: pip install pytest")
        else:
            print("\n✅ All dependencies satisfied")
        
        return len(missing) == 0
    
    def run_specific_test(self, test_file):
        """Run a specific test file."""
        test_path = self.test_dir / test_file
        if test_path.exists():
            cmd = [sys.executable, "-m", "pytest", str(test_path), "-v"]
            subprocess.run(cmd, cwd=self.package_dir)
        else:
            print(f"Test file not found: {test_path}")


def main():
    """Main test runner entry point."""
    runner = TestRunner()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            runner.run_demo()
        elif command == "deps":
            runner.check_dependencies()
        elif command == "unit":
            runner.run_unit_tests()
        elif command == "performance":
            runner.run_performance_tests()
        elif command == "integration":
            runner.run_integration_tests()
        elif command.startswith("test_"):
            runner.run_specific_test(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: demo, deps, unit, performance, integration, test_<filename>")
    else:
        # Check dependencies first
        if runner.check_dependencies():
            # Run all tests
            runner.run_all_tests()
            # Run demo
            runner.run_demo()
        else:
            print("Please install missing dependencies first.")


if __name__ == "__main__":
    main() 