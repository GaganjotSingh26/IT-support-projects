# 🎫 Helpdesk Ticket Management System

A command-line IT helpdesk system inspired by Jira Service Desk.
Create, assign, update and resolve support tickets with KPI reporting.

## Features
- Create tickets with priority, category and description
- Full status lifecycle: Open → In Progress → Pending → Resolved → Closed
- Assign tickets to team members
- Add comments with full audit trail
- KPI report: total tickets, avg resolution time, breakdown by status and priority
- Demo data loader to showcase the system instantly

## Run
python helpdesk.py
(No external dependencies — standard library only)

## Tech
Python 3.8+ · json · uuid · datetime

## Background
Mirrors the real Jira Service Desk setup I built and operated at Sigea Solutions,
where I managed 20-40 IT support tickets per month in a live logistics environment.
