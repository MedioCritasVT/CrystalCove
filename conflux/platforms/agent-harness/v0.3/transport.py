#!/usr/bin/env python3
"""Small VOS RabbitMQ/Ollama harness. Requires pika==1.3.2.

worker --node 1 : process tasks for node 1
ask --node 1 'prompt' : send a task and wait for its result

Environment: VOS_RABBIT_PASSWORD (required), VOS_RABBIT_HOST,
VOS_RABBIT_USER, VOS_MODEL, VOS_OLLAMA_URL (worker override).
Tasks accept text chat history from the WebUI Pipe or a CLI prompt. No tool execution.
Delivery is at least once; a broker interruption can repeat inference.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
import signal
import time
import uuid
from urllib.request import Request, urlopen

import pika

EXCHANGE = 'vos_v03_exchange'


def connect():
    password = os.environ.get('VOS_RABBIT_PASSWORD')
    if not password:
        raise ValueError('VOS_RABBIT_PASSWORD is empty; enter/export it first.')
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=os.getenv('VOS_RABBIT_HOST', 'message_board_rabbitmq'),
        credentials=pika.PlainCredentials(
            os.getenv('VOS_RABBIT_USER', 'vos_worker'), password),
        heartbeat=60, blocked_connection_timeout=30,
        socket_timeout=10, connection_attempts=3, retry_delay=2))


def topology(channel, node):
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=True)
    queue = f'vos_v03_tasks_node{node}'
    status = channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(queue=queue, exchange=EXCHANGE, routing_key=f'agent.node{node}')
    channel.queue_bind(queue=queue, exchange=EXCHANGE, routing_key='agent.all')
    return queue, status.method.consumer_count


def infer(node, messages, tools=None):
    url = os.getenv('VOS_OLLAMA_URL', f'http://ollama_node_{node}:11434')
    payload = {
        'model': os.getenv('VOS_MODEL', 'qwen3.5:4b'),
        'messages': messages,
        'stream': False, 'think': False,
        'options': {'num_predict': 1024},
    }
    if tools:
        payload['tools'] = tools
    request = Request(url.rstrip('/') + '/api/chat',
                      data=json.dumps(payload).encode(),
                      headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=600) as response:
        result = json.load(response)
    if result.get('error'):
        raise RuntimeError(result['error'])
    return result['message']


def publish(channel, key, payload, correlation_id):
    channel.basic_publish(
        exchange=EXCHANGE, routing_key=key,
        body=json.dumps(payload).encode(), mandatory=True,
        properties=pika.BasicProperties(content_type='application/json',
                                        delivery_mode=2,
                                        correlation_id=correlation_id))


def worker(connection, channel, node, queue):
    channel.basic_qos(prefetch_count=1)
    with ThreadPoolExecutor(max_workers=1) as executor:
        def callback(ch, method, properties, body):
            try:
                task = json.loads(body)
                task_id = task['id']
                if not isinstance(task_id, str) or not task_id.isalnum():
                    raise ValueError('Invalid task id')
                messages = task.get('messages')
                if messages is None:
                    messages = [{'role': 'user', 'content': task['prompt']}]
                if not isinstance(messages, list) or not messages:
                    raise ValueError('Missing messages')
                for message in messages:
                    if (not isinstance(message, dict) or
                        message.get('role') not in ('system', 'user', 'assistant', 'tool') or
                        not isinstance(message.get('content'), str)):
                        raise ValueError('Only text chat messages are supported')
            except (ValueError, KeyError, TypeError):
                print('Rejected malformed task', flush=True)
                ch.basic_nack(method.delivery_tag, requeue=False)
                return
            print(f'[node {node}] Received {task_id}', flush=True)
            result = {'id': task_id, 'node': node}
            future = executor.submit(infer, node, messages, task.get('tools'))
            # Keep the RabbitMQ connection alive while Ollama generates.
            while not future.done():
                connection.sleep(0.2)
            try:
                result['message'] = future.result()
            except Exception as exc:
                result['error'] = str(exc)
            try:
                publish(ch, f'result.{task_id}', result, task_id)
            except pika.exceptions.UnroutableError:
                # The requester timed out or disconnected; don't loop forever.
                print(f'[node {node}] Requester gone: {task_id}', flush=True)
            ch.basic_ack(method.delivery_tag)
            print(f'[node {node}] Finished {task_id}', flush=True)
        channel.basic_consume(queue=queue, on_message_callback=callback)
        print(f'READY: node {node} listening on {queue}', flush=True)
        channel.start_consuming()


def ask(connection, channel, node, consumers, prompt):
    if consumers < 1:
        raise RuntimeError(f'No worker is listening for node {node}. Check worker logs.')
    task_id = uuid.uuid4().hex
    queue = f'vos_reply_{task_id}'
    channel.queue_declare(queue=queue, exclusive=True, auto_delete=True)
    channel.queue_bind(queue=queue, exchange=EXCHANGE, routing_key=f'result.{task_id}')
    replies = []
    def received(ch, method, properties, body):
        replies.append(json.loads(body))
        ch.basic_ack(method.delivery_tag)
    channel.basic_consume(queue=queue, on_message_callback=received)
    publish(channel, f'agent.node{node}', {'id': task_id, 'prompt': prompt}, task_id)
    print(f'Task sent to node {node}. Waiting for Ollama...', flush=True)
    deadline = time.monotonic() + 660
    while not replies and time.monotonic() < deadline:
        connection.process_data_events(time_limit=1)
    if not replies:
        raise TimeoutError('No reply after 11 minutes. Check the worker logs.')
    result = replies[0]
    if 'error' in result:
        raise RuntimeError('Ollama worker reported: ' + result['error'])
    print(f"\nNode {node}:\n{result['message'].get('content', '')}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['worker', 'ask'])
    parser.add_argument('--node', type=int, choices=range(1, 5), default=1)
    parser.add_argument('prompt', nargs='?')
    args = parser.parse_args()
    if args.mode == 'ask' and not args.prompt:
        parser.error('ask requires a quoted prompt')
    connection = connect()
    try:
        channel = connection.channel()
        queue, consumers = topology(channel, args.node)
        channel.confirm_delivery()
        if args.mode == 'worker':
            worker(connection, channel, args.node, queue)
        else:
            ask(connection, channel, args.node, consumers, args.prompt)
    finally:
        if connection.is_open:
            connection.close()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
