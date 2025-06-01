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
3. **Google Cloud Project**: Create a project in [Google Cloud Console](https://console.cloud.google.com/)
4. **Enable Google Calendar API**: Enable the Calendar API for your project
5. **OAuth 2.0 Credentials**: Create OAuth 2.0 client credentials
   - Application type: "Desktop application"
   - Add `http://localhost:8080` to authorized redirect URIs

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

Or for development:
```bash
uv run --reload google-calendar-mcp
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
   uv run google-calendar-mcp
   ```
3. Run tests (if you add them):
   ```bash
   uv run pytest
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

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and linting: `uv run black . && uv run ruff check .`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

## License

MIT License - feel free to modify and distribute as needed.

## Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Claude Desktop Configuration](https://claude.ai/docs)