# ☁️ Azure Infrastructure Automation Toolkit

Python CLI tool simulating real Microsoft Azure admin tasks:
user provisioning, group management, resource health and compliance reporting.

## Features
- Create, disable and delete Azure AD user accounts
- Assign and remove users from access groups
- Check resource health (VMs, storage, databases)
- Compliance check: missing MFA, degraded resources, high CPU
- HTML compliance report generated with one command
- Full audit log of every action

## Run
python azure_toolkit.py
(No external dependencies — standard library only)

## Tech
Python 3.8+ · Standard library only
Production swap: azure-identity · azure-mgmt-resource · msgraph-sdk

## Background
Built to demonstrate cloud administration skills developed while managing
Microsoft Azure and Active Directory at Sigea Solutions.
Compliance logic mirrors real IT security audits I performed in production.
