import fitz  # PyMuPDF
import numpy as np
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        # PDF 열기
        doc = fitz.open(pdf_path)
        img_list = []
        
        print(f"📄 PDF 변환 시작: {pdf_path}")
        
        # 1. PDF를 고화질 이미지로 변환 (fitz 사용으로 poppler 필요 없음!)
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            
            # MoviePy는 RGB 색상을 좋아합니다. (OpenCV와 다름)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
            img_list.append(img)
        
        if not img_list: return False

        print(f"🎥 영상 인코딩 중... (어제의 그 품질로 복구합니다)")

        # 2. 영상 제작 (MoviePy 사용)
        # fps=1 : 이미지 1장당 1초 길이로 설정
        clip = ImageSequenceClip(img_list, fps=1) 
        
        # 3. 파일 저장 (fps=24 : 1초를 24프레임으로 쪼개서 부드럽게 만듦)
        # codec='libx264' : VRChat이 가장 좋아하는 포맷
        clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            preset='medium',
            ffmpeg_params=['-pix_fmt', 'yuv420p'], # 호환성 안전장치
            logger=None # 지저분한 로그 숨기기
        )
        
        print(f"✅ 완벽한 영상 변환 완료: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 변환 오류: {e}")
        return False