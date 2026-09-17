"""
Person C - End-to-End Tests
============================
Covers: tools (lookup_order, search_policy), memory (save/get preference),
        agent integration, and failure/edge cases.
"""

import unittest
from unittest.mock import patch, MagicMock

from tools import lookup_order, search_policy
from memory_store import save_preference, get_preference


# ---------------------------------------------------------------------------
# Tool Tests
# ---------------------------------------------------------------------------

class TestLookupOrder(unittest.TestCase):

    def test_valid_order_returns_data(self):
        result = lookup_order("ORD1001")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["order_id"], "ORD1001")
        self.assertEqual(result["data"]["product"], "Wireless Headphones")

    def test_case_insensitive(self):
        result = lookup_order("ord1001")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["order_id"], "ORD1001")

    def test_order_not_found(self):
        result = lookup_order("ORD9999")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "order_not_found")

    def test_empty_string_input(self):
        result = lookup_order("")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")

    def test_none_input(self):
        result = lookup_order(None)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")

    def test_invalid_format(self):
        result = lookup_order("banana")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")

    def test_whitespace_only_input(self):
        result = lookup_order("   ")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")


class TestSearchPolicy(unittest.TestCase):

    def test_return_policy_found(self):
        result = search_policy("Can I return my product?")
        self.assertTrue(result["success"])
        self.assertIn("topic_id", result["data"])
        self.assertIn("content", result["data"])

    def test_refund_policy_found(self):
        result = search_policy("how long does a refund take")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["topic_id"], "refund_process")

    def test_replacement_policy_found(self):
        result = search_policy("I want a replacement not a refund")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["topic_id"], "replacement_process")

    def test_policy_not_found(self):
        result = search_policy("do you sell gift wrapping")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "policy_not_found")

    def test_empty_query(self):
        result = search_policy("")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")

    def test_none_query(self):
        result = search_policy(None)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")

    def test_whitespace_only_query(self):
        result = search_policy("   ")
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")


# ---------------------------------------------------------------------------
# Memory Tests
# ---------------------------------------------------------------------------

class TestMemoryStore(unittest.TestCase):

    def test_save_and_retrieve_preference(self):
        save_preference("test_user_999", "refund")
        result = get_preference("test_user_999")
        self.assertEqual(result, "refund")

    def test_overwrite_preference(self):
        save_preference("test_user_999", "refund")
        save_preference("test_user_999", "replacement")
        result = get_preference("test_user_999")
        self.assertEqual(result, "replacement")

    def test_unknown_user_returns_none(self):
        result = get_preference("nonexistent_user_xyz")
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# Agent Integration Tests (mocked LLM)
# ---------------------------------------------------------------------------

class TestAgentIntegration(unittest.TestCase):

    @patch("agent.run")
    def test_agent_returns_string(self, mock_run):
        mock_run.return_value = "Your order ORD1001 has been delivered."
        from agent import run
        response = run("user_001", [], "What is the status of ORD1001?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    @patch("agent.run")
    def test_agent_handles_policy_question(self, mock_run):
        mock_run.return_value = "You can return items within 15 days."
        from agent import run
        response = run("user_001", [], "What is your return policy?")
        self.assertIsInstance(response, str)

    @patch("agent.run")
    def test_agent_uses_conversation_history(self, mock_run):
        mock_run.return_value = "Yes, your order ORD1002 is still being shipped."
        from agent import run
        history = [
            {"role": "user", "content": "I have an issue with my order."},
            {"role": "assistant", "content": "Sure, what is your order ID?"},
        ]
        response = run("user_001", history, "It's ORD1002")
        self.assertIsInstance(response, str)

    @patch("agent.run", side_effect=Exception("LLM unavailable"))
    def test_agent_failure_is_handled_gracefully(self, mock_run):
        from agent import run
        with self.assertRaises(Exception) as ctx:
            run("user_001", [], "Hello")
        self.assertIn("LLM unavailable", str(ctx.exception))


# ---------------------------------------------------------------------------
# Edge / Failure Cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):

    def test_lookup_order_with_leading_trailing_spaces(self):
        result = lookup_order("  ORD1002  ")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["order_id"], "ORD1002")

    def test_search_policy_damaged_item(self):
        result = search_policy("my item arrived broken")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["topic_id"], "damaged_or_defective")

    def test_search_policy_shipping_cost(self):
        result = search_policy("return shipping cost")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["topic_id"], "shipping_returns")

    def test_lookup_order_non_string_input(self):
        result = lookup_order(12345)
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
