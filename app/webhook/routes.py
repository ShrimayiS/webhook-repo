from flask import Blueprint, json, jsonify, request
import pymongo
from app.webhook.extensions import mongo
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')
from datetime import datetime
# @webhook.route('/receiver', methods=["POST"])
# def receiver():
#     return {}, 200
# @webhook.route('/receiver2', methods=["POST"])
# def receiver2():
#     data = request.json
#     event_type = request.headers.get('X-GitHub-Event')
#     event_data = {
#         'timestamp': datetime.utcnow().isoformat() + 'Z'  # ISO format with UTC 'Z' notation
#     }

#     if event_type == 'push':
#         event_data.update({
#             'request_id': data['after'],
#             'author': data['pusher']['name'],
#             'action': 'PUSH',
#             'to_branch': data['ref'].split('/')[-1]
#         })
#     elif event_type == 'pull_request':
#         event_data.update({
#             'request_id': data['pull_request']['id'],
#             'author': data['pull_request']['user']['login'],
#             'action': 'PULL_REQUEST',
#             'from_branch': data['pull_request']['head']['ref'],
#             'to_branch': data['pull_request']['base']['ref']
#         })
#     elif event_type == 'merge' and data['pull_request']['merged']:
#         event_data.update({
#             'request_id': data['pull_request']['id'],
#             'author': data['pull_request']['merged_by']['login'],
#             'action': 'MERGE',
#             'from_branch': data['pull_request']['head']['ref'],
#             'to_branch': data['pull_request']['base']['ref']
#         })
#     else:
#         return jsonify({"message": "Event type not supported"}), 400

#     mongo.db.events.insert_one(event_data)
#     return jsonify({"message": "Event received"}), 200

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    event_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z'  # ISO format with UTC 'Z' notation
    }

    if event_type == 'push':
        event_data.update({
            'request_id': data['after'],
            'author': data['pusher']['name'],
            'action': 'PUSH',
            'to_branch': data['ref'].split('/')[-1]
        })
    elif event_type == 'pull_request':
        pr_action = data['action']
        if pr_action == 'closed' and data['pull_request']['merged']:
            # Handle merge event
            event_data.update({
                'request_id': data['pull_request']['id'],
                'author': data['pull_request']['merged_by']['login'],
                'action': 'MERGE',
                'from_branch': data['pull_request']['head']['ref'],
                'to_branch': data['pull_request']['base']['ref']
            })
        else:
            # Handle other pull request events
            event_data.update({
                'request_id': data['pull_request']['id'],
                'author': data['pull_request']['user']['login'],
                'action': 'PULL_REQUEST',
                'from_branch': data['pull_request']['head']['ref'],
                'to_branch': data['pull_request']['base']['ref']
            })
    else:
        return jsonify({"message": "Event type not supported"}), 400

    mongo.db.events.insert_one(event_data)
    return jsonify({"message": "Event received"}), 200

@webhook.route('/', methods=["GET"])
def receiver2():
    return {}, 200

@webhook.route('/events', methods=["GET"])
def get_events():
    events = mongo.db.events.find().sort('timestamp', pymongo.DESCENDING)
    event_list = []
    for event in events:
        event_list.append({
            'request_id': event['request_id'],
            'author': event['author'],
            'action': event['action'],
            'from_branch': event.get('from_branch', ''),
            'to_branch': event['to_branch'],
            'timestamp': event['timestamp']
        })
    return jsonify(event_list)
