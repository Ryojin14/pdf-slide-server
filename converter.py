import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip
import shutil
import sys # 실시간 로그 출력용

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "temp_frames_fast"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        frame_files = []
        
        # [수정] 로그가 즉시 찍히도록 flush=True 추가
        print(f"🚀 [시작] 총 {len(doc)}페이지 변환 개시!", flush=True)

        for i, page in enumerate(doc):
            # [수정] 해상도를 0.8로 확 낮춥니다. (일단 작동하는지 확인용)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.8, 0.8))
            frame_path = os.path.join(temp_dir, f"f_{i:04d}.png")
            pix.save(frame_path)
            frame_files.append(frame_path)
            
            # 매 페이지마다 "나 살아있다"고 알림
            print(f"📝 {i+1}/{len(doc)} 페이지 처리 중...", flush=True)
        
        doc.close()
        frame_files.sort()

        print("🎥 영상 인코딩 시작... (여기서 시간이 좀 걸립니다)", flush=True)

        clip = ImageSequenceClip(frame_files, fps=1)
        clip.write_videofile(
            output_path, 
            fps=12,              # [수정] 프레임 수를 줄여서 인코딩 속도 2배 향상
            codec='libx264', 
            audio=False, 
            preset='ultrafast',  # 가장 빠른 속도
            threads=1,
            logger=None
        )
        
        print("✅ [완료] 변환 성공!", flush=True)
        return True

    except Exception as e:
        print(f"❌ [에러] 발생: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)