import discord
from discord.ext import commands
import random
import asyncio

class NumberGuess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = set()

    def can_start_game(self):
        people = len(self.active_games)
        if people >= 5:
            return False
        else:
            return True

    @commands.command()
    async def numberguess(self, ctx):
        if self.can_start_game():
            self.active_games.add(ctx.author.id)
        else:
            await ctx.send("OH WAIT I'm feeling dizzy right now many people are playing, try again later")
            return
        await ctx.send("Guess a number from 1 to 100, i will tell u if your number is HIGHERR or LOWERR!")
        secret = random.randint(1, 100)
        while True:
            try:
                message = await self.bot.wait_for("message", timeout=20)
                if message.author.id != ctx.author.id:
                    continue
                if not message.content.isdigit():
                    await ctx.send("say it in numbers not words")
                    continue
                guess = int(message.content)
                if guess > secret:
                    await ctx.send("A bit lower")
                elif guess < secret:
                    await ctx.send("A bit higher")
                else:
                    await ctx.send("THAT'S THE NUMBER, YOU WONNN")
                    self.active_games.remove(ctx.author.id)
                    break
            except asyncio.TimeoutError:
                await ctx.send("time ended")
                self.active_games.remove(ctx.author.id)
                break

async def setup(bot):
    await bot.add_cog(NumberGuess(bot))
