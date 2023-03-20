from datetime import datetime, timedelta
from sys import argv, exit
from telethon import TelegramClient, events, connection
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from time import mktime, sleep
import telethon.sync
from threading import Thread
import collections
import psycopg2

host = "mypsql.postgres.database.azure.com"
dbname = "tbOnlineAll"
user = "mypsql"
password = "1234567890Aa"
sslmode = "require"

conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

db_connection = psycopg2.connect(conn_string)
db_object = db_connection.cursor()

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_FORMAT2 = '%H:%M:%S'
API_HASH = 'c7be2179ca2ae8e19bd0d7383eec9f52'
API_ID = '10072148'
BOT_TOKEN = "5367973115:AAG2jSpIZIb-50tzKbnHXewSaKCfzBiVACc"
USER_NAME = "ql1l1p7"
client: TelegramClient = TelegramClient('data_thief', API_ID, API_HASH)
client.connect()
client.start()

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

data = {}
destination_user_username=USER_NAME
entity=bot.get_entity(destination_user_username)
entity=client.get_entity(destination_user_username)

help_messages = ['/start - start online monitoring ',
         '/stop - stop online monitoring ',
         '/help - show help ',
         '/add - add user to monitoring list "/add +79991234567 UserName"',
         '/db_add - add user from D_base"',
         '/list - show added users',
         '/clear - clear user list',
         '/remove - remove user from list with position in list (to show use /list command)"/remove 1"',
         '/setdelay - set delay between user check in seconds',
         '/logs - display command log',
         '/clearlogs - clear the command log file',
         '/cleardata - reset configuration',
         '/disconnect - disconnect bot',
         '/getall - status']

print('running')
class Contact:
    online = None
    last_offline = None
    first_online = None
    onlineCount = 0
    totalOnlineTime = 0
    id = ''
    name = ''

    def __init__(self, id, name):
        self.id = id
        self.name = name
    def __str__(self):
        return f'{self.name}: {self.id}'

@bot.on(events.NewMessage(pattern='^/logs$'))
async def logs(event):
    """Send a message when the command /start is issued."""
    str = ''
    with open('spy_log.txt', 'r') as file:
        str = file.read()
    await event.respond(str)

@bot.on(events.NewMessage(pattern='/clearlogs$'))
async def clearLogs(event):
    """Send a message when the command /start is issued."""
    open('spy_log.txt', 'w').close()
    await event.respond('logs has been deleted')

@bot.on(events.NewMessage(pattern='^/clear$'))
async def clear(event):
    """Send a message when the command /start is issued."""
    message = event.message
    id = message.from_id
    data[id] = {}
    await event.respond('User list has been cleared')

@bot.on(events.NewMessage(pattern='^/help$'))
async def help(event):
    await event.respond('\n'.join(help_messages))

@bot.on(events.NewMessage())
async def log(event):
    """Send a message when the command /start is issued."""
    message = event.message
    #id = message.from_id
    str = f'{datetime.now().strftime(DATETIME_FORMAT)}: [{id}]: {message.message}'
    printToFile(str)
    #await bot.send_message(entity=entity,message=str)
    #await event.respond('cleared')

@bot.on(events.NewMessage(pattern='^/stop$'))
async def stop(event):
    """Send a message when the command /start is issued."""
    message = event.message
    id = message.from_id
    if id not in data:
        data[id] = {}
    user_data = data[id]
    user_data['is_running'] = False
    await event.respond('Monitoring has been stopped')

@bot.on(events.NewMessage(pattern='^/cleardata$'))
async def clearData(event):
    data.clear()
    await event.respond('Data has been cleared')

