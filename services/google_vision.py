import os

from google.cloud import vision


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/rodrigo/projects/julius-bot/.key.json'


def detect_text(content):
    image = vision.types.Image(content=content)
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    texts = response.text_annotations
    full_text = ''
    for text in texts:
        full_text = ''.join('{} {}'.format(full_text, text.description))
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return full_text
