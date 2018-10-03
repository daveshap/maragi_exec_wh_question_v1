"""
SUMMARY:
    attempts to answer basic questions using dictionary definitions

INPUT EXCHANGE:
    model_speech

OUTPUT EXCHANGE:
    action_speech
"""

import json
import pika
import nltk
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('tagsets')
nltk.download('wordnet')
input_exchange = 'model_speech'  # I want to listen for recognized speech
output_exchange = 'action_speech'  # I want to say stuff


def maragi_publish(message):
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('maragi-rabbit', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_publish(exchange=output_exchange, body=message, routing_key='')
    channel.close()
    connection.close()


def get_q_tags(question):
    tokens = nltk.word_tokenize(question)
    pos = nltk.pos_tag(tokens)
    return pos


def get_definition(word):
    syns = wordnet.synsets(word)
    return syns[0].definition()


def answer_question(ch, method, properties, body):
    payload = json.loads(body)
    if payload['type'] == 'speech':
        sentence = payload['data']
        if 'what' in sentence or 'when' in sentence or 'why' in sentence or 'where' in sentence or 'who' in sentence:
            tagged = get_q_tags(sentence)
            results = []
            for word in tagged:
                if 'NN' in word[1]:
                    definition = get_definition(word[0])
                    results.append(word[0] + ' ' + definition)
            for r in results:
                payload['data'] = r
                payload['priority'] = 99
                text = json.dumps(payload)
                maragi_publish(text)


def maragi_subscribe():
    parameters = pika.URLParameters('amqp://guest:guest@maragi-rabbit:5672/%2F')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=input_exchange, exchange_type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=input_exchange, queue=queue_name)
    channel.basic_consume(answer_question, queue=queue_name, no_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    while True:
        try:
            maragi_subscribe()
        except Exception as oops:
            print('ERROR:', oops)