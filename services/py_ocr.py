from services.google_vision import detect_text


class CustomOCR(object):

    def __init__(self, image):
        self.decoders = {'Valor Pago:': self.valor_pago_colon_decoder,
                         'Valor Pago': self.valor_pago_decoder,
                         'Valor:': self.valor_colon_decoder,
                         'Valor': self.valor_decoder,
                         'DEBITO A VISTA': self.debito_a_vista_decoder,
                         'CREDITO A VISTA': self.credito_a_vista_decoder}
        self.text = detect_text(image)
        self.command = self.text_to_command()

    @property
    def full_text(self):
        return self.text

    @full_text.setter
    def text_command(self, text):
        self.text = text

    @property
    def text_command(self):
        return self.command

    @text_command.setter
    def text_command(self, command):
        self.command = command

    def valor_decoder(self, text):
        text = text.split('\n')
        value = text[1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_colon_decoder(self, text):
        text = text.split('\n')
        value = text[1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_pago_decoder(self, text):
        text = text.split('\n')
        value = text[1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_pago_colon_decoder(self, text):
        text = text.split('\n')
        value = text[1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def debito_a_vista_decoder(self, text):
        text = text.split('\n')
        return '/gasto {}'.format(text[1])

    def credito_a_vista_decoder(self, text):
        text = text.split('\n')
        return '/gasto {}'.format(text[1])

    def text_to_command(self):
        for key in self.decoders.keys():
            result = self.text.find(key)
            if result > -1:
                return self.decoders[key](self.text[result:])
