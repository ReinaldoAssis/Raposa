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

#último estado do servidor
last_estado_servidor = "Offline"

#link dos memes recentes
memes_recentes = []

#voice client
vc = None

#lista de jogadores online no server de MC
familia = []

#discord.opus.load_opus("./libopus.so.0.8.0")

client = commands.Bot(command_prefix = "+")

def set_global(at, msgid):
  global msg_id
  msg_id = msgid
  global msg_user
  msg_user = at

def get_channel_id(nome):
  text_channel_list = []
  text_channel_ids = []
  for guild in client.guilds:
    for channel in guild.text_channels:
      text_channel_ids.append(channel.id)
      text_channel_list.append(channel.name)
  
  return text_channel_ids[text_channel_list.index(nome)]

async def get_status_servidor():
  url = 'https://caudaderaposa.aternos.me'
  r = requests.get(url, allow_redirects=True)
  soup = BeautifulSoup(r.content, 'lxml')
  element = str(soup.find_all(class_='status-label')[0])
  status = element[element.find('>')+1:element.find('</')]
  return status

def checar_se_jogador(strcheck):
  strcheck = str(strcheck)
  if "[" in strcheck and "]" in strcheck:
    _id = strcheck[strcheck.find("]"):]
    print(_id)
    nick = strcheck[strcheck.find("[")+1:strcheck.find("]")]
    print(nick)

    if db_user(nick, _id) in db:
      return True
    else:
      return False

  else:
    return False  

#trata uma menção de um user e retorna apenas o seu id
def tratar_mencao(mencao):
  return int(str(mencao).replace("@","").replace("<","").replace(">","").replace("!",""))

def db_user(nick, id):
  return f"[{nick}]{id}"

def xingamento_aleatorio():
  lista = ['Vai se lascar','Você é um @bado', 'Eww tosco', 'Foda-se', 'Quem? Pergutou?']
  return random.choice(lista)

async def mostrar_perfil(ctx, target):
  user = None
  if target == None:
    user = ctx.message.author
  else:
    user = target
  #informação sobre o user [no db]
  u = db[db_user(user.name,user.id)]

  e = discord.Embed(title=f"Perfil de {u['nome']}",description="Status:\n"
              f"- Reputação: {u['reputacao']}\n"
              f"- {u['frase']}\n")
  e.set_thumbnail(url=user.avatar_url)
  await ctx.message.channel.send(embed=e)

@client.event
async def on_message_delete(message):
  if message.author.id != client.user.id:
    await message.channel.send(f"uma mensagem de {message.author.mention} foi apagada por...? 👀")

@client.event
async def on_command_error(ctx, error):
  x = str(error)
  if "You are on cooldown" in x:
    index = x.find("in")+2
    await ctx.send(f"{ctx.message.author.mention} calma! Você está em cooldown para este comando. Tente novamente em {x[index:]}")


@client.event
async def on_message(message):
  #se a mensagem não for na dm
  if not message.channel.type == discord.ChannelType.private:
    if message.author.id != client.user.id:
      u = db_user(message.author.name, message.author.id) 
      if u in db:
        data = db[u]
        if "xp" in data:
          data["xp"] += 1
        else:
          data["xp"] = 1
        db[u] = data

        if "xp" in db[u]:
          data = db[u]
          if data["xp"] >= 10:
            data["xp"] = 0
            data["reputacao"] += 1
            db[u] = data

    await client.process_commands(message)


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
        "reputacao":0,
        "frase":"Este user ainda não definiu uma frase : (",
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
  c = get_channel_id(canal)
  await client.get_channel(c).send(txt)

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

@client.command(brief="Manda um meme de um termo.",description="Uso do comando: +meme \"plavra para pesquisar\"", aliases=["m","memes"])
async def meme(ctx, *, arg1):
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

@client.command(brief="Toca a música 'Alôôô galera de Cowboy'", description="Para usar esse comando, é necessário que você esteja em um canal de voz.", aliases=['alogalera','alogaleradecowboy'])
async def alo(ctx, modo=None):
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
async def jojofag(ctx, membro):
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
async def aristoteles(ctx):
  frases = ['Nunca diga nunca!', 'Você nunca saberá se és capaz se nunca tentar, ai tu tentas e vês que não é capaz mesmo.', 'Bora minerar galera.', 'Nunca desista de algo que você começou, desista antes de começar.', 'R.I.P Perolinha, Assassino: Reiziz', 'Suicidio é a opção :D']
  await ctx.send(random.choice(frases))

  #print(text_channel_list)

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
    db["jogadores"] = ['ReizizII','JoJoke','ordeph','carollis',"rbneto"] 
    print("setei os jogadores")
  
  global familia
  familia = await get_jogadores_online()

  #x = db_user("Reiziz",'263433841887150091')
  #print(x)
  #print(db[x])

@client.command(brief="Mostra os status do servidor de MC (online/offline).")
async def server(ctx):
  status = await get_status_servidor()
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
@client.command()
async def del_user(ctx, user):
  if ctx.message.author.id == 263433841887150091:
    t = ctx.guild.get_member(tratar_mencao(user))
    user = db_user(t.name, t.id)
    del db[f"{user}"]
    await ctx.send(f"Key {user} foi deletada")
  else:
    await ctx.send("Você não tem permissão para usar esse comando...")  