@bot.on(events.NewMessage(pattern='^/start$'))
async def start(event):
    message = event.message
    id = message.from_id
    if id not in data:
       data[id] = {}
    user_data = data[id]
    if('is_running' in user_data and user_data['is_running']):
        await event.respond('Spy is already started')
        return

    if 'contacts' not in user_data:
        user_data['contacts'] = []

    contacts = user_data['contacts']

    if(len(contacts) < 1):
        await event.respond('No contacts added')
        return
    await event.respond('__  Monitoring has been started __', parse_mode="Markdown")

    counter = 0
    user_data['is_running'] = True

    f1 = lambda a: (a % 100) // 10 != 1 and a % 10 == 1
    f2 = lambda a: (a % 100) // 10 != 1 and a % 10 in [2, 3, 4]


    while True:
        user_data = data[id]
        if(not user_data['is_running'] or len(contacts) < 1):
            break;
        print(f'running {id}: {counter}')
        counter+=1
        for contact in contacts:
            print(contact)
            account = await client.get_entity(contact.id)
            print (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if isinstance(account.status, UserStatusOffline):
                if contact.online != False:
                    contact.online = False
                    if contact.first_online != None:
                        contact.onlineCount = contact.onlineCount + 1
                        contact.totalOnlineTime = contact.totalOnlineTime + (account.status.was_online.replace(tzinfo=None) - contact.first_online).seconds
                        await event.respond(f'{(utc2localtime(account.status.was_online).strftime(DATETIME_FORMAT))}: __{contact.name}__ went offline. **({str(account.status.was_online.replace(tzinfo=None)-contact.first_online).split(".")[0]})**'
                                            f' ({contact.onlineCount}{" онлайн" if f1(contact.onlineCount) else " онлайна" if f2(contact.onlineCount) else " онлайнов"}, {datetime.fromtimestamp(contact.totalOnlineTime).strftime(DATETIME_FORMAT2)})', parse_mode="Markdown")
                    if contact.first_online == None:
                        await event.respond(f'{utc2localtime(account.status.was_online).strftime(DATETIME_FORMAT)}: __{contact.name}__ went offline.', parse_mode="Markdown")
                elif contact.last_offline != account.status.was_online:
                    if contact.last_offline is not None:
                        contact.onlineCount =contact.onlineCount + 1
                        await event.respond(f'{utc2localtime(account.status.was_online).strftime(DATETIME_FORMAT)}: __{contact.name}__ went offline after being online for short time.'
                                            f' ({contact.onlineCount}{" онлайн" if f1(contact.onlineCount) else " онлайна" if f2(contact.onlineCount) else " онлайнов"} {datetime.fromtimestamp(contact.totalOnlineTime).strftime(DATETIME_FORMAT2)})', parse_mode="Markdown")
                    else:
                        await event.respond(f'{utc2localtime(account.status.was_online).strftime(DATETIME_FORMAT)}: __{contact.name}__ went offline.', parse_mode="Markdown")
                contact.last_offline = account.status.was_online
            elif isinstance(account.status, UserStatusOnline):
                if contact.online != True:
                    contact.first_online = datetime.now()
                if contact.online != True:
                    contact.online = True
                    await event.respond(f'{(datetime.now()+timedelta(minutes=180)).strftime(DATETIME_FORMAT)}: __{contact.name}__ went online.', parse_mode="Markdown")
            else:
                if contact.online != False:
                    contact.online = False
                    await event.respond(f'{(datetime.now()+timedelta(minutes=180)).strftime(DATETIME_FORMAT)}: __{contact.name}__ went offline.', parse_mode="Markdown")
                contact.last_offline = None
        delay = 5
        if('delay' in user_data):
            delay = user_data['delay']
        sleep(delay)
    await event.respond(f'Spy gonna zzzzzz...')

@bot.on(events.NewMessage(pattern='^/remove'))
async def remove(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    index = int(person_info[1])
    id = message.from_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']

    if(len(contacts) > index):
        del contacts[index]
        db_object.execute("SELECT * FROM users")
        id_count = db_object.rowcount
        i = index
        int_index = index
        db_object.execute(f'DELETE FROM users WHERE id = {int_index}')
        db_connection.commit()
        while i < id_count:

            db_object.execute(f'UPDATE users SET id = {i} WHERE id = {i+1}')
            i+=1
            db_connection.commit()
        await event.respond(f'User №{index} has been deleted')
    else:
        await event.respond('Incorrect index')

@bot.on(events.NewMessage(pattern='^/setdelay'))
async def setDelay(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    index = int(person_info[1])
    id = message.from_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    print(index)
    if(index >= 0):
        user_data['delay'] = index
        await event.respond(f'Delay has been updated to {index}')
    else:
        await event.respond('Incorrect delay')

@bot.on(events.NewMessage(pattern='^/disconnect$'))
async def disconnect(event):
    await event.respond('Bot gonna disconnect')
    await bot.disconnect()

@bot.on(events.NewMessage(pattern='/list'))
async def list(event):
    message = event.message
    id = message.from_id
    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']
    response = 'List is empty'
    if(len(contacts)):
        response = 'User list: \n'+'\n'.join([str(x) for x in contacts])
    await event.respond(response)

@bot.on(events.NewMessage(pattern='/getall'))
async def getAll(event):
    response = ''
    for key, value in data.items():
        response += f'{key}:\n'
        for j, i in value.items():
            if (isinstance(i, collections.Sequence)):
                response += f'{j}: ' + '\n'.join([str(x) for x in i]) + '\n'
            else:
                response += f'{j}: {i}\n'
        response += '\n'
    await event.respond(response)


    flag = True

@bot.on(events.NewMessage(pattern='^/add'))
async def add(event):
    message = event.message
    person_info = message.message.split()
    print(person_info)
    phone = person_info[1]
    name = person_info[2]
    id = message.from_id

    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']
    contact = Contact(phone, name)
    contacts.append(contact)

    db_object.execute("SELECT * FROM users")
    id_count = db_object.rowcount
    db_object.execute("INSERT INTO users(id, phone, name) VALUES (%s, %s, %s)", (id_count, phone, name))
    id_count +=1
    db_connection.commit()


    await event.respond(f'{name}: {phone} has been added')

@bot.on(events.NewMessage(pattern='^/db_add'))
async def db_add(event):
    message = event.message
    id = message.from_id

    if id not in data:
        data[id] = {}
    user_data = data[id]

    if 'contacts' not in user_data:
        user_data['contacts'] = []
    contacts = user_data['contacts']

    i=0
    db_object.execute("SELECT * FROM users")
    id_count = db_object.rowcount

    while i < id_count:
        db_object.execute(f"SELECT phone, name FROM users where id = {i}")
        result = db_object.fetchone()
        contact = Contact(result[0].strip(), result[1].strip())
        contacts.append(contact)
        i += 1
        db_connection.commit()
    await event.respond('Вся база добавлена!')


def main():
    """Start the bot."""

    client.send_message('tbtest2bot', '/db_add')
    client.send_message('tbtest2bot', '/start')


    bot.run_until_disconnected()

def utc2localtime(utc):

    pivot = mktime(utc.timetuple())
    offset = datetime.fromtimestamp(pivot) - datetime.utcfromtimestamp(pivot)
    a = timedelta(minutes=180)
    return utc + offset + a

def printToFile(str):
    file_name = 'spy_log.txt'
    with open(file_name,'a') as f:
        print(str)
        f.write(str + '\n')

if __name__ == '__main__':
    main()
