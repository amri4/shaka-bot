Absolutely. Here's a copy-paste README.md designed around your current discord_setup.py, with templates for every public feature and examples of how the pieces fit together.

# discord_setup

A small helper system built on top of `discord.py` that makes commands,
listeners, buttons, selects, modals, UI views, and automatic Cog creation
much easier to write.

The goal is simple:

> Write the Discord logic without repeatedly writing Discord.py boilerplate.

---

# Table of Contents

- [Installation](#installation)
- [Importing](#importing)
- [Commands](#commands)
- [Listeners](#listeners)
- [Buttons](#buttons)
- [Select Menus](#select-menus)
- [UI Views](#ui-views)
- [Modals](#modals)
- [Opening Modals](#opening-modals)
- [Automatic Cogs](#automatic-cogs)
- [Automatic Systems](#automatic-systems)
- [Recommended Folder Structure](#recommended-folder-structure)
- [Complete Example](#complete-example)
- [Important Notes](#important-notes)

---

# Installation

Place your helper somewhere importable by your project.

Example:

```text
project/
│
├── utils/
│   ├── __init__.py
│   └── discord_setup.py
│
├── lilith/
│   ├── __init__.py
│   └── cogs/
│
└── main.py

Then import from it:

from utils.discord_setup import ...


---

Importing

Examples:

from utils.discord_setup import command

from utils.discord_setup import listener

from utils.discord_setup import button

from utils.discord_setup import select

from utils.discord_setup import modal

from utils.discord_setup import ui

You can also import multiple things:

from utils.discord_setup import (
    command,
    button,
    select,
    modal,
    ui
)


---

Commands

The @command() decorator turns a normal function into a discord.py prefix command when the module is automatically loaded.

Basic command

from utils.discord_setup import command


@command()
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )


---

Command with arguments

from utils.discord_setup import command


@command()
async def say(ctx, *, message):

    await ctx.send(
        message
    )

Usage:

Lilith say hello everyone


---

Command options

Any keyword arguments accepted by commands.command() can be passed to @command().

Example:

@command(
    name="hello",
    aliases=["hi"]
)
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )


---

Listeners

The @listener() decorator creates a Cog listener.

Basic listener

from utils.discord_setup import listener


@listener()
async def on_member_join(member):

    print(
        f"{member} joined the server."
    )


---

Specific event name

You can specify the event manually.

from utils.discord_setup import listener


@listener("on_message")
async def message_listener(message):

    print(
        message.content
    )

The name must be a valid Discord.py event.

Examples:

on_ready
on_message
on_member_join
on_member_remove
on_reaction_add


---

Buttons

Buttons use the @button() decorator.

Basic button

from utils.discord_setup import button


@button(
    label="Click Me"
)
async def click_me(
    interaction,
    button
):

    await interaction.response.send_message(
        "You clicked the button!",
        ephemeral=True
    )


---

Button Colors

The built-in color names are:

blue
gray
grey
green
red

Example:

@button(
    label="Approve",
    color="green"
)
async def approve(
    interaction,
    button
):

    await interaction.response.send_message(
        "Approved!",
        ephemeral=True
    )

Another:

@button(
    label="Reject",
    color="red"
)
async def reject(
    interaction,
    button
):

    await interaction.response.send_message(
        "Rejected!",
        ephemeral=True
    )


---

Button Emoji

@button(
    label="Approve",
    color="green",
    emoji="✅"
)
async def approve(
    interaction,
    button
):

    await interaction.response.send_message(
        "Approved!"
    )


---

Button Rows

@button(
    label="Button",
    row=1
)
async def my_button(
    interaction,
    button
):

    await interaction.response.send_message(
        "Clicked!"
    )

Rows normally range from:

0
1
2
3
4


---

Disabled Buttons

@button(
    label="Unavailable",
    disabled=True
)
async def unavailable(
    interaction,
    button
):

    pass


---

Select Menus

Select menus use @select().

Simple options

from utils.discord_setup import select


@select(
    placeholder="Choose something",
    options=[
        "Option 1",
        "Option 2",
        "Option 3"
    ]
)
async def choose(
    interaction,
    select
):

    choice = select.values[0]

    await interaction.response.send_message(
        f"You selected: {choice}",
        ephemeral=True
    )


---

Select Options with Values

You can use dictionaries when you want different labels and values.

@select(
    placeholder="Choose an action",
    options=[
        {
            "label": "Approve",
            "value": "approve"
        },
        {
            "label": "Reject",
            "value": "reject"
        }
    ]
)
async def action(
    interaction,
    select
):

    choice = select.values[0]

    await interaction.response.send_message(
        f"Selected: {choice}",
        ephemeral=True
    )


---

SelectOption Objects

You can also provide normal Discord.py SelectOption objects.

import discord

from utils.discord_setup import select


@select(
    placeholder="Choose",
    options=[
        discord.SelectOption(
            label="Apple",
            value="apple",
            description="An apple"
        ),
        discord.SelectOption(
            label="Orange",
            value="orange",
            description="An orange"
        )
    ]
)
async def fruit(
    interaction,
    select
):

    choice = select.values[0]

    await interaction.response.send_message(
        f"You selected {choice}."
    )


---

Multiple Select Values

@select(
    placeholder="Choose punishments",
    options=[
        "timeout",
        "strike",
        "bounty"
    ],
    min_values=1,
    max_values=3
)
async def punishments(
    interaction,
    select
):

    selected = select.values

    print(
        selected
    )

Example result:

[
    "timeout",
    "strike"
]


---

Disabled Selects

@select(
    placeholder="Unavailable",
    options=[
        "Option 1",
        "Option 2"
    ],
    disabled=True
)
async def unavailable(
    interaction,
    select
):

    pass


---

UI Views

The ui() function creates a fresh discord.ui.View.

Pass decorated buttons or selects to it.

from utils.discord_setup import ui


await ctx.send(
    "Choose:",
    view=ui(
        approve,
        reject
    )
)


---

View with Buttons

from utils.discord_setup import button
from utils.discord_setup import ui


@button(
    label="Approve",
    color="green"
)
async def approve(
    interaction,
    button
):

    await interaction.response.send_message(
        "Approved!"
    )


@button(
    label="Reject",
    color="red"
)
async def reject(
    interaction,
    button
):

    await interaction.response.send_message(
        "Rejected!"
    )


@command()
async def review(ctx):

    await ctx.send(
        "Review the case:",
        view=ui(
            approve,
            reject
        )
    )


---

View with Buttons and Selects

await ctx.send(
    "Choose an action:",
    view=ui(
        approve,
        reject,
        action
    )
)

All components passed to ui() must have been created using @button() or @select().


---

View Timeout

The default timeout is:

180 seconds

You can change it:

view=ui(
    approve,
    reject,
    timeout=300
)


---

Modals

Modals use the @modal() decorator.

Basic Modal

from utils.discord_setup import modal


@modal(
    title="Example Modal"
)
async def example(
    interaction,
    values
):

    print(
        values
    )

    await interaction.response.send_message(
        "Submitted!",
        ephemeral=True
    )

A modal does not automatically have fields.

Fields are added with:

example.input(...)


---

Modal Inputs

example.input(
    "name",
    label="Your Name"
)

The first argument is the internal name.

That name becomes the dictionary key.

For example:

values["name"]


---

Input Placeholder

example.input(
    "name",
    label="Your Name",
    placeholder="Enter your name"
)


---

Default Value

example.input(
    "name",
    label="Your Name",
    default="Unknown"
)


---

Required Inputs

Inputs are required by default.

example.input(
    "name",
    label="Your Name"
)

You can make one optional:

example.input(
    "nickname",
    label="Nickname",
    required=False
)


---

Input Length

example.input(
    "name",
    label="Name",
    min_length=2,
    max_length=30
)


---

Paragraph Inputs

Use Discord's paragraph style:

import discord

from utils.discord_setup import modal


@modal(
    title="Report"
)
async def report_modal(
    interaction,
    values
):

    reason = values["reason"]

    ...


report_modal.input(
    "reason",
    label="Reason",
    placeholder="Explain the problem...",
    style=discord.TextStyle.paragraph
)


---

Reading Modal Values

Suppose you define:

@modal(
    title="Profile"
)
async def profile(
    interaction,
    values
):

    name = values["name"]
    bio = values["bio"]

Then:

values["name"]

contains the user's answer to the name input.

And:

values["bio"]

contains the user's answer to the bio input.

Example:

{
    "name": "Amri",
    "bio": "Hello!"
}

This is a normal Python dictionary.

It is NOT a JSON file.


---

Opening a Modal

A modal can be opened from a button.

Example:

from utils.discord_setup import button

from ..modals.example import example


@button(
    label="Open Modal",
    color="blue"
)
async def open_modal(
    interaction,
    button
):

    await interaction.response.send_modal(
        example()
    )


---

Complete Modal Example

import discord

from utils.discord_setup import modal


@modal(
    title="Report Message"
)
async def report_modal(
    interaction,
    values
):

    reason = values["reason"]

    await interaction.response.send_message(
        f"Report submitted:\n{reason}",
        ephemeral=True
    )


report_modal.input(
    "reason",
    label="Reason",
    placeholder="Explain why you are reporting this message...",
    style=discord.TextStyle.paragraph,
    required=True
)


---

Automatic Cogs

discord_setup can automatically turn modules containing decorated commands and listeners into Cogs.

You do NOT need to manually write:

class MyCog(commands.Cog):

for every module.


---

Example Automatic Cog

File:

lilith/cogs/example.py

Contents:

from utils.discord_setup import command


@command()
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )

The automatic system finds the command and creates the Cog.


---

Multiple Commands in One Module

from utils.discord_setup import command


@command()
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )


@command()
async def goodbye(ctx):

    await ctx.send(
        "Goodbye!"
    )

Both commands are automatically added to the generated Cog.


---

Commands + Listeners

from utils.discord_setup import (
    command,
    listener
)


@command()
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )


@listener()
async def on_member_join(member):

    print(
        f"{member} joined."
    )

Both are automatically detected.


---

setup_module

setup_module() takes one Python module and converts its decorated commands/listeners into a Cog.

Normally you don't need to call this yourself.

Conceptually:

module
  ↓
_build_cog()
  ↓
Cog
  ↓
bot.add_cog()


---

setup_system

setup_system() recursively scans a package and loads its modules.

Example:

from utils.discord_setup import setup_system


async def setup(bot):

    await setup_system(
        bot,
        __package__
    )

If the package is:

cases_system/

it can discover modules inside:

cases_system/
├── commands/
│   ├── report.py
│   └── review.py
│
├── ui/
│   └── buttons.py
│
└── modals/
    └── report.py

Modules are imported automatically.


---

cog.py

A system can have a tiny cog.py.

Example:

from utils.discord_setup import setup_system


async def setup(bot):

    await setup_system(
        bot,
        __package__
    )

This is all the Cog loader needs.


---

Recommended System Structure

For a large system:

lilith/
└── cogs/
    └── cases_system/
        │
        ├── __init__.py
        ├── cog.py
        │
        ├── commands/
        │   ├── __init__.py
        │   ├── report.py
        │   └── review.py
        │
        ├── ui/
        │   ├── __init__.py
        │   ├── case_buttons.py
        │   └── case_selects.py
        │
        ├── modals/
        │   ├── __init__.py
        │   └── punishment_values.py
        │
        └── punishments/
            ├── __init__.py
            ├── timeout.py
            ├── strike.py
            └── bounty.py


---

Recommended Architecture

Keep different responsibilities separate.

commands/
    Commands start actions.

ui/
    Buttons and select menus.

modals/
    Forms that collect user input.

punishments/
    Actual punishment logic.

database/
    Persistent data.

cog.py
    Loads the system.

For example:

Moderator
    ↓
Button / Select
    ↓
Modal
    ↓
Case system
    ↓
Punishment
    ↓
PunksDB


---

Complete Example

File

lilith/cogs/example/commands/test.py

import discord

from utils.discord_setup import (
    command,
    button,
    ui,
    modal
)


@button(
    label="Click Me",
    color="blue",
    emoji="👋"
)
async def click(
    interaction,
    button
):

    await interaction.response.send_message(
        "Button clicked!",
        ephemeral=True
    )


@modal(
    title="Example Form"
)
async def form(
    interaction,
    values
):

    name = values["name"]

    await interaction.response.send_message(
        f"Hello {name}!",
        ephemeral=True
    )


form.input(
    "name",
    label="Name",
    placeholder="Enter your name"
)


@button(
    label="Open Form",
    color="green"
)
async def open_form(
    interaction,
    button
):

    await interaction.response.send_modal(
        form()
    )


@command()
async def test(ctx):

    await ctx.send(
        "Test UI:",
        view=ui(
            click,
            open_form
        )
    )


---

Important Notes

Decorators do not immediately create Discord.py objects

For example:

@button(...)
async def approve(...):
    ...

does not directly create a normal button instance.

The decorator stores configuration on the function.

discord_setup later converts it into the appropriate Discord.py object.


---

Internal Functions

These are mostly implementation details.

You normally should NOT call them manually.

get_button_style()
_make_button()
_make_select()
_make_modal()
_build_cog()
setup_module()

They are used by the public API.


---

Public API

These are the functions you normally use:

command()
listener()
button()
select()
modal()
ui()
setup_system()

For modals:

modal(...)
    ↓
your_modal.input(...)
    ↓
your_modal()


---

No JSON Required

This system does not require JSON files for:

commands

buttons

selects

modals

temporary UI values

punishment selections


For example:

values = {
    "duration": "2h",
    "amount": "1"
}

is simply a Python dictionary in memory.

If something needs to persist after the bot restarts, store it in your database system instead.


---

Design Philosophy

The purpose of discord_setup is to remove repetitive Discord.py boilerplate without hiding the actual behavior of the bot.

Instead of repeatedly writing:

class Something(commands.Cog):

or:

class SomethingView(discord.ui.View):

or:

class SomethingModal(discord.ui.Modal):

you can focus on the actual system.

The helper handles the repetitive setup.


---

Quick Reference

Command

@command()
async def command_name(ctx):
    ...

Listener

@listener()
async def on_event(...):
    ...

Button

@button(
    label="Button",
    color="blue"
)
async def button_name(
    interaction,
    button
):
    ...

Select

@select(
    placeholder="Choose",
    options=[
        "One",
        "Two"
    ]
)
async def select_name(
    interaction,
    select
):
    ...

Modal

@modal(
    title="Example"
)
async def modal_name(
    interaction,
    values
):
    ...

Modal Input

modal_name.input(
    "name",
    label="Name",
    placeholder="Enter your name"
)

View

view=ui(
    button_name,
    select_name
)

Open Modal

await interaction.response.send_modal(
    modal_name()
)

Automatic System Loader

async def setup(bot):

    await setup_system(
        bot,
        __package__
    )


---

Final Example

A minimal system can therefore look like this:

my_system/
├── __init__.py
├── cog.py
├── command.py
├── ui.py
└── modal.py

cog.py:

from utils.discord_setup import setup_system


async def setup(bot):

    await setup_system(
        bot,
        __package__
    )

command.py:

from utils.discord_setup import (
    command,
    ui
)


@command()
async def hello(ctx):

    await ctx.send(
        "Hello!"
    )

ui.py:

from utils.discord_setup import button


@button(
    label="Hello",
    color="blue"
)
async def hello_button(
    interaction,
    button
):

    await interaction.response.send_message(
        "Hello!"
    )

modal.py:

from utils.discord_setup import modal


@modal(
    title="Example"
)
async def example(
    interaction,
    values
):

    await interaction.response.send_message(
        values["name"],
        ephemeral=True
    )


example.input(
    "name",
    label="Name",
    placeholder="Enter your name"
)

The result is a system where the repetitive Cog/View/Modal boilerplate is handled automatically, while the actual bot logic remains in your individual modules.
