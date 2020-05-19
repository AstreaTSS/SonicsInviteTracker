from discord.ext import commands, tasks
import discord, asyncio, copy
import cogs.universals

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_invites.start()

    @tasks.loop(seconds=5)
    async def get_invites(self):
        guilds_invites_dict = {}

        for guild_id in self.bot.tracker_config.keys():
            guild = self.bot.get_guild(guild_id)
            guild_invites = await guild.invites()
            guilds_invites_dict[guild_id] = guild_invites

        self.bot.guilds_invites = copy.deepcopy(guilds_invites_dict)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        current_guild_invites = await guild.invites()
        invite_used = None

        join_chan_id = self.bot.tracker_config[guild.id]["join_chan_id"]
        join_chan = await self.bot.fetch_channel(join_chan_id)

        for invite in current_guild_invites:
            storage_invite = [i for i in self.bot.guilds_invites[guild.id] if i.code == invite.code]
            if storage_invite != []:
                if invite.uses > storage_invite[0].uses:
                    invite_used = invite
                    break

        if invite_used != None:
            inviter_entry = cogs.universals.get_invite_entry(self.bot, invite_used.inviter.id, guild.id)

            inviter_guild_entry = inviter_entry[str(guild.id)]
            if not member.id in inviter_guild_entry["invited"]:
                inviter_guild_entry["invited"].append(member.id)
            inviter_entry[str(guild.id)] = inviter_guild_entry

            invited_entry = cogs.universals.get_invite_entry(self.bot, member.id, guild.id)
            invited_entry[str(guild.id)]["invited_by"] = invite_used.inviter.id

            self.bot.invite_tracker[invite_used.inviter.id]["data"] = inviter_entry
            self.bot.invite_tracker[member.id]["data"] = invited_entry

            invite_amount = cogs.universals.invite_amount(inviter_guild_entry)
            
            join_mes = f"{member.mention} **joined**; Invited by **{str(invite_used.inviter)}** (**{invite_amount}** invites)."
            await join_chan.send(join_mes)
        else:
            await join_chan.send(f"{member.mention} joined, but I can't figure out how they joined.")

        await self.get_invites()


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild

        member_entry = [u for u in self.bot.invite_tracker if u["user_id_bac"] == member.id]
        if member_entry != []:
            invited_by = member_entry[0]["data"][str(guild.id)]["invited_by"]
            inviter_entry = [u for u in self.bot.invite_tracker if u["user_id_bac"] == invited_by]
            if inviter_entry != []:
                invited_list = inviter_entry[0]["data"][str(guild.id)]["invited"]
                if member.id in invited_list:
                    invited_list.remove(member.id)
                    self.bot.invite_tracker[invited_by]["data"][str(guild.id)]["invited"] = invited_list

            del self.bot.invite_tracker[member.id]["data"][str(guild.id)]


def setup(bot):
    bot.add_cog(InviteTracker(bot))