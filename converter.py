import fitz  # PyMuPDF
import os
import shutil
import subprocess
import imageio_ffmpeg # 엔진 위치 찾는 용도

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "engine_direct_frames"
    try:
        # 1. 청소 및 폴더 생성
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        page_count = len(doc)
        print(f"🔥 [엔진 직통 모드] 총 {page_count}페이지 처리 시작", flush=True)

        # 2. 이미지 파일로 저장 (파일명: frame_0000.png, frame_0001.png...)
        # 메모리에 담아두지 않고 바로바로 저장해서 RAM을 아낍니다.
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # 화질 1.5배 (이제 버틸 수 있음)
            filename = os.path.join(temp_dir, f"frame_{i:04d}.png")
            pix.save(filename)
        
        doc.close()

        # ★핵심 해결책: 패딩(Padding) 추가★
        # 마지막 페이지가 1페이지로 튀는 현상 방지용 (마지막 장을 1초 더 연장)
        last_frame_src = os.path.join(temp_dir, f"frame_{page_count-1:04d}.png")
        last_frame_dst = os.path.join(temp_dir, f"frame_{page_count:04d}.png")
        shutil.copy(last_frame_src, last_frame_dst)
        print("🛡️ 마지막 페이지 패딩(Padding) 적용 완료", flush=True)

        # 3. FFmpeg 엔진 직접 호출 (메모리 우회)
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # 명령어 설계:
        # -framerate 1 : 1초에 그림 1장씩 읽어라
        # -r 30 : 출력은 30fps로 뻥튀기해라 (VRChat 호환성)
        # -bf 0 : 앞뒤 참조 하지 마라 (잔상/튐 방지)
        # -g 15 : 0.5초마다 키프레임 박아라 (탐색 최적화)
        command = [
            ffmpeg_exe,
            "-y", # 덮어쓰기 허용
            "-framerate", "1", 
            "-i", os.path.join(temp_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-r", "30", 
            "-pix_fmt", "yuv420p",
            "-bf", "0",
            "-g", "15",
            "-profile:v", "baseline",
            "-preset", "ultrafast",
            output_path
        ]

        print("🚀 엔진 가동! (초고속 변환)", flush=True)
        
        # 파이썬은 여기서 구경만 하고, 실제 일은 C++ 엔진이 수행함 (타임아웃 안 걸림)
        subprocess.run(command, check=True)
        
        print("✅ [완료] 변환 성공. 서버 살아있음.", flush=True)
        return True

    except Exception as e:
        print(f"❌ [엔진 오류]: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)