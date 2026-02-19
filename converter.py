import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # 1. 페이지 추출
        for i in range(len(doc)):
            # 해상도 (2, 2) 권장: 글자가 훨씬 선명해집니다.
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(2, 2))
            path = f"f_{i}.png"
            pix.save(path)
            frame_files.append(path)
        
        # [핵심 1] 마지막 페이지 복사 (절벽 밀어내기)
        # 영상이 끝나서 처음으로 돌아가는 것을 막아주는 '에어백' 역할입니다.
        if frame_files:
            frame_files.append(frame_files[-1])
            
        final_frames = frame_files
        
        # [핵심 2] 영상 제작 (옵션이 중요합니다!)
        clip = ImageSequenceClip(final_frames, fps=1)
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            logger=None,
            # ▼▼▼ 여기가 마법의 주문입니다 ▼▼▼
            # -g 1: 모든 프레임을 독립적인 사진으로 저장 (이동 시 잔상/깜빡임 제거)
            # -bf 0: 예측 프레임 제거 (즉각 반응)
            # -preset ultrafast: 변환 속도 최적화
            ffmpeg_params=['-g', '1', '-bf', '0', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p']
        )
        
        doc.close()
        for f in frame_files:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False