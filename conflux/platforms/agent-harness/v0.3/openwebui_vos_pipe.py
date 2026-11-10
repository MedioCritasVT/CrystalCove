"""
title: Conflux VOS Harness
description: Shared board and bounded peer requests through the VOS controller.
version: 0.3.0
"""
import html
import json
import httpx
from pydantic import BaseModel, Field


class Pipe:
    class Valves(BaseModel):
        HARNESS_URL: str = Field(default='http://vos_v03_coordinator:8080')
        RABBIT_PASSWORD: str = Field(default='', description='Existing vos_worker password; also authenticates this local controller.', json_schema_extra={'format': 'password'})
        TIMEOUT_SECONDS: int = Field(default=960, ge=30, le=1800)

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        return [{'id': f'node{i}', 'name': f'VOS Node {i} — shared board + tools'} for i in range(1, 5)]

    async def pipe(self, body: dict, __task__: str = None):
        node_id = body.get('model', '').rsplit('.', 1)[-1]
        if node_id not in {f'node{i}' for i in range(1, 5)}:
            raise ValueError('Select a VOS Node model.')
        if not self.valves.RABBIT_PASSWORD:
            raise ValueError('Enter the existing RabbitMQ password in Admin Panel → Functions → Valves.')
        messages = []
        for item in body.get('messages', []):
            content = item.get('content')
            if isinstance(content, list):
                if any(part.get('type') != 'text' for part in content):
                    raise ValueError('Text only for now. Start a new chat without images or attachments.')
                content = '\n'.join(part.get('text', '') for part in content)
            if item.get('role') not in ('system', 'user', 'assistant') or not isinstance(content, str):
                raise ValueError('Only ordinary text chat history is supported.')
            messages.append({'role': item['role'], 'content': content})
        if not messages:
            raise ValueError('No messages were provided.')
        last = next((m['content'].strip() for m in reversed(messages) if m['role'] == 'user'), '')
        url = self.valves.HARNESS_URL.rstrip('/')
        headers = {'Authorization': 'Bearer ' + self.valves.RABBIT_PASSWORD}
        async with httpx.AsyncClient(timeout=self.valves.TIMEOUT_SECONDS) as client:
            if not __task__ and last in ('/board', '/receipts'):
                path = '/notes' if last == '/board' else '/events'
                response = await client.get(url + path, headers=headers)
                response.raise_for_status()
                # Escaped raw server data, not a model-generated account of the board.
                return '<pre>' + html.escape(json.dumps(response.json(), indent=2, ensure_ascii=False)) + '</pre>'
            response = await client.post(url + '/chat', headers=headers, json={
                'node': int(node_id[-1]), 'messages': messages, 'use_tools': not bool(__task__)})
            response.raise_for_status()
            result = response.json()
        answer = result.get('answer', result.get('error', 'No response.'))
        if not __task__:
            trace = result.get('trace', [])
            if trace:
                answer += '\n\n<details><summary>Harness receipts — actual tool results</summary><pre>'
                answer += html.escape(json.dumps({'request_id': result.get('request_id'), 'tools': trace}, indent=2, ensure_ascii=False))
                answer += '</pre></details>'
            else:
                answer += '\n\n*Harness: no tools were executed for this reply.*'
        return answer
