#!/usr/bin/env python3.4
#
#   Copyright 2016 - The Android Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

try:
  from unittest import mock  # PY3
except ImportError:
  import mock  # PY2

import unittest

from acts import base_test
from acts import signals
from acts import test_runner

MSG_EXPECTED_EXCEPTION = "This is an expected exception."
MSG_EXPECTED_TEST_FAILURE = "This is an expected test failure."
MSG_UNEXPECTED_EXCEPTION = "Unexpected exception!"

MOCK_EXTRA = {"key": "value", "answer_to_everything": 42}

def never_call():
    raise Exception(MSG_UNEXPECTED_EXCEPTION)

class ActsBaseClassTest(unittest.TestCase):

    def setUp(self):
        self.mock_test_cls_configs = {
            'reporter': mock.MagicMock(),
            'log': mock.MagicMock(),
            'log_path': '/tmp',
            'cli_args': None,
            'user_params': {}
        }
        self.mock_test_name = "test_something"

    def test_current_test_case_name(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.assert_true(self.current_test_name == "test_func", ("Got "
                                 "unexpected test name %s."
                                 ) % self.current_test_name)
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertIsNone(actual_record.details)
        self.assertIsNone(actual_record.extras)

    def test_self_tests_list(self):
        class MockBaseTest(base_test.BaseTestClass):
            def __init__(self, controllers):
                super(MockBaseTest, self).__init__(controllers)
                self.tests = ("test_something",)
            def test_something(self):
                pass
            def test_never(self):
                # This should not execute it's not on default test list.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run()
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_something")

    def test_self_tests_list_fail_by_convention(self):
        class MockBaseTest(base_test.BaseTestClass):
            def __init__(self, controllers):
                super(MockBaseTest, self).__init__(controllers)
                self.tests = ("not_a_test_something",)
            def not_a_test_something(self):
                pass
            def test_never(self):
                # This should not execute it's not on default test list.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        expected_msg = ("Test case name not_a_test_something does not follow "
                        "naming convention test_*, abort.")
        with self.assertRaises(test_runner.USERError, msg=expected_msg):
            bt_cls.run()

    def test_cli_test_selection_override_self_tests_list(self):
        class MockBaseTest(base_test.BaseTestClass):
            def __init__(self, controllers):
                super(MockBaseTest, self).__init__(controllers)
                self.tests = ("test_never",)
            def test_something(self):
                pass
            def test_never(self):
                # This should not execute it's not selected by cmd line input.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_something"])
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_something")

    def test_cli_test_selection_fail_by_convention(self):
        class MockBaseTest(base_test.BaseTestClass):
            def __init__(self, controllers):
                super(MockBaseTest, self).__init__(controllers)
                self.tests = ("not_a_test_something",)
            def not_a_test_something(self):
                pass
            def test_never(self):
                # This should not execute it's not selected by cmd line input.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        expected_msg = ("Test case name not_a_test_something does not follow "
                        "naming convention test_*, abort.")
        with self.assertRaises(test_runner.USERError, msg=expected_msg):
            bt_cls.run(test_names=["not_a_test_something"])

    def test_default_execution_of_all_tests(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_something(self):
                pass
            def not_a_test(self):
                # This should not execute its name doesn't follow test case
                # naming convention.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_something"])
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_something")

    def test_setup_class_fail_by_exception(self):
        class MockBaseTest(base_test.BaseTestClass):
            def setup_class(self):
                raise Exception(MSG_EXPECTED_EXCEPTION)
            def test_something(self):
                # This should not execute because setup_class failed.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.failed[0]
        self.assertEqual(actual_record.test_name, "")
        expected_msg = "setup_class failed for MockBaseTest: %s" % (
                       MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.details, expected_msg)
        self.assertIsNone(actual_record.extras)
        expected_summary = ("Executed 1, Failed 1, Passed 0, Requested 1, "
                            "Skipped 0, Unknown 0")
        self.assertEqual(bt_cls.results.summary_str(), expected_summary)

    def test_setup_test_fail_by_exception(self):
        class MockBaseTest(base_test.BaseTestClass):
            def setup_test(self):
                raise Exception(MSG_EXPECTED_EXCEPTION)
            def test_something(self):
                # This should not execute because setup_test failed.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_something"])
        actual_record = bt_cls.results.unknown[0]
        self.assertEqual(actual_record.test_name, self.mock_test_name)
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertIsNone(actual_record.extras)
        expected_summary = ("Executed 1, Failed 0, Passed 0, Requested 1, "
                            "Skipped 0, Unknown 1")
        self.assertEqual(bt_cls.results.summary_str(), expected_summary)

    def test_setup_test_fail_by_test_signal(self):
        class MockBaseTest(base_test.BaseTestClass):
            def setup_test(self):
                raise signals.TestFailure(MSG_EXPECTED_EXCEPTION)
            def test_something(self):
                # This should not execute because setup_test failed.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_something"])
        actual_record = bt_cls.results.failed[0]
        self.assertEqual(actual_record.test_name, self.mock_test_name)
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertIsNone(actual_record.extras)
        expected_summary = ("Executed 1, Failed 1, Passed 0, Requested 1, "
                            "Skipped 0, Unknown 0")
        self.assertEqual(bt_cls.results.summary_str(), expected_summary)

    def test_setup_test_fail_by_return_False(self):
        class MockBaseTest(base_test.BaseTestClass):
            def setup_test(self):
                return False
            def test_something(self):
                # This should not execute because setup_test failed.
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_something"])
        actual_record = bt_cls.results.failed[0]
        expected_msg = "Setup for %s failed." % self.mock_test_name
        self.assertEqual(actual_record.test_name, self.mock_test_name)
        self.assertEqual(actual_record.details, expected_msg)
        self.assertIsNone(actual_record.extras, None)
        expected_summary = ("Executed 1, Failed 1, Passed 0, Requested 1, "
                            "Skipped 0, Unknown 0")
        self.assertEqual(bt_cls.results.summary_str(), expected_summary)

    def test_abort_class(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_1(self):
                pass
            def test_2(self):
                self.abort_class(MSG_EXPECTED_EXCEPTION)
                never_call()
            def test_3(self):
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_1", "test_2", "test_3"])
        self.assertEqual(bt_cls.results.passed[0].test_name,
                         "test_1")
        self.assertEqual(bt_cls.results.skipped[0].details,
                         MSG_EXPECTED_EXCEPTION)
        self.assertEqual(bt_cls.results.summary_str(),
                         ("Executed 2, Failed 0, Passed 1, Requested 3, "
                          "Skipped 1, Unknown 0"))

    def test_uncaught_exception(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                raise Exception(MSG_EXPECTED_EXCEPTION)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.unknown[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertIsNone(actual_record.extras)

    def test_fail(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.fail(MSG_EXPECTED_EXCEPTION, extras=MOCK_EXTRA)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.failed[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.extras, MOCK_EXTRA)

    def test_assert_true(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.assert_true(False, MSG_EXPECTED_EXCEPTION,
                                 extras=MOCK_EXTRA)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.failed[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.extras, MOCK_EXTRA)

    def test_explicit_pass(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.explicit_pass(MSG_EXPECTED_EXCEPTION,
                                   extras=MOCK_EXTRA)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.extras, MOCK_EXTRA)

    def test_implicit_pass(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                pass
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.passed[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertIsNone(actual_record.details)
        self.assertIsNone(actual_record.extras)

    def test_skip(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.skip(MSG_EXPECTED_EXCEPTION, extras=MOCK_EXTRA)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.skipped[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.extras, MOCK_EXTRA)

    def test_skip_if(self):
        class MockBaseTest(base_test.BaseTestClass):
            def test_func(self):
                self.skip_if(False, MSG_UNEXPECTED_EXCEPTION)
                self.skip_if(True, MSG_EXPECTED_EXCEPTION,
                             extras=MOCK_EXTRA)
                never_call()
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        actual_record = bt_cls.results.skipped[0]
        self.assertEqual(actual_record.test_name, "test_func")
        self.assertEqual(actual_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(actual_record.extras, MOCK_EXTRA)

    def test_unpack_userparams_required(self):
        """Missing a required param should raise an error."""
        required = ["something"]
        bc = base_test.BaseTestClass(self.mock_test_cls_configs)
        expected_msg = ("Missing required user param '%s' in test "
                        "configuration.") % required[0]
        with self.assertRaises(base_test.BaseTestError, msg=expected_msg):
            bc.unpack_userparams(required)

    def test_unpack_userparams_optional(self):
        """Missing an optional param should not raise an error."""
        opt = ["something"]
        bc = base_test.BaseTestClass(self.mock_test_cls_configs)
        bc.unpack_userparams(opt_param_names=opt)

    def test_unpack_userparams_basic(self):
        """Required and optional params are unpacked properly."""
        required = ["something"]
        optional = ["something_else"]
        configs = dict(self.mock_test_cls_configs)
        configs["user_params"]["something"] = 42
        configs["user_params"]["something_else"] = 53
        bc = base_test.BaseTestClass(configs)
        bc.unpack_userparams(req_param_names=required,
                             opt_param_names=optional)
        self.assertEqual(bc.something, 42)
        self.assertEqual(bc.something_else, 53)

    def test_unpack_userparams_default_overwrite(self):
        default_arg_val = "haha"
        actual_arg_val = "wawa"
        arg_name = "arg1"
        configs = dict(self.mock_test_cls_configs)
        configs["user_params"][arg_name] = actual_arg_val
        bc = base_test.BaseTestClass(configs)
        bc.unpack_userparams(opt_param_names=[arg_name],
                             arg1=default_arg_val)
        self.assertEqual(bc.arg1, actual_arg_val)

    def test_unpack_userparams_default_None(self):
        bc = base_test.BaseTestClass(self.mock_test_cls_configs)
        bc.unpack_userparams(arg1="haha")
        self.assertEqual(bc.arg1, "haha")

    def test_generated_tests(self):
        """Execute code paths for generated test cases.

        Three test cases are generated, each of them produces a different
        result: one pass, one fail, and one skip.

        This test verifies that the exact three tests are executed and their
        results are reported correctly.
        """
        static_arg = "haha"
        static_kwarg = "meh"
        itrs = ["pass", "fail", "skip"]
        class MockBaseTest(base_test.BaseTestClass):
            def name_gen(self, setting, arg, special_arg=None):
                return "test_%s_%s" % (setting, arg)
            def logic(self, setting, arg, special_arg=None):
                self.assert_true(setting in itrs,
                                 ("%s is not in acceptable settings range %s"
                                 ) % (setting, itrs))
                self.assert_true(arg == static_arg,
                                 "Expected %s, got %s" % (static_arg, arg))
                self.assert_true(arg == static_arg,
                                 "Expected %s, got %s" % (static_kwarg,
                                                          special_arg))
                if setting == "pass":
                    self.explicit_pass(MSG_EXPECTED_EXCEPTION,
                                       extras=MOCK_EXTRA)
                elif setting == "fail":
                    self.fail(MSG_EXPECTED_EXCEPTION, extras=MOCK_EXTRA)
                elif setting == "skip":
                    self.skip(MSG_EXPECTED_EXCEPTION, extras=MOCK_EXTRA)
            @signals.generated_test
            def test_func(self):
                self.run_generated_testcases(
                    test_func=self.logic,
                    settings=itrs,
                    args=(static_arg,),
                    name_func=self.name_gen
                )
        bt_cls = MockBaseTest(self.mock_test_cls_configs)
        bt_cls.run(test_names=["test_func"])
        self.assertEqual(len(bt_cls.results.requested), 3)
        pass_record = bt_cls.results.passed[0]
        self.assertEqual(pass_record.test_name, "test_pass_%s" % static_arg)
        self.assertEqual(pass_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(pass_record.extras, MOCK_EXTRA)
        skip_record = bt_cls.results.skipped[0]
        self.assertEqual(skip_record.test_name, "test_skip_%s" % static_arg)
        self.assertEqual(skip_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(skip_record.extras, MOCK_EXTRA)
        fail_record = bt_cls.results.failed[0]
        self.assertEqual(fail_record.test_name, "test_fail_%s" % static_arg)
        self.assertEqual(fail_record.details, MSG_EXPECTED_EXCEPTION)
        self.assertEqual(fail_record.extras, MOCK_EXTRA)

if __name__ == "__main__":
   unittest.main()