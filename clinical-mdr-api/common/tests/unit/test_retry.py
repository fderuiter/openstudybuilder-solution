import time
import unittest
from unittest.mock import MagicMock

from neo4j.exceptions import TransientError as Neo4jTransientError
from common.database import is_transient_lock_error, retry_on_transient_lock
from common.exceptions import BusinessLogicException


class TestRetryOnTransientLock(unittest.TestCase):
    def test_is_transient_lock_error(self):
        err = Neo4jTransientError("Database is busy", "Neo.TransientError.Transaction.LockClientStopped")
        self.assertTrue(is_transient_lock_error(err))

        class CustomTransientError(Exception):
            pass

        self.assertTrue(is_transient_lock_error(CustomTransientError("Lock error")))
        self.assertFalse(is_transient_lock_error(ValueError("Invalid value")))
        self.assertFalse(is_transient_lock_error(KeyError("missing_key")))

    def test_successful_execution_without_retry(self):
        mock_fn = MagicMock(return_value="success")
        decorated = retry_on_transient_lock()(mock_fn)

        result = decorated("arg1", kw="kw1")
        self.assertEqual(result, "success")
        self.assertEqual(mock_fn.call_count, 1)

    def test_retry_success_after_transient_error(self):
        attempts = 0

        @retry_on_transient_lock(initial_delay=0.01, backoff_factor=1.0)
        def flaky_function():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise Neo4jTransientError("Lock contention", "Neo.TransientError")
            return "recovered"

        result = flaky_function()
        self.assertEqual(result, "recovered")
        self.assertEqual(attempts, 2)

    def test_non_transient_error_not_retried(self):
        attempts = 0

        @retry_on_transient_lock(initial_delay=0.01)
        def error_function():
            nonlocal attempts
            attempts += 1
            raise ValueError("Business rule failed")

        with self.assertRaises(ValueError):
            error_function()
        self.assertEqual(attempts, 1)

    def test_retries_exhausted_raises_business_logic_exception(self):
        attempts = 0

        @retry_on_transient_lock(max_retries=3, initial_delay=0.01, backoff_factor=1.0)
        def always_failing():
            nonlocal attempts
            attempts += 1
            raise Neo4jTransientError("Lock contention", "Neo.TransientError")

        with self.assertRaises(BusinessLogicException) as ctx:
            always_failing()

        self.assertIn("concurrent database locks", str(ctx.exception))
        self.assertEqual(attempts, 4)

    def test_max_total_delay_capped_at_2_seconds(self):
        start_time = time.time()

        @retry_on_transient_lock(max_retries=100, initial_delay=0.5, backoff_factor=2.0, max_delay=1.0, max_total_delay=0.2)
        def always_failing():
            raise Neo4jTransientError("Lock contention", "Neo.TransientError")

        with self.assertRaises(BusinessLogicException):
            always_failing()

        elapsed = time.time() - start_time
        self.assertLess(elapsed, 1.0)  # Total delay must be bounded below 1s (max 0.2s backoff limit)


if __name__ == "__main__":
    unittest.main()
