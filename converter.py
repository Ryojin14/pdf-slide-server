import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip
import shutil
import re # 숫자 정렬용

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "final_fix_frames"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"📦 [안정화 모드] {len(doc)}페이지 변환 시작", flush=True)

        frame_files = []
        for i, page in enumerate(doc):
            # 해상도를 1.0으로 고정하여 메모리 안정성 확보
            pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            pix.save(frame_path)
            frame_files.append(frame_path)
        
        doc.close()

        # [핵심] 파일명을 숫자 순서대로 정렬 (10페이지가 1페이지 뒤로 가는 현상 방지)
        frame_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

        # 영상 제작: 1초 = 1페이지
        clip = ImageSequenceClip(frame_files, fps=1)
        
        # [VRChat 최적화 설정]
        # - g=1: 모든 프레임을 키프레임으로 만들어 어디를 눌러도 즉시 화면 출력
        # - keyint=1: 탐색(Seek) 시 뒤섞임 방지
        clip.write_videofile(
            output_path, 
            fps=1, # 굳이 24fps로 늘리지 않고 1fps로 유지하여 용량과 안정성 잡기
            codec='libx264', 
            audio=False, 
            ffmpeg_params=[
                "-x264opts", "keyint=1:min-keyint=1", # 모든 프레임을 독립된 사진으로 처리
                "-pix_fmt", "yuv420p" # VRChat 호환성 표준 포맷
            ],
            preset='ultrafast',
            logger=None
        )
        
        print("✅ [성공] 뒤섞임 방지 로직 적용 완료!", flush=True)
        return True

    except Exception as e:
        print(f"❌ 에러: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)