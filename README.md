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

### Handling exceptions

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
