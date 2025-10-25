import unittest
import requests
import random
import time

BASE = "http://127.0.0.1:5000"


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Starting endpoint tests...")
        time.sleep(1)

    # --- ACCOUNTS ---
    def test_accounts(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "phone_number": f"555{random.randint(1000,9999)}",
            "email": f"test{random.randint(100,999)}@example.com",
            "balance": 1000.0
        }
        r = requests.post(f"{BASE}/accounts/", json=data)
        self.assertEqual(r.status_code, 201)

        r = requests.get(f"{BASE}/accounts/")
        self.assertEqual(r.status_code, 200)
        accounts = r.json()
        self.assertTrue(isinstance(accounts, list))
        account_id = accounts[-1]['id']

        r = requests.get(f"{BASE}/accounts/{account_id}")
        self.assertEqual(r.status_code, 200)

        r = requests.patch(f"{BASE}/accounts/{account_id}", json={"balance": 1200})
        self.assertEqual(r.status_code, 200)

        r = requests.delete(f"{BASE}/accounts/{account_id}")
        self.assertEqual(r.status_code, 200)

    # --- TRANSACTIONS ---
    def test_transactions(self):
        # Create two accounts
        a1 = requests.post(f"{BASE}/accounts/", json={
            "first_name": "Origin",
            "last_name": "A",
            "phone_number": f"55{random.randint(10000,99999)}",
            "email": f"o{random.randint(100,999)}@example.com",
            "balance": 1000
        })
        a2 = requests.post(f"{BASE}/accounts/", json={
            "first_name": "Dest",
            "last_name": "B",
            "phone_number": f"55{random.randint(10000,99999)}",
            "email": f"d{random.randint(100,999)}@example.com",
            "balance": 500
        })
        self.assertEqual(a1.status_code, 201)
        self.assertEqual(a2.status_code, 201)

        accs = requests.get(f"{BASE}/accounts/").json()
        id1, id2 = accs[-2]['id'], accs[-1]['id']

        r = requests.post(f"{BASE}/transactions/", json={
            "origin_account": id1,
            "destination_account": id2,
            "amount": 150
        })
        self.assertEqual(r.status_code, 201)

        r = requests.get(f"{BASE}/transactions/")
        self.assertEqual(r.status_code, 200)
        transactions = r.json()
        self.assertTrue(len(transactions) > 0)
        tid = transactions[0]['id']

        r = requests.patch(f"{BASE}/transactions/{tid}", json={"amount": 200})
        self.assertEqual(r.status_code, 200)

        r = requests.delete(f"{BASE}/transactions/{tid}")
        self.assertEqual(r.status_code, 200)

    # --- GOALS ---
    def test_goals(self):
        accounts = requests.get(f"{BASE}/accounts/").json()
        acc_id = accounts[0]['id']

        r = requests.post(f"{BASE}/goals/", json={
            "UserId": acc_id,
            "GoalName": "Save for laptop",
            "Description": "Purchase a new laptop",
            "TargetAmount": 1500,
            "CurrentAmount": 300,
            "Deadline": "2026-01-01"
        })
        self.assertEqual(r.status_code, 201)

        r = requests.get(f"{BASE}/goals/")
        self.assertEqual(r.status_code, 200)
        goal_id = r.json()[-1]['GoalId']

        r = requests.patch(f"{BASE}/goals/{goal_id}", json={"CurrentAmount": 500})
        self.assertEqual(r.status_code, 200)

        r = requests.delete(f"{BASE}/goals/{goal_id}")
        self.assertEqual(r.status_code, 200)

    # --- MISSIONS ---
    def test_missions(self):
        accounts = requests.get(f"{BASE}/accounts/").json()
        acc_id = accounts[0]['id']

        # Need an existing goal to link to
        r_goal = requests.post(f"{BASE}/goals/", json={
            "UserId": acc_id,
            "GoalName": "Short mission goal",
            "TargetAmount": 100,
            "Deadline": "2026-01-01"
        })
        self.assertEqual(r_goal.status_code, 201)
        goals = requests.get(f"{BASE}/goals/").json()
        goal_id = goals[-1]['GoalId']

        r = requests.post(f"{BASE}/missions/", json={
            "UserId": acc_id,
            "GoalId": goal_id,
            "Title": "Save 100 this week",
            "Description": "Test mission creation",
            "Type": "SAVE",
            "TargetAmount": 100,
            "Deadline": "2026-02-01"
        })
        self.assertEqual(r.status_code, 201)

        r = requests.get(f"{BASE}/missions/")
        self.assertEqual(r.status_code, 200)
        mid = r.json()[-1]['MissionId']

        r = requests.patch(f"{BASE}/missions/{mid}", json={"IsCompleted": 1})
        self.assertEqual(r.status_code, 200)

        r = requests.delete(f"{BASE}/missions/{mid}")
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
