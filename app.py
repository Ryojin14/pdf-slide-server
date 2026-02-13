import base64
import requests
from flask import Flask, render_template, request, jsonify
import os

# ▼▼▼ [핵심 1] 운전기사(변환 함수) 강제 소환 ▼▼▼
try:
    from converter import convert_pdf_to_video
except ImportError as e:
    print(f"❌ converter.py 임포트 실패: {e}")
    # 에러가 나도 서버가 꺼지지 않게 임시 함수 생성 (로그 확인용)
    def convert_pdf_to_video(path, out):
        print("함수가 연결되지 않았습니다. requirements.txt를 확인하세요.")
        return False

app = Flask(__name__)

# ▼▼▼ [핵심 2] 사용자님이 지적하신 저장소 정보 수정 ▼▼▼
# 스크린샷 보고 맞춘 정보입니다. 틀리면 수정해주세요!
GITHUB_TOKEN = "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"  # (여기는 본인 토큰 그대로 두세요!)
REPO_OWNER = "Ryojin14"        # 사용자님 아이디
REPO_NAME = "pdf-slide-server" # 새로 만든 저장소 이름!

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files: return jsonify({'error': '파일 없음'}), 400
    file = request.files['pdf_file']
    if file.filename == '': return jsonify({'error': '선택된 파일 없음'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    output_video = os.path.join(OUTPUT_FOLDER, 'presentation.mp4')

    # 변환 시도
    if convert_pdf_to_video(filepath, output_video):
        try:
            video_url = upload_to_github(output_video)
            return jsonify({'message': '성공', 'video_url': video_url})
        except Exception as e:
            return jsonify({'error': f'변환 성공, 업로드 실패: {str(e)}'})
    else:
        return jsonify({'error': 'PDF 변환 실패 (로그 확인 필요)'}), 500

def upload_to_github(file_path):
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    file_name = "presentation.mp4" # 파일명 고정
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None

    data = {"message": "Update via Render", "content": content}
    if sha: data["sha"] = sha

    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{file_name}"
    else:
        raise Exception(f"GitHub 오류: {response.text}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)