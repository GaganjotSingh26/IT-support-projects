"""
Helpdesk Ticket Management System
Author: Gaganjot Singh | Gothenburg, Sweden
"""
import json, os, datetime, uuid

DATA_FILE = "data/tickets.json"
VALID_PRIORITIES = ["Low", "Medium", "High", "Critical"]
VALID_STATUSES   = ["Open", "In Progress", "Pending", "Resolved", "Closed"]
VALID_CATEGORIES = ["Hardware", "Software", "Network", "Access", "Other"]

def load_tickets():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save_tickets(tickets):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

def create_ticket(title, description, priority, category, reporter):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of: {VALID_PRIORITIES}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Category must be one of: {VALID_CATEGORIES}")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": "TKT-" + str(uuid.uuid4())[:8].upper(),
        "title": title, "description": description,
        "priority": priority, "category": category,
        "status": "Open", "reporter": reporter, "assignee": None,
        "created_at": now, "updated_at": now,
        "resolved_at": None, "comments": [],
    }

def update_ticket(tickets, ticket_id, **kwargs):
    for t in tickets:
        if t["id"] == ticket_id:
            for k, v in kwargs.items():
                if k == "status" and v not in VALID_STATUSES:
                    raise ValueError(f"Status must be one of: {VALID_STATUSES}")
                t[k] = v
            t["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if kwargs.get("status") in ("Resolved", "Closed"):
                t["resolved_at"] = t["updated_at"]
            return t
    raise ValueError(f"Ticket {ticket_id} not found.")

def add_comment(tickets, ticket_id, author, message):
    for t in tickets:
        if t["id"] == ticket_id:
            t["comments"].append({
                "author": author, "message": message,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return
    raise ValueError(f"Ticket {ticket_id} not found.")

def print_ticket(t):
    print("\n" + "─"*60)
    print(f"  {t['id']}  —  {t['title']}")
    print("─"*60)
    print(f"  Status   : {t['status']}")
    print(f"  Priority : {t['priority']}")
    print(f"  Category : {t['category']}")
    print(f"  Reporter : {t['reporter']}")
    print(f"  Assignee : {t['assignee'] or 'Unassigned'}")
    print(f"  Created  : {t['created_at']}")
    print(f"  Description: {t['description']}")
    if t["comments"]:
        print("  Comments:")
        for c in t["comments"]:
            print(f"    [{c['timestamp']}] {c['author']}: {c['message']}")
    print("─"*60)

def print_list(tickets, filter_status=None):
    filtered = [t for t in tickets if not filter_status or t["status"] == filter_status]
    if not filtered:
        print("  No tickets found.")
        return
    print(f"\n  {'ID':<14} {'Priority':<10} {'Status':<14} {'Title'}")
    print("  " + "─"*70)
    for t in filtered:
        print(f"  {t['id']:<14} {t['priority']:<10} {t['status']:<14} {t['title'][:35]}")

def print_kpi(tickets):
    if not tickets:
        print("  No tickets.")
        return
    by_status, by_priority, times = {}, {}, []
    for t in tickets:
        by_status[t["status"]]     = by_status.get(t["status"], 0) + 1
        by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
        if t["resolved_at"]:
            c = datetime.datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S")
            r = datetime.datetime.strptime(t["resolved_at"], "%Y-%m-%d %H:%M:%S")
            times.append((r - c).total_seconds() / 3600)
    avg = round(sum(times)/len(times), 1) if times else "N/A"
    print("\n" + "="*50)
    print("  HELPDESK KPI REPORT")
    print("="*50)
    print(f"  Total Tickets      : {len(tickets)}")
    print(f"  Avg Resolution Time: {avg} hours")
    print("\n  By Status:")
    for s, n in by_status.items(): print(f"    {s:<16} {n}")
    print("\n  By Priority:")
    for p, n in by_priority.items(): print(f"    {p:<10} {n}")
    print("="*50)

def load_demo(tickets):
    demos = [
        ("Laptop not booting",    "Dell laptop black screen",           "Critical", "Hardware", "Anna Lindqvist"),
        ("VPN access issue",       "Cannot connect to company VPN",      "High",     "Network",  "Erik Johansson"),
        ("Password reset request", "User locked out of AD account",      "Medium",   "Access",   "Maria Svensson"),
        ("Outlook not syncing",    "Emails not updating since morning",  "Medium",   "Software", "Lars Bergstrom"),
        ("Printer offline",        "Office printer shows offline",       "Low",      "Hardware", "Sofia Nilsson"),
    ]
    for args in demos:
        tickets.append(create_ticket(*args))
    update_ticket(tickets, tickets[0]["id"], status="In Progress", assignee="Gaganjot Singh")
    update_ticket(tickets, tickets[2]["id"], status="Resolved",    assignee="Gaganjot Singh")
    add_comment(tickets, tickets[0]["id"], "Gaganjot Singh", "Replacing RAM module.")
    add_comment(tickets, tickets[2]["id"], "Gaganjot Singh", "Password reset done. Access confirmed.")
    save_tickets(tickets)
    print(f"  {len(demos)} demo tickets loaded.")
    return tickets

def main():
    tickets = load_tickets()
    while True:
        print("\n" + "="*45)
        print("  HELPDESK TICKET SYSTEM  —  Gaganjot Singh")
        print("="*45)
        print("  1. Create ticket   2. View all   3. View by ID")
        print("  4. Update status   5. Assign     6. Add comment")
        print("  7. KPI Report      8. Demo data  0. Exit")
        choice = input("\n  Choose: ").strip()

        if choice == "1":
            try:
                t = create_ticket(
                    input("  Title       : "),
                    input("  Description : "),
                    input(f"  Priority {VALID_PRIORITIES}: ").capitalize(),
                    input(f"  Category {VALID_CATEGORIES}: ").capitalize(),
                    input("  Your name   : ")
                )
                tickets.append(t)
                save_tickets(tickets)
                print(f"  Ticket created: {t['id']}")
            except ValueError as e: print(f"  Error: {e}")
        elif choice == "2":
            f = input("  Status filter (blank=all): ").strip().title() or None
            print_list(tickets, f)
        elif choice == "3":
            tid = input("  Ticket ID: ").strip().upper()
            match = next((t for t in tickets if t["id"] == tid), None)
            if match: print_ticket(match)
            else: print("  Not found.")
        elif choice == "4":
            try:
                update_ticket(tickets, input("  Ticket ID: ").strip().upper(),
                              status=input(f"  New status {VALID_STATUSES}: ").strip().title())
                save_tickets(tickets)
                print("  Updated.")
            except ValueError as e: print(f"  {e}")
        elif choice == "5":
            try:
                update_ticket(tickets, input("  Ticket ID: ").strip().upper(),
                              assignee=input("  Assign to: ").strip(), status="In Progress")
                save_tickets(tickets)
                print("  Assigned.")
            except ValueError as e: print(f"  {e}")
        elif choice == "6":
            try:
                add_comment(tickets, input("  Ticket ID: ").strip().upper(),
                            input("  Your name: ").strip(), input("  Comment: ").strip())
                save_tickets(tickets)
                print("  Comment added.")
            except ValueError as e: print(f"  {e}")
        elif choice == "7": print_kpi(tickets)
        elif choice == "8": tickets = load_demo(tickets)
        elif choice == "0": print("  Goodbye!"); break
        else: print("  Invalid option.")

if __name__ == "__main__":
    main()
