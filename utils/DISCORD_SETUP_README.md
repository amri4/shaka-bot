# Discord Setup Module

> A decorator-based system that simplifies Discord bot development. Write command handlers, event listeners, and UI components in a clean, modular way.

## Table of Contents

- Overview
- Core Concepts
  - Decorators
  - Markers
- Usage Guide
  - Commands
  - Event Listeners
  - Buttons
  - Select Menus
- UI Components
  - Creating Views with `ui()`
- Automatic Cog Creation
  - `setup_module()`
  - Example Module
- Real-World Example: Report Command
- Internal Architecture
  - `_build_cog(bot, module)`
  - `_make_button(func)` and `_make_select(func)`
- Benefits
- See Also

---

## Overview

This module is built around Python decorators that mark functions as Discord commands, listeners, buttons, and selects. These decorators attach metadata to functions, which is then read by the module'[...] 

## Core Concepts

### Decorators

The module provides four main decorators for marking functions:

1. **`@command`** - Marks a function as a Discord command
2. **`@listener`** - Marks a function as an event listener
3. **`@button`** - Marks a function as a button click handler
4. **`@select`** - Marks a function as a select menu handler

### Markers

Internally, decorators work by attaching special marker attributes to functions:

- `__discord_setup_command__` - Contains command metadata
- `__discord_setup_listener__` - Contains listener name
- `__discord_setup_button__` - Contains button configuration
- `__discord_setup_select__` - Contains select menu configuration

## Usage Guide

### Commands

Use the `@command` decorator to create a Discord command:

```python
from utils.discord_setup import command

@command(
    name="greet",
    description="Greet a user",
    usage="<name>"
)
async def greet(ctx, *, name: str):
    await ctx.send(f"Hello, {name}!")
```

**Decorator Parameters:**
- Any parameters supported by `discord.ext.commands.command()` (e.g., `name`, `description`, `usage`, etc.)

### Event Listeners

Use the `@listener` decorator to create event handlers:

```python
from utils.discord_setup import listener

@listener(name="on_message")
async def handle_message(message):
    if message.author == message.guild.me:
        return
    print(f"Message from {message.author}: {message.content}")
```

**Decorator Parameters:**
- `name` (optional) - The event name to listen for. If `None`, uses the function name.

### Buttons

Use the `@button` decorator to create interactive buttons:

```python
from utils.discord_setup import button

@button(
    label="Click Me",
    color="blue",
    emoji="👍"
)
async def my_button(interaction):
    await interaction.response.send_message("Button clicked!")
```

**Decorator Parameters:**
- `label` (required) - The button's display label
- `color` (optional, default: `"gray"`) - Button color: `"blue"`, `"gray"`/`"grey"`, `"green"`, or `"red"`
- `emoji` (optional) - An emoji to display on the button
- `row` (optional) - Row position in the UI (0-4)
- `disabled` (optional, default: `False`) - Whether the button is disabled

**Supported Colors:**
- `"blue"` → `discord.ButtonStyle.primary`
- `"gray"` / `"grey"` → `discord.ButtonStyle.secondary`
- `"green"` → `discord.ButtonStyle.success`
- `"red"` → `discord.ButtonStyle.danger`

### Select Menus

Use the `@select` decorator to create dropdown select menus:

```python
from utils.discord_setup import select

@select(
    placeholder="Choose an option",
    options=["Option 1", "Option 2", "Option 3"],
    min_values=1,
    max_values=1
)
async def my_select(interaction, values):
    await interaction.response.send_message(f"You selected: {values[0]}")
```

**Decorator Parameters:**
- `placeholder` (optional) - Placeholder text shown when no option is selected
- `options` (optional, default: `[]`) - List of options (strings, dicts, or `discord.SelectOption` objects)
- `min_values` (optional, default: `1`) - Minimum number of options to select
- `max_values` (optional, default: `1`) - Maximum number of options to select
- `row` (optional) - Row position in the UI (0-4)
- `disabled` (optional, default: `False`) - Whether the select menu is disabled

