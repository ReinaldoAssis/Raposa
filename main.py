import discord
from discord import File
import requests
from discord.ext import commands
import os
from bs4 import BeautifulSoup
import asyncio
import random
from keep_alive import keep_alive
from replit import db
from googleapiclient.discovery import build

msg_id = None
msg_user = None

#voice client
vc = None

_jogadores = []

#discord.opus.load_opus("./libopus.so.0.8.0")

client = commands.Bot(command_prefix = "+")

#@client.event
#async def on_message(message):
#  if message.author == client.user:
#    return

  
  #if str(message.content).find('@')

def google_search(search_term, **kwargs):
    apikey = os.getenv("GKEY")
    cse = os.getenv("GID")
    service = build("customsearch", "v1", developerKey=apikey)
    res = service.cse().list(q=search_term, cx=cse, **kwargs).execute()
    #print(res)
    return res

async def mensagem(canal, txt):
  await client.get_channel(get_channel_id(canal)).send(txt)

async def get_jogadores_online():
  url = 'https://caudaderaposa.aternos.me'
  r = requests.get(url, allow_redirects=True)
  soup = BeautifulSoup(r.content, 'lxml')
  
  jogadores:list = []

  players = soup.find_all("div", class_="player-image")
  for jogador in players: 
    jogador = str(jogador)
    nick = jogador[jogador.find("title=")+7:jogador.find("\"",134)-9]
    jogadores.append(nick)

  return jogadores

@client.command()
async def bomdia(ctx):
  links=["https://i.ibb.co/g3GRS9q/image.png","https://i.ibb.co/dD0f46C/image.png","https://i.ibb.co/TL3j6WM/image.png","https://i.ibb.co/5T3Ww3F/image.png","https://i.ibb.co/SP8XSxs/image.png"]

  e = discord.Embed()
  e.set_image(url=random.choice(links))
  await ctx.send(embed = e)

@client.command()
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

@client.command()
async def meme(ctx, arg1):
  g = google_search("meme "+str(arg1).replace("\"", ""), searchType="image")
  print("=========================")
  items = g["items"]
  index = random.randint(0,len(items)-1)

  e = discord.Embed(title=items[index]["title"], description=f"Resultados: {len(items)}")
  e.set_image(url=items[index]["link"])

  print(len(items))

  #await ctx.send(f"Resultados: {len(items)}")
  await ctx.send(embed=e)

@client.command()
async def ojostristes(ctx, arg1=None):
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

@client.command()
async def alo(ctx):
  channel = ctx.message.author.voice.channel

  if channel != "":
    await ctx.send(f"ALOOOO [...] :3 - \"{channel}\"")
    global vc
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio('alo.mp3'))
    await asyncio.sleep(13)
    await vc.disconnect()
  else:
    await ctx.send("Você não está em um canal de voz")


@client.command()
async def jojofag(ctx, arg1):
  t = int(str(arg1).replace("@","").replace("<","").replace(">","").replace("!",""))
  print(t)
  nome = ctx.guild.get_member(t).name

  mention = ctx.message.author.mention

  embed = discord.Embed(
    title="🥳 "+nome+" é agora um JojoFag 🥰",
    color=0xff5e00,
    description=mention+" condenou "+arg1+" como um novo JojoFag. Sem bullying pessoal, nesse servidor respeitamos a diversidade! :3",
  )

  embed.set_thumbnail(url='https://i.ibb.co/BtJYcv5/jojofag.jpg')

  mensagem = await ctx.send(embed=embed)

@client.command()
async def mimir(ctx):
  mention = ctx.message.author.mention
  nome = ctx.message.author.name

  embed = discord.Embed(
    title="😴 "+nome+" está a mimir 🥱",
    color=0xff5e00,
    description=mention+" está com soninho, vamos dormir galerinha!",
  )

  embed.set_thumbnail(url='https://i.ibb.co/tBG4C98/image.png')

  mensagem = await ctx.send(embed=embed)

  channel = ctx.message.author.voice.channel

  if channel:
    await ctx.send(f"mimindo no canal \"{channel}\"")
    global vc
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio('a-mimir.mp3'))
    await asyncio.sleep(4)
    await vc.disconnect()

