from datetime import datetime, date, time, timedelta
import nextcord, time, datetime, random, sys, os, io, re, string, json, sqlite3, emoji
from nextcord import Interaction, Member, Emoji
from nextcord.ext import commands, tasks, application_checks
from nextcord import Member, channel, Status, ChannelType, User, Guild, VoiceState, Message, CategoryChannel, Embed, CustomActivity, TextChannel, AuditLogAction, AuditLogDiff, AuditLogEntry, VoiceChannel, Permissions
from nextcord.abc import GuildChannel
from nextcord.ext.commands import MemberConverter, Bot
from nextcord.raw_models import RawMessageUpdateEvent
from nextcord.utils import get

prefixes = ['!']
def get_prefix(client, msg):
    return commands.when_mentioned_or(*prefixes)(client, msg)

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix = get_prefix, intents = intents)
client.remove_command("help")

#'''
try:
    a = open('token.txt', 'r')
    token = a.readline()
except:
    print("Brak tokenu, proszę podać token do bota. Jest on na stronie https://discord.com/developers/applications potem należy wejść z moje aplikacje, jak nie masz to utwórz nową, potem wejść z zakładkę bot i skopiować token. Do bota tez należy włączyć wszystkie opcje w Privileged Gateway Intents")
    token = input()
    b = open("token.txt", 'a+')
    b.write(token)
    b.close()
#'''

check_ban = False
snipe_uzytkownik = ''
snipe_wiadomosc = ''

liczby = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'keycap_ten'
}

try:
    with open("konfiguracja.json") as f:
        konfig = json.load(f)
        print("Plik .json został uruchomiony poprawnie")
        conn = sqlite3.connect('lvl.db')
        cursor = conn.cursor()
        print("Baza danych jest uruchomiona")
except Exception:
    konfig = {}
    print("Plik .json nie istnieje, należy wykonać konfigurację")

def zapisz():
    with open("konfiguracja.json", 'w+') as f:
        json.dump(konfig, f, sort_keys= True, indent = 4)

def check_its_mod(member):
    try:
        mody = open("mod.txt", "r")
        lista = mody.readlines()
        for i in lista:
            if f"{str(member.id)}\n" == i:
                return True
        return False
    except:
        return False

async def check_konfig(ctx):
    try:
        with open("konfiguracja.json") as f:
            return True
    except Exception:
        print("Konfiguracja nie została wykonana")
        return False

async def wyslij_logi_komendy(ctx, akcja: str, member: nextcord.Member = None, czas: str = None):
    try:
        if konfig[str(ctx.guild.id)]["log"]: pass
        else: return
    except: return
    kanal = konfig[str(ctx.guild.id)]["log"]
    e = nextcord.Embed(color = ctx.author.color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = f"Użytkownik {ctx.author.name}#{ctx.author.discriminator} użył komendy")
    try: e.set_thumbnail(url = ctx.author.avatar.url)
    except: pass
    e.add_field(name = f"Użycie komendy lub zdarzenie", value = akcja, inline = False)
    e.add_field(name = f"Użyta przez", value = ctx.author.mention, inline = False)
    if member is not None:
        e.add_field(name = f"Użyta komenda na użytkowniku", value = member.mention, inline = False)
    if czas is not None:
        znak = czas[-1].lower()
        czas = czas.removesuffix(znak)
        match znak:
            case 's':
                czas += " sekund"
            case 'm':
                czas += " minut"
            case 'h':
                czas += " godzin"
            case 'd':
                czas += " dni"
            case _:
                return
        e.add_field(name = f"Czas działania komendy", value = czas, inline = False)
    return await client.get_channel(int(kanal)).send(embed = e)

async def konwerter_czasu(ctx, czas: str):
    znak = czas[-1].lower()
    czas = czas.removesuffix(znak)
    try: int(czas)
    except:
        await ctx.send("Błędny format czasu")
        return False
    czas = int(czas)
    match znak:
        case 's':
            return 1*czas
        case 'm':
            return 60*czas
        case 'h':
            return 60*60*czas
        case 'd':
            return 24*60*60*czas
        case _:
            await ctx.send("Błędny format czasu")
            return False

def getIntTime(time:int):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        a = now + datetime.timedelta(0,time)
        return a
    except:
        return False

async def wyslij_logi_zdarzenie(ctx, e):
    try:
        if konfig[str(ctx.id)]["log"]: pass
        else: return
    except: return
    kanal = konfig[str(ctx.id)]["log"]
    await client.get_channel(int(kanal)).send(embed = e)
    e.clear_fields()
    e.remove_author()
    return

@client.event
async def on_ready():
    print(f"{client.user.name} został zalogowany")
    await client.change_presence(status = nextcord.Status.online, activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"Jestem nowym projektem xd"))
    print("Moim prefixem każdej komendy jest \"!\", wpisz !help aby widzieć więcej komend")

@client.command()
async def konfiguracja(ctx):
    serwer = ctx.guild.id
    if str(serwer) not in konfig:
        konfig[str(serwer)] = {}
        konfig[str(serwer)]["ID Bot"] = client.user.id
        zapisz()
        return await ctx.send("Konfiguracja została wykonana pomyślnie. Trzeba zrestartować bota w celu potwierdzenia wygenerowania danych")
    else:
        return await ctx.send("Konfiguracja została wcześniej wykonana")
    
def binary_search_string(L, left, right, y): #https://ufkapano.github.io/algorytmy/lekcja12/binarne.html
    y = f"{y}\n"
    try:
        while left <= right:
            k = (left + right) // 2
            if k == 0 and y != L[k]:
                return False
            if y == L[k]:
                return True
            if y > L[k]:
                left = k+1
            else:
                right = k
        return False
    except Exception as e:
        print("Błąd w funkcji")
        print(e)
        return False

@client.command()
@commands.has_permissions(administrator = True)
async def mod(ctx, member:nextcord.Member = None):
    if member is None:
        return await ctx.send("Który użytkownik ma posiadać dostęp do bota?")
    try:
        mody = open('mod.txt', 'r')
        lista = mody.readlines()
        mody.close()
        if len(lista) != 0 and binary_search_string(lista, 0, len(lista), member.id):
            return await ctx.send("Użytkownik posiada dostęp")
        mody = open('mod.txt', 'a+')
        mody.write(f"{member.id}\n")
        mody.close()
    except:
        mody = open('mod.txt', 'a+')
        mody.write(f"{member.id}\n")
        mody.close()
    mody = open('mod.txt', 'r')
    lista = mody.readlines()
    mody.close()
    lista = sorted(lista)
    mody = open('mod.txt', 'w+')
    mody.writelines(lista)
    mody.close()
    return await ctx.send(f"Użytkownik {member.mention} został pomyślnie dodany do listy moderatorskiej")

def binary_search(L, left, right, y): #https://ufkapano.github.io/algorytmy/lekcja12/binarne.html
    y = f"{y}\n"
    while left <= right:
        k = (left+right) // 2
        if y == L[k]:
            return k
        if y > L[k]:
            left = k+1
        else:
            right = k-1
    return None

@client.command()
@commands.has_permissions(administrator = True)
async def delmod(ctx, user:nextcord.User = None):
    if user is None:
        return await ctx.send("Którego użytkownika mam usunąć z listy moderatorskiej?")
    mody = open('mod.txt', "r")
    lista = mody.readlines()
    mody.close()
    a = binary_search(lista, 0, len(lista), user.id)
    del lista[a]
    mody = open('mod.txt', 'w+')
    mody.writelines(lista)
    mody.close()
    return await ctx.send(f"Użytkownik {user.mention} został pomyślnie usunięty z listy moderatorskiej")

