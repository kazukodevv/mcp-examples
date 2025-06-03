# Google Calendar MCP Server (Python + uv)

A Model Context Protocol (MCP) server that provides access to Google Calendar functionality using Python and uv. This server allows AI assistants to interact with Google Calendar to create, read, update, and delete calendar events.

## Features

- 📅 List calendar events with flexible filtering
- ➕ Create new calendar events
- ✏️ Update existing events
- 🗑️ Delete events
- 📋 List available calendars
- 🔍 Search events by text
- 👥 Manage event attendees
- 📍 Set event locations
- 🕐 Handle timezones properly

## Prerequisites

1. **Python 3.9+**: Make sure you have Python 3.9 or higher installed
2. **uv**: Install uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **Google Cloud Project & API Setup**: Follow the detailed setup below

### Google Cloud Project Setup

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "my-calendar-app")
4. Click "Create"

#### Step 2: Enable Google Calendar API
1. In your Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on "Google Calendar API" from the results
4. Click the "Enable" button
5. Wait for the API to be enabled (you'll see a green checkmark)

#### Step 3: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in the required fields:
     - App name: Your app name (e.g., "My Calendar MCP Server")
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue" through the remaining steps
4. For OAuth client ID creation:
   - Application type: Select "Desktop application"
   - Name: Give it a name (e.g., "Calendar MCP Client")
   - Click "Create"
5. **Important**: Add authorized redirect URI:
   - Click on your newly created OAuth client to edit it
   - Under "Authorized redirect URIs", click "ADD URI"
   - Enter exactly: `http://localhost:8080`
   - Click "Save"
6. Download your credentials:
   - Click the download button (⬇️) next to your OAuth client
   - Save the JSON file (you'll need the client ID and secret from this file)

#### Quick Setup Summary

**TL;DR**: 
1. Create a Google Cloud project → Enable "Google Calendar API" → Create "Desktop application" OAuth credentials → Add redirect URI `http://localhost:8080` → Download credentials JSON
2. From the downloaded JSON, extract your `client_id` and `client_secret`
3. Create a `.env` file with these values and run the auth setup

**Need more help?** The detailed steps above guide you through each screen in the Google Cloud Console.

## Installation

1. Clone or download the project files
2. Install the package with uv:
   ```bash
   uv sync
   ```

## Project Structure

```
google-calendar-mcp-server/
├── src/
│   └── google_calendar_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       └── auth.py           # Authentication helper
├── pyproject.toml            # uv project configuration
├── .env                      # Environment variables (create this)
└── README.md                # This file
```

## Authentication Setup

1. **Set up environment variables** by creating a `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

2. **Run the authentication script**:
   ```bash
   export OAUTHLIB_INSECURE_TRANSPORT=1

   uv run google-calendar-auth
   ```

3. **Follow the prompts** to complete OAuth authentication

4. **Add the refresh token** to your `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   GOOGLE_REFRESH_TOKEN=your-refresh-token-here
   ```

## Usage

### Running the Server

Start the MCP server:
```bash
uv run google-calendar-mcp
```

### Available Tools

The server provides the following tools:

#### `list_events`
List upcoming calendar events with optional filtering.

**Parameters:**
- `calendar_id` (optional): Calendar ID (default: "primary")
- `max_results` (optional): Maximum number of events (default: 10)
- `time_min` (optional): Start time filter (RFC3339 timestamp)
- `time_max` (optional): End time filter (RFC3339 timestamp)
- `query` (optional): Free text search

#### `create_event`
Create a new calendar event.

**Parameters:**
- `calendar_id` (optional): Calendar ID (default: "primary")
- `summary` (required): Event title
- `description` (optional): Event description
- `start_datetime` (required): Start time (ISO 8601)
- `end_datetime` (required): End time (ISO 8601)
- `timezone` (optional): Timezone (default: "UTC")
- `attendees` (optional): Array of attendee objects with email and displayName
- `location` (optional): Event location

#### `update_event`
Update an existing calendar event.

**Parameters:**
- `calendar_id` (optional): Calendar ID (default: "primary")
- `event_id` (required): Event ID to update
- Other parameters same as `create_event` (all optional for updates)

#### `delete_event`
Delete a calendar event.

**Parameters:**
- `calendar_id` (optional): Calendar ID (default: "primary")
- `event_id` (required): Event ID to delete

#### `get_event`
Get details of a specific event.

**Parameters:**
- `calendar_id` (optional): Calendar ID (default: "primary")
- `event_id` (required): Event ID to retrieve

#### `list_calendars`
List all available calendars.

**Parameters:** None

## Configuration with Claude Desktop

To use this server with Claude Desktop, add it to your `claude_desktop_config.json`:

```sh
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "uv",
      "args": ["run", "google-calendar-mcp"],
      "cwd": "/path/to/your/google-calendar-mcp-server",
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_REFRESH_TOKEN": "your-refresh-token"
      }
    }
  }
}
```

Alternatively, if you have a `.env` file, you can just use:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "uv",
      "args": ["run", "google-calendar-mcp"],
      "cwd": "/path/to/your/google-calendar-mcp-server"
    }
  }
}
```

## Development with uv

### Setting up for Development

