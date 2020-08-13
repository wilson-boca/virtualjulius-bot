import pytz
import firebase_admin
import telegram
import requests
import pathlib

from os import getenv
from datetime import datetime
from decimal import Decimal
from flask import Flask, request
from flask_cors import CORS

from telebot.credentials import bot_token, URL
from firebase_admin import credentials, firestore
from services.py_ocr import CustomOCR
from PIL import Image

pvt_key = getenv('private_key').replace('|', '\n').replace('\\=', '=')
credential_json = {
  "type": "service_account",
  "project_id": "virtualjulius-bot",
  "private_key_id": getenv('private_key_id'),
  "private_key": pvt_key,
  "client_email": getenv('client_email'),
  "client_id": getenv('client_id'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": getenv('client_x509_cert_url')
}
folder = pathlib.Path(__file__).parent
print('Docker path: {}'.format(folder))
cred = credentials.Certificate(credential_json)
firebase_admin.initialize_app(cred)
db = firestore.client()
finances_ref = db.collection('finances')
balances_ref = db.collection('balances')
global bot
global TOKEN

TOKEN = bot_token
bot = telegram.Bot(token=bot_token)
app = Flask(__name__)
CORS(app)


def process_image(file_id, chat_id):
    url = 'https://api.telegram.org/bot{}/getFile?file_id={}'.format(TOKEN, file_id)
    result = requests.get(url)
    bot.sendMessage(chat_id=chat_id, text=result.status_code, parse_mode=telegram.ParseMode.HTML)
    file_path = result.json()['result']['file_path']
    file_url = 'https://api.telegram.org/file/bot{}/{}'.format(TOKEN, file_path)
    bot.sendMessage(chat_id=chat_id, text=file_url, parse_mode=telegram.ParseMode.HTML)
    image = Image.open(requests.get(file_url, stream=True).raw)
    bot.sendMessage(chat_id=chat_id, text=image.format, parse_mode=telegram.ParseMode.HTML)
    ocr = CustomOCR(image)
    bot.sendMessage(chat_id=chat_id, text=ocr.command, parse_mode=telegram.ParseMode.HTML)
    bot.sendMessage(chat_id=chat_id, text=ocr.full_text, parse_mode=telegram.ParseMode.HTML)
    return ocr.command


@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    json_dict = request.get_json(force=True)
    if 'photo' in json_dict['message']:
        result = process_image(json_dict['message']['photo'][-1]['file_id'], json_dict['message']['chat']['id'])
        if result:
            json_dict['message']['text'] = result
    if json_dict.get('message', None) is None:
        return 'ok'
    if json_dict.get('message', None).get('text', None) is None:
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
        finance_object = {"income": 0.0, "spent": 0.0, "available": 0.0}
        balance_object = {"closures": []}
        finances_ref.document(str(chat_id)).set(finance_object)
        balances_ref.document(str(chat_id)).set(balance_object)
        response = '<b>Olá {}, seus dados foram corretamente criados, para aprender a usar digite /ajuda</b>'.format(name)
        finance = finances_ref.document(id).get().to_dict()
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/entrada'):
        if len(incoming_msg) < 10:
            response = '<i>Hum, esse comando precisa de um valor...</i>'
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        income = Decimal(finance['income'])
        extra = Decimal((incoming_msg[9:].replace(',', '.')))
        income_extra = income + extra
        new_available = Decimal(finance['available']) + extra
        finance['income'] = round(float(income_extra), 2)
        finance['available'] = round(float(new_available), 2)
        finances_ref.document(id).update(finance)
        response = "Uhul!, você recebeu uma entrada de {}, continue assim...".format(extra)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/gasto'):
        if len(incoming_msg) < 8:
            response = '<i>Hum, esse comando precisa de um valor...</i>'
            bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        spent = Decimal(finance['spent'])
        new_spent = spent + Decimal((incoming_msg[7:].replace(',', '.')))
        new_available = Decimal(finance['income']) - new_spent
        finance['spent'] = round(float(new_spent), 2)
        finance['available'] = round(float(new_available), 2)
        finances_ref.document(id).update(finance)
        if finance['available'] < 0.0:
            response = "Olá!, você já gastou <b>R${}</b> de <b>R${}</b>, e está NEGATIVO em <b>-R${}</b>, acho melhor não comprar mais 😔".format(
                finance['spent'],
                finance['income'],
                abs(finance['available']))
        else:
            response = "Olá!, você já gastou <b>R${}</b>, de <b>R${}</b>, ainda tem <b>R${}</b> para gastar, se você não comprar o desconto é maior 👀".format(finance['spent'],
                                                                                                              finance['income'],
                                                                                                              finance['available'])
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg in ('/start', '/ajuda'):
        response = """
        <b>
        Olá, eu sou o Julius, seu assistente pessoal financeiro 💸
        </b>
        Eu consigo entender algumas palavras que começam com /
        Por exemplo, para que eu saiba que você recebeu algum
        valor digite /entrada seguido do valor ex: /entrada 500
        Comece adicionando sua renda líquida mensal!
        Quando gastar digite /gasto valor, ex: /gasto 12,99
        ou /gasto 12.99
        Não se preocupe eu vou calcular tudo pra você...
        Para fechar o mês e zerar suas contas use /fechamento
        Para ver o histórico de fechamentos digite /histórico
        O seu saldo pode ser consultado sempre com /saldo
        Isso é tudo, viu como é fácil... 🕺
        """.format(name)
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/saldo'):
        response = "Olá!, você já gastou <b>R${}</b>, de <b>R${}</b>, ainda tem <b>R${}</b> para gastar, se você não comprar o desconto é maior 👀".format(finance['spent'],
                                                                                                              finance['income'],
                                                                                                              finance['available'])
        bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
        return 'ok'
    if incoming_msg.startswith('/histórico'):
        balance = balances_ref.document(id).get().to_dict()
        closures = balance['closures']
        if len(closures) == 0:
            response = "Você ainda não tem nenhum fechamento..."
            bot.sendMessage(chat_id=chat_id, text=response, parse_mode=telegram.ParseMode.HTML)
            return 'ok'
        response = 'Histórico de Fechamentos:'
        for closure in closures:
            response += '''
            -----------------------------------
            Data: {}
            Objetivo {}
            Despesas: {}
            Saldo Final {}'''.format(closure['date'].strftime("%d/%m/%Y %H:%M"), closure['closure']['income'], closure['closure']['spent'],
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
        finance['income'] = 0.0
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
