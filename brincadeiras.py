import discord
from discord import File
from discord.ext import commands
import os
import asyncio
import random
from replit import db
from googleapiclient.discovery import build

#link dos memes recentes
memes_recentes = []

#0 -> seriao
#1 -> niggaigorzao
#2 -> bigfat
big_emoticons_urls = ["https://i.ibb.co/pjL2s8f/alt8.png","https://i.ibb.co/XFCfw0g/alt3.png","https://i.ibb.co/hmYCSrF/alt4.png"]

#FUNÇÕEEEEEEEEEEEEEEEEEEEEEEEEEEEES

def tratar_mencao(mencao):
   return int(str(mencao).replace("@","").replace("<","").replace(">","").replace("!",""))

def google_search(search_term, **kwargs):
  apikey = os.getenv("GKEY")
  cse = os.getenv("GID")
  service = build("customsearch", "v1", developerKey=apikey)
  res = service.cse().list(q=search_term, cx=cse, **kwargs).execute()
  #print(res)
  return res

class Brincadeiras(commands.Cog):
  client = commands.Bot(command_prefix="+")

  #COMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANDOS
  @client.command(brief="Manda um bom dia aleatório")
  async def bomdia(self, ctx):
    links=["https://i.ibb.co/g3GRS9q/image.png","https://i.ibb.co/dD0f46C/image.png","https://i.ibb.co/TL3j6WM/image.png","https://i.ibb.co/5T3Ww3F/image.png","https://i.ibb.co/SP8XSxs/image.png","https://i.ibb.co/pKDtSMJ/3-EA081-D0-F8-B5-41-D4-953-E-BDB20-EB11603.jpg","https://i.pinimg.com/originals/d6/d2/42/d6d24260f480a1f9d4370a3d7b4af93f.jpg","https://i.pinimg.com/originals/f2/08/47/f208471fc4c71faa4f96f8085c7ceb25.jpg"]

    e = discord.Embed()
    e.set_image(url=random.choice(links))
    await ctx.send(embed = e)

  @client.command(brief="Miado no canal de voz.", description="Você precisa estar em um canal de voz para utilizar este comando.")
  async def peu(ctx: commands.Context):
    channel = ctx.message.author.voice.channel

    if channel:
      await ctx.send(f"Miau :3 - \"{channel}\"")
    else:
      await ctx.send("Você não está em um canal de voz")

    global vc
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio('meow.mp3'))
    await asyncio.sleep(3)
    await vc.disconnect()

  @client.command(brief="Manda um meme de um termo.",description="Uso do comando: +meme \"plavra para pesquisar\"", aliases=["m","memes"])
  async def meme(self, ctx, *, arg1):
    g = google_search("meme "+str(arg1).replace("\"", ""), searchType="image")
    items = g["items"]
    index = random.randint(0,len(items)-1)

    if len(memes_recentes) >= 4:
      memes_recentes.pop(0)

    #tentativas de pegar um meme diferente
    i = 0

    while items[index]["link"] in memes_recentes:
      index = random.randint(0,len(items)-1)
      i+=1
      if 1 >= 10:
        break

    e = discord.Embed(title=items[index]["title"], description=f"Resultados: {len(items)}")
    e.set_image(url=items[index]["link"])

    memes_recentes.append(items[index]["link"])

    #await ctx.send(f"Resultados: {len(items)}")
    msg = await ctx.send(embed=e)
    await msg.add_reaction("💖")
    await msg.add_reaction("💔")

  @client.command(brief="Toca ou manda um gif do meme El muchacho!", description="Se você estiver em um canal de voz, o bot mandará um gif e tocará a música, se você não estiver em um canal ele mandará um vídeo da música no chat.")
  async def ojostristes(self, ctx, arg1=None):
    is_voice = True
    channel = None

    try:
      channel = ctx.message.author.voice.channel
    except:
      print("Cmd[Ojostristes] -> não estava em voice channel")
      is_voice = False

    txt_channel = ctx.message.channel
    aut = ctx.message.author.mention

    if is_voice:
      await ctx.send(f"El muchaco ಡ ﹏ ಡ")
      global vc
      vc = await channel.connect()
      link = "https://i.ibb.co/Jrn8GWV/sad-cat-song.gif"
      e = discord.Embed(title="EL MUCHACHO DE LOS OJOS TRISTES")
      e.set_image(url=link)
      await ctx.send(embed=e)
      vc.play(discord.FFmpegPCMAudio('ojostristes.mp3'))
      await asyncio.sleep(35)
      await vc.disconnect()
    else:
      f = open(r"sad-cat-song.mp4",'rb')
      await txt_channel.send(file=File(f),content=f"{aut} EL MUCHACHO DE LOS OJOS TRISTES")

  @client.command(brief="Toca a música 'Alôôô galera de Cowboy'", description="Para usar esse comando, é necessário que você esteja em um canal de voz.", aliases=['alogalera','alogaleradecowboy'])
  async def alo(self, ctx, modo=None):
    channel = None
    try:
      channel = ctx.message.author.voice.channel
    except:
      pass
    
  # if modo == 
    if channel != None:
      await ctx.send(f"ALOOOO [...] :3 - \"{channel}\"")
      global vc
      vc = await channel.connect()
      vc.play(discord.FFmpegPCMAudio('alo.mp3'))
      await asyncio.sleep(13)
      await vc.disconnect()
    else:
      #await ctx.send("Você não está em um canal de voz")
      e = discord.Embed(title="Alooooo?")
      e.set_image(url="https://i.ibb.co/9cnXKqy/cowboy-Alo.png")
      await ctx.send(embed=e)


  @client.command(brief="Chama um usuário de JojoFag", description="Uso do comando: +jojofag @usuario que é um jojofag.")
  async def jojofag(self, ctx, membro):
    t = tratar_mencao(membro)
    nome = ctx.guild.get_member(t).name

    mention = ctx.message.author.mention

    embed = discord.Embed(
      title="🥳 "+nome+" é agora um JojoFag 🥰",
      color=0xff5e00,
      description=mention+" condenou "+membro+" como um novo JojoFag. Sem bullying pessoal, nesse servidor respeitamos a diversidade! :3",
    )

    embed.set_thumbnail(url='https://i.ibb.co/BtJYcv5/jojofag.jpg')

    mensagem = await ctx.send(embed=embed)

  @client.command(brief="A mimir.. zzzzz", description="Manda uma mensagem de 'a mimir' e se você estiver em um canal de voz, toca um aúdio 'a mimir'.")
  async def mimir(self, ctx):
    mention = ctx.message.author.mention
    nome = ctx.message.author.name

    embed = discord.Embed(
      title="😴 "+nome+" está a mimir 🥱",
      color=0xff5e00,
      description=mention+" está com soninho, vamos dormir galerinha!",
    )

    embed.set_thumbnail(url='https://i.ibb.co/tBG4C98/image.png')

    mensagem = await ctx.send(embed=embed)

    channel = None

    try:
      channel = ctx.message.author.voice.channel
    except:
      pass

    if channel != None:
      await ctx.send(f"mimindo no canal \"{channel}\"")
      global vc
      vc = await channel.connect()
      vc.play(discord.FFmpegPCMAudio('a-mimir.mp3'))
      await asyncio.sleep(4)
      await vc.disconnect()

  @client.command(brief="'Já dizia Aristóteles...'",description="Escreve uma frase aleatória.")
  async def aristoteles(self, ctx):
    frases = ['Nunca diga nunca!', 'Você nunca saberá se és capaz se nunca tentar, ai tu tentas e vês que não é capaz mesmo.', 'Bora minerar galera.', 'Nunca desista de algo que você começou, desista antes de começar.', 'R.I.P Perolinha, Assassino: Reiziz', 'Suicidio é a opção :D']
    await ctx.send(random.choice(frases))

    #print(text_channel_list)

  @client.command(brief="Brincadeira do quinto ano...", description="Não tenho nem como te explicar esse comando...")
  async def ei(self, ctx):
    await ctx.send('Eu disse ei não disse olha! kk')


  @client.command(brief="Se você me xingar, eu xingo de volta!")
  async def puta(self, ctx):
    pl = ctx.message.author.mention
    await ctx.send(pl+' Puta é você, seu merda :3')

  @client.command(brief="Chama um usuário de gostoso(a)", description="Uso do comando: +gostoso @usuário")
  async def gostoso(self, ctx, arg1):
    lista=["😳","🥰","🤩","🥵","😍"]
    pl = ctx.message.author.mention
    await ctx.send(pl+" está chamando "+arg1+" de gostoso(a) "+ random.choice(lista))

  @client.command(brief="seriao", description="seriao")
  async def seriao(self, ctx):
    e = discord.Embed()
    e.set_image(url=big_emoticons_urls[0])
    await ctx.send(embed = e)

  @client.command(brief="niggaigorzao", description="niggaigorzao")
  async def niggaigorzao(self, ctx):
    e = discord.Embed()
    e.set_image(url=big_emoticons_urls[1])
    await ctx.send(embed = e)

  @client.command(brief="bigfat", description="bigfat")
  async def bigfat(self, ctx):
    e = discord.Embed()
    e.set_image(url=big_emoticons_urls[2])
    await ctx.send(embed = e)