**Option Formats:**
Options can be provided in three ways:

```python
# Simple strings (label and value are the same)
options=["Option 1", "Option 2"]

# Dictionaries (converted to SelectOption)
options=[
    {"label": "First", "value": "opt1"},
    {"label": "Second", "value": "opt2"}
]

# discord.SelectOption objects
options=[
    discord.SelectOption(label="First", value="opt1"),
    discord.SelectOption(label="Second", value="opt2")
]
```

## UI Components

### Creating Views with `ui()`

The `ui()` function creates a fresh `discord.ui.View` with button and select components:

```python
from utils.discord_setup import ui, button, select

@button(label="Approve", color="green")
async def approve_btn(interaction):
    await interaction.response.send_message("Approved!")

@button(label="Reject", color="red")
async def reject_btn(interaction):
    await interaction.response.send_message("Rejected!")

@select(placeholder="Choose...", options=["A", "B", "C"])
async def choose_select(interaction, values):
    await interaction.response.send_message(f"You chose: {values[0]}")

# Create the view
view = ui(approve_btn, reject_btn, choose_select)

# Send it in a message
await ctx.send("Choose an action:", view=view)
```

**Key Features:**
- Returns a fresh `discord.ui.View` instance each call
- Components are positioned using the `row` parameter
- Default timeout is 180 seconds (can be customized with `timeout=` parameter)

## Automatic Cog Creation

### `setup_module()`

The `setup_module()` function automatically converts decorated functions in a module into a Discord cog:

```python
from utils.discord_setup import setup_module
import mycog

async def setup(bot):
    await setup_module(bot, mycog)
```

**How it works:**
1. Scans the module for functions with Discord markers
2. Wraps them with appropriate discord.py decorators
3. Groups them into a dynamically created `Cog` class
4. Registers the cog with the bot

### Example Module

Create a file like `cogs/my_feature.py`:

```python
from utils.discord_setup import command, listener

@command(name="ping", description="Ping the bot")
async def ping_cmd(ctx):
    await ctx.send(f"Pong! {ctx.bot.latency * 1000:.0f}ms")

@listener(name="on_ready")
async def on_ready_event():
    print("Bot is ready!")
```

Then load it in your main bot file:

```python
from utils.discord_setup import setup_module
import cogs.my_feature as my_feature

@bot.event
async def on_ready():
    await setup_module(bot, my_feature)
```

## Real-World Example: Report Command

Here's how the module is used in the `report.py` command (from the Cases System):

```python
from utils.discord_setup import command

@command("🔴 Reports", description="Report a message to staff", usage="<reply to message> <reason>")
async def report(ctx, *, reason: str):
    # Validate message reference
    if not ctx.message.reference:
        await ctx.send("❌️ You must reply to the message you're reporting, *sigh*")
        return
    
    reported_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    
    # Insert report into database
    db.insert("cases", ..., (...))
    
    # Send confirmation embeds
    await ctx.send(embed=embed)
    await report_channel.send(embed=mod_embed)
```

The `@command` decorator with metadata is converted into a proper Discord command that can be invoked like `/report <reason>`.

## Internal Architecture

### `_build_cog(bot, module)`

This function:
1. Iterates through all callables in a module
2. Checks for marker attributes
3. Applies appropriate discord.py decorators
4. Assembles attributes into a new Cog class using `type()`
5. Returns an instance of the dynamically created cog

### `_make_button(func)` and `_make_select(func)`

These functions:
1. Extract metadata from the marker attributes
2. Convert simplified parameters into discord.py's lower-level API calls
3. Return the decorated function ready for the View

## Benefits

- **Less Boilerplate** - No need for manual cog classes or complex inheritance
- **Declarative Style** - Decorators make intent clear at a glance
- **Modular Code** - Commands and listeners are grouped logically
- **Dynamic UI** - Generate views on-the-fly without subclassing
- **Type Safety** - Parameters are documented in decorators

## See Also

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord API Reference](https://discord.com/developers/docs/intro)