@client.command()
async def aristoteles(ctx):
  frases = ['Nunca diga nunca!', 'Você nunca saberá se és capaz se nunca tentar, ai tu tentas e vês que não é capaz mesmo.', 'Bora minerar galera.', 'Nunca desista de algo que você começou, desista antes de começar.', 'R.I.P Perolinha, Assassino: Reiziz', 'Suicidio é a opção :D']
  await ctx.send(random.choice(frases))

def get_channel_id(nome):
  text_channel_list = []
  text_channel_ids = []
  for guild in client.guilds:
    for channel in guild.text_channels:
      text_channel_ids.append(channel.id)
      text_channel_list.append(channel.name)

  #print(text_channel_list)
  return text_channel_ids[text_channel_list.index(nome)]

@client.command()
async def ei(ctx):
  await ctx.send('Eu disse ei não disse olha! kk')


@client.command()
async def puta(ctx):
  pl = ctx.message.author.mention
  await ctx.send(pl+' Puta é você, seu merda :3')

@client.command()
async def gostoso(ctx, arg1):
  lista=["😳","🥰","🤩","🥵","😍"]
  pl = ctx.message.author.mention
  await ctx.send(pl+" está chamando "+arg1+" de gostoso(a) "+ random.choice(lista))

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="Criado por Reinaldo Assis"))
  print(client.user.name)
  if not "jogadores" in db:
    db["jogadores"] = ['ReizizII','JoJoke','ordeph','carollis'] 
    print("setei os jogadores")

@client.command()
async def server(ctx):
  url = 'https://caudaderaposa.aternos.me'
  r = requests.get(url, allow_redirects=True)
  soup = BeautifulSoup(r.content, 'lxml')
  element = str(soup.find_all(class_='status-label')[0])
  status = element[element.find('>')+1:element.find('</')]
  mes = "> Status do servidor?\n"+"O servidor está "+status
  await ctx.send(mes)

@client.command()
async def painel(ctx):
  embed = discord.Embed(
    title="Painel de controle",
    color=0xff5e00,
    description="- Status = 🎮\n"
                "- Iniciar servidor = 🚀\n"
                "- Reiniciar servidor = 🛠\n"
  )

  mensagem = await ctx.send(embed=embed)
  await mensagem.add_reaction("🎮")
  await mensagem.add_reaction("🚀")
  await mensagem.add_reaction("🛠")

  global msg_id
  msg_id = mensagem.id
  global msg_user
  msg_user = mensagem.author
  
#Alguém entrou ou saiu do server
async def entrou():
  await asyncio.sleep(2)
  global _jogadores
  while True:
    #*************************
    players:list = await get_jogadores_online()
    
    #print(players)
    #print("------")
    #print(_jogadores)

    if len(players) < len(_jogadores):
      for j in players:
        _jogadores.remove(j)

      for resto in _jogadores:
        print(resto+" saiu")
        await mensagem("geral", f"Jogador {resto} saiu do servidor!")
    
    elif len(players) > len(_jogadores):
      for j in _jogadores:
        players.remove(j)

      for resto in players:
        print(f"{resto} entrou")
        await mensagem("geral", f"Jogador {resto} entrou no servidor!")

    _jogadores = players
    await asyncio.sleep(2)
  

@client.command(pass_context=True)
async def teste(ctx):
  await ctx.send("teste!")
  #await print(client.get_channel(6))
  await client.get_channel(get_channel_id("bots")).send("outro teste!")

@client.command()
async def jogadores(ctx):
  jogadores = ""

  lista = await get_jogadores_online()

  for j in lista:
    jogadores += ("- "+j+"\n")

  embed = discord.Embed(
    title="Jogadores online",
    color=0xff5e00,
    description=jogadores
  )

  mensagem = await ctx.send(embed=embed)

@client.event
async def on_reaction_add(reaction, user):
  msg = reaction.message
  channel = msg.channel
  await client.send_message(channel, "teste")

client.loop.create_task(entrou())
keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
