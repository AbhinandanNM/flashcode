#!/usr/bin/env node
/**
 * Comprehensive test runner for CodeCrafts MVP frontend
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

function runCommand(command, args, description) {
  return new Promise((resolve) => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Running: ${description}`);
    console.log(`Command: ${command} ${args.join(' ')}`);
    console.log(`${'='.repeat(60)}`);

    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      cwd: __dirname
    });

    child.on('close', (code) => {
      if (code === 0) {
        console.log(`✅ ${description} completed successfully`);
        resolve(true);
      } else {
        console.log(`❌ ${description} failed with code ${code}`);
        resolve(false);
      }
    });

    child.on('error', (error) => {
      console.error(`Error running ${description}:`, error);
      resolve(false);
    });
  });
}

async function main() {
  console.log('CodeCrafts MVP - Frontend Test Suite');
  console.log('='.repeat(60));

  // Check if node_modules exists
  if (!fs.existsSync(path.join(__dirname, 'node_modules'))) {
    console.log('Installing dependencies...');
    const installSuccess = await runCommand('npm', ['install'], 'Dependency Installation');
    if (!installSuccess) {
      console.log('Failed to install dependencies. Exiting.');
      process.exit(1);
    }
  }

  const testCommands = [
    {
      command: 'npm',
      args: ['run', 'test', '--', '--watchAll=false', '--coverage=false', '--testPathPattern=components/common'],
      description: 'Common Components Tests'
    },
    {
      command: 'npm',
      args: ['run', 'test', '--', '--watchAll=false', '--coverage=false', '--testPathPattern=hooks'],
      description: 'Custom Hooks Tests'
    },
    {
      command: 'npm',
      args: ['run', 'test', '--', '--watchAll=false', '--coverage=false', '--testPathPattern=services'],
      description: 'Service Layer Tests'
    },
    {
      command: 'npm',
      args: ['run', 'test', '--', '--watchAll=false', '--coverage=false', '--testPathPattern=userFlows'],
      description: 'End-to-End User Flow Tests'
    },
    {
      command: 'npm',
      args: ['run', 'test', '--', '--watchAll=false', '--coverage=false', '--testPathPattern=components/auth'],
      description: 'Authentication Component Tests'
    }
  ];

  let passedTests = 0;
  let failedTests = 0;

  // Run individual test suites
  for (const test of testCommands) {
    const success = await runCommand(test.command, test.args, test.description);
    if (success) {
      passedTests++;
    } else {
      failedTests++;
    }
  }

  // Run comprehensive test suite with coverage
  console.log(`\n${'='.repeat(60)}`);
  console.log('Running comprehensive test suite with coverage...');
  console.log(`${'='.repeat(60)}`);

  const coverageSuccess = await runCommand(
    'npm',
    ['run', 'test', '--', '--watchAll=false', '--coverage=true', '--coverageDirectory=coverage'],
    'Full Test Suite with Coverage'
  );

  if (coverageSuccess) {
    console.log('\n✅ Coverage report generated in coverage/lcov-report/index.html');
  }

  // Run linting
  console.log(`\n${'='.repeat(60)}`);
  console.log('Running code quality checks...');
  console.log(`${'='.repeat(60)}`);

  const lintSuccess = await runCommand('npm', ['run', 'lint'], 'ESLint Code Quality Check');

  // Run type checking
  const typeCheckSuccess = await runCommand('npx', ['tsc', '--noEmit'], 'TypeScript Type Checking');

  // Build test
  console.log(`\n${'='.repeat(60)}`);
  console.log('Testing production build...');
  console.log(`${'='.repeat(60)}`);

  const buildSuccess = await runCommand('npm', ['run', 'build'], 'Production Build Test');

  // Summary
  console.log(`\n${'='.repeat(80)}`);
  console.log('TEST SUMMARY');
  console.log(`${'='.repeat(80)}`);
  console.log(`✅ Passed test suites: ${passedTests}`);
  console.log(`❌ Failed test suites: ${failedTests}`);
  console.log(`📊 Total test suites: ${passedTests + failedTests}`);
  console.log(`🔍 Linting: ${lintSuccess ? 'PASSED' : 'FAILED'}`);
  console.log(`📝 Type checking: ${typeCheckSuccess ? 'PASSED' : 'FAILED'}`);
  console.log(`🏗️  Build: ${buildSuccess ? 'PASSED' : 'FAILED'}`);

  const allPassed = failedTests === 0 && lintSuccess && typeCheckSuccess && buildSuccess;

  if (allPassed) {
    console.log('\n🎉 All tests passed! The frontend is ready for deployment.');
    process.exit(0);
  } else {
    console.log('\n⚠️  Some tests failed. Please review the errors above.');
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n\nTest runner interrupted by user');
  process.exit(1);
});

process.on('SIGTERM', () => {
  console.log('\n\nTest runner terminated');
  process.exit(1);
});

main().catch((error) => {
  console.error('Test runner failed:', error);
  process.exit(1);
});