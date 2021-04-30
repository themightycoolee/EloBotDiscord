from replit import db
import discord
import csv
from datetime import datetime

def calcul_elo(attaquant:str, defie:str, type_defi:str, resultat:str):
  data_att = db[attaquant]
  data_def = db[defie]
  if type_defi=='main':
    elo = 1
  else: elo = 2

  diff = data_def[elo] - data_att[elo]
  if abs(diff) <= 200:
    if resultat=="V": points = 20
    else: points = -20
  elif diff<0:
    if resultat=="V": points = 5
    else: points = -30
  elif diff<300:
    if resultat=="V": points = 30
    else: points = -15
  else:
    if resultat=="V": points = 40
    else: points = -10
  
  data_att[elo] = max(0, int(data_att[elo])+points)
  data_def[elo] = max(0, int(data_def[elo])-points)
  db[attaquant] = data_att
  db[defie] = data_def
  if(points)>0:
    embed=discord.Embed(title="Challenge", description="résultat", color=0x00ff00)
    embed.add_field(name=data_att[0], value=str(data_att[elo])+" (+"+str(points)+ ")", inline=True)
    embed.add_field(name=data_def[0], value=str(data_def[elo])+" ("+str(-points)+ ")", inline=True)
  else:
    embed=discord.Embed(title="Challenge", description="résultat", color=0xff0000)
    embed.add_field(name=data_att[0], value=str(data_att[elo])+" ("+str(points)+ ")", inline=True)
    embed.add_field(name=data_def[0], value=str(data_def[elo])+" (+"+str(-points)+ ")", inline=True)
  return embed

def match_elo(gagnant:str, perdant:str, type_defi:str):
  gag = db[gagnant][:]
  per = db[perdant][:]
  points = 5
  if type_defi.lower()=='trial':
    elo = 2
  else: elo = 1

  diff = gag[elo] - per[elo]
  if abs(diff)<=200:
    points = 20
  if diff<-300:
    points = 40
  elif diff<-200:
    points = 30
  elif abs(diff)<=200:
    points = 20
  elif diff<300:
    points = 15
  else:
    points = 10
  
  gag[elo] = max(0, int(gag[elo]) + points)
  gag[elo+4] = int(gag[elo+4]) + 1
  gag[elo+6] = int(gag[elo+6]) + 1
  per[elo] = max(0, int(per[elo]) - points)
  per[elo+6] = int(per[elo+6]) + 1
  db[gagnant] = gag
  db[perdant] = per

  embed=discord.Embed(title="Challenge", description="résultat", color=0x00ff00)
  embed.add_field(name=gag[0], value=str(gag[elo])+" (+"+str(points)+ ")", inline=True)
  embed.add_field(name=per[0], value=str(per[elo])+" ("+str(-points)+ ")", inline=True)
  return embed

def send_elo(key:str):
  data = db[key]
  embed=discord.Embed(title=data[0], color=0x00ff00)
  embed.add_field(name="main", value=data[1], inline=True)
  embed.add_field(name="trial", value=data[2], inline=True)
  return embed

def print_top(ctx, type_classement = "main", nbr = 10):
  membres = [db[i][:] for i in db.keys()]
  if type_classement.lower() == "trial":
    elo = 2
    membres = sorted(membres, key=lambda x: x[4])
  else:
    elo = 1
    membres = sorted(membres, key=lambda x: x[3])
  embed=discord.Embed(title="Classement elo " + type_classement.lower(), description="Classement des " + str(min(len(membres),nbr)) + " meilleurs joueurs", color=0xffff00)
  embed.add_field(name="Pseudo", value = "\u200B", inline=True)
  embed.add_field(name="Elo", value="\u200B", inline=True)
  embed.add_field(name="Rang", value="\u200B", inline=True)
  for i in range(min(len(membres),nbr)):
    embed.add_field(name="\u200B", value=membres[i][0], inline=True)
    embed.add_field(name="\u200B", value=membres[i][elo], inline=True)
    embed.add_field(name="\u200B", value=membres[i][elo+2], inline=True)
  return embed

def update_classement_main():
  membres = [[i]+db[i][:] for i in db.keys()]
  membres_main = sorted(membres, key=lambda x: x[2], reverse=True)
  membres_main[0][4] = 1
  for i in range(len(membres)):
    if membres_main[max(0,i-1)][2] == membres_main[i][2]:
      membres_main[i][4] = membres_main[max(0,i-1)][4]
    else:
      membres_main[i][4] = i+1
    db[membres_main[i][0]] = membres_main[i][1:]
  # print(membres)
  return

def update_classement_trial():
  membres = [[i]+db[i][:] for i in db.keys()]
  membres_trial = sorted(membres, key=lambda x: x[3], reverse=True)
  membres_trial[0][5] = 1
  for i in range(len(membres)):
    if membres_trial[max(0,i-1)][3] == membres_trial[i][3]:
      membres_trial[i][5] = membres_trial[max(0,i-1)][5]
    else:
      membres_trial[i][5] = i+1
    db[membres_trial[i][0]] = membres_trial[i][1:]
  # print(membres)
  return

def generate_csv():
  now = datetime.now() # current date and time

  name = "out_"+now.strftime("%m%d%Y%H%M%S")+".csv"
  membres = [[i]+db[i][:] for i in db.keys()]
  writer = csv.writer(open("files/"+name, 'w'))
  writer.writerow(['id','name', 'elo_main', 'elo_trial', 'rank_main','rank_trial','nbr_victoires_main','nbr_victoires_trial','nbr_matchs_main','nbr_matchs_trial'])
  for item in membres:
    writer.writerow(item)
  return name