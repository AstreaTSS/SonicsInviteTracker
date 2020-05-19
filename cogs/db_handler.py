from discord.ext import commands, tasks
import discord, os, asyncio, aiomysql, copy, json

class DBHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commit_loop.start()

    async def get_dbs(self):
        invite_tracker_db = await self.run_command("SELECT * FROM invite_tracker")
        tracker_config_db = await self.run_command("SELECT * FROM tracker_config")

        invite_tracker_dict = {}
        tracker_config_dict = {}

        for row in invite_tracker_db:
            invite_tracker_dict[row[0]] = {
                "data": json.loads(row[1]),
                "user_id_bac": row[0]
            }

        for row in tracker_config_db:
            tracker_config_dict[row[0]] = {
                "join_chan_id": row[1]
            }

        self.bot.invite_tracker = invite_tracker_dict
        self.bot.tracker_config = tracker_config_dict
        self.bot.invite_tracker_bac = copy.deepcopy(invite_tracker_dict)
        self.bot.tracker_config_bac = copy.deepcopy(tracker_config_dict)

    @tasks.loop(minutes=2.5)
    async def commit_loop(self):
        list_of_cmds = []
        invite_tracker = self.bot.invite_tracker
        invite_bac = self.bot.invite_tracker_bac

        for user in invite_tracker.keys():
            if user in invite_bac.keys():
                if not invite_tracker[user] == invite_bac[user]:
                    list_of_cmds.append(f"UPDATE invite_tracker SET data = {json.dumps(invite_tracker[user]['data'])} WHERE user_id = {user}")
            else:
                list_of_cmds.append("INSERT INTO invite_tracker "+
                f"(user_id, data) VALUES {user}, {json.dumps(invite_tracker[user]['data'])};")
                
        self.bot.invite_tracker_bac = copy.deepcopy(self.bot.invite_tracker)

        tracker_config = self.bot.tracker_config
        tracker_config_bac = self.bot.tracker_config_bac

        for server in tracker_config.keys():
            if server in tracker_config_bac.keys():
                if not tracker_config[server] == tracker_config_bac[server]:
                    list_of_cmds.append(f"UPDATE tracker_config SET join_chan_id = {tracker_config[server]['join_chan_id']}, " + 
                    f"WHERE server_id = {server}")
        self.bot.star_config_bac = copy.deepcopy(self.bot.star_config)

        if list_of_cmds != []:
            await self.run_command(list_of_cmds, a_list = True, commit = True)

    @commit_loop.before_loop
    async def before_commit_loop(self):
        await self.get_dbs()

        while self.bot.star_config == {} or self.bot.starboard == {}:
            await asyncio.sleep(0.1)

        await asyncio.sleep(60)

    async def run_command(self, command, a_list = False, commit = False):
        output = None

        host = os.environ.get("DB_HOST_URL")
        port = os.environ.get("DB_PORT")
        username = os.environ.get("DB_USERNAME")
        password = os.environ.get("DB_PASSWORD")
        db = os.environ.get("DB_NAME")

        pool = await aiomysql.create_pool(host=host, port=int(port),
                                          user=username, password=password,
                                          db=db)

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                if a_list:
                    for a_command in command:
                        await cur.execute(a_command)
                else:
                    await cur.execute(command)

                if commit:
                    await conn.commit()
                output = await cur.fetchall()
                
        pool.close()
        await pool.wait_closed()

        return output
    
def setup(bot):
    bot.add_cog(DBHandler(bot))