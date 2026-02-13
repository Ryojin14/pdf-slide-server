import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # 1. 모든 페이지를 이미지로 추출
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(1, 1))
            path = f"f_{i}.png"
            pix.save(path)
            frame_files.append(path)
        
        # 2. [핵심] 시작하자마자 2페이지로 가는 문제 해결
        # VRChat 스크립트가 1초부터 읽는 경우가 많으므로, 맨 앞에 가짜 0초(1페이지 복사본)를 하나 더 넣습니다.
        final_frames = [frame_files[0]] + frame_files
        
        # 3. 영상 제작 (가장 가벼운 설정)
        clip = ImageSequenceClip(final_frames, fps=1)
        clip.write_videofile(output_path, fps=1, codec='libx264', audio=False, logger=None)
        
        # 4. 임시 파일 삭제
        doc.close()
        for f in frame_files:
            if os.path.exists(f): os.remove(f)
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False