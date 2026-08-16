"""Shared setup wizard labels and configuration constants."""

API_KEY_ENV = "DREAM_API_KEY"
DISCORD_ID_ENV = "DREAM_DISCORD_ID"
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
    "codex": "Codex reads both values through env_vars.",
    "claude": "Claude Code reads both values through ${DREAM_API_KEY} and ${DREAM_DISCORD_ID}.",
    "opencode": "OpenCode reads both values through {env:DREAM_API_KEY} and {env:DREAM_DISCORD_ID}.",
    "pi": "Pi MCP support requires pi-mcp-adapter or another compatible MCP extension.",
}
