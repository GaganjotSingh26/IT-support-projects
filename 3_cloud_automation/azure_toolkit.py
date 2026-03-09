"""
Azure Infrastructure Automation Toolkit
Author: Gaganjot Singh | Gothenburg, Sweden
Simulates real Azure AD admin tasks in Python.
"""
import os, datetime, uuid, random

class MockAzureClient:
    def __init__(self):
        self._users, self._groups, self._resources, self._audit = {}, {}, {}, []
        self._seed()

    def _log(self, action, detail):
        self._audit.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action, "detail": detail
        })

    def _seed(self):
        for g in ["IT-Admins","Developers","Finance","HR","ReadOnly-Guest"]:
            self._groups[g] = {"name": g, "members": []}
        for username, name, group, email in [
            ("anna.lindqvist", "Anna Lindqvist", "IT-Admins",  "anna@company.se"),
            ("erik.johansson",  "Erik Johansson",  "Developers", "erik@company.se"),
            ("maria.svensson",  "Maria Svensson",  "Finance",    "maria@company.se"),
            ("lars.bergstrom",  "Lars Bergstrom",  "HR",         "lars@company.se"),
        ]:
            self._users[username] = {
                "id": str(uuid.uuid4())[:8], "username": username,
                "display_name": name, "email": email, "groups": [group],
                "enabled": True, "mfa_enabled": random.choice([True, True, False]),
                "created_at": "2024-01-15",
            }
            self._groups[group]["members"].append(username)
        for name, rtype, region in [
            ("vm-gothenburg-01", "VirtualMachine", "Sweden Central"),
            ("vm-gothenburg-02", "VirtualMachine", "Sweden Central"),
            ("storage-backup-01","StorageAccount",  "North Europe"),
            ("sql-db-prod",      "SQLDatabase",     "Sweden Central"),
            ("keyvault-main",    "KeyVault",        "Sweden Central"),
        ]:
            self._resources[name] = {
                "name": name, "type": rtype, "region": region,
                "status": random.choice(["Running","Running","Running","Stopped","Degraded"]),
                "cpu_percent": random.randint(10, 95),
            }

    def create_user(self, username, display_name, email, group):
        if username in self._users: raise ValueError(f"User '{username}' already exists.")
        if group not in self._groups: raise ValueError(f"Group '{group}' not found.")
        self._users[username] = {
            "id": str(uuid.uuid4())[:8], "username": username,
            "display_name": display_name, "email": email,
            "groups": [group], "enabled": True, "mfa_enabled": False,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        }
        self._groups[group]["members"].append(username)
        self._log("CREATE_USER", f"{username} added to {group}")
        return self._users[username]

    def disable_user(self, username):
        if username not in self._users: raise ValueError(f"User '{username}' not found.")
        self._users[username]["enabled"] = False
        self._log("DISABLE_USER", f"{username} disabled")

    def delete_user(self, username):
        if username not in self._users: raise ValueError(f"User '{username}' not found.")
        for g in self._users[username]["groups"]:
            if username in self._groups.get(g, {}).get("members", []):
                self._groups[g]["members"].remove(username)
        del self._users[username]
        self._log("DELETE_USER", f"{username} deleted")

    def assign_group(self, username, group):
        if username not in self._users: raise ValueError(f"User not found.")
        if group not in self._groups: raise ValueError(f"Group not found.")
        if group not in self._users[username]["groups"]:
            self._users[username]["groups"].append(group)
            self._groups[group]["members"].append(username)
            self._log("ASSIGN_GROUP", f"{username} -> {group}")

    def remove_group(self, username, group):
        if username not in self._users: raise ValueError(f"User not found.")
        if group in self._users[username]["groups"]:
            self._users[username]["groups"].remove(group)
            if username in self._groups[group]["members"]:
                self._groups[group]["members"].remove(username)
            self._log("REMOVE_GROUP", f"{username} removed from {group}")

    def list_users(self): return list(self._users.values())
    def list_groups(self): return self._groups
    def list_resources(self): return list(self._resources.values())
    def get_audit_log(self): return self._audit

    def get_health(self):
        return {
            "total":    len(self._resources),
            "running":  sum(1 for r in self._resources.values() if r["status"]=="Running"),
            "stopped":  sum(1 for r in self._resources.values() if r["status"]=="Stopped"),
            "degraded": sum(1 for r in self._resources.values() if r["status"]=="Degraded"),
        }

def compliance_check(client):
    users   = client.list_users()
    issues  = []
    no_mfa  = [u["username"] for u in users if not u["mfa_enabled"] and u["enabled"]]
    if no_mfa:
        issues.append({"severity":"HIGH",   "issue":"MFA not enabled",          "affected": no_mfa})
    degraded = [r["name"] for r in client.list_resources() if r["status"]=="Degraded"]
    if degraded:
        issues.append({"severity":"HIGH",   "issue":"Degraded resources",        "affected": degraded})
    high_cpu = [r["name"] for r in client.list_resources() if r["cpu_percent"]>85]
    if high_cpu:
        issues.append({"severity":"MEDIUM", "issue":"High CPU (>85%)",           "affected": high_cpu})
    return {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_users":  len(users),
        "active_users": sum(1 for u in users if u["enabled"]),
        "health":       client.get_health(),
        "issues":       issues,
        "status":       "FAIL" if any(i["severity"]=="HIGH" for i in issues) else "PASS",
    }

