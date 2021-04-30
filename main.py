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
    db[str(ctx.author.id)] = [args[0],1000,1000,0,0]
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
@commands.has_permissions(administrator=True)
async def match(ctx, *args):
  return

@bot.command()
@commands.has_permissions(administrator=True)
async def generate_csv(ctx, *args):
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