@client.command()
@commands.has_permissions(administrator = True)
async def listmod(ctx):
    try:
        mody = open("mod.txt", 'r')
        lista = mody.readlines()
        if lista == []:
            return await ctx.send("Brak użytkowników na liście")
        return await ctx.send(lista)
    except:
        return await ctx.send("Nie istnieje plik")

@client.command()
@commands.has_permissions(administrator = True)
async def logi(ctx):
    if await check_konfig(ctx) == True:
        konfig[str(ctx.guild.id)]["log"] = ctx.channel.id
        zapisz()
        return await ctx.send("Ten kanał będzie wyświetlał logi")

@client.command()
@commands.has_permissions(administrator = True)
async def lvl(ctx, check:bool = None):
    if await check_konfig(ctx) == True:
        try:
            if konfig[str(ctx.guild.id)]["lvl"]:
                if check is None:
                    return await ctx.send("Aby wyłączyć system lvl'i, należy wpisać komendę: !lvl False")
                elif check is False:
                    konfig[str(ctx.guild.id)]["lvl"] = False
                    zapisz()
                    return await ctx.send("System lvl'i został wyłączony")
            else:
                if check is None:
                    return await ctx.send("Aby włączyć wystem lvl'i napeży wpisać komendę: !lvl True")
                elif check is True:
                    konfig[str(ctx.guild.id)]["lvl"] = True
                    zapisz()
                    return await ctx.send("System lvl'i został włączony")
        except:
            try:
                create_table = "CREATE TABLE IF NOT EXISTS levels (ID integer PRIMARY KEY, LVL integer NOT NULL, EXP integer NOT NULL);"
                cursor.execute(create_table)
                conn.commit()
                for i in ctx.guild.members:
                    if i.bot == True:
                        continue
                    cursor.execute("INSERT INTO levels (ID, LVL, EXP) VALUES ({0.id}, 0, 0)".format(i))
                conn.commit()
                konfig[str(ctx.guild.id)]["lvl"] = True
                zapisz()
                return await ctx.send("Wszyscy użytkownicy zostali dodani do utworzonej tablicy\nAby dodać liczenie poziomu, użyj komendy: !generatelvl, jeżeli już wcześniej było robione, to można zmienić mnożnik na nowo")
            except:
                return await ctx.send("Brak resetu programu")

@client.command()
async def deletelvl(ctx):
    if await check_konfig(ctx) is True:
        def check(m:nextcord.Message):
            return m.content == 'tak' and m.channel.id == ctx.channel.id
        await ctx.send("Czy jesteś pewien aby usunąć poziomy i punkty użytkowników? Napisz \"tak\" pod tą wiadomością w ciągu 15 sekund")
        try: msg = await client.wait_for('message',timeout = 15.0, check = check)
        except TimeoutError: return await ctx.send("Brak odpowiedzi w ciągu 15 sekund, czynność przerwana")
        if msg.content == 'tak':
            cursor.execute("DROP TABLE IF EXISTS levels")
            conn.commit()
            del konfig[str(ctx.guild.id)]['lvl']
            zapisz()
            return await ctx.send("Pomyślnie usunięto tabelę z poziomem i punktami użytkowników\nAby przywrócić, należy ją stworzyć na nowo")

@client.command()
async def rank(ctx, member:nextcord.Member = None):
    if await check_konfig(ctx) is True:
        try: 
            if member is None:
                member = ctx.author
            cursor.execute("SELECT * FROM levels WHERE ID = ?",(f'{member.id}',))
            tabelka = cursor.fetchall()[0]
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = f"Poziom użytkownika {member.name}")
            e.add_field(name = "Poziom", value = tabelka[1], inline = False)
            e.add_field(name = "Ilość punktów", value = tabelka[2], inline = False)
            cursor.execute("SELECT EXP FROM lvl WHERE LVL = ?", (tabelka[1],))
            e.add_field(name = "Brakuje do następnego poziomu", value = int(cursor.fetchone()[0] - tabelka[2]), inline = False)
            try: e.set_thumbnail(url = member.avatar)
            except: pass
            return await ctx.send(embed = e)
        except:
            return await ctx.send("Na tym serwerze nie został włączony system lvl'i")
    else:
        return await ctx.send("Na tym serwerze nie została wykonana konfiguracja")

@client.command()
@commands.has_permissions(administrator = True)
async def generatelvl(ctx, levels:int = None, mnoznik:float = None):
    try:
        if await check_konfig(ctx) is True and konfig[str(ctx.guild.id)]['lvl']:
            if mnoznik == None and levels == None:
                e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
                e.set_author(name = "Generator lvl")
                e.add_field(name = "Użycie", value = "Aby użyć ten komendy, należy podać ilość poziomów i mnożnik poziomu", inline = False)
                e.add_field(name = "Przykładowe użycie", value = "!generatelvl 10 50", inline = False)
                e.add_field(name = "Dobra praktyka", value = "W zależności od aktywności naszego serwera, można zmodyfikować wielkość poziomów\n Przykładowo jak mamy mniej aktywny serwer, możemy zmniejszyć mnożnik aby szybciej nabijac poziomy, i na odwrót", inline = False)
                e.add_field(name = "Uwaga!", value = "Jeżeli zostaną zmienione poziomy, to użytkownikowi nie zmienia się poziom", inline = False)
                return await ctx.send(embed = e)
            elif mnoznik == None or levels == None:
                return await ctx.send("Brakuje jednego argumentu, dopisz go")
            cursor.execute("DROP TABLE IF EXISTS lvl")
            conn.commit()
            cursor.execute("CREATE TABLE IF NOT EXISTS lvl (LVL intiger PRIMARY KEY, EXP intiger NOT NULL)")
            conn.commit()
            for i in range(levels + 1):
                exp = 100 * i * mnoznik
                cursor.execute(f"INSERT INTO lvl (LVL, EXP) VALUES ({i}, {exp})")
            conn.commit()
            return await ctx.send("Nowe lvl'e zostały zrobione pomyślnie")
    except KeyError:
        return await ctx.send("Brak włączonych lvl'i, należy je uruchomić\nAby je uruchomić, wpisz komendę: !lvl")

@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        if message.author != message.author.bot:
            try:
                dlugosc = len(message.content)
                cursor.execute("SELECT EXP FROM levels WHERE ID = ?",(f'{message.author.id}',))
                exp_user = cursor.fetchone()[0]
                exp_user += int(dlugosc * 0.2)
                cursor.execute("SELECT LVL FROM levels WHERE ID = ?", (f"{message.author.id}",))
                lvl_user = cursor.fetchone()[0]
                cursor.execute("SELECT EXP FROM lvl WHERE LVL = ?", (f'{lvl_user}',))
                exp = cursor.fetchone()[0]
                if exp > exp_user:
                    cursor.execute("UPDATE levels SET EXP = ? WHERE ID = ?", (exp_user, f'{message.author.id}'))
                    conn.commit()
                else:
                    if exp == 0:
                        exp = exp_user
                        lvl_user = 1
                    while exp_user > exp:
                        exp_user -= exp
                        lvl_user += 1
                    cursor.execute("UPDATE levels SET EXP = ? WHERE ID = ?", (exp_user, f'{message.author.id}'))
                    cursor.execute("UPDATE levels SET LVL = ? WHERE ID = ?", (lvl_user, f'{message.author.id}'))
                    conn.commit()
                    await message.channel.send(f"Brawo {message.author.mention}! Masz poziom {lvl_user}")
            except: pass
        await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator = True)