def save_report(report):
    os.makedirs("reports", exist_ok=True)
    color = "#27ae60" if report["status"]=="PASS" else "#c0392b"
    rows  = ""
    for i in report["issues"]:
        c = "#c0392b" if i["severity"]=="HIGH" else "#e67e22"
        rows += f"<tr><td style='color:{c};font-weight:bold'>{i['severity']}</td><td>{i['issue']}</td><td>{', '.join(i['affected'])}</td></tr>"
    html = f"""<!DOCTYPE html><html><head><title>Compliance Report</title>
<style>body{{font-family:Arial;margin:40px}} h1{{color:#1A3A5C}}
.badge{{background:{color};color:white;padding:6px 18px;border-radius:4px;font-weight:bold}}
table{{border-collapse:collapse;width:100%;margin-top:20px}}
th{{background:#1A3A5C;color:white;padding:10px}} td{{padding:8px;border-bottom:1px solid #ddd}}</style>
</head><body>
<h1>Azure Compliance Report</h1>
<p>Generated: {report['generated_at']} &nbsp; Status: <span class="badge">{report['status']}</span></p>
<p>Total Users: <b>{report['total_users']}</b> &nbsp;|&nbsp;
   Active: <b>{report['active_users']}</b> &nbsp;|&nbsp;
   Resources: <b>{report['health']['total']}</b> &nbsp;|&nbsp;
   Running: <b>{report['health']['running']}</b></p>
{'<p>No issues found.</p>' if not report['issues'] else f'<table><tr><th>Severity</th><th>Issue</th><th>Affected</th></tr>{rows}</table>'}
</body></html>"""
    path = "reports/compliance_report.html"
    with open(path, "w") as f: f.write(html)
    return path

def print_users(users):
    print(f"\n  {'Username':<22} {'Name':<22} {'Groups':<20} {'MFA':<6} {'Status'}")
    print("  " + "─"*85)
    for u in users:
        print(f"  {u['username']:<22} {u['display_name']:<22} {', '.join(u['groups']):<20} {'Yes' if u['mfa_enabled'] else 'No':<6} {'Active' if u['enabled'] else 'Disabled'}")

def print_resources(resources):
    icons = {"Running":"Running","Stopped":"Stopped","Degraded":"Degraded"}
    print(f"\n  {'Name':<24} {'Type':<18} {'Region':<18} {'Status':<12} {'CPU'}")
    print("  " + "─"*80)
    for r in resources:
        print(f"  {r['name']:<24} {r['type']:<18} {r['region']:<18} {r['status']:<12} {r['cpu_percent']}%")

def main():
    print("\n  Connecting to Azure... (simulation mode)")
    client = MockAzureClient()
    print("  Connected. Demo environment loaded.")
    while True:
        print("\n" + "="*50)
        print("  AZURE AUTOMATION TOOLKIT  —  Gaganjot Singh")
        print("="*50)
        print("  1. List users          2. Create user")
        print("  3. Disable/Delete user 4. Manage groups")
        print("  5. List resources      6. Compliance check")
        print("  7. Save HTML report    8. Audit log")
        print("  0. Exit")
        choice = input("\n  Choose: ").strip()

        if choice == "1":
            print_users(client.list_users())
        elif choice == "2":
            try:
                u = client.create_user(
                    input("  Username     : ").strip().lower(),
                    input("  Display Name : ").strip(),
                    input("  Email        : ").strip(),
                    input(f"  Group {list(client.list_groups().keys())}: ").strip()
                )
                print(f"  Created: {u['id']} — {u['display_name']}")
            except ValueError as e: print(f"  Error: {e}")
        elif choice == "3":
            username = input("  Username: ").strip().lower()
            action   = input("  (d)isable or (x)delete: ").strip().lower()
            try:
                if action == "d": client.disable_user(username); print("  Disabled.")
                elif action == "x": client.delete_user(username); print("  Deleted.")
            except ValueError as e: print(f"  {e}")
        elif choice == "4":
            try:
                username = input("  Username: ").strip().lower()
                group    = input(f"  Group {list(client.list_groups().keys())}: ").strip()
                action   = input("  (a)dd or (r)emove: ").strip().lower()
                if action == "a": client.assign_group(username, group); print("  Added.")
                elif action == "r": client.remove_group(username, group); print("  Removed.")
            except ValueError as e: print(f"  {e}")
        elif choice == "5":
            print_resources(client.list_resources())
            h = client.get_health()
            print(f"\n  Running: {h['running']}  Stopped: {h['stopped']}  Degraded: {h['degraded']}")
        elif choice == "6":
            r = compliance_check(client)
            print(f"\n  Status: {'PASS' if r['status']=='PASS' else 'FAIL'}")
            print(f"  Issues: {len(r['issues'])}")
            for i in r["issues"]: print(f"    [{i['severity']}] {i['issue']}: {', '.join(i['affected'])}")
        elif choice == "7":
            path = save_repor
