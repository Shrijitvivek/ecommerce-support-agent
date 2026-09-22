"""
 End-to-End Tests
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
# Agent Integration Tests (real run() loop with mocked OpenAI boundary)
# ---------------------------------------------------------------------------

class TestAgentIntegration(unittest.TestCase):

    @patch("agent.client")
    def test_run_executes_tool_call_then_returns_final_response(self, mock_client):
        from agent import run

        tool_call = MagicMock()
        tool_call.type = "function_call"
        tool_call.name = "lookup_order"
        tool_call.call_id = "call_123"
        tool_call.arguments = '{"order_id": "ORD1001"}'

        first_response = MagicMock()
        first_response.output = [tool_call]

        final_response = MagicMock()
        final_response.output = []
        final_response.output_text = "Your order ORD1001 was delivered on  2026-08-30."

        mock_client.responses.create.side_effect = [first_response, final_response]

        response = run("user_001", [], "What is the status of ORD1001?")

        self.assertEqual(response, "Your order ORD1001 was delivered on  2026-08-30.")
        self.assertEqual(mock_client.responses.create.call_count, 2)

    @patch("agent.save_preference")
    @patch("agent.client")
    def test_run_saves_preference_for_replacement_request(self, mock_client, mock_save_preference):
        from agent import run

        final_response = MagicMock()
        final_response.output = []
        final_response.output_text = "I can help with a replacement."
        mock_client.responses.create.return_value = final_response

        run("user_007", [], "I prefer a replacement for my order")

        mock_save_preference.assert_called_once_with("user_007", "replacement")

    @patch("agent.client")
    def test_run_uses_conversation_history_when_building_messages(self, mock_client):
        from agent import run

        final_response = MagicMock()
        final_response.output = []
        final_response.output_text = "Yes, that's for ORD1002."
        mock_client.responses.create.return_value = final_response

        history = [
            {"role": "user", "content": "I have an issue with my order."},
            {"role": "assistant", "content": "Sure, what is your order ID?"},
        ]

        run("user_002", history, "It's ORD1002")

        payload = mock_client.responses.create.call_args.kwargs
        self.assertIn("input", payload)
        passed_input = payload["input"]
        contents = [m["content"] if isinstance(m, dict) else None for m in passed_input]
        self.assertIn("I have an issue with my order.", contents)


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
