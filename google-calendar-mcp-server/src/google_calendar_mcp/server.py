# src/google_calendar_mcp/server.py
#!/usr/bin/env python3

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server


class GoogleCalendarServer:
    def __init__(self):
        self.app = Server("google-calendar-server")
        self.credentials = None
        self.service = None
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="list_events",
                    description="List upcoming calendar events",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                                "default": "primary",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of events to return (default: 10)",
                                "default": 10,
                            },
                            "time_min": {
                                "type": "string",
                                "description": "Lower bound for events (RFC3339 timestamp)",
                            },
                            "time_max": {
                                "type": "string",
                                "description": "Upper bound for events (RFC3339 timestamp)",
                            },
                            "query": {
                                "type": "string",
                                "description": "Free text search terms",
                            },
                        },
                    },
                ),
                types.Tool(
                    name="create_event",
                    description="Create a new calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                                "default": "primary",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Event title",
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description",
                            },
                            "start_datetime": {
                                "type": "string",
                                "description": "Start date/time (ISO 8601 format)",
                            },
                            "end_datetime": {
                                "type": "string",
                                "description": "End date/time (ISO 8601 format)",
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Time zone (default: UTC)",
                                "default": "UTC",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "displayName": {"type": "string"},
                                    },
                                    "required": ["email"],
                                },
                                "description": "List of attendees",
                            },
                            "location": {
                                "type": "string",
                                "description": "Event location",
                            },
                        },
                        "required": ["summary", "start_datetime", "end_datetime"],
                    },
                ),
                types.Tool(
                    name="update_event",
                    description="Update an existing calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                                "default": "primary",
                            },
                            "event_id": {
                                "type": "string",
                                "description": "Event ID to update",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Event title",
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description",
                            },
                            "start_datetime": {
                                "type": "string",
                                "description": "Start date/time (ISO 8601 format)",
                            },
                            "end_datetime": {
                                "type": "string",
                                "description": "End date/time (ISO 8601 format)",
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Time zone",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "displayName": {"type": "string"},
                                    },
                                    "required": ["email"],
                                },
                                "description": "List of attendees",
                            },
                            "location": {
                                "type": "string",
                                "description": "Event location",
                            },
                        },
                        "required": ["event_id"],
                    },
                ),
                types.Tool(
                    name="delete_event",
                    description="Delete a calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                                "default": "primary",
                            },
                            "event_id": {
                                "type": "string",
                                "description": "Event ID to delete",
                            },
                        },
                        "required": ["event_id"],
                    },
                ),
                types.Tool(
                    name="get_event",
                    description="Get details of a specific calendar event",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "calendar_id": {
                                "type": "string",
                                "description": "Calendar ID (default: primary)",
                                "default": "primary",
                            },
                            "event_id": {
                                "type": "string",
                                "description": "Event ID to retrieve",
                            },
                        },
                        "required": ["event_id"],
                    },
                ),
                types.Tool(
                    name="list_calendars",
                    description="List available calendars",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.app.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            try:
                await self.ensure_authenticated()
                
                if name == "list_events":
                    return await self.list_events(arguments)
                elif name == "create_event":
                    return await self.create_event(arguments)
                elif name == "update_event":
                    return await self.update_event(arguments)
                elif name == "delete_event":
                    return await self.delete_event(arguments)
                elif name == "get_event":
                    return await self.get_event(arguments)
                elif name == "list_calendars":
                    return await self.list_calendars(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error executing {name}: {str(e)}"
                    )
                ]

    async def ensure_authenticated(self):
        """Ensure we have valid credentials and service."""
        if not self.credentials:
            await self.authenticate()
        
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
        
        if not self.service:
            self.service = build('calendar', 'v3', credentials=self.credentials)

    async def authenticate(self):
        """Authenticate with Google Calendar API."""
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Missing Google OAuth credentials. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )
        
        if refresh_token:
            # Use refresh token to get credentials
            self.credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=[
                    'https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/calendar.events'
                ]
            )
        else:
            raise ValueError(
                "No refresh token found. Please run the authentication script first to get GOOGLE_REFRESH_TOKEN."
            )

    async def list_events(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """List calendar events."""
        calendar_id = args.get('calendar_id', 'primary')
        max_results = args.get('max_results', 10)
        time_min = args.get('time_min')
        time_max = args.get('time_max')
        query = args.get('query')
        
        # Default to current time if no time_min specified
        if not time_min:
            time_min = datetime.now(timezone.utc).isoformat()
        
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                q=query
            ).execute()
            
            events = events_result.get('items', [])
            
            result = {
                'events': events,
                'summary': f'Found {len(events)} events'
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to list events: {e}")

    async def create_event(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Create a new calendar event."""
        calendar_id = args.get('calendar_id', 'primary')
        summary = args['summary']
        description = args.get('description')
        start_datetime = args['start_datetime']
        end_datetime = args['end_datetime']
        timezone = args.get('timezone', 'UTC')
        attendees = args.get('attendees', [])
        location = args.get('location')
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': timezone,
            },
            'location': location,
        }
        
        if attendees:
            event['attendees'] = attendees
        
        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            result = {
                'event': created_event,
                'message': 'Event created successfully'
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to create event: {e}")

    async def update_event(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Update an existing calendar event."""
        calendar_id = args.get('calendar_id', 'primary')
        event_id = args['event_id']
        
        try:
            # Get existing event
            existing_event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update only provided fields
            if 'summary' in args:
                existing_event['summary'] = args['summary']
            if 'description' in args:
                existing_event['description'] = args['description']
            if 'location' in args:
                existing_event['location'] = args['location']
            if 'attendees' in args:
                existing_event['attendees'] = args['attendees']
            
            if 'start_datetime' in args:
                existing_event['start'] = {
                    'dateTime': args['start_datetime'],
                    'timeZone': args.get('timezone', existing_event['start'].get('timeZone', 'UTC')),
                }
            
            if 'end_datetime' in args:
                existing_event['end'] = {
                    'dateTime': args['end_datetime'],
                    'timeZone': args.get('timezone', existing_event['end'].get('timeZone', 'UTC')),
                }
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            result = {
                'event': updated_event,
                'message': 'Event updated successfully'
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to update event: {e}")

    async def delete_event(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Delete a calendar event."""
        calendar_id = args.get('calendar_id', 'primary')
        event_id = args['event_id']
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            result = {
                'message': f'Event {event_id} deleted successfully'
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to delete event: {e}")

    async def get_event(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get details of a specific calendar event."""
        calendar_id = args.get('calendar_id', 'primary')
        event_id = args['event_id']
        
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            result = {
                'event': event
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to get event: {e}")

    async def list_calendars(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """List available calendars."""
        try:
            calendars_result = self.service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            result = {
                'calendars': calendars,
                'summary': f'Found {len(calendars)} calendars'
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )
            ]
            
        except HttpError as e:
            raise Exception(f"Failed to list calendars: {e}")


async def main():
    """Main entry point for the server."""
    server = GoogleCalendarServer()
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.app.run(
            read_stream,
            write_stream,
            NotificationOptions(),
        )

def cli_main():
    asyncio.run(main())