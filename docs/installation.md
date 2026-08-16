# Manual installation

Use this guide when you want to configure the DreamMS MCP without the setup
wizard. The wizard is the recommended path for local setup; see the
[Getting Started section](../README.md#getting-started) in the README.

## Prerequisites

- Python 3.11 or newer.
- [`uv`](https://docs.astral.sh/uv/).
- A Dream MS API key.
- Your Discord user ID if you plan to use app-authenticated account/content APIs.
- An MCP client that supports local stdio servers.

## Install the project

Clone the repository and create its locked environment:

```bash
git clone https://github.com/roych98/dreamms-mcp.git
cd dreamms-mcp
uv sync
```

## Configure the API key

The MCP server reads `DREAM_API_KEY` from the environment of the process that
launches it. Do not put the real key in command arguments, JSON committed to a
repository, or shell history.

```bash
# macOS / Linux
export DREAM_API_KEY="your-dream-ms-api-key"

# Windows PowerShell
$env:DREAM_API_KEY = "your-dream-ms-api-key"

# Windows cmd.exe
set DREAM_API_KEY=your-dream-ms-api-key
```

For a persistent Windows setup, save `DREAM_API_KEY` as a User Environment
Variable and restart the MCP client afterward.

### Optional Discord ID

Set `DREAM_DISCORD_ID` to make your Discord user ID the default for
`get_account` and `get_content`. Tool calls may still provide an explicit
`discord_id`.

```bash
# macOS / Linux
export DREAM_DISCORD_ID="your-discord-user-id"

# Windows PowerShell
$env:DREAM_DISCORD_ID = "your-discord-user-id"

# Windows cmd.exe
set DREAM_DISCORD_ID=your-discord-user-id
```

## Authorize app endpoints

The local MCP cannot grant OAuth access. Dream MS authorizes these requests by
checking your registered app, API key, Discord ID, and approved scope:

1. Open **Developer → My App** on Dream MS and register your app/bot.
2. Use the app's authorization flow to approve `characters:read` and/or
   `content:read` for the Discord account you want to query.
3. Configure the same account's Discord ID with `DREAM_DISCORD_ID`, then run
   the MCP with your Dream MS API key.
4. Restart the MCP client and call `get_account` or `get_content`.

The API returns `404 No authorized data` when the Discord account has not
authorized the registered app for the requested scope. See the [Dream MS API
docs](https://dreamms.gg/api/docs) for current app registration requirements.

## Configure an MCP client

Replace `C:/path/to/dreamms-mcp` with the absolute path to your clone. Supply
the key through the client's environment or your local secret-management
approach.

### Claude Desktop

Add the server under `mcpServers` in Claude Desktop's configuration file:

```json
{
  "mcpServers": {
    "dreamms": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/dreamms-mcp", "run", "dreamms-mcp"],
      "env": {
        "DREAM_API_KEY": "${DREAM_API_KEY}",
        "DREAM_DISCORD_ID": "${DREAM_DISCORD_ID}"
      }
    }
  }
}
```

### Cursor

Use the same stdio server definition in Cursor's MCP configuration:

```json
{
  "mcpServers": {
    "dreamms": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/dreamms-mcp", "run", "dreamms-mcp"],
      "env": {
        "DREAM_API_KEY": "${DREAM_API_KEY}",
        "DREAM_DISCORD_ID": "${DREAM_DISCORD_ID}"
      }
    }
  }
}
```

### VS Code-style MCP JSON

For clients using a `.vscode/mcp.json`-style file:

```json
{
  "servers": {
    "dreamms": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "C:/path/to/dreamms-mcp", "run", "dreamms-mcp"],
      "env": {
        "DREAM_API_KEY": "${DREAM_API_KEY}",
        "DREAM_DISCORD_ID": "${DREAM_DISCORD_ID}"
      }
    }
  }
}
```

### Codex

Codex uses TOML for local stdio MCP servers. Add this block to
`~/.codex/config.toml` for user scope, or `.codex/config.toml` in the project
for project scope:

```toml
[mcp_servers.dreamms]
command = "uv"
args = ["--directory", "C:/path/to/dreamms-mcp", "run", "dreamms-mcp"]
env_vars = ["DREAM_API_KEY", "DREAM_DISCORD_ID"]
enabled = true
```

Alternatively, let Codex create the basic entry, then add
`env_vars = ["DREAM_API_KEY", "DREAM_DISCORD_ID"]`:

```bash
codex mcp add dreamms -- uv --directory /path/to/dreamms-mcp run dreamms-mcp
codex mcp list
codex mcp get dreamms
```

Restart or reload the client after saving its configuration. In the Codex TUI,
use `/mcp` to view active servers. See the [official OpenAI MCP guide](https://developers.openai.com/codex/mcp/)
for current Codex options.

## Verify the API independently

```bash
# macOS / Linux
curl https://dreamms.gg/api/v1/usage \
  -H "X-API-Key: $DREAM_API_KEY"

# Windows PowerShell
curl.exe https://dreamms.gg/api/v1/usage `
  -H "X-API-Key: $env:DREAM_API_KEY"
```

## Troubleshooting

If the client says the server exited, confirm that `uv sync` completed, the
configured directory is correct, and `DREAM_API_KEY` is present in the client
process environment. If using app-authenticated tools without an explicit ID,
also confirm `DREAM_DISCORD_ID` is present. The API requires a valid key and
returns `401` when it is missing or invalid. Restart the client after changing
environment variables.
