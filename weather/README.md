# weather

```sh
# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# run mcp server
uv run weather.py
```

```sh
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

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

## Docs

- https://modelcontextprotocol.io/introduction
- https://modelcontextprotocol.io/quickstart/server#python