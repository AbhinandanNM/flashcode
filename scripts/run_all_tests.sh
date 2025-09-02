#!/bin/bash

# CodeCrafts MVP - Complete Test Suite Runner
# This script runs all tests: unit, integration, and end-to-end validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
LOG_FILE="./logs/test_results_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory
mkdir -p logs

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Test result tracking
declare -A test_results
total_suites=0
passed_suites=0
failed_suites=0

run_test_suite() {
    local suite_name="$1"
    local command="$2"
    local description="$3"
    
    total_suites=$((total_suites + 1))
    
    log "Running $suite_name: $description"
    echo "Command: $command" >> "$LOG_FILE"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        success "$suite_name completed successfully"
        test_results["$suite_name"]="PASS"
        passed_suites=$((passed_suites + 1))
        return 0
    else
        error "$suite_name failed"
        test_results["$suite_name"]="FAIL"
        failed_suites=$((failed_suites + 1))
        return 1
    fi
}

check_services() {
    log "Checking service availability..."
    
    # Check backend
    if curl -f -s "$BACKEND_URL/health" > /dev/null 2>&1; then
        success "Backend is running at $BACKEND_URL"
    else
        warning "Backend not available at $BACKEND_URL"
        info "Starting backend services..."
        
        # Try to start services
        if [ -f "docker-compose.yml" ]; then
            docker-compose up -d backend db redis
            sleep 10
            
            if curl -f -s "$BACKEND_URL/health" > /dev/null 2>&1; then
                success "Backend started successfully"
            else
                error "Failed to start backend services"
                return 1
            fi
        else
            error "Backend not available and no docker-compose.yml found"
            return 1
        fi
    fi
    
    # Check frontend (optional)
    if curl -f -s "$FRONTEND_URL" > /dev/null 2>&1; then
        success "Frontend is running at $FRONTEND_URL"
    else
        warning "Frontend not available at $FRONTEND_URL (this is optional for API tests)"
    fi
    
    return 0
}

run_backend_tests() {
    log "Running Backend Test Suite..."
    
    cd backend
    
    # Unit tests
    run_test_suite "Backend Unit Tests" \
        "python -m pytest test_auth.py test_lessons.py test_questions.py test_code_execution.py test_duels.py -v" \
        "Core backend functionality tests"
    
    # Integration tests
    run_test_suite "Backend Integration Tests" \
        "python -m pytest test_integration.py test_lesson_integration.py test_question_integration.py test_code_execution_integration.py test_duel_integration.py -v" \
        "Backend service integration tests"
    
    # Database tests
    run_test_suite "Database Tests" \
        "python -m pytest test_models.py test_database_integration.py -v" \
        "Database model and integration tests"
    
    # API endpoint tests
    run_test_suite "API Endpoint Tests" \
        "python -m pytest test_api_endpoints.py -v" \
        "Complete API endpoint validation"
    
    # Complete integration tests
    run_test_suite "Complete Integration Tests" \
        "python -m pytest test_complete_integration.py -v" \
        "End-to-end backend integration tests"
    
    cd ..
}

run_frontend_tests() {
    log "Running Frontend Test Suite..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        npm install
    fi
    
    # Unit tests
    run_test_suite "Frontend Unit Tests" \
        "npm test -- --watchAll=false --coverage=false --testPathPattern='components|hooks|utils'" \
        "React component and hook tests"
    
    # Service tests
    run_test_suite "Frontend Service Tests" \
        "npm test -- --watchAll=false --coverage=false --testPathPattern='services'" \
        "Frontend service layer tests"
    
    # Integration tests
    run_test_suite "Frontend Integration Tests" \
        "npm test -- --watchAll=false --coverage=false --testPathPattern='userFlows'" \
        "Frontend user flow tests"
    
    # Build test
    run_test_suite "Frontend Build Test" \
        "npm run build" \
        "Production build validation"
    
    cd ..
}

run_integration_tests() {
    log "Running Application Integration Tests..."
    
    # Make scripts executable
    chmod +x scripts/integration_test.py
    chmod +x scripts/validate_features.py
    
    # API Integration tests
    run_test_suite "API Integration Tests" \
        "python3 scripts/integration_test.py" \
        "Complete API workflow validation"
    
    # Feature validation tests
    run_test_suite "Feature Validation Tests" \
        "python3 scripts/validate_features.py" \
        "All feature functionality validation"
}

run_performance_tests() {
    log "Running Performance Tests..."
    
    # Database performance
    run_test_suite "Database Performance Tests" \
        "cd backend && python -m pytest test_database_integration.py::TestDatabasePerformance -v" \
        "Database query performance validation"
    
    # API performance (basic load test)
    if command -v ab > /dev/null 2>&1; then
        run_test_suite "API Load Test" \
            "ab -n 100 -c 10 $BACKEND_URL/health" \
            "Basic API load testing with Apache Bench"
    else
        warning "Apache Bench (ab) not available, skipping load tests"
    fi
}

run_security_tests() {
    log "Running Security Tests..."
    
    # Authentication security
    run_test_suite "Authentication Security Tests" \
        "cd backend && python -m pytest test_api_endpoints.py::TestErrorHandling -v" \
        "Authentication and authorization security"
    
    # Input validation
    run_test_suite "Input Validation Tests" \
        "cd backend && python -m pytest test_api_endpoints.py::TestErrorHandling::test_invalid_json_payload test_api_endpoints.py::TestErrorHandling::test_missing_required_fields -v" \
        "Input validation and sanitization"
}

