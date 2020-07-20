import pytz
from datetime import datetime
from decimal import Decimal
from flask import Flask, request
import telegram
from telebot.credentials import bot_token, URL, port
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
finances_ref = db.collection('finances')
balances_ref = db.collection('balances')
global bot
global TOKEN

TOKEN = bot_token
bot = telegram.Bot(token=bot_token)
app = Flask(__name__)


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    json_dict = request.get_json(force=True)
    if json_dict.get('message', None) is None:
        print(json_dict)
        return 'ok'
    if json_dict.get('message', None).get('text', None) is None:
        print(json_dict)
        return 'ok'
    incoming_msg = json_dict['message']['text']
    if not incoming_msg.startswith('/'):
        return 'ok'
    chat_id = json_dict['message']['chat']['id']
    id = str(chat_id)
    msg_id = json_dict['message']['message_id']
    name = json_dict['message']['from']['first_name']
    finance = finances_ref.document(id).get().to_dict()
    if finance is None:
        finance_object = {"amount": 0.0, "spent": 0.0, "available": 0.0}
        balance_object = {"closures": []}
        finances_ref.document(str(chat_id)).set(finance_object)
        balances_ref.document(str(chat_id)).set(balance_object)
        response = '<b>Olá {}, seus dados foram corretamente criados, digite /start para começar...</b>'.format(name)
        finance = finances_ref.document(id).get().to_dict()
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/gasto'):
        if finance['amount'] == 0.0:
            response = "Antes de qualquer outro comando o objetivo de ser adicionado, use /objetivo valor"
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        if len(incoming_msg) < 8:
            response = '<i>Hum, esse comando precisa de um valor...</i>'
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        spent = Decimal(finance['spent'])
        new_spent = spent + Decimal((incoming_msg[7:].replace(',', '.')))
        new_available = Decimal(finance['amount']) - new_spent
        finance['spent'] = round(float(new_spent), 2)
        finance['available'] = round(float(new_available), 2)
        finances_ref.document(id).update(finance)
        if finance['available'] < 0.0:
            response = "Olá!, você já gastou <b>R${}</b>, de <b>R${}</b>, está NEGATIVO em <b>-R${}</b>, objetivo não foi atingido 😔".format(
                finance['spent'],
                finance['amount'],
                abs(finance['available']))
        else:
            response = "Olá!, você já gastou <b>R${}</b>, de <b>R${}</b>, ainda tem <b>R${}</b> para gastar, se você não comprar o desconto é maior 👀".format(finance['spent'],
                                                                                                              finance['amount'],
                                                                                                              finance['available'])
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg in ('/start', '/help', '/ajuda', '/tutorial'):
        response = """
        <b>
        Olá, eu sou Virtual Julius,...
        Seu assistente financeiro pessoal 💸
        </b>
        Comece verificando seu saldo com o comando /saldo
        Em seguida adicione seu objetivo de gastos para o mês
        com o comando /objetivo seguido do valor ex: /objetivo 1000
        Depois é só ir incluir gastos com o comando /gasto valor
        Valor com virgula ou ponto, ex: /gasto 12,99 ou /gasto 12.99
        Para recomeçar quando trocar o mês use o comando 
        /fechamento e em seguida adicione seu novo objetivo para 
        o mês com o comando /objetivo valor
        Para ver o seu histórico de fechamentos digite /histórico
        Viu como é fácil... 🕺
        """.format(name)
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/saldo'):
        response = "Olá!, você já gastou <b>R${}</b>, de <b>R${}</b>, ainda tem <b>R${}</b> para gastar, se você não comprar o desconto é maior 👀".format(finance['spent'],
                                                                                                              finance['amount'],
                                                                                                              finance['available'])
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/objetivo'):
        if len(incoming_msg) < 11:
            response = '<i>Hum, esse comando precisa de um valor...</i>'
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        if finance['amount'] != 0.0:
            response = "Já existe um objetivo em andamento, se o mês mudou use o comando /fechamento antes"
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        finance['amount'] = float((incoming_msg[9:].replace(',', '.')))
        finance['available'] = finance['amount'] - finance['spent']
        finances_ref.document(id).update(finance)
        response = "Olá!, seu novo objetivo foi setado para <b>R${}</b>".format(finance['amount'])
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/histórico'):
        balance = balances_ref.document(id).get().to_dict()
        closures = balance['closures']
        if len(closures) == 0:
            response = "Você ainda não tem nenhum fechamento..."
            bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        response = 'Fechamentos:'
        for closure in closures:
            response += '''
            -----------------------------------
            Data: {}
            Objetivo {}
            Despesas: {}
            Saldo Final {}'''.format(closure['date'].strftime("%d/%m/%Y %H:%M"), closure['closure']['amount'], closure['closure']['spent'],
                       closure['closure']['available'])
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/fechamento'):
        if finance['spent'] == 0.0:
            response = "Para realizar o fechamento adicione pelo menos um gasto..."
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        closure = {
            "date": datetime.now(pytz.timezone("America/Sao_Paulo")),
            "closure": finance
        }
        balance = balances_ref.document(id).get().to_dict()
        balance['closures'].append(closure)
        balances_ref.document(id).update(balance)
        finance['spent'] = 0.0
        finance['amount'] = 0.0
        finance['available'] = 0.0
        finances_ref.document(id).update(finance)
        response = "<b>Olá!, passado é passado, tudo pronto para o próximo mês 🗓</b>️, não se esqueça de adicionar o objetivo  mensal 📝"
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    bot.sendMessage(chat_id=chat_id, text='Comando não encontrado, /start mostra os comandos disponíveis...', parse_mode=telegram.ParseMode.HTML)
    return 'nok'


@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup to {} is okay now".format(URL)
    else:
        return "webhook setup to  {} failed!!!".format(URL)


@app.route('/', methods=['GET'])
def index():
    return "It's ALIVE!, listening on:{}".format(URL)


if __name__ == '__main__':
    app.run(threaded=True)
