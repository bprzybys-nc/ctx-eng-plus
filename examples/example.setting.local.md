This is how you set settings.local.md file always:

```json
{
  "permissions": {
    "allow": [
      "Bash(*)",
      "Read(**)",
      "Write(**)",
      "Edit(**)",
      "mcp__*",
      "WebSearch(*)"
    ],
    "deny": [],
    "ask": []
  }
}```