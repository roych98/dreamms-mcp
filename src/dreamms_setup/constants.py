"""Shared setup wizard labels and configuration constants."""

API_KEY_ENV = "DREAM_API_KEY"
SUPPORTED_CLIENTS = ("codex", "claude", "opencode", "pi")
SUPPORTED_SCOPES = ("user", "project")

CLIENT_LABELS = {
    "codex": "Codex",
    "claude": "Claude Code",
    "opencode": "OpenCode",
    "pi": "Pi",
}

SCOPE_LABELS = {
    "user": "User (all projects)",
    "project": "Project (this repository)",
}

CLIENT_NOTES = {
    "codex": "Codex reads the environment variable through env_vars.",
    "claude": "Claude Code reads the environment variable through ${DREAM_API_KEY}.",
    "opencode": "OpenCode reads the environment variable through {env:DREAM_API_KEY}.",
    "pi": "Pi MCP support requires pi-mcp-adapter or another compatible MCP extension.",
}