async def welcome(ctx, akcja = None, *, string = None):
    if await check_konfig(ctx) is True:
        if akcja is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Dostępne komendy")
            e.add_field(name = "utwórz", value = "Aby wykonać czynności związane z przyjściem użytkownika, należy najpierw utworzyć w konfiguracji", inline = False)
            e.add_field(name = "kanał", value = "Napisanie tej komendy na kanale spowoduje, że kanał będzie wysyłał wiadomości o dołączeniu użytkownika", inline = False)
            e.add_field(name = "wiadomość", value = "Wiadomość która będzie wysyłana przez bota, kiedy użytkownik wejdzie na serwer", inline = False)
            e.add_field(name = "Uwaga do komendy wiadomość", value = "Aby użytkownik, który przyszedł na serwer, został wyświetlony, nalezy napisać {user}", inline = False)
            return await ctx.send(embed = e)
        elif akcja == "utwórz" or akcja == "utworz":
            try:
                if konfig[str(ctx.guild.id)]["welcome"] is not None:
                    await ctx.send("Zostało już utworzone")
            except:
                konfig[str(ctx.guild.id)]["welcome"] = {}
                zapisz()
                return await ctx.send("Pomyślnie utworzono możliwość dodawania wiadomości powitalnych")
        elif akcja == "kanał" or akcja == "kanal":
            try:
                if konfig[str(ctx.guild.id)]["welcome"]["channel"]:
                    konfig[str(ctx.guild.id)]["welcome"]["channel"] = ctx.channel.id
                    zapisz()
                    return await ctx.send("Zmieniono kanał, który będzie wyświetlał wiadomości o dołączeniu")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['welcome']:
                        konfig[str(ctx.guild.id)]["welcome"]["channel"] = ctx.channel.id
                        zapisz()
                        return await ctx.send("Ten kanał będzie wyświetlał informację o użytkowniku, który dołączył na serwer")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        elif akcja == "wiadomość" or akcja == "wiadomosc":
            try:
                if konfig[str(ctx.guild.id)]["welcome"]["wiadomosc"]:
                    konfig[str(ctx.guild.id)]["welcome"]["wiadomosc"] = str(string)
                    zapisz()
                    return await ctx.send("Zmieniono wiadomość dla wiadomości powitalnej")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['welcome'] is not None:
                        konfig[str(ctx.guild.id)]["welcome"]["wiadomosc"] = str(string)
                        zapisz()
                        return await ctx.send("Pomyślnie dodano wiadomość powitalną")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        else:
            return await ctx.send("Błędny drugi argument, popraw go lub wpisz: !welcome, aby zobaczyć dostępne argumenty")

