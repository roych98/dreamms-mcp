# DreamMS MCP

An MCP server for reading Dream MS player, economy, ranking, event, expedition, population, changelog, and authorized-account data from the [Dream MS Stats API](https://dreamms.gg/api/docs).

DreamMS MCP is designed for MCP-compatible clients such as Claude Desktop, Cursor, and VS Code-style agent clients. It is read-only: an assistant can query published statistics through MCP, but this project does not modify game accounts, submit trades, or perform game actions.

> **Project status:** This project is a local, read-only MCP server. It calls Dream MS directly with the API key supplied to the local process and does not proxy credentials through a hosted service.

## Contents

- [How it works](#how-it-works)
- [Security model: bring your own key](#security-model-bring-your-own-key)
- [Installation and setup](#installation-and-setup)
- [MCP client configuration](#mcp-client-configuration)
- [Available tools](#available-tools)
- [Local development and testing](#local-development-and-testing)
- [Troubleshooting and rate limits](#troubleshooting-and-rate-limits)
- [Contributing](#contributing)
- [License](#license)

## How it works

The MCP server translates tool calls into authenticated `GET` requests to the Dream MS Stats API v1:

```text
https://dreamms.gg/api/v1/<resource>
```

The server should pass the caller's `DREAM_API_KEY` using the recommended `X-API-Key` header, return the API's JSON response, and avoid exposing the key in tool output. The API also accepts `Authorization: Bearer <key>` and `?key=<key>`, but the query-string form is discouraged because URLs can be logged.

API reference: [dreamms.gg/api/docs](https://dreamms.gg/api/docs).

## Security model: bring your own key

DreamMS MCP uses a BYOK model. You obtain a personal API key from Dream MS Account Settings and provide it to the local MCP process through the `DREAM_API_KEY` environment variable.

- The key is not bundled with this repository and is not sent to an MCP host as a tool argument.
- Keep the key in the MCP client's environment configuration or another local secret store. Do not commit it to JSON, `.env` files, shell history, screenshots, or issue reports.
- Use one key per person. Dream MS documents that using multiple keys can revoke all access.
- The API key is sent only to `https://dreamms.gg` by the MCP server; this project does not proxy it through a third-party service.
- Rotate or revoke the key through Dream MS if it is exposed.

Dream MS currently limits key creation. If you cannot create one, follow the access instructions in the [official API documentation](https://dreamms.gg/api/docs).

## Installation and setup

### Prerequisites

- Python 3.11 or newer (use the version declared by the project's `pyproject.toml` when it is available).
- [`uv`](https://docs.astral.sh/uv/).
- A Dream MS API key.
- An MCP client that supports local stdio servers.

### Install with uv

From a clone of the repository:

```bash
git clone https://github.com/roych98/dreamms-mcp.git
cd dreamms-mcp
uv sync
```

Set the key in the environment used to launch the MCP server:

```bash
# macOS / Linux
export DREAM_API_KEY="your-dream-ms-api-key"

# Windows PowerShell
$env:DREAM_API_KEY = "your-dream-ms-api-key"

# Windows cmd.exe
set DREAM_API_KEY=your-dream-ms-api-key
```

Do not paste the real key into the client configuration's `args` array. Pass it through `env` as shown below.

## MCP client configuration

The examples use a repository-local launch through `uv` so the client uses the project's locked environment. Replace the path with the absolute path to your clone. The `DREAM_API_KEY` value must be supplied by your local secret-management approach.

### Claude Desktop

Add the server under `mcpServers` in Claude Desktop's configuration file:

```json
{
  "mcpServers": {
    "dreamms": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/dreamms-mcp",
        "run",
        "dreamms-mcp"
      ],
      "env": {
        "DREAM_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### Cursor

In Cursor's MCP configuration, use the same stdio server definition:

```json
{
  "mcpServers": {
    "dreamms": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/dreamms-mcp",
        "run",
        "dreamms-mcp"
      ],
      "env": {
        "DREAM_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### VS Code-style MCP JSON

For clients that use a `.vscode/mcp.json`-style file:

```json
{
  "servers": {
    "dreamms": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "C:/path/to/dreamms-mcp",
        "run",
        "dreamms-mcp"
      ],
      "env": {
        "DREAM_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Restart or reload the client after saving its configuration, then ask it to list the available DreamMS tools. If the client cannot start the process, first run the equivalent `uv` command from a terminal.

## Available tools

The MCP tool names mirror the API resources below. All tools are read-only and return the corresponding JSON data. Required parameters are marked **required**.

| Tool | API resource | Parameters |
| --- | --- | --- |
| `get_usage` | `GET /api/v1/usage` | None |
| `get_economy` | `GET /api/v1/economy` | `item` (**required**, exact item name); `period` (optional: `7`, `14`, `30`, `90`, `180`, or `all`; default `30`) |
| `get_player` | `GET /api/v1/player` | `name` (**required**, one or more exact names, comma-separated; maximum 18) |
| `get_rankings` | `GET /api/v1/rankings` | `type` (optional: `overall`, `job`, `dpm`, `mdpm`, `fame`; default `overall`); `job` (required when `type=job`); `page` (optional, default `1`); `limit` (optional, default `25`, maximum `50`) |
| `get_expeditions` | `GET /api/v1/expeditions` | `range` (optional: `24h`, `7d`, `30d`, `90d`, `all`; default `all`); `type` (optional: `completions`, `classes`, `fastest`, `records`) |
| `get_event` | `GET /api/v1/event` | `event` (**required**, documented event ID); `type` (optional: `jq` or `pq`; otherwise the event's default) |
| `get_population` | `GET /api/v1/population` | None |
| `get_changelog` | `GET /api/v1/changelog` | `count` (optional, default `5`, maximum `20`); `format` (optional: `html` or `text`; default `html`) |
| `get_account` | `GET /api/v1/account` | `discord_id` (**required**); requires a registered app and `characters:read` authorization scope |
| `get_content` | `GET /api/v1/content` | `discord_id` (**required**); requires a registered app and `content:read` authorization scope |

`get_account` and `get_content` are app endpoints. They do not reveal arbitrary account data: the player must have authorized the registered Dream MS app for the required scope. See the [API docs](https://dreamms.gg/api/docs) for the current event IDs and job IDs.

## Local development and testing

The development workflow uses `uv` to keep dependencies and commands reproducible:

```bash
uv sync --dev
uv run dreamms-mcp
uv run python -m dreamms_mcp
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The MCP process communicates over stdio, so do not print logs to stdout. Send diagnostics to stderr or use the project's configured logging facility. For an authenticated smoke test independent of MCP, the API documentation provides a supported request to `/api/v1/usage`:

```bash
# macOS / Linux
curl https://dreamms.gg/api/v1/usage \
  -H "X-API-Key: $DREAM_API_KEY"

# Windows PowerShell
curl.exe https://dreamms.gg/api/v1/usage `
  -H "X-API-Key: $env:DREAM_API_KEY"
```

The console-script entry point and `python -m dreamms_mcp` both launch the same stdio server.

## Troubleshooting and rate limits

### The client says the server exited

Run the configured command manually from the repository directory. Confirm that `uv sync` completed, that the module/entry point exists, and that `DREAM_API_KEY` is present in the process environment. Do not test by putting the key on a command line where it may be captured in shell history.

### Authentication fails

The API requires a key for every request. Check the variable name exactly (`DREAM_API_KEY`), that the key is active, and that the server uses `X-API-Key`. The documented HTTP status for an invalid or missing key is `401`.

### Rate limits

Dream MS documents a global limit of 30 requests per minute and 500 per hour, with some resources having stricter limits. The documented endpoint-specific limits include:

- Economy: 5/minute; cached for 3600 seconds.
- Player: 10/minute; cached for 120 seconds.
- Rankings: global limit; cached for 300 seconds.
- Expeditions: global limit; cached for 21600 seconds.
- Event: global limit; cached for 300 seconds.
- Population: global limit; cached for 60 seconds.
- Changelog: global limit; cached for 1800 seconds.
- Usage and app endpoints: documented separately in the API reference.

On `429`, respect the API's `Retry-After` response and back off. Avoid asking an assistant to repeatedly refresh a value that is already cached. Supporters receive 2x usage according to the API docs; higher usage can be requested from the Dream MS administrator.

### Other API errors

`400` means a parameter is missing or invalid, `404` means no matching record, `405` means the method is not supported, and `503` means the backend is temporarily unavailable. Check the tool parameter spelling and allowed values before retrying.

## Contributing

Contributions are welcome. Before opening a pull request:

1. Open an issue for substantial behavior or API-surface changes.
2. Keep API keys and personal data out of commits, tests, fixtures, and logs.
3. Add or update tests for tool validation, authentication handling, and API error mapping.
4. Run the `uv` checks listed above.
5. Update this README whenever a tool, parameter, launch command, or security behavior changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) when the project-specific contribution guide is added.

## License

MIT License

Copyright (c) 2026 roych98

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Summary

DreamMS MCP gives MCP clients a small, read-only interface to Dream MS statistics. Install the project with `uv`, provide your own `DREAM_API_KEY` to the local server process, configure the client for stdio, and use the documented tools for player, economy, rankings, events, expeditions, population, changelog, usage, and authorized app data.
