from discord.ext import commands, menus
from discord.ext.commands.cooldowns import BucketType
import discord, random, asuna_api, math, chardet, mystbin, alexflipnote, os, typing, aioimgur, time, asyncio, contextlib, async_cleverbot
import utils
from discord.ext.menus.views import ViewMenuPages

class Extra(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    bot.loop.create_task(self.__ainit__())

  async def __ainit__(self):
    await self.bot.wait_until_ready()

    self.cleverbot = async_cleverbot.Cleverbot(os.environ["cleverbot_key"], session = self.bot.session)

  @commands.command(brief="a way to look up minecraft usernames",help="using the official minecraft api, looking up minecraft information has never been easier(tis only gives minecraft account history relating to name changes)")
  async def mchistory(self, ctx, *, args = None):
    
    if args is None:
      await ctx.send("Please pick a minecraft user.")

    if args:
      asuna = asuna_api.Client(self.bot.session)
      minecraft_info=await asuna.mc_user(args)
      embed=discord.Embed(title=f"Minecraft Username: {args}",color=random.randint(0, 16777215))
      embed.set_footer(text = f"Minecraft UUID: {minecraft_info.uuid}")
      embed.add_field(name="Orginal Name:", value = minecraft_info.name)

      for y, x in enumerate(minecraft_info.from_dict):

        if y > 0:
          embed.add_field(name = f"Username:\n{x.name}",value=f"Date and Time Changed:\n{discord.utils.format_dt(x.changed_at, style = 'd')} \n{discord.utils.format_dt(x.changed_at, style = 'T')}")
        
      embed.set_author(name=f"Requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
      await ctx.send(embed=embed)

  @mchistory.error
  async def mchistory_error(self, ctx, error):
    await ctx.send(error)

  async def cog_command_error(self, ctx, error):
    if ctx.command or not ctx.command.has_error_handler():
      await ctx.send(error)
      import traceback
      traceback.print_exc()

  class RandomHistoryEmbed(menus.ListPageSource):
    async def format_page(self, menu, item):
      embed=discord.Embed(title = "Random History:", description = f"{item}", color = random.randint(0, 16777215))
      embed.set_footer(text = "powered by Sp46's api: \nhistory.geist.ga")
      return embed

  @commands.command(help="This gives random history using Sp46's api.",brief="a command that uses SP46's api's random history command to give you random history responses")
  async def random_history(self,ctx,*,args=None):
    if args is None:
      args = 1
    asuna = asuna_api.Client(self.bot.session)
    response = await asuna.random_history(args)

    pag = commands.Paginator()
    for x in response:
      pag.add_line(f":earth_africa: {x}")
    
    pages = [page.strip("`") for page in pag.pages]

    menu = ViewMenuPages(self.RandomHistoryEmbed(pages, per_page=1),delete_message_after=True)
    await menu.start(ctx)

  @random_history.error
  async def random_history_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief="gives you the digits of pi that Python knows")
  async def pi(self, ctx):
    await ctx.send(math.pi)

  @commands.command(brief="reverses text")
  async def reverse(self,ctx,*,args=None):
    if args:

      reversed = args[::-1]

      await ctx.send(content = f"{reversed}", allowed_mentions=discord.AllowedMentions.none())
      
    if args is None:
      await ctx.send("Try sending actual to reverse")

  @commands.command(brief="Oh no Dad Jokes, AHHHHHH!")
  async def dadjoke(self,ctx):
    response=await self.bot.session.get("https://icanhazdadjoke.com/",headers={"Accept": "application/json"})
    joke=await response.json()
    embed = discord.Embed(title="Random Dad Joke:",color=random.randint(0, 16777215))
    embed.set_author(name=f"Dad Joke Requested by {ctx.author}",icon_url=(ctx.author.display_avatar.url))
    embed.add_field(name="Dad Joke:",value=joke["joke"])
    embed.set_footer(text=f"View here:\n https://icanhazdadjoke.com/j/{joke['id']}")
    await ctx.send(embed=embed)

  @commands.command(brief="gets a panel from the xkcd comic",aliases=["astrojoke","astro_joke"])
  async def xkcd(self,ctx):
    response=await self.bot.session.get("https://xkcd.com/info.0.json")
    info=await response.json()

    num = random.randint(1,info["num"])
    comic = await self.bot.session.get(f"https://xkcd.com/{num}/info.0.json")
    data=await comic.json()
    title = data["title"]
    embed=discord.Embed(title=f"Title: {title}",color=random.randint(0, 16777215))
    embed.set_image(url=data["img"])
    embed.set_footer(text=f"Made on {data['month']}/{data['day']}/{data['year']}")
    await ctx.send(embed=embed)

  @commands.command(brief = "Gets a cat based on http status code", aliases = ["http"])
  async def http_cat(self, ctx, * , args : typing.Optional[typing.Union[int,str]] = None ):
    if args is None: code = "404"

    if args:
      if isinstance(args,int):
        if args > 99 and args < 600: code = args
        else: code = "404"
      
      else:
        await ctx.send("Not a valid arg using 404")
        code = "404"
    
    response = await self.bot.session.get(f"https://http.cat/{code}")
    if response.status:
      image = f"https://http.cat/{code}.jpg"

    embed=discord.Embed(title=f"Status Code: {code}",color=random.randint(0, 16777215))
    embed.set_author(name=f"Requested by {ctx.author}",icon_url=ctx.author.display_avatar.url)
    embed.set_image(url=image)
    embed.set_footer(text="Powered by http.cat")
    await ctx.send(embed=embed)

  @commands.command(help="Gives advice from JDJG api.",aliases=["ad"])
  async def advice(self,ctx):
    r=await self.bot.session.get('https://jdjgapi.nom.mu/api/advice')
    res = await r.json()
    embed = discord.Embed(title = "Here is some advice for you!",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this helped!")
    embed.set_footer(text="Powered by JDJG Api!")
    try:
      await ctx.send(embed=embed)
    except:
      await ctx.send("was too long...")

  @commands.command(help="gives random compliment")
  async def compliment(self, ctx):
    r=await self.bot.session.get('https://jdjgapi.nom.mu/api/compliment')
    res = await r.json()
    embed = discord.Embed(title = "Here is a compliment:",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this helped your day!")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives an insult")
  async def insult(self,ctx):
    r=await self.bot.session.get('https://jdjgapi.nom.mu/api/insult')
    res = await r.json()
    embed = discord.Embed(title = "Here is a insult:",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "Hopefully this Helped?")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives response to slur")
  async def noslur(self,ctx):
    r=await self.bot.session.get('https://jdjgapi.nom.mu/api/noslur')
    res = await r.json()
    embed = discord.Embed(title = "Don't Swear",color=random.randint(0, 16777215))
    embed.add_field(name = f"{res['text']}", value = "WHY MUST YOU SWEAR?")
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="gives random message",aliases=["rm"])
  async def random_message(self,ctx):
    r=await self.bot.session.get('https://jdjgapi.nom.mu/api/randomMessage')
    res = await r.json()
    embed = discord.Embed(title = "Random Message:",color=random.randint(0, 16777215))
    embed.add_field(name="Here:",value=res["text"])
    embed.set_footer(text="Powered by JDJG Api!")
    await ctx.send(embed=embed)

  @commands.command(help="a command to talk to Google TTS",brief="using the power of the GTTS module you can now do tts")
  async def tts(self, ctx, * ,args = None):
    if args:
      await ctx.send("if you have a lot of text it may take a bit")
      tts_file = await utils.google_tts(args)
      await ctx.send(file=tts_file)
    
    if ctx.message.attachments:
      for x in ctx.message.attachments:
        file=await x.read()
        if file:

          encoding=chardet.detect(file)["encoding"]
          if encoding:
            text = file.decode(encoding)
            
            await ctx.send("if you have a lot of text it may take a bit")
            tts_file = await utils.google_tts(text)
            await ctx.send(file=tts_file)

          if encoding is None:
            await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439")
        if not file:
          await ctx.send("this doesn't contain any bytes.")
          

    if args is None and not ctx.message.attachments:
      await ctx.send("You didn't specify any text.")

  @commands.command()
  async def tts_test(self, ctx, *, args = None):
    args = args or "Test"

    time_before=time.perf_counter() 
    file1=await utils.google_tts(args)
    time_after=time.perf_counter()

    await ctx.send(content=f"Time to do this: {int((time_after - time_before)*1000)} MS",file=file1)

  @commands.command(brief="Uses google translate to make text to latin in a voice mode :D",aliases=["latin_tts"])
  async def tts_latin(self, ctx, *, args = None):
    if not args:

      await ctx.send("you can't have No text to say")

    else:
      
      time_before=time.perf_counter() 
      file=await utils.latin_google_tts(args)
      time_after=time.perf_counter()

      await ctx.send(content=f"Time to do this: {int((time_after - time_before)*1000)} MS",file=file)

  @commands.command(help="learn about a secret custom xbox controller",brief="this will give you a message of JDJG's classic wanted xbox design.")
  async def secret_controller(self,ctx):
    embed = discord.Embed(color=random.randint(0, 16777215))
    embed.set_author(name="Secret Xbox Image:")
    embed.add_field(name="Body:",value="Zest Orange")
    embed.add_field(name="Back:",value="Zest Orange")
    embed.add_field(name="Bumpers:",value="Zest Orange")
    embed.add_field(name="Triggers:",value="Zest Orange")
    embed.add_field(name="D-pad:",value="Electric Green")
    embed.add_field(name="Thumbsticks:",value="Electric Green")
    embed.add_field(name="ABXY:",value="Colors on Black")
    embed.add_field(name="View & Menu:",value="White on Black")
    embed.add_field(name="Engraving(not suggested):",value="JDJG Inc.")
    embed.add_field(name="Disclaimer:",value="I do not work at microsoft,or suggest you buy this I just wanted a place to represent a controller that I designed a while back.")
    embed.set_image(url="https://i.imgur.com/QCh4M2W.png")
    embed.set_footer(text="This is Xbox's custom controller design that I picked for myself.\nXbox is owned by Microsoft. I don't own the image")
    await ctx.send(embed=embed)

  @commands.command(brief="repeats what you say",help="a command that repeats what you say the orginal message is deleted")
  async def say(self, ctx, *, args = None):
    if args is None:
      args = "You didn't give us any text to use."

    args = discord.utils.escape_markdown(args, as_needed = False,ignore_links = False)
    try:
      await ctx.message.delete()

    except discord.errors.Forbidden:
      pass

    await ctx.send(args,allowed_mentions=discord.AllowedMentions.none())

  @commands.command(brief = "does say but more powerful with the optional option of a channel to say in")
  async def say2(self, ctx, channel : typing.Optional[typing.Union[discord.TextChannel, discord.Thread]] = None, *, args = None):
   
    channel = channel or ctx.channel

    args = args or "You didn't give us any text to use."
    args = discord.utils.escape_markdown(args, as_needed = False,ignore_links = False)
    
    bot_member = channel.me if isinstance(channel, discord.DMChannel) else channel.guild.me
      
    if channel.permissions_for(bot_member).send_messages or not channel.id == ctx.channel.id:

      if isinstance(bot_member, discord.Member):

        author_member = await self.bot.getch_member(bot_member.guild, ctx.author.id)

        channel = channel if author_member else ctx.channel

      await channel.send(f"{args}\nMessage From {ctx.author}", allowed_mentions = discord.AllowedMentions.none())

    else:
      await ctx.send("doesn't have permissions to send in that channel.")

  @commands.command(brief="a command to backup text",help="please don't upload any private files that aren't meant to be seen")
  async def text_backup(self, ctx, *, args = None):
    if ctx.message.attachments:
      for x in ctx.message.attachments:
        file=await x.read()
        if file:
          encoding=chardet.detect(file)["encoding"]
          if encoding:
            text = file.decode(encoding)
            mystbin_client = mystbin.Client(session=self.bot.session)
            paste = await mystbin_client.post(text)
            await ctx.send(content=f"Added text file to mystbin: \n{paste.url}")
          if encoding is None:
            await ctx.send("it looks like it couldn't decode this file, if this is an issue DM JDJG Inc. Official#3439 or it wasn't a text file.")
        if not file:
          await ctx.send("this doesn't contain any bytes.")

    if args:
      await ctx.send("this is meant to backup text files and such.")

    if not args and not ctx.message.attachments:
      await ctx.send("you didn't give it any attachments.")
          
          
  @commands.group(name="apply",invoke_without_command=True)
  async def apply(self,ctx):
    await ctx.send("this command is meant to apply")

  @apply.command(brief="a command to apply for our Bloopers.",help="a command to apply for our bloopers.")
  async def bloopers(self, ctx, *, args=None):
    if args is None:
      await ctx.send("You didn't give us any info.")
    if args:
      if isinstance(ctx.message.channel, discord.TextChannel):
        await ctx.message.delete()

      for x in [708167737381486614,168422909482762240]:
        apply_user = await self.bot.getch_user(x)
      
      if (apply_user.dm_channel is None):
        await apply_user.create_dm()
      
      embed_message = discord.Embed(title=args,color=random.randint(0, 16777215),timestamp=(ctx.message.created_at))
      embed_message.set_author(name=f"Application from {ctx.author}",icon_url=ctx.author.display_avatar.url)
      embed_message.set_footer(text = f"{ctx.author.id}")
      embed_message.set_thumbnail(url="https://i.imgur.com/PfWlEd5.png")
      await apply_user.send(embed=embed_message)

  @commands.command(aliases = ["bird", "birb"])
  async def caw(self, ctx):
    alex_api = alexflipnote.Client(os.environ["alex_apikey"], session=self.bot.session)
    url=await alex_api.birb()
    await ctx.send(url)

  @commands.command(aliases = ["bark", "dogs"])
  async def dog(self, ctx):
    alex_api = alexflipnote.Client(os.environ["alex_apikey"], session=self.bot.session)
    url=await alex_api.dogs()
    await ctx.send(url)

  @commands.command(aliases = ["meow", "cats"])
  async def cat(self, ctx):
    alex_api = alexflipnote.Client(os.environ["alex_apikey"], session=self.bot.session)
    url=await alex_api.cats()
    await ctx.send(url)

  @commands.command(aliases=["joke"])
  async def jokeapi(self, ctx):
    jokeapi_grab=await self.bot.session.get("https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single")
    response_dict=await jokeapi_grab.json()
    embed=discord.Embed(title=f"{response_dict['joke']}",color=random.randint(0, 16777215))
    embed.set_author(name=f"{response_dict['category']} Joke:")
    embed.add_field(name="Language:",value=f"{response_dict['lang']}")
    embed.add_field(name=f"Joke ID:",value=f"{response_dict['id']}")
    embed.add_field(name="Type:",value=f"{response_dict['type']}")
    embed.set_footer(text=f"Joke Requested By {ctx.author} \nPowered by jokeapi.dev")
    await ctx.send(embed=embed)

  @jokeapi.error
  async def jokeapi_error(self, ctx, error):
    await ctx.send(error)

  @commands.command()
  async def cookieclicker_save(self, ctx):
    import io

    mystbin_client = mystbin.Client(session=self.bot.session)
    paste=await mystbin_client.get("https://mystb.in/ClubsFloppyElections.perl")
    s = io.StringIO()
    s.write(paste.paste_content)
    s.seek(0)
    await ctx.reply("The save editor used: https://coderpatsy.bitbucket.io/cookies/v10466/editor.html \n Warning may be a bit cursed. (because of the grandmas having madness at this level.) \n To be Used with https://orteil.dashnet.org/cookieclicker/",file=discord.File(s, filename="cookie_save.txt"))

  @commands.command()
  async def call_text(self, ctx, *, args = None):

    alex_api = alexflipnote.Client(os.environ["alex_apikey"],session=self.bot.session)

    args = args or "You called No one :("
    image=await alex_api.calling(text=args)

    imgur_client = aioimgur.ImgurClient(os.environ["imgur_id"],os.environ["imgur_secret"]) 

    imgur_url = await imgur_client.upload(await image.read())

    await ctx.send(imgur_url["link"])

  @commands.command(brief="allows you to quote a user, without pings")
  async def quote(self, ctx, *, message = None):

    message =  message or "Empty Message :("

    await ctx.send(f"> {message} \n -{ctx.message.author}",allowed_mentions=discord.AllowedMentions.none())

  @commands.command(brief = "hopefully use this to show to not laugh but instead help out and such lol")
  async def letsnot(self, ctx):
    emoji=discord.utils.get(self.bot.emojis,name="commandfail")
    await ctx.send(f"Let's not go like {emoji} instead let's try to be nice about this. \nGet a copy of this image from imgur: https://i.imgur.com/CykdOIz.png", reference = ctx.message.reference, allowed_mentions = discord.AllowedMentions.none())

  @commands.command(brief = "edits a message with a specific twist(100)% lol")
  async def edit_that(self, ctx):
    message = await ctx.send("Hello guys I am going to be edited")
    await asyncio.sleep(2)
    await message.edit(content = "hello guys I am going to be edited \u202B  Heck yeah")

  
  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "cleansup bot message's history in a channel if need be.(Doesn't cleanup other people's message history)")
  async def cleanup(self, ctx,  *,  amount : typing.Optional[int] = None):

    if isinstance(ctx.channel,discord.DMChannel):
      return await ctx.send("doesn't work in DMS, due to discord limitations about builking deletes messages(if we could we would)")

    amount = amount or 10
    if amount > 100:
      await ctx.send("max 100 messages, going to 10 messages.")

      amount = 10
      amount += 1

    if not utils.cleanup_permission(ctx):
      amount = 10

      await ctx.send("you don't have manage messages permissions nor is it a dm")
      amount += 1

    await ctx.send("attempting to delete history of commands")
    amount += 1

    messages = None
    with contextlib.suppress(discord.Forbidden, discord.HTTPException):  
      messages = await ctx.channel.purge(limit = amount , bulk = False, check = utils.Membercheck(ctx))
      
    if not messages:
      return await ctx.send("it likely errored with not having the proper manage message permissions(shouldn't happen), or any http exception happened.")
     

    page = "\n".join(f"{msg.author} ({('Bot' if msg.author.bot else 'User')}) : {msg.content}" for msg in messages)

    mystbin_client = mystbin.Client(session=self.bot.session)
    try:
      paste = await mystbin_client.post(page)
    except:
      return await ctx.send("failed posting back of messages")

    await ctx.author.send(content=f"Added text file to mystbin: \n{paste.url}")

  @commands.cooldown(1, 40, BucketType.user)
  @commands.command(brief = "allows you to review recent embeds", aliases = ["embedhistory", "embed_history"])
  async def closest_embed(self, ctx):
    embed_history = await ctx.channel.history(limit = 50).flatten()
    embeds = [embed for e in embed_history for embed in e.embeds][:10]
    menu = ViewMenuPages(utils.QuickMenu(embeds, per_page = 1),delete_message_after=True)

    if not embeds:
      return await ctx.send("No embeds found :D")

    await ctx.send("Sending you the previous 10 embeds sent in 50 messages if under 10 well the amount that exists, if none well you get none.")
    await menu.start(ctx)

  @commands.command(brief = "takes two numbers and does a cool command")
  async def radical(self, ctx, *numbers : typing.Union[int, str]):
    
    if not numbers:
      return await ctx.send("sorry boss you didn't give us any numbers to use.")

    numbers=sorted(list(filter(lambda x: isinstance(x, int), numbers)))

    if not numbers:
      return await ctx.send("Not enough numbers")

    elif len(numbers) < 2:
      num = 1
      
    elif len(numbers) > 1:
      num = numbers[0]
    
    root = numbers[-1]

    embed = discord.Embed(title = "The Radical Function Has Been Completed!",color=random.randint(0, 16777215))

    embed.set_footer(text = f"{ctx.author} | {ctx.author.id}")
    embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")
    embed.add_field(name = f"Formula: {num}√ {root}", value = f"Result: {int(root**(1/num))}")

    await ctx.send(embed = embed)

  @commands.command(brief = "takes two numbers and does a cool command")
  async def power(self, ctx, *numbers : typing.Union[int, str]):
    
    if not numbers:
      return await ctx.send("sorry boss you didn't give us any numbers to use.")

    numbers=sorted(list(filter(lambda x: isinstance(x, int), numbers)))

    if not numbers:
      return await ctx.send("Not enough numbers")

    elif len(numbers) < 2:
      root = 1
      
    elif len(numbers) > 1:
      root = numbers[0]
    
    num = numbers[-1]

    embed = discord.Embed(title = f"Result of the function",color=random.randint(0, 16777215))
    embed.add_field(name = f"Formula: {num} ^ {root}", value = f"Result: {(num**root)}")
    embed.set_footer(text = f"{ctx.author.id}")
    embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")
    await ctx.send(embed = embed)
  
  @commands.max_concurrency(number = 1, per = BucketType.channel, wait = True)
  @commands.max_concurrency(number = 1, per = BucketType.user, wait = False)
  @commands.command(brief = "a way to talk to cleverbot", aliases = ["chatbot"])
  async def cleverbot(self, ctx, *, args = None):
    
    args = args or "Hello CleverBot"

    await ctx.reply("we firstly apoligize if chatbot offends you or hurts your feelings(like actually does so not as a joke or trying to cause drama thing.) use chat*stop, chat*close, or chat*cancel to stop the chatbot link. (powered by Travita api and the wrapper async_cleverbot). if someone else runs a different session, they will need to wait")

    res = await self.cleverbot.ask(args, ctx.author.id)
    await ctx.reply(res.text, mention_author=False, allowed_mentions=discord.AllowedMentions.none())

    while True:
      try:
        msg = await self.bot.wait_for("message", check=lambda msg: msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id, timeout=30)
      except asyncio.TimeoutError:
        await ctx.send(f"Shut it off as {ctx.author} didn't respond :(")
        break
      
      else:
        if msg.content.lower() in ["chat*stop", "chat*close", "chat*cancel"]:
          await ctx.send("shut off chatbot.")
          break
        else:
          async with ctx.typing():
            res = await self.cleverbot.ask(msg.content, msg.author.id)
            await msg.reply(res.text, mention_author=False, allowed_mentions=discord.AllowedMentions.none())

    return

  @cleverbot.error
  async def cleverbot_error(self, ctx, error):
    await ctx.send(error)
    import traceback
    traceback.print_exc()

  @commands.command(brief = "a command to create a voice channel")
  async def voice_create(self, ctx, *, args = None):
   
    if isinstance(ctx.channel, discord.DMChannel):
      return await ctx.send("you can't make a voice channel in a DM")

    if not args:
      return await ctx.send("You need to give me some text to use.")

    if not utils.create_channel_permission(ctx):
      return await ctx.send("you don't have permission to use that.")

    if not ctx.me.guild_permissions.manage_channels:
      return await ctx.send("I can't make a voice channel! If you want this to work you need to give manage channel permissions :(")

    channel = await ctx.guild.create_voice_channel(args)

    invite = "N/A"
    if channel.permissions_for(ctx.me).create_instant_invite:
      invite = await channel.create_invite()

    await ctx.send(f"join the channel at {channel.mention} \n Invite to join: {invite}")

  @commands.command(brief  = "a command to create a text channel")
  async def channel_create(self, ctx, *, args = None):

    if isinstance(ctx.channel, discord.DMChannel):
      return await ctx.send("you can't make a text channel in a DM") 
    
    if not args:
      return await ctx.send("You need to give me some text to use.")

    if not utils.create_channel_permission(ctx):
      return await ctx.send("you don't have permission to use that.")

    if not ctx.me.guild_permissions.manage_channels:
      return await ctx.send("I can't make a text channel! If you want this to work you need to give manage channel permissions :(")    

    channel = await ctx.guild.create_text_channel(args)

    invite = "N/A"
    if channel.permissions_for(ctx.me).create_instant_invite:
      invite = await channel.create_invite()

    await ctx.send(f"join the channel at {channel.mention} \n Invite to join: {invite}")

  @commands.command(brief = "makes a discord profile link")
  async def profile_link(self, ctx, user: utils.BetterUserconverter = None):
    user = user or ctx.author

    await ctx.send(f"The profile for {user} is https://discord.com/users/{user.id}")

  @commands.command(bried = "tells you the current time with discord's speacil time converter", name = "time")
  async def _time(self, ctx):
    
    embed = discord.Embed(title="Current Time :",description=f"{discord.utils.format_dt(ctx.message.created_at, style = 'd')}{discord.utils.format_dt(ctx.message.created_at, style = 'T')}",color=random.randint(0, 16777215))

    embed.set_footer(text = f"Requested By {ctx.author}")
    await ctx.send(embed = embed)

  @commands.command(brief = "takes three values lol")
  async def arithmetic(self, ctx, *numbers : typing.Union[int, str]):
    
    if not numbers:
      return await ctx.send("sorry boss you didn't give us any numbers to use.")

    numbers = sorted(list(filter(lambda x: isinstance(x, int), numbers)))

    if not numbers:
      return await ctx.send("Not enough numbers, you need 3 values ")

    elif len(numbers) < 3:
      return await ctx.send("Not enough numbers, you need 3 values (the orginal number, how many times it per time you run it, and how many times it goes)")
      
    elif len(numbers) > 2:
      
      orginal = numbers[0]
      number_each_time = numbers[1]
      times_ran = numbers[-1]

      embed = discord.Embed(title = f"Result of the function",color = random.randint(0, 16777215))

      embed.add_field(name=f"Formula: {orginal} + {number_each_time} * ( {times_ran} - 1 )",value = f"Result: {orginal+number_each_time*(times_ran-1)}")

      embed.set_footer(text = f"{ctx.author.id}")
      embed.set_thumbnail(url="https://i.imgur.com/E7GIyu6.png")
    
    await ctx.send(embed=embed)

  @commands.command(brief = "a command that uses discord.py's query_members to cache users(only use this if you want to cache yourself, you can't cache others to with this)")
  async def cache_member(self, ctx):
    if isinstance(ctx.channel, discord.DMChannel):
      return await ctx.send("querying members doesn't work in dms.")

    view = utils.BasicButtons(ctx)
   
    msg = await ctx.send("Do you agree to cache yourself in the temp guild members list(this is something in discord.py where it caches members, but it's gone after bot startup, it will also not be stored anywhere else as that would be bad if it did, it will only be used to bring api calls down)?", view = view)

    await view.wait()

    if view.value is None:
      await ctx.reply("You let me time out :(")
      return await msg.delete()
    
    if view.value:
      if not ctx.guild.get_member(ctx.author.id):
        await msg.delete()

        msg = await ctx.send("attempting to cache you with query_members in discord.py(this way you don't need to make api calls if you wish.) If you don't trust us you can always use the support command to get info about this or jdjgsummon, and I'll gladly so you this what I say.")
        
        try:
          await ctx.guild.query_members(cache = True, limit = 5, user_ids = [ctx.author.id]) 

        except Exception as e:
          await asyncio.sleep(1)
          return await msg.edit(f"failed caching members with query_members in discord.py with error {e}")

        await asyncio.sleep(1)
        await msg.edit("successfully cached you")

      else:
        await msg.delete()
        return await ctx.send("You are already cached :D, you don't need to cache again")

    if not view.value:
      await msg.delete()
      await ctx.reply("You didn't agree to being cached.")

  @cache_member.error
  async def cache_member_error(self, ctx, error):
    await ctx.send(error)

  @commands.command(brief = "says nook nook and shows an image")
  async def pingu(self, ctx):
    embed = discord.Embed(description = f"nook nook", color = random.randint(0, 16777215))
    embed.set_image(url = "https://i.imgur.com/Z6NURwi.gif")
    embed.set_author(name = f"Pingu has been summoned by {ctx.author}:", icon_url = ctx.author.display_avatar.url)
    await ctx.send("nook nook", embed = embed)


  @commands.cooldown(1, 30, BucketType.user)
  @commands.command(brief = "generates a random sm64 color code", aliases = ["generate_cc", "generate_colorcode", "g_cc", "cc_generator"])
  async def generate_color_code(self, ctx):

    embed = discord.Embed(description = f"```{utils.cc_generate()}```", color = random.randint(0, 16777215))

    embed.set_author(name = f"{ctx.author} Generated A Random CC:", icon_url = ctx.author.display_avatar.url)

    embed.set_footer(text = "Generated a random sm64 color code.")
    await ctx.send(embed = embed)

  
  @commands.command(brief = "brings up two sites of logical fallicies")
  async def fallacies_list(self, ctx):
    await ctx.send(f"https://www.futurelearn.com/info/courses/logical-and-critical-thinking/0/steps/9131 \nhttps://yourlogicalfallacyis.com/")

  @commands.command(brief = "based on pog bot's nitro command")
  async def nitro(self, ctx):

    embed = discord.Embed(title = "You've been gifted a subscription!", description = "You've been gifted Nitro for **1 month!**\nExpires in **24 hours**", color = 3092790)
    embed.set_thumbnail(url = "https://i.imgur.com/w9aiD6F.png")
    
    view = utils.nitroButtons(timeout = 180.0)
    view.message = await ctx.send(embed = embed, view = view)

  @commands.cooldown(1, 60, BucketType.user)
  @commands.cooldown(1, 60, BucketType.channel)
  @commands.command(brief = "gets the first message in a channel", aliases = ["first_message"])
  async def firstmsg(self, ctx, channel : typing.Optional [typing.Union[discord.TextChannel, discord.Thread, discord.DMChannel, discord.GroupChannel, discord.User, discord.Member]] = None) :

    channel = channel or ctx.channel
    print(type(channel))

    messages = await channel.history(limit = 1, oldest_first = True).flatten()

    if not messages:
      return await ctx.send("Couldn't find the first message or any message :shrug: Not sure why")

    embed = discord.Embed(color = random.randint(0, 16777215), timestamp = ctx.message.created_at, description = f"Click on [message link]({messages[0].jump_url}) to see the channel listed below's first message")
    embed.add_field(name = f"Channel:", value = f"{channel.mention}")
    embed.set_author(name = f"Message Author: {messages[0].author}", icon_url = f"{messages[0].author.display_avatar.url}")

    await ctx.send(content = "here's the first message in that channel", embed = embed)
      

def setup(bot):
  bot.add_cog(Extra(bot))
