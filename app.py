from pathlib import Path
import json

from roll import Roll
from roll.extensions import simple_server

from models import (
  get_user,
  transfer_credit,
  get_transaction,
  create_transaction,
  complete_transaction
)


app = Roll()


@app.route('/')
async def index(request, response):
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    template = Path(__file__).parent / 'index.html'
    with open(template, 'r') as f:
        response.body = f.read()


@app.route('/transaction', methods=['POST'])
async def post_transaction(request, response):
    sender_id = request.headers.get('AUTH')
    if not sender_id:
        raise Exception(f'You must be authenticated')
    amount = int(request.json.get('amount'))
    if not 0 < amount <= 1000:
        raise Exception(f'Amount must be between 1 and 1000. It is {amount}.')
    transaction_id = create_transaction(sender_id, amount)
    response.body = json.dumps({"url": f'/transaction/{transaction_id}'})



@app.route('/transaction/{id}')
async def get_transation(request, response, id):
    transaction = get_transaction(id)
    if not transaction:
        raise Exception(f'No transaction matches {id}')
    sender = get_user(transaction[1])
    if not sender:
        raise Exception(f'No sender found for {transaction[1]}')
    amount = int(transaction[3])
    name = f'{sender[1]} {sender[2]}'

    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    template = Path(__file__).parent / 'transaction.html'
    with open(template, 'r') as f:
        response.body = f.read() \
          .replace('{amount}', str(amount)) \
          .replace('{user}', name) \
          .replace('{id}', id)


@app.route('/transaction/{id}', methods=['PATCH'])
async def patch_transation(request, response, id):
    recipient_id = request.headers.get('AUTH')
    if not recipient_id:
        raise Exception(f'You must be authenticated')
    # import ipdb; ipdb.set_trace()
    [uid, sender_id, _, amount] = get_transaction(id)[:4]
    if not uid:
        raise Exception(f'No transaction matches {id}')
    complete_transaction(uid, recipient_id)
    transfer_credit(sender_id, recipient_id, amount)


if __name__ == '__main__':
    simple_server(app)
