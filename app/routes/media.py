from flask import Blueprint, jsonify

bp = Blueprint('media', __name__, url_prefix='/media')

@bp.route('/refresh', methods=['POST'])
def refresh():
    # TODO: Implement actual refresh logic
    return jsonify({
        'status': 'ok',
        'message': 'Media refresh endpoint - TODO: Implement actual refresh logic'
    }) 