generate_coverage_report() {
    log "Generating Coverage Reports..."
    
    # Backend coverage
    if [ -d "backend" ]; then
        cd backend
        if run_test_suite "Backend Coverage Report" \
            "python -m pytest --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml" \
            "Backend code coverage analysis"; then
            info "Backend coverage report generated in backend/htmlcov/"
        fi
        cd ..
    fi
    
    # Frontend coverage
    if [ -d "frontend" ]; then
        cd frontend
        if run_test_suite "Frontend Coverage Report" \
            "npm test -- --coverage --watchAll=false --coverageDirectory=coverage" \
            "Frontend code coverage analysis"; then
            info "Frontend coverage report generated in frontend/coverage/"
        fi
        cd ..
    fi
}

print_summary() {
    log ""
    log "="*80
    log "CODECRAFTS MVP - COMPLETE TEST SUITE RESULTS"
    log "="*80
    
    log "Test Suite Results:"
    for suite in "${!test_results[@]}"; do
        result="${test_results[$suite]}"
        if [ "$result" = "PASS" ]; then
            success "$suite: PASSED"
        else
            error "$suite: FAILED"
        fi
    done
    
    log ""
    log "Summary Statistics:"
    log "Total Test Suites: $total_suites"
    log "Passed: $passed_suites"
    log "Failed: $failed_suites"
    
    if [ $failed_suites -eq 0 ]; then
        success_rate="100.0"
    else
        success_rate=$(echo "scale=1; $passed_suites * 100 / $total_suites" | bc -l)
    fi
    
    log "Success Rate: ${success_rate}%"
    
    log ""
    log "Detailed logs available in: $LOG_FILE"
    
    if [ $failed_suites -eq 0 ]; then
        log ""
        success "🎉 ALL TESTS PASSED! CodeCrafts MVP is ready for production deployment."
        log ""
        log "Next steps:"
        log "1. Review coverage reports for any gaps"
        log "2. Run deployment validation: ./scripts/deploy.sh --skip-backup"
        log "3. Perform final manual testing"
        log "4. Deploy to production environment"
    else
        log ""
        error "⚠️  $failed_suites test suite(s) failed. Please review the errors above."
        log ""
        log "Troubleshooting steps:"
        log "1. Check the detailed log file: $LOG_FILE"
        log "2. Ensure all services are running properly"
        log "3. Verify database connectivity and migrations"
        log "4. Check for missing dependencies or configuration"
    fi
}

cleanup() {
    log "Cleaning up test environment..."
    
    # Stop any test containers if they were started
    if [ -f "docker-compose.yml" ]; then
        docker-compose down > /dev/null 2>&1 || true
    fi
    
    # Clean up temporary files
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

main() {
    log "Starting CodeCrafts MVP Complete Test Suite"
    log "Backend URL: $BACKEND_URL"
    log "Frontend URL: $FRONTEND_URL"
    log "Log file: $LOG_FILE"
    
    # Parse command line arguments
    RUN_BACKEND=true
    RUN_FRONTEND=true
    RUN_INTEGRATION=true
    RUN_PERFORMANCE=false
    RUN_SECURITY=true
    GENERATE_COVERAGE=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                RUN_FRONTEND=false
                RUN_INTEGRATION=false
                shift
                ;;
            --frontend-only)
                RUN_BACKEND=false
                RUN_INTEGRATION=false
                shift
                ;;
            --integration-only)
                RUN_BACKEND=false
                RUN_FRONTEND=false
                shift
                ;;
            --skip-performance)
                RUN_PERFORMANCE=false
                shift
                ;;
            --include-performance)
                RUN_PERFORMANCE=true
                shift
                ;;
            --skip-coverage)
                GENERATE_COVERAGE=false
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --backend-only       Run only backend tests"
                echo "  --frontend-only      Run only frontend tests"
                echo "  --integration-only   Run only integration tests"
                echo "  --include-performance Include performance tests"
                echo "  --skip-performance   Skip performance tests (default)"
                echo "  --skip-coverage      Skip coverage report generation"
                echo "  --help               Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check service availability
    if ! check_services; then
        error "Service check failed. Cannot proceed with tests."
        exit 1
    fi
    
    # Run test suites based on configuration
    if [ "$RUN_BACKEND" = true ]; then
        run_backend_tests
    fi
    
    if [ "$RUN_FRONTEND" = true ]; then
        run_frontend_tests
    fi
    
    if [ "$RUN_INTEGRATION" = true ]; then
        run_integration_tests
    fi
    
    if [ "$RUN_PERFORMANCE" = true ]; then
        run_performance_tests
    fi
    
    if [ "$RUN_SECURITY" = true ]; then
        run_security_tests
    fi
    
    if [ "$GENERATE_COVERAGE" = true ]; then
        generate_coverage_report
    fi
    
    # Print final summary
    print_summary
    
    # Cleanup
    cleanup
    
    # Exit with appropriate code
    if [ $failed_suites -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Handle script interruption
trap 'error "Test suite interrupted"; cleanup; exit 1' INT TERM

# Run main function
main "$@"