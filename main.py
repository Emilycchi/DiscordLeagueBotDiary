import asyncio
import discord
import requests
import gspread
import os
import json
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3
from datetime import timedelta, datetime
import pandas as pd
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_TOKEN = os.getenv('RIOT_TOKEN')
with open('soloqdiary.json', 'r') as file:
    gspread_credentials = json.load(file)
GSPREAD_CREDENTIALS = gspread_credentials
gc = gspread.service_account_from_dict(GSPREAD_CREDENTIALS)


intents = discord.Intents.all()


bot = commands.Bot(command_prefix=".", intents=intents)


@bot.command()
async def account(ctx):
    await ctx.send('Please type in your League ID, example: Emycchi#EUW')
    user_id = ctx.author.id

    def check(m):
        return m.author == ctx.author

    try:
        answer = await bot.wait_for('message', timeout=90.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Timed out")
        return
    else:
        if answer.content == "stop":
            await ctx.send("stopped")
            return
        else:
            connection = sqlite3.connect("test.db")
            cursor = connection.cursor()
            riot_id = answer.content.split('#')
            puuid_request = requests.get(
                f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{str(riot_id[0]).replace(' ', '%20')}/{riot_id[1]}?api_key={RIOT_TOKEN}")
            puuid = puuid_request.json()['puuid']
            cursor.execute(f"SELECT user_id, puuid FROM main WHERE user_id = {user_id}")

            result = cursor.fetchone()

            if result is None:
                cursor.execute(f"INSERT INTO main (user_id, puuid) VALUES ({user_id}, '{puuid}')")
                await ctx.send("Thank you for traveling with Deutsche Bahn")
            else:
                cursor.execute(f"UPDATE main SET puuid = '{puuid}' WHERE user_id = {user_id}")
                await ctx.send("Updated your League ID for you o7")
            connection.commit()
            connection.close()


@bot.command()
async def addquestion(ctx):
    await ctx.send('Please type in the question you would like to add, every user has a max of 10 question at the same time. If you want to see your current questions, type "info"')
    user_id = ctx.author.id

    def check(m):
        return m.author == ctx.author

    try:
        answer = await bot.wait_for('message', timeout=90.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timed out')
        return
    else:
        if answer.content == "stop":
            await ctx.send('stopped')
            return
        elif answer.content == "info":
            db = sqlite3.connect('test.db')
            cursor = db.cursor()
            cursor.execute(
                f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
            results = cursor.fetchone()
            columns = ['question1', 'question2', 'question3', 'question4', 'question5',
                       'question6', 'question7', 'question8', 'question9', 'question10']
            non_empty_columns = {columns[i]: value for i, value in enumerate(results) if value and value != ''}
            await ctx.send(list(non_empty_columns.values()))
            db.commit()
            db.close()
        else:
            db = sqlite3.connect('test.db')
            cursor = db.cursor()
            cursor.execute(
                f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
            results = cursor.fetchone()
            columns = ['question1', 'question2', 'question3', 'question4', 'question5',
                       'question6', 'question7', 'question8', 'question9', 'question10']
            first_empty_column = None
            for i, value in enumerate(results):
                if value is None or value == '':  # Check for NULL or empty string
                    first_empty_column = columns[i]
                    break
            if first_empty_column is None:
                await ctx.send('Error, probably no empty questions left, please try to delete some questions')
                db.commit()
                db.close()
                return
            else:
                cursor.execute(f"UPDATE main SET {first_empty_column} = '{answer.content}' WHERE user_id = {user_id}")
                await ctx.send('Successfully added the question')
                db.commit()
                db.close()


@bot.command()
async def delquestion(ctx):
    user_id = ctx.author.id
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute(
        f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
    results = cursor.fetchone()
    columns = ['question1', 'question2', 'question3', 'question4', 'question5',
               'question6', 'question7', 'question8', 'question9', 'question10']
    non_empty_columns = {columns[i]: value for i, value in enumerate(results) if value and value != ''}
    non_empty_columns_list = list(non_empty_columns.values())
    non_empty_columns_list_keys = list(non_empty_columns.keys())
    await ctx.send(f"Your current questions are:{non_empty_columns_list} please type the number of the question you would like to delete. Please keep in mind that deleting a question will delete the answers associated with that question")

    def check(m):
        return m.author == ctx.author
    try:
        deletequestion = await bot.wait_for('message', timeout=90.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timed out')
        db.commit()
        db.close()
        return
    else:
        if deletequestion.content.isnumeric():
            if 1 <= int(deletequestion.content) <= len(non_empty_columns_list):
                delquest = non_empty_columns_list[int(deletequestion.content)-1]
                delcol = non_empty_columns_list_keys[int(deletequestion.content)-1]
                delanswer = "answer"+str(results.index(delquest)+1)
                cursor.execute(f"UPDATE main SET {delcol} = NULL WHERE user_id = {user_id}")
                cursor.execute(f"UPDATE answers SET {delanswer} = NULL WHERE user_id = {user_id}")
                await ctx.send(f"Deleted the question: {delquest}")
                db.commit()
                db.close()
            else:
                await ctx.send('Please try again next time with a valid number')
                db.commit()
                db.close()
                return
        else:
            await ctx.send('Please try a number next time :)')
            db.commit()
            db.close()
            return


@bot.command()
async def game(ctx):
    user_id = ctx.author.id

    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT puuid FROM main WHERE user_id = {user_id}")
    puuid = cursor.fetchone()
    cursor.execute(
        f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
    results = cursor.fetchone()
    columns = ['question1', 'question2', 'question3', 'question4', 'question5',
               'question6', 'question7', 'question8', 'question9', 'question10']
    get_user_questions = {columns[i]: value for i, value in enumerate(results)}
    user_questions = ['How many games did you play today?']
    user_questions.extend((list(get_user_questions.values())))
    timenow = datetime.now()
    answers = [str(user_id), timenow.strftime("%Y-%m-%d %H:%M:%S")]
    match_id_full = requests.get(
        f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={RIOT_TOKEN}")
    match_id = match_id_full.json()[0].split('_')[1]
    await ctx.send(f"Game: https://www.leagueofgraphs.com/match/euw/{match_id}#matchDataTable")
    answers_msg = discord.Embed(title="Answers", colour=discord.Color.blue())
    q = 0
    for i in user_questions:
        if i is None:
            answers.append(None)
            q = q + 1
        else:
            await ctx.send(i)

            def check(m):
                return m.author == ctx.author

            try:
                msg = await bot.wait_for('message', timeout=90.0, check=check)

            except asyncio.TimeoutError:
                await ctx.send("Timed out")
                return

            else:
                if msg.content == "stop":
                    await ctx.send("stopped")
                    return
                else:
                    answers_msg.add_field(name=user_questions[q], value=msg.content, inline=False)
                    answers.append(msg.content)
                    q = q+1

    await ctx.send(embed=answers_msg)
    cursor.execute("INSERT INTO answers (user_id, date, gamenumber, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(answers))
    db.commit()
    db.close()


@bot.command()
async def createnewdoc(ctx):
    await ctx.send('Please type in your email address to share the google sheet to(preferably a gmail address). This will take a moment')
    user_name = ctx.author.name
    user_id = ctx.author.id

    def check(m):
        return m.author == ctx.author

    try:
        user_email = await bot.wait_for('message', timeout=90.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Timed out')
        return
    else:
        if user_email.content == "stop":
            await ctx.send('stopped')
            return
        else:
            db = sqlite3.connect('test.db')
            cursor = db.cursor()
            cursor.execute(f"SELECT docurl FROM main WHERE user_id = {user_id}")
            savedurl = cursor.fetchone()
            if savedurl[0] is None:
                sh = gc.create(user_name + ' stats')
                sh.share(user_email.content, perm_type='user', role='writer')
                wks = sh.sheet1
                wks.update_title('Your document')
                docurl = sh.url
                cursor.execute(f"UPDATE main SET docurl = '{docurl}' WHERE user_id = {user_id}")
                await ctx.send(
                    'Created your document, check your email to find it, try .doc to get your link! You can now use the command createsheet to add to your personal document')
            else:
                await ctx.send("You seem to already have a document, try .doc to get your link, if you encountered an unexpected issue, please contact my mom")
            db.commit()
            db.close()


@bot.command()
async def doc(ctx):
    user_id = ctx.author.id
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT docurl FROM main WHERE user_id = {user_id}")
    docurl = cursor.fetchone()
    await ctx.send(f"Your document link: {docurl[0]}")
    db.commit()
    db.close()


@bot.command()
async def createsheet(ctx):
    user_id = ctx.author.id
    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    headerq = ['Date', '#Game that day']
    db = sqlite3.connect('test.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT docurl FROM main WHERE user_id = {user_id}")
    docurl = cursor.fetchone()
    try:
        sh = gc.open_by_url(docurl[0])
    except gspread.exceptions.NoValidUrlKeyFound:
        await ctx.send("You don't seem to have a document")
        return
    else:
        wks = sh.add_worksheet(timenow, rows=500, cols=15)

        cursor.execute(
            f"SELECT date, gamenumber, answer1, answer2, answer3, answer4, answer5, answer6, answer7, answer8, answer9, answer10 from answers where user_id = {user_id} ORDER BY date DESC")
        results = cursor.fetchmany(100)
        df = pd.DataFrame(results)
        df_no_null_columns = df.dropna(axis=1, how="all")

        cursor.execute(
            f"SELECT question1, question2, question3, question4, question5, question6, question7, question8, question9, question10 FROM main WHERE user_id = {user_id}")
        questions = list(cursor.fetchone())
        columns = ['question1', 'question2', 'question3', 'question4', 'question5',
                   'question6', 'question7', 'question8', 'question9', 'question10']
        get_user_questions = {columns[i]: value for i, value in enumerate(questions)}
        headerq.extend((list(get_user_questions.values())))
        wks.update([headerq] + df_no_null_columns.values.tolist())
        await ctx.send('Successfully created your sheet')
        db.commit()
        db.close()


bot.run(DISCORD_TOKEN)
