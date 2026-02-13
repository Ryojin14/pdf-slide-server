import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip
import shutil

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "temp_frames"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        frame_files = []
        
        print(f"📄 초경량 변환 시작: {len(doc)}페이지")

        # 1. 페이지를 하나씩 이미지 파일로 저장 (메모리 아끼기)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            pix.save(frame_path)
            frame_files.append(frame_path)
        
        doc.close()

        # 2. 파일 경로 리스트를 이용해 영상 제작 (RAM 사용량 최소화)
        clip = ImageSequenceClip(frame_files, fps=1)
        clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            preset='ultrafast',
            threads=1,
            logger=None
        )
        
        print("✅ 변환 완료!")
        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir) # 임시 폴더 삭제