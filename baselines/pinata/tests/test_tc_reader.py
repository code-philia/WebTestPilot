import pytest
from VTAAS.data.testcase import TestCase, TestCaseCollection  # type: ignore


class DisablePyTestCollectionMixin(object):
    __test__: bool = False


class TestimonialFactory(DisablePyTestCollectionMixin):
    pass


@pytest.fixture
def test_collection() -> TestCaseCollection:
    return TestCaseCollection(
        "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
    )


@pytest.fixture
def test_case(test_collection: TestCaseCollection) -> TestCase:
    return test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )


def test_collection_number(test_collection: TestCaseCollection):
    assert len(test_collection) == 31


def test_TC_id_getter(test_collection: TestCaseCollection):
    # Get test cases in different ways
    specific_test = test_collection.get_test_case_by_id("28")
    assert specific_test.name == "Edit Account Information"


def test_TC_name_getter(test_collection: TestCaseCollection):
    name_test = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )
    assert int(name_test.id) == 3


def test_action_assertion_numbers(test_collection: TestCaseCollection):
    test_case = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )

    assert len(test_case.actions) == len(test_case.expected_results)

    # test with empty action
    test_case = test_collection.get_test_case_by_name("test_empty_action")
    print(test_case.actions)
    assert len(test_case.actions) == len(test_case.expected_results)

    # test with empty assertion
    test_case = test_collection.get_test_case_by_name("test_empty_assertion")
    assert len(test_case.actions) == len(test_case.expected_results)


def test_step_getter():
    test_collection = TestCaseCollection(
        "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
    )

    test_case = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )

    step = test_case.get_step(1)
    assert (
        step[0]
        == "Navigate to One Stop Market website at http://www.vtaas-benchmark.com:7770/"
    )
    assert step[1] == "Home page loads with category navigation menu visible"

    step = test_case.get_step(7)
    assert "Review cart contents:\r\nItem:" in step[0]
    assert "Shipping: $5.00 (Flat Rate - Fixed)" in step[0]
    assert step[1] == "All features are correct"


def test_step_getter_0():
    test_collection = TestCaseCollection(
        "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
    )

    test_case = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )
    with pytest.raises(ValueError):
        _ = test_case.get_step(0)


def test_step_getter_too_much():
    test_collection = TestCaseCollection(
        "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
    )

    test_case = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )
    with pytest.raises(ValueError):
        _ = test_case.get_step(8)


def test_steps_generator():
    test_collection = TestCaseCollection(
        "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
    )

    name_test = test_collection.get_test_case_by_name(
        "Product Selection and Cart Verification"
    )
    i = 0
    for _ in name_test:
        i += 1

    assert i == 7
