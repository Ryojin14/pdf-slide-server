import fitz  # PyMuPDF
import numpy as np
import os
from moviepy.editor import ImageSequenceClip
import gc # 메모리 청소부

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        img_list = []
        
        print(f"📄 PDF 변환 시작: 총 {len(doc)}페이지")
        
        # [수정 1] 화질 다이어트
        # 기존 2.0 -> 1.0 (기본 해상도)
        # 무료 서버에서는 이 정도가 한계입니다. (글씨는 충분히 보입니다!)
        mat = fitz.Matrix(1.0, 1.0) 

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=mat)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
            img_list.append(img)
            
            # [수정 2] 메모리 폭발 방지
            # 5장 처리할 때마다 찌꺼기 청소
            if i % 5 == 0: gc.collect()

        if not img_list: return False

        print("🎥 영상 인코딩 중... (속도 우선 모드)")

        # [수정 3] 인코딩 속도 최적화
        clip = ImageSequenceClip(img_list, fps=1) 
        
        clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            preset='ultrafast',  # ★핵심: 화질 압축을 대충 해서 속도를 올림
            threads=1,           # ★핵심: CPU 1개만 써서 뻗는 것 방지
            logger=None
        )
        
        print(f"✅ 변환 완료: {output_path}")
        doc.close()
        return True

    except Exception as e:
        print(f"❌ 변환 오류: {e}")
        return False