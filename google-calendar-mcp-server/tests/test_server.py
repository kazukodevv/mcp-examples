#!/usr/bin/env python3
"""
Unit tests for Google Calendar MCP Server
Place: tests/test_server.py
"""

import asyncio
import os
import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from google_calendar_mcp.server import GoogleCalendarServer


class TestGoogleCalendarServer:
    """Test the GoogleCalendarServer class."""
    
    def test_server_initialization(self):
        """Test server can be initialized."""
        server = GoogleCalendarServer()
        assert server.app is not None
        assert server.credentials is None
        assert server.service is None
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that server can list available tools."""
        server = GoogleCalendarServer()
        
        # Find the list_tools handler
        list_tools_handler = None
        for handler_name, handler in server.app._request_handlers.items():
            if "list_tools" in str(handler_name):
                list_tools_handler = handler
                break
        
        assert list_tools_handler is not None, "list_tools handler not found"
        
        tools = await list_tools_handler()
        assert len(tools) == 6
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'list_events', 'create_event', 'update_event', 
            'delete_event', 'get_event', 'list_calendars'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not found"
    
    @pytest.mark.asyncio
    async def test_call_tool_without_auth(self):
        """Test tool calls fail gracefully without authentication."""
        server = GoogleCalendarServer()
        
        # Find the call_tool handler
        call_tool_handler = None
        for handler_name, handler in server.app._request_handlers.items():
            if "call_tool" in str(handler_name):
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None, "call_tool handler not found"
        
        # Test without authentication (should fail gracefully)
        result = await call_tool_handler("list_events", {})
        assert len(result) == 1
        assert "Error executing" in result[0].text
    
    def test_authentication_missing_credentials(self):
        """Test authentication fails with missing credentials."""
        server = GoogleCalendarServer()
        
        # Clear environment variables for this test
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing Google OAuth credentials"):
                asyncio.run(server.authenticate())
    
    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret'
    })
    def test_authentication_missing_refresh_token(self):
        """Test authentication fails with missing refresh token."""
        server = GoogleCalendarServer()
        
        with pytest.raises(ValueError, match="No refresh token found"):
            asyncio.run(server.authenticate())
    
    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test_client_id',
        'GOOGLE_CLIENT_SECRET': 'test_client_secret',
        'GOOGLE_REFRESH_TOKEN': 'test_refresh_token'
    })
    @patch('google_calendar_mcp.server.Credentials')
    def test_authentication_success(self, mock_credentials):
        """Test successful authentication."""
        server = GoogleCalendarServer()
        mock_creds = Mock()
        mock_credentials.return_value = mock_creds
        
        asyncio.run(server.authenticate())
        
        assert server.credentials == mock_creds
        mock_credentials.assert_called_once()


class TestToolParameters:
    """Test tool parameter validation."""
    
    def test_list_events_schema(self):
        """Test list_events has correct schema."""
        server = GoogleCalendarServer()
        
        # Get tools
        async def get_tools():
            for handler_name, handler in server.app._request_handlers.items():
                if "list_tools" in str(handler_name):
                    return await handler()
            return []
        
        tools = asyncio.run(get_tools())
        list_events_tool = next((t for t in tools if t.name == "list_events"), None)