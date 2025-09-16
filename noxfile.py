# noxfile.py
import nox
import json
import datetime
import subprocess
import sys

nox.options.default_venv_backend = "uv"

@nox.session
def quality(session):
    """Run all quality checks and report results"""
    print("🔍 Running code quality checks...\n")

    results = {
        'timestamp': datetime.datetime.now().isoformat(),
        'tools': {}
    }
    
    # Run ruff on src
    print("📝 Ruff src (linting)...")
    try:
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "src"],
            capture_output=True, text=True, check=True
        )
        results['tools']['ruff_src'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Ruff src: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['ruff_src'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Ruff src: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['ruff_src'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Ruff src: FAIL - {str(e)}")

    # Run ruff on tests
    print("\n📝 Ruff tests (linting)...")
    try:
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "tests"],
            capture_output=True, text=True, check=True
        )
        results['tools']['ruff_tests'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Ruff tests: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['ruff_tests'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Ruff tests: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['ruff_tests'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Ruff tests: FAIL - {str(e)}")
    
    # Run pyright
    print("\n🔧 Pyright (type checking)...")
    try:
        result = subprocess.run(
            ["npx", "pyright"],
            capture_output=True, text=True, check=True
        )
        results['tools']['pyright'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Pyright: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['pyright'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Pyright: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['pyright'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Pyright: FAIL - {str(e)}")
    
    # Run unit tests
    print("\n🧪 Unit Tests...")
    try:
        result = subprocess.run(
            ["uv", "run", "--env-file", ".env.testing", "pytest", "tests/unit/", "-v"],
            capture_output=True, text=True, check=True
        )
        results['tools']['unit_tests'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Unit Tests: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['unit_tests'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Unit Tests: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['unit_tests'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Unit Tests: FAIL - {str(e)}")

    # Run integration tests
    print("\n🧪 Integration Tests...")
    try:
        result = subprocess.run(
            ["uv", "run", "--env-file", ".env.testing", "pytest", "tests/integration/", "-v"],
            capture_output=True, text=True, check=True
        )
        results['tools']['integration_tests'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Integration Tests: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['integration_tests'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Integration Tests: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['integration_tests'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Integration Tests: FAIL - {str(e)}")

    # Run behave
    print("\n🧪 Behave (BDD tests)...")
    try:
        result = subprocess.run(
            ["uv", "run", "--env-file", ".env.testing", "behave", "tests/bdd", "--quiet", "--no-capture"],
            capture_output=True, text=True, check=True
        )
        results['tools']['behave'] = {'success': True, 'output': result.stdout, 'errors': result.stderr}
        print("✅ Behave: PASS")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        results['tools']['behave'] = {'success': False, 'output': e.stdout, 'errors': e.stderr}
        print("❌ Behave: FAIL")
        if e.stdout.strip():
            print(f"Output: {e.stdout}")
        if e.stderr.strip():
            print(f"Errors: {e.stderr}")
    except Exception as e:
        results['tools']['behave'] = {'success': False, 'output': '', 'errors': str(e)}
        print(f"❌ Behave: FAIL - {str(e)}")
    
    # Summary
    all_passed = all(result['success'] for result in results['tools'].values())
    results['overall_success'] = all_passed
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
    else:
        print("❌ SOME CHECKS FAILED")
        failed_tools = [tool for tool, result in results['tools'].items() if not result['success']]
        print(f"Failed: {', '.join(failed_tools)}")
    print("="*50)
    
    # Write results to file
    with open('quality-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Detailed results written to: quality-results.json")
    
    if not all_passed:
        session.error("Quality checks failed")