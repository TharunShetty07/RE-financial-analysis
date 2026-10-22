
import unittest

from src.client_isolation import ClientDataStore, ClientIsolationError


class TestClientIsolation(unittest.TestCase):

    def setUp(self):
        self.store = ClientDataStore()

        # Register 10 fictional clients with distinct financial data.
        for number in range(1, 11):
            client_id = f"CLIENT-{number:03d}"
            self.store.add_client(
                client_id,
                {
                    "company": f"Fictional Company {number}",
                    "revenue": number * 10000,
                    "net_income": number * 1500,
                },
            )

    def test_all_ten_clients_are_registered(self):
        self.assertEqual(self.store.client_count(), 10)

    def test_each_client_can_access_its_own_data(self):
        for number in range(1, 11):
            client_id = f"CLIENT-{number:03d}"
            data = self.store.get_client_data(client_id)

            self.assertEqual(
                data["company"], f"Fictional Company {number}"
            )
            self.assertEqual(data["revenue"], number * 10000)

    def test_client_cannot_access_another_clients_data(self):
        with self.assertRaises(ClientIsolationError):
            self.store.get_client_data(
                "CLIENT-001", target_client_id="CLIENT-002"
            )

    def test_unknown_client_is_rejected(self):
        with self.assertRaises(ClientIsolationError):
            self.store.get_client_data("CLIENT-999")

    def test_duplicate_registration_is_rejected(self):
        with self.assertRaises(ClientIsolationError):
            self.store.add_client(
                "CLIENT-001", {"company": "Replacement Company"}
            )

    def test_returned_data_cannot_mutate_stored_data(self):
        data = self.store.get_client_data("CLIENT-001")
        data["revenue"] = 999999999

        original = self.store.get_client_data("CLIENT-001")
        self.assertEqual(original["revenue"], 10000)

    def test_client_ids_are_sorted(self):
        expected = [f"CLIENT-{n:03d}" for n in range(1, 11)]
        self.assertEqual(self.store.list_client_ids(), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
