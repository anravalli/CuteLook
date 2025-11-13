from functools import wraps


class TestFailedException(BaseException): ...


def TestFunction(test):
    @wraps(test)
    def TestWrapper():
        print(f"Running test: {test.__name__}")
        try:
            test()
            print("PASS")
        except TestFailedException as e:
            print("FAILED")
            raise e

    return TestWrapper


def RunTest(test_list: list[any]) -> tuple[int, int]:
    passed = failed = 0
    total = len(test_list)

    for test in test_list:
        try:
            test()
            passed += 1
        except TestFailedException as e:
            failed += 1
    print(f"{passed}/{total} tests passed")
    print(f"{failed} tests failed")

    return (passed, failed)
