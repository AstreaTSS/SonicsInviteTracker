from discord.ext import commands
import discord, datetime, re
import cogs.universals

async def proper_permissions(ctx):
    permissions = ctx.author.guild_permissions
    return (permissions.administrator or permissions.manage_messages)

class NormCMDS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        help_msg = """
        There are a couple of commands:
        """
        await ctx.send(help_msg)

    @commands.command()
    async def ping(self, ctx):
        current_time = datetime.datetime.utcnow().timestamp()
        mes_time = ctx.message.created_at.timestamp()

        ping_discord = round((self.bot.latency * 1000), 2)
        ping_personal = round((current_time - mes_time) * 1000, 2)

        await ctx.send(f"Pong!\n`{ping_discord}` ms from discord.\n`{ping_personal}` ms personally (not accurate)")

    @commands.command()
    async def invites(self, ctx, user_mention = None):
        member = None

        if user_mention != None:
            if re.search("[<@>]", member):
                user_id = re.sub("[<@>]", "", member)
                user_id = user_id.replace("!", "")
                member = ctx.guild.get_member(int(user_id))
        else:
            member = ctx.author

        if member != None:
            member_entry = cogs.universals.get_invite_entry(self.bot, member.id, ctx.guild.id)

            invite_amount = cogs.universals.invite_amount(member_entry[str(ctx.guild.id)])
            guild_entry = member_entry[str(ctx.guild.id)]

            content = (f"Has **{invite_amount}** invites (**{len(guild_entry['invited'])}** normal, " +
            f"**{guild_entry['synced_invites']}** synced, **{'bonus_invites'}** bonus)")
            icon = str(ctx.author.avatar_url_as(format="jpg", size=128))

            send_embed = discord.Embed(colour=discord.Colour(0x4378fc), description=content, timestamp=ctx.message.created_at)
            send_embed.set_author(name=str(ctx.author), icon_url=icon)

            await ctx.send(embed=send_embed)
        else:
            await ctx.send("That's not a user mention! Try again with a user mention.")

    @commands.command(name = "top", aliases = ["leaderboard", "lb"])
    async def top(self, ctx):
        def by_stars(elem):
            return cogs.universals.invite_amount(elem["data"][str(ctx.guild.id)])

        content = ""

        member_entries = [u for u in self.bot.invite_tracker if str(ctx.guild.id) in u["data"].keys()]
        member_entries.sort(reversed=True, key=by_stars)

        for i in range(len(member_entries)):
            if i > 9:
                break

            entry = member_entries[i]["data"][str(ctx.guild.id)]
            user = ctx.guild.get_member(member_entries[i]["user_id_bac"])
            invite_amount = cogs.universals.invite_amount(entry)

            content += (f"**#{i+1}**    **»**    {str(user)}:\n" +
            f"**{invite_amount}** invites (**{len(entry['invited'])}** normal, " +
            f"**{entry['synced_invites']}** synced, **{'bonus_invites'}** bonus)\n"
            )

        author_entry = [u for u in member_entries if u["user_id_bac"] == ctx.author.id]
        if author_entry != []:
            author_index = member_entries.index(author_entry[0])
            content += f"\nYour position: #{author_index + 1}"
        else:
            content += f"\nYour position: N/A (You have no entry!)"

        icon = str(ctx.guild.icon_url_as(format="jpg", size=128))
        send_embed = discord.Embed(colour=discord.Colour(0x4378fc), description=content, timestamp=ctx.message.created_at)
        send_embed.set_author(name="Top Invites Leaderboard", icon_url=icon)
        await ctx.send(embed=send_embed)

def setup(bot):
    bot.add_cog(NormCMDS(bot))