# Encrata Python Library

[![PyPI version](https://img.shields.io/pypi/v/encrata.svg)](https://pypi.org/project/encrata/)
[![Python](https://img.shields.io/pypi/pyversions/encrata.svg)](https://pypi.org/project/encrata/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

The Encrata Python library provides convenient access to the [Encrata API](https://docs.encrata.com) from applications written in Python. Look up any person by their email address — get their name, company, job title, social profiles, breach history, and more.

## API Documentation

See the [Encrata API docs](https://docs.encrata.com).

## Installation

```bash
pip install encrata
```

### Requirements

- Python 3.9+
- No external dependencies (uses `urllib` from the standard library)

## Usage

The library needs to be configured with your account's API key, available in your [Encrata Dashboard](https://encrata.com/settings/api-keys).

```python
from encrata import Encrata

client = Encrata("enc_live_...")
```

### Look up a person by email

```python
person = client.lookup("elon@tesla.com")

print(person.name)        # "Elon Musk"
print(person.company)     # "Tesla"
print(person.role)        # "CEO"
print(person.location)    # "Austin, Texas"
print(person.validity)    # "valid"
```

Each lookup costs **1 credit**. Cached results within 24 hours are served from cache.

### Select specific fields

Only return the fields you need to minimize response size:

```python
person = client.lookup("satya@microsoft.com", fields=["name", "company", "role", "socials"])

print(person.name)             # "Satya Nadella"
print(person.socials.linkedin) # "https://linkedin.com/in/satyanadella"
```

Available fields: `name`, `email`, `company`, `role`, `industry`, `location`, `bio`, `age`, `gender`, `education`, `phone`, `photo`, `validity`, `socials`, `breaches`, `registered_services`, `news`, `publications`.

### Validate an email address (free)

Check if an email is deliverable without using any credits:

```python
result = client.validate("test@example.com")

print(result.validity)  # "valid", "invalid", "disposable", or "unknown"
print(result.message)   # "Email is deliverable and valid."
```

### Check data breaches (free)

See if an email has been exposed in known data breaches:

```python
report = client.breaches("user@example.com")

print(report.count)         # 3
print(report.services)      # ["Adobe", "LinkedIn", "Dropbox"]
print(report.exposed_data)  # ["email", "password", "username"]
```

## Monitoring

Set up monitors to track changes in email intelligence over time. When a person changes jobs, gets a new title, or appears in a breach — you'll know.

### Create a monitor

```python
monitor = client.create_monitor(
    "Sales Leads",
    emails=["ceo@company.com", "cto@startup.io"],
    frequency="weekly",
)

print(monitor.id)           # "mon_abc123..."
print(monitor.email_count)  # 2
```

### List monitors

```python
monitors = client.list_monitors()
for m in monitors:
    print(f"{m.name}: {m.email_count} emails, {m.status}")
```

### Trigger a run

```python
result = client.trigger_run(monitor.id)
print(result["run_id"])   # "run_xyz789..."
print(result["status"])   # "running"
```

### Get run results

```python
runs, total = client.list_runs(monitor.id)
for run in runs:
    print(f"Run {run.id}: {run.changes_detected} changes")

# Get detailed results for a run
snapshots, total = client.get_run_results(monitor.id, runs[0].id, changes_only=True)
for snap in snapshots:
    print(f"{snap.email}: changes={snap.changes}")
```

### List all runs across monitors

```python
all_runs, total = client.list_all_runs(limit=10)
all_results, total = client.list_all_results(changes_only=True)
```

## Contact Lists

Manage reusable email lists that can be used as data sources for monitors.

### Create a contact list

```python
contact_list = client.create_contact_list(
    "Engineering Team",
    emails=["alice@company.com", "bob@company.com"],
)
print(contact_list.id)
```

### Manage list emails

```python
# List all contact lists
lists = client.list_contact_lists()

# Add emails
client.add_contact_list_emails(contact_list.id, ["charlie@company.com"])

# List emails in a list
emails = client.list_contact_list_emails(contact_list.id)

# Remove emails
client.delete_contact_list_emails(contact_list.id, ["bob@company.com"])

# Delete the list
client.delete_contact_list(contact_list.id)
```

### Use a list as a monitor source

```python
monitor = client.create_monitor("Team Monitor", list_id=contact_list.id)
```

## Handling exceptions

```python
from encrata import Encrata, AuthenticationError, InsufficientCreditsError

client = Encrata("enc_live_...")

try:
    person = client.lookup("someone@example.com")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("No credits remaining — top up at encrata.com/settings/billing")
```

| Exception | Cause |
|-----------|-------|
| `AuthenticationError` | Invalid or missing API key |
| `InsufficientCreditsError` | Account has 0 credits remaining |
| `InvalidRequestError` | Malformed request (e.g. invalid email) |
| `RateLimitError` | Too many requests |
| `APIConnectionError` | Network connectivity issue |
| `APIError` | Unexpected server error |

### Configuration options

```python
client = Encrata(
    "enc_live_...",
    base_url="https://api.encrata.com",  # default
    timeout=30,                           # request timeout in seconds
)
```

### Force fresh lookup

Bypass the 24-hour cache to get the latest data:

```python
person = client.lookup("elon@tesla.com", nocache=True)
```

## MCP (Model Context Protocol)

Encrata also provides an MCP server for AI agent frameworks like Claude, Cursor, and Windsurf. Add this to your MCP configuration:

```json
{
  "mcpServers": {
    "encrata": {
      "url": "https://api.encrata.com/mcp",
      "headers": {
        "Authorization": "Bearer enc_live_..."
      }
    }
  }
}
```

## Support

- Documentation: [docs.encrata.com](https://docs.encrata.com)
- Dashboard: [encrata.com](https://encrata.com)
- Email: support@encrata.com

## License

MIT