@client.event
async def on_member_join(member:nextcord.Member):
    if await check_konfig(member) is True:
        user = member.mention
        try:
            if konfig[str(member.guild.id)]["welcome"]["channel"] is not None:
                try:
                    if konfig[str(member.guild.id)]["welcome"]["wiadomosc"] is not None:
                        wiad = konfig[str(member.guild.id)]["welcome"]["wiadomosc"].split(" ")
                        wiad1, wiad2 = "", ""
                        check = False
                        for i in wiad:
                            if i == "{user}":
                                check = True
                                continue
                            if check == False:
                                wiad1 += i + " "
                            else:
                                wiad2 += i + " "
                        if check == True:
                            await client.get_channel(int(konfig[str(member.guild.id)]["welcome"]["channel"])).send(f"{wiad1}{user} {wiad2}")
                        else:
                            await client.get_channel(int(konfig[str(member.guild.id)]["welcome"]["channel"])).send(f"{wiad1}")
                except: pass
        except: pass
        try:
            if konfig[str(member.guild.id)]['lvl']:
                cursor.execute("INSERT INTO levels (ID, LVL, EXP) VALUES ({0.id}, 0, 0)".format(member))
                conn.commit()
        except: pass
        e = nextcord.Embed(color = member.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = "Użytkownik przyszedł na serwer")
        e.add_field(name = "Nick", value = member.name, inline = False)
        e.add_field(name = "ID", value = member.id, inline = False)
        e.add_field(name = "Utworzone konto", value = member.created_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
        e.add_field(name = "Dołączył na serwer", value = member.joined_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
        try: e.set_thumbnail(url = member.avatar.url)
        except: pass
        return await wyslij_logi_zdarzenie(member.guild, e)

@client.command()
@commands.has_permissions(administrator = True)
async def left(ctx, akcja = None, *, string = None):
    if await check_konfig(ctx) == True:
        if akcja is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Dostępne komendy")
            e.add_field(name = "utwórz", value = "Aby wykonać czynności związane z wyjściem, należy najpierw utworzyć w konfiguracji", inline = False)
            e.add_field(name = "kanał", value = "Napisanie tej komendy na kanale spowoduje, że kanał będzie wysyłał wiadomości o wyjściu użytkownika", inline = False)
            e.add_field(name = "wiadomość", value = "Wiadomość, która będzie wysyłana przez bota, kiedy użytkownik wyjdzie z serwera", inline = False)
            e.add_field(name = "Uwaga do komendy wiadomość", value = "Aby użytkownik, który wyszedł z serwera, został wyświetlony, nalezy napisać {user}", inline = False)
            return await ctx.send(embed = e)
        if akcja == "utwórz" or akcja == "utworz":
            try:
                if konfig[str(ctx.guild.id)]["left"] is not None:
                    return await ctx.send("Zostało już utworzone")
            except:
                konfig[str(ctx.guild.id)]["left"] = {}
                zapisz()
                return await ctx.send("Pomyślnie utworzono możliwość dodawania wiadomości pożegnalnych")
        elif akcja == "kanał" or akcja == "kanal":
            try:
                if konfig[str(ctx.guild.id)]["left"]["channel"]:
                    konfig[str(ctx.guild.id)]["left"]["channel"] = ctx.channel.id
                    zapisz()
                    return await ctx.send("Zmieniono kanał, który będzie wyświetlał wiadomości o wyjściu")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['left'] is not None:
                        konfig[str(ctx.guild.id)]["left"]["channel"] = ctx.channel.id
                        zapisz()
                        return await ctx.send("Ten kanał będzie wyświetlał informację o użytkowniku, który wyszedł z serwera")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        elif akcja == "wiadomość" or akcja == "wiadomosc":
            try:
                if konfig[str(ctx.guild.id)]["left"]['wiadomosc']:
                    konfig[str(ctx.guild.id)]["left"]['wiadomosc'] = str(string)
                    zapisz()
                    return await ctx.send("Zmieniono wiadomość dla wiadomości pożegnalnej")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['left'] is not None:
                        konfig[str(ctx.guild.id)]["left"]["wiadomosc"] = str(string)
                        zapisz()
                        return await ctx.send("Pomyślnie dodano wiadomość pożegnalną")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        else:
            return await ctx.send("Błędny drugi argument, popraw go lub wpisz: !left, aby zobaczyć dostępne argumenty")

@client.event
async def on_member_remove(member:nextcord.Member):
    global check_ban
    if check_ban == True:
        check_ban = False
        return
    if await check_konfig(member) is True:
        user = f"{member.name}#{member.discriminator}"
        try:
            if konfig[str(member.guild.id)]["left"]:
                wiad = konfig[str(member.guild.id)]["left"]["wiadomosc"].split(" ")
                wiad1, wiad2 = "", ""
                check = False
                for i in wiad:
                    if i == "{user}":
                        check = True
                        continue
                    if check == False:
                        wiad1 += i + " "
                    else:
                        wiad2 += i + " "
                if check == True:
                    await client.get_channel(int(konfig[str(member.guild.id)]["left"]["channel"])).send(f"{wiad1}{user} {wiad2}")
                else:
                    await client.get_channel(int(konfig[str(member.guild.id)]["left"]["channel"])).send(f"{wiad1}")
        except: pass
        e = nextcord.Embed(color = member.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = "Użytkownik opuścił serwer")
        e.add_field(name = "Nick", value = member.name, inline = False)
        e.add_field(name = "ID", value = member.id, inline = False)
        e.add_field(name = "Utworzone konto", value = member.created_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
        try: e.set_thumbnail(url = member.avatar.url)
        except: pass
        return await wyslij_logi_zdarzenie(member.guild, e)

@client.event
async def on_member_update(before, after):
    if await check_konfig(before) is True:
        e = nextcord.Embed(color = before.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        if before.roles != after.roles:
            async for author in before.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.member_role_update):
                user = '{0.user.mention}'.format(author)
                dodanie = '{0.after.roles}'.format(author)
                regex = r"'(.*)'"
                if re.search(regex, dodanie, re.MULTILINE) is not None:
                    matches = re.finditer(regex, dodanie, re.MULTILINE)
                    for match in matches:
                        role = match.group()
                        role = role.replace(role[0], '').replace(role[-1], '')
                zdjecie = '{0.before.roles}'.format(author)
                if re.search(regex, zdjecie, re.MULTILINE) is not None:
                    matches = re.finditer(regex, zdjecie, re.MULTILINE)
                    for match in matches:
                        role = match.group()
                        role = role.replace(role[0], '').replace(role[-1], '')
            if len(before.roles) < len(after.roles):
                e.set_author(name = "Dodanie roli użytkownikowi")
            elif len(before.roles) > len(after.roles):
                e.set_author(name = "Usuwanie roli użytkownikowi")
            e.add_field(name = "Użytkownik", value = before.mention, inline = False)
            e.add_field(name = "Rola", value = role, inline = False)
            e.add_field(name = "Przez", value = user, inline = False)
            try: e.set_thumbnail(url = before.avatar.url)
            except: pass
            return await wyslij_logi_zdarzenie(before.guild, e)
        if before.display_name != after.display_name:
            e.set_author(name = "Zmiana pseudonimu użytkownika")
            e.add_field(name = "Użytkownik", value = before.mention, inline = False)
            e.add_field(name = "Poprzedni pseudonim", value = before.display_name, inline = False)
            e.add_field(name = "Obecny pseudonim", value = after.display_name, inline = False)
            try: e.set_thumbnail(url = before.avatar.url)
            except: pass
            return await wyslij_logi_zdarzenie(before.guild, e)

@client.command()
async def banned(ctx, akcja = None, *, string = None):
    if await check_konfig(ctx) is True:
        if akcja is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Dostępne komendy")
            e.add_field(name = "utwórz", value = "Aby wykonac czynności związanie z banowaniem, należy utworzyć w konfiguracji", inline = False)
            e.add_field(name = "kanał", value = "Napisanie tej komendy na kanale spowoduje, że kanał będzie wysyłał wiadomości o zbanowaniu użytkownika", inline = False)
            e.add_field(name = "wiadomość", value = "Wiadomość, która będzie wysyłana przez bota, kiedy użytkownik zostanie zbanowany na serwerze", inline = False)
            e.add_field(name = "Uwaga do komendy wiadomość", value = "Aby użytkownik, który został zbanowany na serwerze, został wyświetlony, nalezy napisać {user}", inline = False)
            return await ctx.send(embed = e)
        if akcja == "utwórz" or akcja == "utworz":
            try:
                if konfig[str(ctx.guild.id)]['ban'] is not None:
                    return await ctx.send("Zostało już stworzone")
            except:
                konfig[str(ctx.guild.id)]['ban'] = {}
                zapisz()
                return await ctx.send("Pomyślnie utworzono możliwość dodawania wiadomości banowanych")
        elif akcja == "kanał" or akcja == "kanal":
            try:
                if konfig[str(ctx.guild.id)]['ban']['channel']:
                    konfig[str(ctx.guild.id)]['ban']['channel'] = ctx.channel.id
                    zapisz()
                    return await ctx.send("Zmieniono kanał, na którym będzie wyświetlana wiadomość")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['ban'] is not None:
                        konfig[str(ctx.guild.id)]['ban']['channel'] = ctx.guild.id
                        zapisz()
                        return await ctx.send("Ten kanał będzie wyświetlał informacje o użytkowniku, który został zbanowany na serwerze")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        elif akcja == "wiadomość" or akcja == "wiadomosc":
            try:
                if konfig[str(ctx.guild.id)]['ban']['wiadomosc']:
                    konfig[str(ctx.guild.id)]['ban']['wiadomosc'] = str(string)
                    zapisz()
                    return await ctx.send("Zmieniono wiadomość dla wiadomości banowanej")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['ban'] is not None:
                        konfig[str(ctx.guild.id)]['ban']['wiadomosc'] = str(string)
                        zapisz()
                        return await ctx.send("Pomyślnie dodano wiadomość banowaną")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        else:
            return await ctx.send("Błędny drugi argument, popraw go lub wpisz: !banned, aby zobaczyć dostępne argumenty")

@client.event
async def on_member_ban(guild, user):
    global check_ban
    if await check_konfig(guild) is True:
        member = f"{user.name}#{user.discriminator}"
        try:
            if konfig[str(guild.id)]["ban"]:
                wiad = konfig[str(guild.id)]["ban"]["wiadomosc"].split(" ")
                wiad1, wiad2 = "", ""
                check = False
                for i in wiad:
                    if i == "{member}":
                        check = True
                        continue
                    if check == False:
                        wiad1 += i + " "
                    else:
                        wiad2 += i + " "
                if check == True:
                    await client.get_channel(int(konfig[str(guild.id)]["ban"]["channel"])).send(f"{wiad1}{user} {wiad2}")
                else:
                    await client.get_channel(int(konfig[str(guild.id)]["ban"]["channel"])).send(f"{wiad1}")
        except: pass
        e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = "Użytkownik został zbanowany")
        e.add_field(name = "Nick", value = user.name, inline = False)
        e.add_field(name = "ID", value = user.id, inline = False)
        e.add_field(name = "Utworzone konto", value = user.created_at.strftime(("%d.%m.Y o godzinie: %H:%M")), inline = False)
        try: e.set_thumbnail(url = user.avatar.url)
        except: pass
        check_ban = True
        return await wyslij_logi_zdarzenie(guild, e)

@client.command()
async def unbanned(ctx, akcja = None, *, string = None):
    if await check_konfig(ctx) is True:
        if akcja is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Dostępne komendy")
            e.add_field(name = "utwórz", value = "Aby wykonac czynności związanie z banowaniem, należy utworzyć w konfiguracji", inline = False)
            e.add_field(name = "kanał", value = "Napisanie tej komendy na kanale spowoduje, że kanał będzie wysyłał wiadomości o zbanowaniu użytkownika", inline = False)
            e.add_field(name = "wiadomość", value = "Wiadomość, która będzie wysyłana przez bota, kiedy użytkownik zostanie zbanowany na serwerze", inline = False)
            e.add_field(name = "Uwaga do komendy wiadomość", value = "Aby użytkownik, który został odbanowany na serwerze, został wyświetlony, nalezy napisać {user}", inline = False)
            return await ctx.send(embed = e)
        if akcja == "utwórz" or akcja == "utworz":
            try:
                if konfig[str(ctx.guild.id)]['unban'] is not None:
                    return await ctx.send("Zostało już stworzone")
            except:
                konfig[str(ctx.guild.id)]['unban'] = {}
                zapisz()
                return await ctx.send("Pomyślnie utworzono możliwość dodawania wiadomości odbanowanych")
        elif akcja == "kanał" or akcja == "kanal":
            try:
                if konfig[str(ctx.guild.id)]['unban']['channel']:
                    konfig[str(ctx.guild.id)]['unban']['channel'] = ctx.channel.id
                    zapisz()
                    return await ctx.send("Zmieniono kanał, na którym będzie wyświetlana wiadomość")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['unban'] is not None:
                        konfig[str(ctx.guild.id)]['unban']['channel'] = ctx.guild.id
                        zapisz()
                        return await ctx.send("Ten kanał będzie wyświetlał informacje o użytkowniku, który został odbanowany na serwerze")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        elif akcja == "wiadomość" or akcja == "wiadomosc":
            try:
                if konfig[str(ctx.guild.id)]['unban']['wiadomosc']:
                    konfig[str(ctx.guild.id)]['unban']['wiadomosc'] = str(string)
                    zapisz()
                    return await ctx.send("Zmieniono wiadomość dla wiadomości odbanowanej")
            except:
                try:
                    if konfig[str(ctx.guild.id)]['unban'] is not None:
                        konfig[str(ctx.guild.id)]['unban']['wiadomosc'] = str(string)
                        zapisz()
                        return await ctx.send("Pomyślnie dodano wiadomość odbanowaną")
                except:
                    return await ctx.send("Nie została utworzona konfiguracja dla tej komendy, wpisz zamiast tego: utwórz")
        else:
            return await ctx.send("Błędny drugi argument, popraw go lub wpisz: !banned, aby zobaczyć dostępne argumenty")

@client.event
async def on_member_unban(guild, user):
    if await check_konfig(guild) is True:
        member = f"{user.name}#{user.discriminator}"
        try:
            if konfig[str(guild.id)]["unban"]:
                wiad = konfig[str(guild.id)]["unban"]["wiadomosc"].split(" ")
                wiad1, wiad2 = "", ""
                check = False
                for i in wiad:
                    if i == "{member}":
                        check = True
                        continue
                    if check == False:
                        wiad1 += i + " "
                    else:
                        wiad2 += i + " "
                if check == True:
                    await client.get_channel(int(konfig[str(guild.id)]["unban"]["channel"])).send(f"{wiad1}{user} {wiad2}")
                else:
                    await client.get_channel(int(konfig[str(guild.id)]["unban"]["channel"])).send(f"{wiad1}")
        except: pass
        e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = "Użytkownik został odbanowany")
        e.add_field(name = "Nick", value = user.name, inline = False)
        e.add_field(name = "ID", value = user.id, inline = False)
        e.add_field(name = "Utworzone konto", value = user.created_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
        try: e.set_thumbnail(url = user.avatar.url)
        except: pass
        return await wyslij_logi_zdarzenie(guild, e)

@client.command()
@commands.has_permissions(administrator = True)
async def role(ctx, zakres:str = None, *, tresc:str = None):
    if await check_konfig(ctx) == True:
        if zakres == None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy role")
            e.add_field(name = "Wybranie zakresu z ról poniżej podanych", value= "Przykład: !role 20-50", inline = False)
            e.add_field(name = "Zakres", value = "Zakres powinien być liczbą całkowitą, poprzedzony \"-\" i kolejną liczbą całkowitą: np: 20-50, 50-80, 129-250", inline = False)
            e.add_field(name = "Uwaga!", value = "Role wszystkie są podawane od dołu do góry (tak jak widzi to discord)", inline = False)
            e.add_field(name = "Uwaga!", value = "Napisana komenda na danym kanale, będzie oznaczać, że tutaj będą występować autorole", inline = False)
            e.add_field(name = "Uwaga!", value = "Nie zaczynamy od 0, ponieważ jest to rola @everyone, którą posiada każdy użytkownik niezależnie, jak i jej nie można zabrać", inline = False)
            e.add_field(name = "Uwaga!", value = "Jeżeli źle zostaną wygenerowane emotki związane z autorolami, to nie należy się przejmować i wygenerować na nowo", inline = False)
            e.add_field(name = "Dobra praktyka", value = "Dajemy rangę bota jak najwyżej (na tyle ile możemy sobie pozwolić, więc najlepiej pod rangami dla moderatorów i administratorów), a potem wybieramy role, które mają być przyznawane użytkownikom", inline = False)
            await ctx.send(embed = e)
            wszystkie_role: str = ""
            for i, j in zip(ctx.guild.roles, range(len(ctx.guild.roles))):
                if j == 0:
                    continue
                if len(wszystkie_role) <= 2000 and len(wszystkie_role) >= 1900:
                    await ctx.send(f"```{wszystkie_role}```")
                    wszystkie_role = ""
                if i.is_bot_managed():
                    continue
                wszystkie_role += f"{j} {i.name}\n"
            return await ctx.send(f"```{wszystkie_role}```")
        try:
            if konfig[str(ctx.guild.id)]['rangi'] and not ctx.channel.id in konfig[str(ctx.guild.id)]['rangi']:
                konfig[str(ctx.guild.id)]['rangi'].append(ctx.channel.id)
                zapisz()
        except:
            konfig[str(ctx.guild.id)]['rangi'] = []
            konfig[str(ctx.guild.id)]['rangi'].append(ctx.channel.id)
            zapisz()
        zakres = zakres.split("-")
        poczatek:int = int(zakres[0])
        koniec:int = int(zakres[1])
        ile_roli:int = int(len(ctx.guild.roles)-1)
        if poczatek > koniec or poczatek > ile_roli or koniec > ile_roli or poczatek == 0 or koniec == 0:
            return await ctx.send("Błędnie podany zakres, popraw")
        e = nextcord.Embed(color = ctx.author.color)
        if tresc != None: e.set_author(name = tresc)
        a = 1
        while poczatek <= koniec:
            e.add_field(name = f":{liczby[a]}:", value = ctx.guild.roles[poczatek], inline = False)
            poczatek += 1
            if a == 10:
                await ctx.send(embed = e)
                for i in range(1,a+1):
                    await client.get_channel(ctx.channel.id).last_message.add_reaction(emoji = emoji.emojize(f":keycap_{i}:"))
                e.clear_fields()
                a = 1
                continue
            a += 1
        try:
            if a == 1: return
            await ctx.send(embed = e)
            for i in range(1,a):
                await client.get_channel(ctx.channel.id).last_message.add_reaction(emoji = emoji.emojize(f":keycap_{i}:"))
        except: pass

@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id == client.user.id: return
    guild = client.get_guild(payload.guild_id)
    if payload.channel_id in konfig[str(guild.id)]['rangi']:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)
        emotka = emoji.demojize(payload.emoji.name)
        emotka = emotka.replace(":keycap_", '').replace(":", '')
        emotka = int(emotka)
        for i in message.embeds:
            ranga = nextcord.utils.get(guild.roles, name = i.fields[emotka - 1].value)
        return await member.add_roles(ranga, reason = None)

@client.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == client.user.id:
        return
    guild = client.get_guild(payload.guild_id)
    if payload.channel_id in konfig[str(guild.id)]['rangi']:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = guild.get_member(payload.user_id)
        emotka = emoji.demojize(payload.emoji.name)
        emotka = emotka.replace(":keycap_", '').replace(":", '')
        emotka = int(emotka)
        for i in message.embeds:
            ranga = nextcord.utils.get(guild.roles, name = i.fields[emotka - 1].value)
        return await member.remove_roles(ranga, reason = None)

@client.event  
async def on_guild_update(before, after):
    async for author in before.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.guild_update):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    if before.name != after.name:
        e.set_author(name = f"Zmiana nazwy serwera!")
        e.add_field(name = f"Wcześniejsza nazwa: ", value = before.name, inline = False)
        e.add_field(name = f"Teraźniejsza nazwa: ", value = after.name, inline = False)
        e.add_field(name = f"Przez: ", value = user.mention, inline = False)
        try: e.set_thumbnail(url = user.avatar)
        except: pass
    return await wyslij_logi_zdarzenie(before, e)

