# Weather MCP Server Setup Guide

## Overview
This guide walks through setting up a weather MCP (Model Context Protocol) server that can be integrated with Claude Desktop.

## Prerequisites
- Python with `uv` package manager installed
- Access to Claude Desktop application
- Basic command line familiarity

## Setup Instructions

### 1. Project Environment Setup
Create and activate a virtual environment for the weather server:

```bash
# Create virtual environment
uv venv

# Activate the environment
source .venv/bin/activate
```

### 2. Run the MCP Server
Execute the weather server:

```bash
# Start the weather MCP server
uv run weather.py
```

### 3. Configure Claude Desktop Integration

#### Edit Configuration File
Open the Claude Desktop configuration file:

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Add Server Configuration
Add the weather server configuration to your `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "weather": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather",
                "run",
                "weather.py"
            ]
        }
    }
}
```

**Important:** Replace `/ABSOLUTE/PATH/TO/PARENT/FOLDER/weather` with the actual absolute path to your weather project directory.

## Configuration Notes

- The `command` field specifies using `uv` as the package manager
- The `--directory` argument points to your project folder
- The final argument `weather.py` is your MCP server script
- Ensure the path is absolute, not relative

## Troubleshooting

If the server doesn't connect:
1. Verify the absolute path in the configuration is correct
2. Ensure `weather.py` exists and is executable
3. Check that all dependencies are installed in the virtual environment
4. Restart Claude Desktop after configuration changes

## Additional Resources

- [MCP Introduction](https://modelcontextprotocol.io/introduction)
- [MCP Python Server Quickstart](https://modelcontextprotocol.io/quickstart/server#python)
- Model Context Protocol documentation for advanced configuration options