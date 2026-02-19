import fitz  # PyMuPDF
import os
import gc    # 메모리 강제 청소
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # 1. 페이지 추출 (JPG 변경 및 메모리 청소 유지)
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(1, 1))
            path = f"f_{i}.jpg"
            pix.save(path)
            frame_files.append(path)
            
            del pix
            gc.collect()
        
        # 마지막 페이지 복사 (영상 끝남 방지)
        if frame_files:
            frame_files.append(frame_files[-1])
            
        final_frames = frame_files
        
        # 2. 영상 제작
        clip = ImageSequenceClip(final_frames, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=4,  
            codec='libx264', 
            audio=False, 
            logger=None,
            preset='ultrafast', 
            threads=4,          
            # ▼▼▼ 여기가 수정된 부분입니다 ▼▼▼
            # -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 : 가로나 세로가 홀수면 짝수로 자동 보정!
            ffmpeg_params=[
                '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', 
                '-tune', 'stillimage', 
                '-g', '4', 
                '-bf', '0', 
                '-pix_fmt', 'yuv420p'
            ]
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