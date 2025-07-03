# Testing Guide for Arush LLM Package

This guide provides comprehensive instructions for testing the Arush LLM package, including unit tests, performance tests, and demo scenarios.

## Quick Start

### Run All Tests and Demo
```bash
cd backend/arush_llm
python run_tests.py
```

### Run Just the Performance Demo
```bash
python run_tests.py demo
```

### Run Specific Test Categories
```bash
python run_tests.py unit           # Unit tests only
python run_tests.py performance    # Performance tests only
python run_tests.py integration    # Integration tests only
```

## Test Structure

### Test Organization
```
tests/
├── __init__.py           # Test package setup
├── conftest.py           # Shared fixtures and configuration
├── pytest.ini           # Pytest configuration
├── test_cache.py         # Cache module tests
├── test_prompts.py       # Prompts module tests
├── test_parsers.py       # Parsers module tests
├── test_memory.py        # Memory module tests
└── test_location.py      # Location module tests
```

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Fast, isolated tests for individual components
- Test basic functionality and edge cases
- Validate O(1) time complexity assertions
- Example: Testing LRU cache put/get operations

#### Performance Tests (`@pytest.mark.performance`)
- Measure execution time and throughput
- Validate O(1) performance characteristics
- Benchmark against performance requirements
- Example: Testing 10,000 cache operations < 1ms each

#### Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- Validate end-to-end workflows
- Test data compatibility and API contracts
- Example: Complete agent decision cycle

## Test Coverage

### Core Components Tested

#### 1. Cache Module (`utils/cache.py`)
- **LRUCache**
  - ✅ Basic operations (put, get, delete)
  - ✅ LRU eviction policy
  - ✅ TTL expiration
  - ✅ Performance (O(1) operations)
  - ✅ Capacity management

- **AgentDataCache**
  - ✅ Multi-cache management
  - ✅ Data persistence
  - ✅ Cache invalidation
  - ✅ Type-specific caching

#### 2. Prompts Module (`utils/prompts.py`)
- **PromptTemplates**
  - ✅ Template compilation
  - ✅ Prompt generation for all action types
  - ✅ Caching effectiveness
  - ✅ Performance optimization
  - ✅ Context building

#### 3. Parsers Module (`utils/parsers.py`)
- **ResponseParser**
  - ✅ JSON extraction from various formats
  - ✅ Action extraction from text
  - ✅ Response sanitization
  - ✅ Pre-compiled regex performance

- **ActionValidator**
  - ✅ Action validation rules
  - ✅ Error reporting
  - ✅ Correction suggestions
  - ✅ Custom validation rules

#### 4. Memory Module (`agent/memory.py`)
- **AgentMemory**
  - ✅ Memory addition with indexing
  - ✅ Salience-based retrieval
  - ✅ Context-based retrieval
  - ✅ Memory search functionality
  - ✅ Persistence and loading

- **MemoryContextBuilder**
  - ✅ Context building for actions
  - ✅ Temporal context generation
  - ✅ Memory prioritization
  - ✅ Caching optimization

#### 5. Location Module (`agent/location.py`)
- **LocationTracker**
  - ✅ Position tracking and indexing
  - ✅ Object proximity detection
  - ✅ Movement option generation
  - ✅ Pathfinding algorithms
  - ✅ Spatial query optimization

## Performance Benchmarks

### Expected Performance Targets

| Operation | Target Time | Achieved |
|-----------|-------------|-----------|
| Cache Put | < 0.1ms | ✅ |
| Cache Get | < 0.1ms | ✅ |
| Memory Add | < 1ms | ✅ |
| Memory Query | < 1ms | ✅ |
| Prompt Generation | < 1ms | ✅ |
| JSON Parsing | < 0.1ms | ✅ |
| Location Update | < 1ms | ✅ |
| Integration Cycle | < 10ms | ✅ |

### Scalability Validation

The tests verify O(1) performance scaling:
- Cache performance remains constant with 100x data increase
- Memory operations scale logarithmically with indexing
- Prompt generation benefits from template caching
- Parser operations use pre-compiled patterns

## Demo Scenarios

### Performance Showcase Demo

The comprehensive demo (`demo/performance_showcase.py`) includes:

1. **Cache Performance Demo**
   - LRU Cache with 10,000 operations
   - AgentDataCache with multi-type storage
   - Performance comparison and validation

2. **Prompt Performance Demo**
   - 1,000 prompt generations
   - Template caching effectiveness
   - Speedup measurement vs manual formatting

3. **Parser Performance Demo**
   - JSON extraction from various formats
   - Action validation with different rules
   - Pre-compiled regex performance

4. **Memory Performance Demo**
   - 1,000 memory additions with indexing
   - Salience/context-based retrieval
   - Search and context building

5. **Location Performance Demo**
   - Position tracking and spatial indexing
   - Object proximity queries
   - Movement and pathfinding operations

6. **Integration Scenario Demo**
   - 100 complete agent decision cycles
   - Component interaction validation
   - End-to-end performance measurement

7. **Scalability Demo**
   - Performance scaling with data size
   - O(1) characteristic validation
   - Resource usage analysis

## Running Tests

### Prerequisites
```bash
pip install pytest
```

### Basic Test Execution
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_cache.py

# Run specific test method
pytest tests/test_cache.py::TestLRUCache::test_basic_operations

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m performance   # Performance tests only
```

### Advanced Test Options
```bash
# Run with timing information
pytest --durations=10

# Run with output capture disabled (for performance prints)
pytest -s

# Run with specific pattern
pytest -k "cache"

# Run with coverage (if pytest-cov installed)
pytest --cov=arush_llm
```

## Interpreting Results

### Performance Test Output
Performance tests include timing output like:
```
Put performance: 0.000045s per operation
Get performance: 0.000032s per operation
Cache hit rate: 99.8%
```

### Success Criteria
- All unit tests pass (functionality verified)
- Performance tests meet time targets (< 1ms for most operations)
- Integration tests complete without errors
- Demo runs successfully and shows expected performance

### Troubleshooting

#### Common Issues
1. **Import Errors**: Ensure `backend` directory is in Python path
2. **Missing Dependencies**: Run `pip install pytest`
3. **Permission Errors**: Check file permissions for test files
4. **Performance Failures**: May indicate system load or hardware constraints

#### Debug Mode
```bash
# Run tests with debugging
pytest --pdb              # Drop into debugger on failure
pytest --capture=no -v    # Show all output
```

## Continuous Integration

### Test Automation
The package includes automated test scripts:
- `run_tests.py`: Comprehensive test runner
- Dependency checking
- Performance regression detection
- Automated reporting

### Performance Monitoring
Tests include performance regression detection:
- Baseline performance metrics
- Automated performance comparison
- Scalability validation
- Resource usage monitoring

## Contributing Tests

### Adding New Tests
1. Create test file in `tests/` directory
2. Use appropriate pytest markers (`@pytest.mark.unit`, etc.)
3. Include performance assertions where relevant
4. Add to test coverage documentation

### Test Standards
- Use descriptive test names
- Include docstrings explaining test purpose
- Test both success and error cases
- Validate performance characteristics
- Use fixtures for common test data 