from PIL import Image
import pytesseract


class OCRTotal(object):

    def valor_colon_decoder(self, text):
        pass

    def valor_pago_decoder(self, text):
        pass

    def valor_pago_colon_decoder(self, text):
        pass

    def debito_a_vista_decoder(self, text):
        pass

    def total_reais_decoder(self, text):
        pass

    def __init__(self):
        self.decoders = {'Valor:': self.valor_colon_decoder, 'Valor Pago': self.valor_pago_decoder,
                         'Valor Pago:': self.valor_pago_colon_decoder, 'DEBITO A VISTA': self.debito_a_vista_decoder,
                         'TOTAL R$': self.total_reais_decoder}

    def look_for_value(self, text):
        for key in self.decoders.keys():
            text.find(key)


def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(Image.open(filename)).split('\n\n')
    pos = 0
    try:
        pos = text.index('Valor:')
        value = text[pos + 1].replace('RS ', '/gasto ')
        value = value.replace('R$ ', '/gasto ')
        return value
    except Exception:
        try:
            pos = text.index('Valor Pago')
            value = text[pos + 1].replace('RS ', '/gasto ')
            value = value.replace('R$ ', '/gasto ')
            return value
        except Exception:
            arr = []
            for item in text:
                if len(item.split('\n')) > 1:
                    splitted = item.split('\n')
                    if splitted[0] == 'Valor Pago:':
                        return item.split('\n')[1].replace('RS ', '/gasto ')
