# Google Calendar MCP Server Setup Guide

## Overview

## Prerequisites
- Python with `uv` package manager installed
- Access to Claude Desktop application
- Basic command line familiarity

## Setup Instructions

### 1. Project Environment Setup
Create and activate a virtual environment for the google calendar server:

```bash
# Create virtual environment
uv venv

# Activate the environment
source .venv/bin/activate
```

### 2. Run the MCP Server

```bash
uv run server.py
```
