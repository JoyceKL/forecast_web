from flask import Blueprint, request, jsonify
import os

explain_bp = Blueprint('explain_bp', __name__)

@explain_bp.route('/explain', methods=['POST'])
def explain():
    topic = request.form.get('topic', 'minmax')
    file_path = os.path.join('docs', f'{topic}.md')
    if not os.path.exists(file_path):
        return jsonify({'markdown': f'## Không tìm thấy giải thích cho `{topic}`'})
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'markdown': content})
