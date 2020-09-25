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

def db_user(nick, id):
  return f"[{nick}]{id}"

def xingamento_aleatorio():
  lista = ['Vai se lascar','Você é um @bado', 'Eww tosco', 'Foda-se', 'Quem? Pergutou?']
  return random.choice(lista)

async def mostrar_perfil(ctx):
  user = ctx.message.author
  #informação sobre o user [no db]
  u = db[db_user(user.name,user.id)]

  e = discord.Embed(title=f"Perfil de {u['nome']}",description="Status:\n"
              f"- Energia: {u['energia']}\n"
              f"- Razos: {u['coins']}\n")
  e.set_thumbnail(url=user.avatar_url)
  await ctx.message.channel.send(embed=e)

@client.event
async def on_message_delete(message):
  await message.channel.send(f"uma mensagem de {message.author.mention} foi apagada por...? 👀")

@client.event
async def on_reaction_add(reaction, user):
  msg = reaction.message
  channel = msg.channel
  #CRIAÇÃO DE PERFIL
  if user == msg_user and msg_id == msg.id:
    if reaction.emoji == "❌":

      await msg.channel.send(xingamento_aleatorio())

    elif reaction.emoji == "👌":
      database_id = db_user(user.name,user.id)

      db[database_id] = {
        "id":user.id,
        "coins":100,
        "energia":100,
        "nome":user.name
      }

      if database_id in db:
        await channel.send(f"{user.mention} você se registrou com sucesso!")

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

@client.command(brief="Manda um bom dia aleatório")
async def bomdia(ctx):
  links=["https://i.ibb.co/g3GRS9q/image.png","https://i.ibb.co/dD0f46C/image.png","https://i.ibb.co/TL3j6WM/image.png","https://i.ibb.co/5T3Ww3F/image.png","https://i.ibb.co/SP8XSxs/image.png"]

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

@client.command(brief="Manda um meme de um termo.",description="Uso do comando: +meme \"plavra para pesquisar\"")
async def meme(ctx, arg1):
  g = google_search("meme "+str(arg1).replace("\"", ""), searchType="image")
  print("=========================")
  items = g["items"]
  index = random.randint(0,len(items)-1)

  e = discord.Embed(title=items[index]["title"], description=f"Resultados: {len(items)}")
  e.set_image(url=items[index]["link"])

  print(len(items))

  #await ctx.send(f"Resultados: {len(items)}")
  msg = await ctx.send(embed=e)
  await msg.add_reaction("💖")
  await msg.add_reaction("💔")

@client.command(brief="Toca ou manda um gif do meme El muchacho!", description="Se você estiver em um canal de voz, o bot mandará um gif e tocará a música, se você não estiver em um canal ele mandará um vídeo da música no chat.")
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

@client.command(brief="Toca a música 'Alôôô galera de Cowboy'", description="Para usar esse comando, é necessário que você esteja em um canal de voz.")
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


@client.command(brief="Chama um usuário de JojoFag", description="Uso do comando: +jojofag @usuario que é um jojofag.")
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

@client.command(brief="A mimir.. zzzzz", description="Manda uma mensagem de 'a mimir' e se você estiver em um canal de voz, toca um aúdio 'a mimir'.")
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

@client.command(brief="'Já dizia Aristóteles...'",description="Escreve uma frase aleatória.")
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

@client.command(brief="Brincadeira do quinto ano...", description="Não tenho nem como te explicar esse comando...")
async def ei(ctx):
  await ctx.send('Eu disse ei não disse olha! kk')


@client.command(brief="Se você me xingar, eu xingo de volta!")
async def puta(ctx):
  pl = ctx.message.author.mention
  await ctx.send(pl+' Puta é você, seu merda :3')

@client.command(brief="Chama um usuário de gostoso(a)", description="Uso do comando: +gostoso @usuário")
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

@client.command(brief="Mostra os status do servidor de MC (online/offline).")
async def server(ctx):
  url = 'https://caudaderaposa.aternos.me'
  r = requests.get(url, allow_redirects=True)
  soup = BeautifulSoup(r.content, 'lxml')
  element = str(soup.find_all(class_='status-label')[0])
  status = element[element.find('>')+1:element.find('</')]
  mes = "> Status do servidor?\n"+"O servidor está "+status
  await ctx.send(mes)

@client.command(brief="Comando ainda em desenvolvimento...")
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
  

@client.command(pass_context=True, brief="Comando inútil, apenas ferramenta de teste para o desenvolvedor - Rei.")
async def teste(ctx):
  await ctx.send("teste!")
  #await print(client.get_channel(6))
  await client.get_channel(get_channel_id("bots")).send("outro teste!")

@client.command(brief="Mostra os jogadores online no servidor de MC.")
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

@client.command(brief="Minerar para ganhar pontos de servidor.", description="")
async def minerar(ctx):
  pass

@client.command()
async def del_db(ctx):
  if ctx.message.author.id == 263433841887150091:
    for k in db.keys():
      del db[f"{k}"]
      await ctx.send(f"Key {k} foi deletada")
  else:
    await ctx.send("Você não tem permissão para usar esse comando...")  

@client.command(brief="Criar ou visualiza seu perfil no servidor")
async def perfil(ctx):
  author = ctx.message.author.mention
  name = ctx.message.author.name
  user = db_user(name,ctx.message.author.id)

  if not user in db:
    print(f"{author} usou o comando '+perfil', mas não possui uma conta'")

    e = discord.Embed(title=f"{name} não possui uma conta!", description="Selecione uma opção.\n"
                         "- Criar uma conta 👌\n"
                         "- Cancelar ❌",
    color=0xff5e00)

    await ctx.send(f"{author} usou o comando '+perfil', mas não possui uma conta")

    msg = await ctx.send(embed=e)

    await msg.add_reaction("👌")
    await msg.add_reaction("❌")

    global msg_id
    msg_id = msg.id
    global msg_user
    msg_user = ctx.message.author

  else:
    await mostrar_perfil(ctx)

client.loop.create_task(entrou())
keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
