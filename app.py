import base64
import requests
from flask import Flask, render_template, request, jsonify
import os
import sys

# 방금 수정한 converter.py 불러오기
try:
    from converter import convert_pdf_to_video
except ImportError:
    print("❌ converter.py 파일이 없거나 함수 이름이 다릅니다!")

app = Flask(__name__)

# ==========================================
# [설정] 여기에 본인 정보를 입력하세요! (따옴표 유지)
# ==========================================
GITHUB_TOKEN = "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"  
REPO_OWNER = "Ryojin14"     
REPO_NAME = "Slide_Assets"
# ==========================================

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

    # 파일 저장
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # 변환된 영상 경로
    output_video = os.path.join(OUTPUT_FOLDER, 'presentation.mp4')

    # 1. 영상 변환
    if convert_pdf_to_video(filepath, output_video):
        # 2. 깃허브 업로드
        try:
            video_url = upload_to_github(output_video)
            return jsonify({
                'message': '✅ 변환 및 깃허브 업로드 성공!', 
                'video_url': video_url
            })
        except Exception as e:
            return jsonify({'message': '변환은 됐는데 업로드 실패..', 'error': str(e)})
    else:
        return jsonify({'error': '변환 실패'}), 500

def upload_to_github(file_path):
    # 파일을 읽어서 깃허브가 좋아하는 형식(Base64)으로 포장
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # 업로드할 주소 만들기
    file_name = os.path.basename(file_path)
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # "혹시 이미 파일이 있나요?" 확인 (덮어쓰기 위해)
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None

    # 업로드 데이터 준비
    data = {
        "message": "Update slide video via Web",
        "content": content
    }
    if sha: data["sha"] = sha # 기존 파일이 있으면 교체

    # 전송!
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        # VRChat 비디오 플레이어용 'Raw' 주소 반환
        return f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{file_name}"
    else:
        raise Exception(f"GitHub 오류: {response.text}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)