@client.command()
async def set_db(ctx, *args):
  print(args[1])


@client.command(brief="Criar ou visualiza seu perfil no servidor", pass_context=True)
async def perfil(ctx, target=None):
  author = ctx.message.author.mention
  name = ctx.message.author
  user = None

  if target == None:
    user = db_user(name.name, name.id)
    print("perfil sem target")
  else:
    mencao = tratar_mencao(target)
    guild_user = ctx.guild.get_member(mencao)
    user = db_user(guild_user.name,guild_user.id)
    target = guild_user

  if not user in db:
    print(f"{author} usou o comando '+perfil', mas não possui uma conta'")

    e = discord.Embed(title=f"{name.name} não possui uma conta!", description="Selecione uma opção.\n"
                         "- Criar uma conta 👌\n"
                         "- Cancelar ❌",
    color=0xff5e00)

    print(target.id +"|"+name.id)

    if target.id == name.id:
      await ctx.send(f"{author} usou o comando '+perfil', mas não possui uma conta")
    else:
      await ctx.send(f"{author} usou o comando '+perfil', mas {target.name} não possui uma conta")

    msg = await ctx.send(embed=e)

    await msg.add_reaction("👌")
    await msg.add_reaction("❌")

    global msg_id
    msg_id = msg.id
    global msg_user
    msg_user = ctx.message.author

  else:
    await mostrar_perfil(ctx, target)

@commands.cooldown(1, 60, commands.BucketType.user)
@client.command(brief="Você pode dar reputação a outro membro")
async def reputacao(ctx, membro):
  autor = ctx.message.author
  honrado = ctx.guild.get_member(tratar_mencao(membro))
  db_id = db_user(honrado.name, honrado.id)
  data = None

  if db_id in db:
    data = db[db_id]

  print(f"Honrado:{honrado.name} | autor: {autor.name}")

  if honrado.id == autor.id:
    await ctx.send("Você não pode dar reputação para você mesmo!")
    return

  if db_id in db:

    e = discord.Embed(title=f"{autor.name} presenteou {honrado.name} com reputação")
    e.set_thumbnail(url=honrado.avatar_url)
    await ctx.send(embed=e)
    data["reputacao"] += 1
    db[db_id] = data

  else:
    await ctx.send(f"O membro {membro} ainda não possui um perfil cadastrado! (use +perfil para criar um)")

@client.command()
async def frase(ctx, *, frase):
  autor = ctx.message.author
  db_id = db_user(autor.name,autor.id)
  if db_id in db:
    data = db[db_id]
    data["frase"] = str(frase).replace("\"","")
    db[db_id] = data
    await ctx.send(f"{autor.mention} Pronto! Agora sua frase foi modificada.")
  else:
    await ctx.send("Você precisa de uma conta para setar uma frase de perfil! (use o comando +perfil para criar um)")

async def entrou():

  global last_estado_servidor

  await asyncio.sleep(4)
  global familia
  while True:
    #*************************
    players:list = await get_jogadores_online()

    server_status = await get_status_servidor()

    if server_status != last_estado_servidor:
      last_estado_servidor = server_status
      mes = "> Status do servidor?\n"+"O servidor está "+server_status
      await mensagem("geral",mes)

    #c = get_channel_id("geral")

    if len(players) > len(familia):
      
      for p in players:
        if not p in familia:
          familia.append(p)
          await mensagem("geral", f"{p} entrou no servidor!")
    
    if len(players) < len(familia):
      for f in familia:
        if not f in players:
          familia.remove(f)
          await mensagem("geral", f"{p} saiu no servidor!")
        

      
    await asyncio.sleep(2)

@client.command()
async def limpar(ctx):
  print("limpando mensagens")
  msgs = await ctx.channel.history(limit=10).flatten()
  i = 0
  for msg in msgs:
    if msg.author.id == client.user.id:
      i+=1
      await msg.delete()
  await ctx.send(f"{i} mensagens limpadas")

@client.command(brief="Mostra os 5 usuários com mais reputação.")
async def ranque(ctx):
  keys = list(db)
  users = list()

  r1 = 0
  r2 = 0
  r3 = 0
  r4 = 0
  r5 = 0

  u1 = ""
  u2 = ""
  u3 = ""
  u4 = ""
  u5 = ""

  for k in keys:
    if "[" in k:
      user = db[k]
      rp = user["reputacao"]
      if r1 < rp:
        r1 = rp
        u1 = user["nome"] 

      if rp <= r1 and r2 < rp and user["nome"] != u1:
        r2 = rp
        u2 = user["nome"]
      
      if rp <= r2 and r3 < rp and user["nome"] != u2:
        r3 = rp
        u3 = user["nome"]
      
      if rp <= r3 and r4 < rp and user["nome"] != u3:
        r4 = rp
        u4 = user["nome"]
      
      if rp <= r4 and r5 < rp and user["nome"] != u4:
        r5 = rp
        u5 = user["nome"]

  e = discord.Embed(title="Ranque Atual", description=f"1. {u1} [{r1}]\n"
                                                      f"2. {u2} [{r2}]\n"
                                                      f"3. {u3} [{r3}]\n"
                                                      f"4. {u4} [{r4}]\n"
                                                      f"5. {u5} [{r5}]\n")
  
  await ctx.send(embed=e)

client.loop.create_task(entrou())
keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))