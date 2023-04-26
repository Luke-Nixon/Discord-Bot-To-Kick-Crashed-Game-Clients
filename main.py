from rcon.source import rcon
import mysql.connector
import discord
from discord.ext import commands


# RconConnectionInfo class used to store rcon connection data for each server
class RconConnectionInfo:
    def __init__(self, ip, port, password):
        self.rcon_ip = ip
        self.rcon_port = port
        self.rcon_password = password


# array of rcon connection information for each server to run the kick command on.
rcon_connections = [
    RconConnectionInfo("Your IP", 27054, "Your Password"),
    RconConnectionInfo("Your IP", 27055, "Your Password"),
    RconConnectionInfo("Your IP", 27056, "Your Password"),
    RconConnectionInfo("Your IP", 27057, "Your Password"),
    RconConnectionInfo("Your IP", 27058, "Your Password"),
    RconConnectionInfo("Your IP", 27059, "Your Password"),
    RconConnectionInfo("Your IP", 27060, "Your Password"),
    RconConnectionInfo("Your IP", 27061, "Your Password"),
    RconConnectionInfo("Your IP", 27062, "Your Password"),
    RconConnectionInfo("Your IP", 27063, "Your Password"),
    RconConnectionInfo("Your IP", 27064, "Your Password"),
    RconConnectionInfo("Your IP", 27065, "Your Password"),
    RconConnectionInfo("Your IP", 27066, "Your Password")
]

# MYSQL login information
mysql_host = "Your IP"
mysql_username = "your MYSQL username"
mysql_password = "Your MYSQL password"
mysql_db = "Your MYSQL db"

# discord bot auth token
bot_token = "Your Bot Token"
# desired bot command channel
channel_id = 0000000000000000

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("synced")


@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction):
    # defer the result of this command to ignore discords default 3 second timeout.
    await interaction.response.defer(ephemeral=True)

    # only allow commands from within the desired channel
    if interaction.channel_id != channel_id:
        return

    # discord ID of the user who used the command.
    discord_id = str(interaction.user.id)

    # establish a database connection
    database_connector = mysql.connector.connect(
        host=mysql_host,
        user=mysql_username,
        password=mysql_password,
        database=mysql_db
    )
    # create a cursor object to execute SQL queries
    cursor = database_connector.cursor(buffered=True)

    # execute the SQL command
    sql = "SELECT * FROM " + mysql_db + " WHERE DiscordId = '" + discord_id + "' LIMIT 1"
    cursor.execute(sql)

    # check that the SQL found a result
    if cursor.rowcount == 0:
        # if no steam ID exists registered to this users discord ID.
        # inform the user
        await interaction.followup.send(
            "No steam ID is associated with Discord ID:" + discord_id + "\n\n To link your Discord account to your "
                                                                        "ark character, type `/linkgame " +
            discord_id + "` in game chat.",
            ephemeral=True)
        cursor.close()
        database_connector.close()
        return

    # retrieve the first row of the result set
    steamid = str(cursor.fetchone()[1])

    # close the cursor and database connection
    cursor.close()
    database_connector.close()

    # run the kick command on the RCON for each server
    for rcon_connection in rcon_connections:

        # try as connection to remote host is not guaranteed.
        try:
            await rcon('KickPlayer ' + steamid, host=rcon_connection.rcon_ip, port=rcon_connection.rcon_port,
                       passwd=rcon_connection.rcon_password)
        except Exception as e:
            print(e)

    await interaction.followup.send("Character with SteamID:" + steamid + " Was kicked from the game.", ephemeral=True)


bot.run(bot_token)
