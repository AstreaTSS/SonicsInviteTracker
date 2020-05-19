import discord, os, asyncio
from discord.ext import commands

async def _prefix(bot, msg):
    bot_id = bot.user.id
    return [f"<@{bot_id}> ", f"<@!{bot_id}> ", "i!"]

bot = commands.Bot(command_prefix=_prefix, fetch_offline_members=True)

bot.remove_command("help")

@bot.event
async def on_ready():
    bot.invite_tracker = {}
    bot.tracker_config = {}
    bot.load_extension("cogs.db_handler")
    while bot.invite_tracker == {} or bot.tracker_config == {}:
        await asyncio.sleep(0.1)

    cogs_list = ["cogs.commands"]

    for cog in cogs_list:
        bot.load_extension(cog)

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------\n')

    activity = discord.Activity(name = 'for invites!', type = discord.ActivityType.watching)
    await bot.change_presence(activity = activity)
    
@bot.check
async def block_dms(ctx):
    return ctx.guild is not None
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        original = error.original
        if not isinstance(original, discord.HTTPException):
            print(original)

            application = await ctx.bot.application_info()
            owner = application.owner
            await ctx.send(f"{owner.mention}: {original}")
    elif isinstance(error, (commands.ConversionError, commands.UserInputError)):
        await ctx.send(error)
    elif isinstance(error, commands.CheckFailure):
        if ctx.guild != None:
            await ctx.send("You do not have the proper permissions to use that command.")
    elif isinstance(error, commands.CommandNotFound):
        ignore = True
    else:
        print(error.original)
        
        application = await ctx.bot.application_info()
        owner = application.owner
        await ctx.send(f"{owner.mention}: {error.original}")

bot.run(os.environ.get("MAIN_TOKEN"))