1. Clone the repository
2. Install with development dependencies:
   ```bash
   uv sync --dev
   ```

3. Run formatting and linting:
   ```bash
   uv run black .
   uv run ruff check .
   uv run mypy src/
   ```

### Making Changes

1. Edit the source files in `src/google_calendar_mcp/`
2. Test your changes:
   ```bash
   # Run unit tests
   uv run pytest
   
   # Test server manually
   uv run python scripts/mcp_client_test.py
   
   # Basic server test
   uv run google-calendar-mcp
   ```
3. Run code quality checks:
   ```bash
   uv run black .
   uv run ruff check .
   uv run mypy src/
   ```

### uv Commands

- **Install dependencies**: `uv sync`
- **Add new dependency**: `uv add package-name`
- **Add dev dependency**: `uv add --dev package-name`
- **Run server**: `uv run google-calendar-mcp`
- **Run auth**: `uv run google-calendar-auth`
- **Run with environment**: `uv run --env KEY=value google-calendar-mcp`
- **Build package**: `uv build`

## Environment Variables

Create a `.env` file in your project root:

```env
# Required
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token

# Optional
GOOGLE_ACCESS_TOKEN=your-access-token  # Auto-refreshed
```

You can also set these via command line with uv:
```bash
uv run --env GOOGLE_CLIENT_ID=your_id --env GOOGLE_CLIENT_SECRET=your_secret google-calendar-mcp
```

## Example Usage with AI Assistant

Once configured, you can ask your AI assistant to:

- "Show me my calendar events for tomorrow"
- "Create a meeting with John at 2 PM next Tuesday titled 'Project Review'"
- "Cancel my 3 PM meeting today"
- "Update my morning standup to include Sarah as an attendee"
- "What calendars do I have access to?"
- "Find all meetings with 'standup' in the title this week"

## Security Notes

- Keep your client secret and refresh token secure
- The refresh token provides ongoing access to your calendar
- Use environment variables or `.env` files for credentials
- Add `.env` to your `.gitignore` file
- Regularly review OAuth app permissions in your Google account

## Troubleshooting

### Authentication Issues
- Ensure your OAuth client is configured correctly
- Check that redirect URI is exactly `http://localhost:8080`
- Verify client ID and secret are correct
- Make sure Google Calendar API is enabled in your Google Cloud project
- Try regenerating your OAuth credentials if issues persist

### uv Issues
- Make sure uv is installed: `uv --version`
- Update uv: `uv self update`
- Clear cache: `uv cache clean`
- Reinstall dependencies: `rm -rf .venv && uv sync`

### Import Errors
- Ensure you're using the right Python version: `uv run python --version`
- Check if all dependencies are installed: `uv sync`
- Verify the package structure matches the imports

### API Errors
- Check Google Calendar API quotas and limits
- Verify calendar permissions
- Ensure event IDs are valid when updating/deleting
- Check network connectivity

### Claude Desktop Integration
- Verify the path in `claude_desktop_config.json` is correct
- Check that environment variables are properly set
- Look at Claude Desktop logs for error messages
- Test the server manually first: `uv run google-calendar-mcp`

## Testing

The project includes several ways to test the MCP server:

### 1. Unit Tests

Run the full test suite with pytest:

```bash
# Install development dependencies first
uv sync --dev

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/google_calendar_mcp

# Run specific test file
uv run pytest tests/test_server.py

# Run specific test method
uv run pytest tests/test_server.py::TestGoogleCalendarServer::test_server_initialization
```

### 2. Manual MCP Client Test

Use the included test script to simulate an MCP client:

```bash
# Run the MCP client test script
uv run python scripts/mcp_client_test.py
```

This script will:
- Test server initialization
- List available tools
- Try calling basic functions
- Verify MCP protocol compliance

### 3. Basic Server Test

Test server startup and tool listing:

```bash
# Quick server startup test
uv run python -c "
from src.google_calendar_mcp.server import GoogleCalendarServer
server = GoogleCalendarServer()
print('✅ Server initialized successfully')
"
```

### 4. Manual MCP Protocol Test

Test the server manually using JSON-RPC over stdin/stdout:

```bash
# Test tools list
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
  uv run python src/google_calendar_mcp/server.py

# Test initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | \
  uv run python src/google_calendar_mcp/server.py
```

### 5. Integration Test with Authentication

If you have set up authentication, test actual calendar operations:

```bash
# Test listing events (requires authentication)
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_events", "arguments": {"max_results": 5}}}' | \
  uv run python src/google_calendar_mcp/server.py
```

### 6. Development Testing

When developing, use these commands for continuous testing:

```bash
# Install dev dependencies
uv sync --dev

# Run linting and formatting
uv run ruff check .
uv run black .
uv run mypy src/

# Run tests in watch mode (requires pytest-watch)
uv add --dev pytest-watch
uv run ptw tests/
```

### Test Environment Variables

For testing without real Google credentials, you can use mock environment variables:

```bash
# Set test credentials
export GOOGLE_CLIENT_ID="test_client_id"
export GOOGLE_CLIENT_SECRET="test_client_secret"
export GOOGLE_REFRESH_TOKEN="test_refresh_token"

# Run tests
uv run pytest
```

## Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Claude Desktop Configuration](https://claude.ai/docs)