@client.event
async def on_guild_role_create(role:nextcord.Role):
    async for author in role.guild.audit_logs(limit = 1 ,oldest_first = False, action = nextcord.AuditLogAction.role_create):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = f"Utworzenie rangi!")
    e.add_field(name = f"Nazwa rangi:", value = role.name, inline = False)
    e.add_field(name = f"Przez:", value = user.mention, inline = False)
    try: e.set_thumbnail(url = user.avatar)
    except: pass
    return await wyslij_logi_zdarzenie(role.guild, e)

@client.event
async def on_guild_role_delete(role:nextcord.Role):
    async for author in role.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.role_delete):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = f"Usunięcie rangi!")
    e.add_field(name = f"Nazwa rangi: ", value = role.name, inline = False)
    e.add_field(name = f"Przez: ", value = user.mention, inline = False)
    e.add_field(name = f"Pozycja na liście (od końca): ", value = role.position, inline = False)
    try: e.set_thumbnail(url = user.avatar)
    except: pass
    return await wyslij_logi_zdarzenie(role.guild, e)

@client.event
async def on_guild_role_update(before, after):
    async for author in before.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.role_update):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    try: e.set_thumbnail(url = user.avatar)
    except: pass
    if before.name != after.name:
        e.set_author(name = f"Zmiana nazwy rangi!")
        e.add_field(name = f"Wcześniejsza nazwa: ", value = before.name, inline = False)
        e.add_field(name = f"Obecna nazwa: ", value = after.name, inline = False)
        e.add_field(name = f"Przez: ", value = user.mention, inline = False)
        return await wyslij_logi_zdarzenie(before.guild, e)
    if before.mentionable is False and after.mentionable is True or before.mentionable is True and after.mentionable is False:
        e.set_author(name = f"Zmiana wzmianek rangi:")
        e.add_field(name = f"Ranga: ", value = before.name, inline = False)
        e.add_field(name = f"Możliwość wzmianki: ", value = after.mentionable, inline = False)
        e.add_field(name = f"Przez: ", value = user.mention, inline = False)
        return await wyslij_logi_zdarzenie(before.guild, e)
    if before.hoist is False and after.hoist is True or before.hoist is True and after.hoist is False:
        e.set_author(name = f"Zmiana wyróżnienia rangi!")
        e.add_field(name = f"Ranga: ", value = before.name, inline = False)
        e.add_field(name = f"Status wyróznienia", value = after.hoist, inline = False)
        e.add_field(name = f"Przez: ", value = user.mention, inline = False)
        return await wyslij_logi_zdarzenie(before.guild, e)

