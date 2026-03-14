from tools.docker_test_tool import run_isolated_test

def test_polyglot_lab():
    tests = [
        ("print('Python: Online')", "test.py"),
        ("console.log('JS: Online')", "test.js"),
        ("#include <iostream>\nint main() { std::cout << 'C++: Online' << std::endl; return 0; }", "test.cpp")
    ]

    for code, filename in tests:
        print(f"--- Testing {filename} ---")
        success, logs = run_isolated_test(code, filename)
        if success:
            print(f"✅ Success: {logs.strip()}")
        else:
            print(f"❌ Failed: {logs}")

if __name__ == "__main__":
    test_polyglot_lab()