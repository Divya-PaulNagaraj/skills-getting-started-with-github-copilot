# Tests for Mergington High School Activities API

This directory contains comprehensive test suites for the FastAPI application using pytest.

## Test Structure

- `test_api.py` - Core API endpoint tests
- `test_edge_cases.py` - Edge cases and error handling tests  
- `test_performance.py` - Performance and load tests
- `conftest.py` - Shared test fixtures and configuration

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run with coverage report:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/test_api.py
```

### Run specific test class:
```bash
pytest tests/test_api.py::TestSignupEndpoint
```

### Run specific test method:
```bash
pytest tests/test_api.py::TestSignupEndpoint::test_signup_success
```

## Test Coverage

The test suite provides comprehensive coverage including:

- ✅ All API endpoints (GET /activities, POST /activities/{name}/signup, DELETE /activities/{name}/participants/{email})
- ✅ Success and error scenarios
- ✅ Data validation and edge cases
- ✅ URL encoding and special characters
- ✅ Concurrent operations simulation
- ✅ Performance testing
- ✅ Integration workflows

## Test Categories

### Core API Tests (`test_api.py`)
- Root endpoint redirection
- Activities retrieval
- Student signup functionality
- Participant removal
- Integration scenarios

### Edge Cases (`test_edge_cases.py`)
- Special characters in emails
- Case sensitivity
- Data consistency
- Concurrent operations
- Error handling
- Input validation

### Performance Tests (`test_performance.py`)
- Response time validation
- Load testing with multiple requests
- Stress scenarios
- Concurrency simulation

## Fixtures

The `conftest.py` file provides:
- Test client setup
- Activity data reset between tests
- Sample test data

## Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support  
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

## Notes

- Tests automatically reset the activities data before each test
- All tests are isolated and can run independently
- 100% code coverage achieved
- Tests handle URL encoding properly for special characters