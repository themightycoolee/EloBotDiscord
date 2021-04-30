import discord
from discord.ext import commands
import os
from replit import db
from keep_alive import keep_alive
import checks
import fonctions

client = discord.Client()
bot = commands.Bot("$")

# Format database : {pseudo, elo main, elo trial, classement_main, classement_elo}

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def hello(ctx, *args):
  message = ctx.message
  retour = 'Hello '
  print(message)
  print(message.content)
  print(message.author.id)
  print(message.guild.roles)
  if message.mentions:
    print(message.mentions)
    retour += message.mentions[0].name
  retour += ' !'
  await message.channel.send(retour)

@bot.command()
async def register(ctx, *args):
  retour = ""
  if len(args)==0:
    retour = "Command use: $register [name]"
  elif str(ctx.author.id) not in db.keys():
    db[str(ctx.author.id)] = [args[0],1000,1000,0,0,0,0,0,0]
    retour = "Successfully registered as " + db[str(ctx.author.id)][0] + " !"
  else:
    name = db[str(ctx.author.id)][0]
    retour = "Already registered as " + name + " !"
  await ctx.send(retour)

@bot.command()
async def unregister(ctx):
  if str(ctx.author.id) in db.keys():
    del db[str(ctx.author.id)]
    await ctx.send("Successfully unregistered")
  else:
    await ctx.send("You are not registered !")

@bot.command()
async def challenge(ctx, *args):
  retour = ""
  print(args)
  print(len(ctx.message.mentions[:]))
  if len(args)!=3 or len(ctx.message.mentions)!=1:
    retour = "Command use: $challenge [main/trial] [@adversaire] [V/D]"
  else:
    if args[0].lower()!='main' and args[0].lower()!='trial':
      retour = "Argument 1: main ou trial uniquement"
    elif str(ctx.message.mentions[0].id) not in db.keys():
      retour = "Argument 1: adversaire non enregistré / introuvable"
    elif str(ctx.author.id) not in db.keys():
      retour = "Vous n'êtes pas enregistré"
    elif args[2].upper()!='V' and args[2].upper()!='D':
      retour = "Argument 2: V ou D uniquement"
    else:
      embed = fonctions.calcul_elo(str(ctx.author.id), str(ctx.message.mentions[0].id), args[0].lower(), args[2].upper())
      await ctx.send(embed=embed)
      return
  await ctx.send(retour)

@bot.command()
async def elo(ctx):
  if str(ctx.author.id) not in db.keys():
    await ctx.send("You are not registered !")
  else:
    await ctx.send(embed=fonctions.send_elo(str(ctx.author.id)))

@bot.command()
@commands.has_role("☯ Hakaï Tenshi")
async def match(ctx, *args):
  retour = ""
  # print(args)
  # print(len(ctx.message.mentions[:]))
  if len(args)!=5 or len(ctx.message.mentions)!=2:
    retour = "Command use: $match [@adversaire 1] [nombre de manches gagnées pour 1] [@adversaire 2] [nombre de manches gagnées pour 2] [type = main/trial]"
  else:
    if args[4].lower()!='main' and args[4].lower()!='trial':
      retour = "Argument 5: 'main' ou 'trial' uniquement"
    elif str(ctx.message.mentions[0].id) not in db.keys():
      retour = "Argument 1: adversaire non enregistré / introuvable"
    elif str(ctx.message.mentions[1].id) not in db.keys():
      retour = "Argument 3: adversaire non enregistré / introuvable"
    elif args[1].isnumeric() == False:
      retour = "Argument 2: uniquement des chiffres"
    elif args[3].isnumeric() == False:
      retour = "Argument 4: uniquement des chiffres"
    else:
      if int(args[1])>int(args[3]):
        embed = fonctions.match_elo(str(ctx.message.mentions[0].id), str(ctx.message.mentions[1].id), args[4].lower())
      else:
        embed = fonctions.match_elo(str(ctx.message.mentions[1].id), str(ctx.message.mentions[0].id),args[4].lower())
      if args[4].lower()=='main':
        fonctions.update_classement_main()
      else:
        fonctions.update_classement_trial()
      await ctx.send(embed=embed)
      return
  await ctx.send(retour)
  return

@bot.command()
@commands.has_role("☯ Hakaï Tenshi")
async def generate_csv(ctx, *args):
  nom_fichier = fonctions.generate_csv() # TODO auto classement selon type main/trial
  embed=discord.Embed(title="Votre fichier", url="https://EloBotDiscord.themightycoolee.repl.co/get/" + nom_fichier, color=0xffff00)
  await ctx.send(embed=embed)
  return

@bot.command()
@commands.has_role("☯ Hakaï Tenshi")
async def set_elo(ctx, *args):
  if len(args)!=3:
    await ctx.send("Command use: $set_elo [@user] [type: main/trial] [valeur]")
    return
  else:
    if str(ctx.message.mentions[0].id) not in db.keys():
      await ctx.send("Argument 1: adversaire non enregistré / introuvable")
      return
    elif args[1].lower()!='main' and args[1].lower()!='trial':
      await ctx.send("Argument 2: 'main' ou 'trial' uniquement")
      return
    elif args[2].isnumeric() == False:
      await ctx.send("Argument 3: uniquement des chiffres")
      return
    else:
      data = db[str(ctx.message.mentions[0].id)][:]
      if args[1].lower()=='main':
        elo = 1
      else: elo = 2
      data[elo] = int(args[2])
      db[str(ctx.message.mentions[0].id)] = data
      await ctx.send("Utilisateur {} désomais à {} sur l'elo ".format(data[0], data[elo]) + args[1].lower())
      return

@bot.command()
@commands.has_role("☯ Hakaï Tenshi")
async def admin_register(ctx, *args):
  if len(args)!=2:
    await ctx.send("Command use: $admin_register [@user] [pseudo]")
    return
  else:
    if str(ctx.message.mentions[0].id) in db.keys():
      await ctx.send("Argument 1: adversaire déjà enregistré en tant que " + db[str(ctx.message.mentions[0].id)][0])
      return
    else:
      db[str(ctx.message.mentions[0].id)] = [args[1],1000,1000,0,0,0,0,0,0]
      await ctx.send("Successfully registered as " + db[str(ctx.message.mentions[0].id)][0] + " !")
      return

@bot.command()
async def classements(ctx):
  fonctions.update_classement_main()
  await ctx.send(embed=fonctions.print_top(ctx, "main"))
  fonctions.update_classement_trial()
  await ctx.send(embed=fonctions.print_top(ctx, "trial"))
  return


# Global checks for each command
@bot.check
def is_not_user(ctx):
  return ctx.author.id != bot.user.id

keep_alive()
bot.run(os.getenv('TOKEN')) # token in secrets (.env)

'''
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
      return

    if message.content.startswith('$register'):
      return
    
    if message.content.startswith('$fight'):
      return
    
    if message.content.startswith('$annuler'):
      return
    
    if message.content.startswith('$hello'):
      retour = 'Hello '
      print(message)
      print(message.content)
      print(message.author.id)
      if message.mentions:
        print(message.mentions)
        retour += message.mentions[0].name
        retour += ' !'
      await message.channel.send(retour)

client.run(os.getenv('TOKEN'))
'''