@client.event
async def on_guild_channel_create(channel):
    async for author in channel.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.channel_create):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    try: e.set_thumbnail(url = user.avatar)
    except: pass
    e.set_author(name = f"Utworzenie kanału")
    e.add_field(name = f"Nazwa kanału:", value = channel.name, inline = False)
    e.add_field(name = f"W kategorii:", value = channel.category, inline = False)
    e.add_field(name = f"Przez:", value = user.mention, inline = False)
    return await wyslij_logi_zdarzenie(channel.guild, e)

@client.event
async def on_guild_channel_delete(channel):
    async for author in channel.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.channel_delete):
        member = '{0.user.id}'.format(author)
        user = await client.fetch_user(member)
    e = nextcord.Embed(color = user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    try: e.set_thumbnail(url = user.avatar)
    except: pass
    e.set_author(name = f"Usunięcie kanału")
    e.add_field(name = f"Nazwa kanału:", value = channel.name, inline = False)
    e.add_field(name = f"W kategorii:", value = channel.category, inline = False)
    e.add_field(name = f"Przez:", value = user.mention, inline = False)
    return await wyslij_logi_zdarzenie(channel.guild, e)

@client.event
async def on_guild_channel_update(before, after):
    e = nextcord.Embed(color = client.user.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    if before.name != after.name:
        async for author in before.guild.audit_logs(limit = 1, oldest_first = False, action = nextcord.AuditLogAction.channel_update):
            member = '{0.user.id}'.format(author)
            user = await client.fetch_user(member)
        try: e.set_thumbnail(url = user.avatar)
        except: pass
        e.set_author(name = f"Zmiana nazwy kanału")
        e.add_field(name = f"Poprzednia nazwa", value = before.name, inline = False)
        e.add_field(name = f"Nowa nazwa", value = after.name, inline = False)
        e.add_field(name = f"Przez", value = user.mention, inline = False)
        return await wyslij_logi_zdarzenie(before.guild, e)

@client.event
async def on_message_edit(before, after):
    if not client.user.id == before.author.id and before.author.bot is False and await check_konfig(before) is True:
        e = nextcord.Embed(color = before.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Wiadomość edytowana od {before.author.name}")
        e.set_thumbnail(url = before.author.avatar)
        e.add_field(name = f"Z kanału:", value = before.channel.mention, inline = False)
        e.add_field(name = f"Wiadomość oryginalna:", value = before.content, inline = False)
        e.add_field(name = f"Wiadomość edytowana:", value = after.content, inline = False)
        return await wyslij_logi_zdarzenie(before.guild, e)

@client.event
async def on_message_delete(message):
    global snipe_uzytkownik, snipe_wiadomosc
    if not client.user.id == message.author.id and await check_konfig(message.channel) is True:
        e = nextcord.Embed(color = message.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Wiadomośc usunięta od {message.author.name}#{message.author.discriminator}")
        e.set_thumbnail(url = message.author.display_avatar)
        e.add_field(name = f"Z kanału:", value = f"<#{message.channel.id}>", inline = False)
        e.add_field(name = f"Wiadomość:", value = message.content, inline = False)
        snipe_uzytkownik = message.author
        snipe_wiadomosc = message.content
        return await wyslij_logi_zdarzenie(message.channel.guild, e)

@client.command()
async def ban(ctx, user:nextcord.User = None, * , powod = None):
    if ctx.author.guild_permissions.ban_members is True or check_its_mod(ctx.author) is True:
        if user is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy ban")
            e.add_field(name = "Użycie", value = "!ban <@user> (opcjonalnie) powód", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!ban @Noob ", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!ban @Noob wynocha mi z serwera", inline = False)
            return await ctx.send(embed = e)
        await ctx.guild.ban(user, reason = powod)
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Użytkownik {user.name}#{user.discriminator} został zbanowany")
        await ctx.send(embed = e)
        return await wyslij_logi_komendy(ctx, "ban", user)

@client.command()
async def unban(ctx, user:nextcord.User = None):
    if ctx.author.guild_permissions.ban_members is True or check_its_mod(ctx.author) is True:
        if user is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy unban")
            e.add_field(name = "Uzycie", value = "!unban <@user>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!unban @Noob", inline = False)
            return await ctx.send(embed = e)
        await ctx.guild.unban(user)
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Użytkownik {user.name}#{user.discriminator} został odbanowany")
        await ctx.send(embed = e)
        return await wyslij_logi_komendy(ctx, "unban", user)

@client.command()
async def kick(ctx, user:nextcord.User = None, *, powod = None):
    if ctx.author.guild_permissions.kick_members is True or check_its_mod(ctx.author) is True:
        if user is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy kick")
            e.add_field(name = "Użycie", value = "!kick <@user> (opcjonalnie) powód", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!kick @Noob ", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!kick @Noob U noob ok?", inline = False)
            return await ctx.send(embed = e)
        await ctx.guild.kick(user, reason = powod)
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Użytkownik {user.name}#{user.discriminator} został wyrzucony")
        await ctx.send(embed = e)
        return await wyslij_logi_komendy(ctx, "kick", user)

@client.command()
async def purge(ctx, ilosc:int = None):
    if ctx.author.guild_permissions.manage_messages is True or check_its_mod(ctx.author) is True:
        def not_pinned(msg):
            return not msg.pinned
        if ilosc is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy purge")
            e.add_field(name = "Użycie", value = "!purge <ilość>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!purge 123", inline = False)
            e.add_field(name = "Limit wiadomości dla tej komendy", value = 10000, inline = False)
            return await ctx.send(embed = e)
        try: int(ilosc)
        except ValueError: return await ctx.send("Błędna ilość wiadomości")
        if int(ilosc) > 10000:
            return await ctx.send("Za duża liczba do wykonania polecenia. Limit wynosi 10000")
        await ctx.channel.purge(limit = int(ilosc), check = not_pinned)
        return await wyslij_logi_komendy(ctx, "purge")

@client.command()
async def mute(ctx, member: nextcord.Member = None, czas: str = None):
    if ctx.author.guild_permissions.mute_members is True or check_its_mod(ctx.author) is True or ctx.author.guild_permissions.moderate_members is True:
        if member is None or czas is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy mute")
            e.add_field(name = "Formaty czasu", value = "s - sekundy\n m - minuty\n h - godziny\n d - dni", inline = False)
            e.add_field(name = "Użycie", value = "!mute <użytkownik> <czas>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!mute @Noob 20s\n !mute Noob 20h", inline = False)
            e.add_field(name = "Działanie mute", value = "Mute działa na zasadzie wysyłania użytkownika na przerwę, nie posiada on dostępu do pisania na kanałach tekstowych i mówienia na kanałach głowosych", inline = False)
            return await ctx.send(embed = e)
        total_czas = getIntTime(await konwerter_czasu(ctx, czas))
        if total_czas is False: return
        await member.edit(timeout = total_czas)
        await ctx.send(f"Użytkownik {member.mention} został zmutowany")
        return await wyslij_logi_komendy(ctx, "Mute", member, czas)

@client.command()
async def unmute(ctx, member: nextcord.Member = None):
    if ctx.author.guild_permissions.mute_members is True or check_its_mod(ctx.author) is True or ctx.author.guild_permissions.moderate_members is True:
        if member is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy unmute")
            e.add_field(name = "Użycie", value = "!unmute <użytkownik>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!unmute @Noob\n", inline = False)
            return await ctx.send(embed = e)
        await member.edit(timeout = None)
        await ctx.send(f"Użytkownik {member.mention} został odmutowany pomyślnie")
        return await wyslij_logi_komendy(ctx, "Unmute", member)

@client.command()
async def serverinfo(ctx):
    if ctx.author.guild_permissions.view_audit_log is True or check_its_mod(ctx.author) is True:
        boty = 0
        for i in ctx.guild.members:
            if i.bot is True:
                boty += 1
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.add_field(name = "Nazwa serwera", value = ctx.guild.name, inline = False)
        try:
            if ctx.guild.icon is not None:
                e.set_thumbnail(url = ctx.guild.icon)
        except: pass
        e.add_field(name = "Host serwera", value = ctx.guild.owner, inline = False)
        e.add_field(name = "Nick hosta", value = ctx.guild.owner.display_name, inline = False)
        e.add_field(name = "ID serwera", value = ctx.guild.id, inline = False)
        e.add_field(name = "Ilość użytkowników", value = len(ctx.guild.members) - boty, inline = False)
        e.add_field(name = "Ilość botów", value = boty, inline = False)
        e.add_field(name = "Ilość rang", value = len(ctx.guild.roles), inline = False)
        e.add_field(name = "Ilość kanałów tekstowych", value = len(ctx.guild.text_channels), inline = False)
        e.add_field(name = "Ilość kanałów głosowych", value = len(ctx.guild.voice_channels), inline = False)
        e.add_field(name = "Data utworzenia:", value = ctx.guild.created_at.strftime(("%H:%M:%S - %d.%m.%Y")), inline = False)
        return await ctx.send(embed = e)

@client.command(pass_context = True, alias = ['warny'])
async def warn(ctx, member:nextcord.Member = None, *, reason = "Brak podanego powodu"):
    if check_its_mod(ctx.author) is True or ctx.author.guild_permissions.mute_members is True:
        create_table = "CREATE TABLE IF NOT EXISTS warny (NUMER integer PRIMARY KEY AUTOINCREMENT, ID integer NOT NULL, WARN text NOT NULL);"
        cursor.execute(create_table)
        conn.commit()
        if member is None:
            return await ctx.send("Brak użytkownika")
        cursor.execute(f"INSERT INTO warny (ID, WARN) VALUES ({member.id}, '{reason}');")
        conn.commit()
        return await ctx.send("Użytkownik został zwarnowany")

@client.command(pass_content = True, alias = ['warns'])
async def checkwarn(ctx, member:nextcord.Member = None):
    if ctx.author.guild_permissions.mute_members is True or check_its_mod(ctx.author) is True:
        if member is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy check_warn (checkwarn, warns)")
            e.add_field(name = "Uzycie", value = "!check_warn <@user>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!check_warn @Noob", inline = False)
            return await ctx.send(embed = e)
        cursor.execute("SELECT WARN FROM warny WHERE ID = ?",(member.id,))
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Warny użytkownika {member.name}")
        tabelka = cursor.fetchall()
        if len(tabelka) == 0:
            return await ctx.send("Użytkownik nie posiada żadnych warnów")
        for i, j in zip(tabelka, range(len(tabelka))):
            e.add_field(name = f"Powód nr {j+1}", value = i[0], inline = False)
            if j % 9 == 0 and j != 0:
                await ctx.send(embed = e)
                e.clear_fields()
        return await ctx.send(embed = e)

@client.command()
async def delwarn(ctx, member:nextcord.Member = None):
    if ctx.author.guild_permissions.mute_members is True or check_its_mod(ctx.author) is True:
        if member is None:
            e = nextcord.Embed(color = ctx.author.color, timestamp= datetime.datetime.now(datetime.timezone.utc))
            e.set_author(name = "Prawidłowe użycie komendy delwarn")
            e.add_field(name = "Uzycie", value = "!delwarn <@user>", inline = False)
            e.add_field(name = "Przykładowe użycie", value = "!delwarn @Noob", inline = False)
            e.add_field(name = "Uwaga!", value = "Komenda usuwa wszystkie warny jakie posiada użytkownik", inline = False)
            return await ctx.send(embed = e)
        cursor.execute("DELETE FROM warny WHERE ID = ?", (member.id,))
        conn.commit()
        e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
        e.set_author(name = f"Usunięto pomyślnie wszystkie warny użytkownikowi {member.name}")
        return await ctx.send(embed = e)

@client.command()
async def snipe(ctx):
    global snipe_uzytkownik, snipe_wiadomosc
    if snipe_uzytkownik == '' or snipe_wiadomosc == '':
        return await ctx.send("Brak wiadomości usuniętej")
    e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = "Usunięta wiadomość")
    e.add_field(name = "Użytkownik", value = snipe_uzytkownik.mention, inline = False)
    e.add_field(name = "Treść", value = snipe_wiadomosc, inline = False)
    try:
        if snipe_uzytkownik.display_avatar is not None:
            e.set_thumbnail(url = snipe_uzytkownik.display_avatar)
    except: pass
    snipe_uzytkownik = snipe_wiadomosc = ''
    return await ctx.send(embed = e)

@client.command()
async def avatar(ctx, member: nextcord.Member = None):
    if member is None:
        member = ctx.author
    e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = f"Avatar użytkownika {member.name}#{member.discriminator}")
    try: e.set_image(url = member.avatar.url)
    except: return await ctx.send("Użytkownik nie posiada ustawionego avataru")
    return await ctx.send(embed = e)

@client.command()
async def info(ctx, member: nextcord.Member = None):
    if member is None: member = ctx.author
    e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = f"Informacje o użytkowniku {member.name}#{member.discriminator}")
    try:
        if member.avatar is not None:
            e.set_thumbnail(url = member.avatar.url)
    except: pass
    e.add_field(name = "Użytkownik", value = member.mention, inline = False)
    try: e.add_field(name = "Nick użytkownika na serwerze", value = member.display_name, inline = False)
    except: pass
    e.add_field(name = "ID użytkownika", value = member.id, inline = False)
    e.add_field(name = "Data powstania konta", value = member.created_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
    try: e.add_field(name = "Data dołączenia na serwer", value = member.joined_at.strftime(("%d.%m.%Y o godzinie: %H:%M")), inline = False)
    except: pass
    return await ctx.send(embed = e)

@client.command()
async def countusers(ctx):
    return await ctx.send(f"Członków serwera jest: {len(ctx.guild.members)}")

@client.command()
async def ping(ctx):
    return await ctx.send(f"Pong! Mój ping wynosi: {round(client.latency * 1000)}ms")

@client.command()
async def help(ctx):
    e = nextcord.Embed(color = ctx.author.color, timestamp = datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name = "Dostępne komendy dla administratorów")
    if ctx.author.guild_permissions.mute_members is True or check_its_mod(ctx.author) is True or ctx.author.guild_permissions.view_audit_log is True or ctx.author.guild_permissions.moderate_members is True or ctx.author.guild_permissions.kick_members is True or ctx.author.guild_permissions.ban_members is True:
        e.add_field(name = "!konfiguracja", value = "Wykonuje konfigurację serwera i odblokowuje dostęp do części komend", inline = False)
        e.add_field(name = "!mod", value = "Daje upoważnienie wybranym osobom do wykonywania niektórych komend (ban, kick, mute, unmute, warn itp)", inline = False)
        e.add_field(name = "!delmod", value = "Zabiera upoważnienie wybranym osobom do wykonywania niektórych komend", inline = False)
        e.add_field(name = "!listmod", value = "Wypisuje listę użytkowników, którzy zostali dodani do moderacji przez komendę \"mod\"", inline = False)
        e.add_field(name = "!logi", value = "Należy wpisać na kanał z logami, aby były one wyświetlane na serwerze", inline = False)
        e.add_field(name = "!lvl", value = "Włącza/wyłącza system poziomów na serwerze", inline = False)
        e.add_field(name = "!deletelvl", value = "Usuwa tabelę z użytkownikami, która posiada poziomy i punkty", inline = False)
        e.add_field(name = "!generatelvl", value = "Zmienia mnożnik poziomów", inline = False)
        e.add_field(name = "!welcome", value = "Wyświetla informacje na temat użytkowników, którzy przychodzą na serwer", inline = False)
        e.add_field(name = "!left", value = "Wyświetla informacje na temat użytkowników, którzy wyszli z serwera", inline = False)
        e.add_field(name = "!banned", value = "Wyświetla informacje na temat użytkowników, którzy zostali zbanowani na serwerze", inline = False)
        e.add_field(name = "!unbanned", value = "Wyświetla informacje na temat użytkowników, którzy zostali odbanowani na serwerze", inline = False)
        e.add_field(name = "!role", value = "Generuje autorole dostępne dla użytkowników", inline = False)
        e.add_field(name = "!ban", value = "Banuje użytkownika na serwerze", inline = False)
        e.add_field(name = "!unban", value = "Odbanowuje użytkownika na serwerze", inline = False)
        e.add_field(name = "!kick", value = "Wyrzuca użytkownika z serwera", inline = False)
        e.add_field(name = "!purge", value = "Usuwa określoną ilość wiadomości na danym kanale", inline = False)
        e.add_field(name = "!mute", value = "Wycisza użytkownika na serwerze na określony czas", inline = False)
        e.add_field(name = "!unmute", value = "Odcisza użytkownika na serwerze", inline = False)
        e.add_field(name = "!serverinfo", value = "Wyświetla informacje o serwerze", inline = False)
        e.add_field(name = "!warn", value = "Daje ostrzeżenie dla wybranego użytkownika", inline = False)
        e.add_field(name = "!checkwarn", value = "Sprawdza, ile użytkownik ma ostrzeżeń", inline = False)
        e.add_field(name = "!delwarn", value = "Usuwa wszystkie ostrzeżenia wybranemu użytkownikowi", inline = False)
        await ctx.send(embed = e)
        e.clear_fields()
        e.remove_author()
    e.set_author(name = "Dostępne komendy dla użytkowników")
    e.add_field(name = "!rank", value = "Wyświetla ranking osoby na serwerze", inline = False)
    e.add_field(name = "!snipe", value = "Wyświetla ostatnią usuniętą wiadomość", inline = False)
    e.add_field(name = "!avatar", value = "Wyświetla avatar użytkownika, o ile jest dostępny", inline = False)
    e.add_field(name = "!info", value = "Wyświetla informacje na temat użytkownika", inline = False)
    e.add_field(name = "!help", value = "Wyświetla dostępne komendy", inline = False)
    e.add_field(name = "!countusers", value = "Wyświetla liczbę członków serwera", inline = False)
    e.add_field(name = "!ping", value = "Wyświetla ping pomiędzy botem, a serwerem", inline = False)
    return await ctx.send(embed = e)

@client.command()
async def test(ctx):
    pass

client.run(token)
