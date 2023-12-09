import interactions
from interactions import Option, OptionType
from py1337x import py1337x
from topsecret import email, password, bot_token
from seedr import SeedrAPI

torrents = py1337x() 
bot = interactions.Client(token=bot_token)
seedr = SeedrAPI(email=email, password=password)

search_results = {}
RESULTS_PER_QUERY = 5

def get_torrent_links_by_title(title, results_per_query):
    results = torrents.search(title, category='movies', sortBy='seeders', order='desc')
    return results['items'][:RESULTS_PER_QUERY]

def get_magnet_link_from_torrent_link(link):
    return torrents.info(link=link)['magnetLink']

def add_torrent_to_seedr(magnet_link):
    output = seedr.add_torrent(magnet_link)
    return output


@bot.command(
    name="pirate",
    description="Add the title to the torrent you're looking for",
    options=[
        Option(
            name="title",
            description="Name of the movie",
            type=OptionType.STRING,
            required=True
        )
    ]
)
async def pirate_command(ctx: interactions.CommandContext, title: str):
    top_five = get_torrent_links_by_title(title, RESULTS_PER_QUERY)
    search_results[ctx.author.id] = top_five

    embed = interactions.Embed(
        title="Top 5 Torrents",
        description=f"Search results for *{title}*",
        color=0xB42F00
    )
    for index, torrent in enumerate(top_five):
        embed.add_field(
            name=f"{index + 1}) {torrent['name']}",
            value=f"Size: {torrent['size']} | Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']}",
            inline=False
        )

    options = [
        interactions.SelectOption(
            label=f"{index + 1}",
            description=torrent['name'][:100],
            value=str(index)
        )
        for index, torrent in enumerate(top_five)
    ]

    select_menu = interactions.SelectMenu(
        custom_id="select_torrent",
        options=options,
        placeholder="Select a torrent...",
    )

    await ctx.send(embeds=[embed], components=[select_menu])

@bot.component("select_torrent")
async def on_torrent_select(ctx: interactions.CommandContext, selected_option: interactions.SelectOption):
    index = int(selected_option[0])
    top_five = search_results[ctx.author.id]
    torrent_link = top_five[index]['link'] 
    magnet_link = get_magnet_link_from_torrent_link(torrent_link)
    add_torrent_to_seedr(magnet_link)
    await ctx.send("Torrent successfully added.")

bot.start()