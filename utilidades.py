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

#voice client
vc = None

#permitir comandos especiais sobre a casa
casa_automatica = False

#lista de jogadores online no server de MC
familia = []

#discord.opus.load_opus("./libopus.so.0.8.0")

def set_global(at, msgid):
  global msg_id
  msg_id = msgid
  global msg_user
  msg_user = at

def db_user(nick, id):
  return f"[{nick}]{id}"

def get_channel_id(self, nome):
  text_channel_list = []
  text_channel_ids = []
  for guild in self.client.guilds:
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

async def mensagem(self, canal, txt):
  c = get_channel_id(canal)
  await self.client.get_channel(c).send(txt)

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

class Utilidades(commands.Cog):
  client = commands.Bot(command_prefix="+")

  def __init__(self, bot):
    self.client = bot
    global client
    client = bot

  @client.event
  async def on_message_delete(self, message):
    if message.author.id != self.client.user.id:
      await message.channel.send(f"uma mensagem de {message.author.mention} foi apagada por...? 👀")

  @client.event
  async def on_command_error(ctx, error):
    x = str(error)
    if "You are on cooldown" in x:
      index = x.find("in")+2
      await ctx.send(f"{ctx.message.author.mention} calma! Você está em cooldown para este comando. Tente novamente em {x[index:]}")


  @client.event
  async def on_message(self,message):
    #se a mensagem não for na dm
    if not message.channel.type == discord.ChannelType.private:
      if message.author.id != self.client.user.id:
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

      await self.client.process_commands(message)


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

  @client.event
  async def on_ready(self):
    await self.client.change_presence(activity=discord.Game(name="Criado por Reinaldo Assis"))
    print(self.client.user.name)
    if not "jogadores" in db:
      db["jogadores"] = ['ReizizII','JoJoke','ordeph','carollis',"rbneto"] 
      print("setei os jogadores")
    
    global familia
    familia = await get_jogadores_online()

    #x = db_user("Reiziz",'263433841887150091')
    #print(x)
    #print(db[x])

  @commands.command(brief="Mostra os status do servidor de MC (online/offline).")
  async def server(ctx):
    status = await get_status_servidor()
    mes = "> Status do servidor?\n"+"O servidor está "+status
    await ctx.send(mes)

  @commands.command(brief="Comando ainda em desenvolvimento...")
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
    


  @commands.command(pass_context=True, brief="Comando inútil, apenas ferramenta de teste para o desenvolvedor - Rei.")
  async def teste(self, ctx):
    await ctx.send("teste!")
    #await print(self.client.get_channel(6))
    await self.client.get_channel(get_channel_id("bots")).send("outro teste!")

  @commands.command(brief="Mostra os jogadores online no servidor de MC.")
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

  @commands.command(brief="Minerar para ganhar pontos de servidor.", description="")
  async def minerar(ctx):
    pass

  @commands.command()
  async def del_db(ctx):
    if ctx.message.author.id == 263433841887150091:
      for k in db.keys():
        del db[f"{k}"]
        await ctx.send(f"Key {k} foi deletada")
    else:
      await ctx.send("Você não tem permissão para usar esse comando...")  
  @commands.command()
  async def del_user(ctx, user):
    if ctx.message.author.id == 263433841887150091:
      t = ctx.guild.get_member(tratar_mencao(user))
      user = db_user(t.name, t.id)
      del db[f"{user}"]
      await ctx.send(f"Key {user} foi deletada")
    else:
      await ctx.send("Você não tem permissão para usar esse comando...")  
  @commands.command()
  async def set_db(ctx, *args):
    print(args[1])


  @commands.command(brief="Criar ou visualiza seu perfil no servidor", pass_context=True)
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
  @commands.command(brief="Você pode dar reputação a outro membro")
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

  @commands.command()
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

  @commands.command()
  async def limpar(self, ctx):
    print("limpando mensagens")
    msgs = await ctx.channel.history(limit=10).flatten()
    i = 0
    for msg in msgs:
      if msg.author.id == self.client.user.id:
        i+=1
        await msg.delete()
    await ctx.send(f"{i} mensagens limpadas")

  @commands.command(brief="Mostra os 5 usuários com mais reputação.")
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