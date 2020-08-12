from PIL import Image
import pytesseract


class CustomOCR(object):

    def __init__(self, image):
        self.decoders = {'Valor Pago:': self.valor_pago_colon_decoder,
                         'Valor Pago': self.valor_pago_decoder,
                         'Valor:': self.valor_colon_decoder,
                         'Valor': self.valor_decoder,
                         'DEBITO A VISTA': self.debito_a_vista_decoder}
        self.text = pytesseract.image_to_string(Image.open(image))

    def valor_decoder(self, text):
        text = text.split('\n\n')
        pos = text.index('Valor:')
        value = text[pos + 1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_colon_decoder(self, text):
        text = text.split('\n\n')
        pos = text.index('Valor:')
        value = text[pos + 1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_pago_decoder(self, text):
        text = text.split('\n\n')
        pos = text.index('Valor Pago')
        value = text[pos + 1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def valor_pago_colon_decoder(self, text):
        text = text.split('\n')
        pos = text.index('Valor Pago:')
        value = text[pos + 1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value

    def debito_a_vista_decoder(self, text):
        return '/gasto {}'.format(text[15:].split('\n')[0])

    def text_to_command(self):
        for key in self.decoders.keys():
            result = self.text.find(key)
            if result > -1:
                return self.decoders[key](self.text[result:])


ocr = CustomOCR('/home/rodrigo/projects/julius-bot/teste02.jpg')
command = ocr.text_to_command()
print(command)
