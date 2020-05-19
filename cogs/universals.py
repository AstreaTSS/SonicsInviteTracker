def default_db_entry(user_id):
    entry = {
        "data": "",
        "user_id_bac": user_id
    }
    return entry

def default_invite_create(guild_id):
    user_entry = {
        str(guild_id): {
            "invited": [],
            "invited_by": None,
            "bonus_invites": 0,
            "synced_invites": 0
        }
    }

    return user_entry

def get_invite_entry(bot, user_id, guild_id):
    member_entry = [u for u in bot.invite_tracker if u["user_id_bac"] == user_id]
    if member_entry == []:
        bot.invite_tracker[user_id] = default_db_entry(user_id)
        member_entry = default_invite_create(guild_id)
        bot.invite_tracker[user_id]["data"] = member_entry
    else:
        member_entry = member_entry[0]["data"]
        if not str(guild_id) in member_entry.keys():
            member_entry[str(guild_id)] = {
                "invited": [],
                "invited_by": None,
                "bonus_invites": 0,
                "synced_invites": 0
            }
    
    return member_entry

def invite_amount(guild_entry):
    return guild_entry["bonus_invites"] + guild_entry["synced_invites"] + len(guild_entry["invited"])