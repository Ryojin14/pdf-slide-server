import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # [속도 핵심 1] 화질 다이어트 (1, 1)
        # 2배 확대(Matrix 2,2)는 무료 서버에서 너무 느립니다. 
        # 원본 해상도(1, 1)로 해도 VRChat에서는 글씨 잘 보입니다.
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(1, 1)) 
            path = f"f_{i}.png"
            pix.save(path)
            frame_files.append(path)
        
        # [기능 유지] 마지막 페이지 복사 (재생 끝남 방지)
        if frame_files:
            frame_files.append(frame_files[-1])
            
        final_frames = frame_files
        
        # [속도 핵심 2] 영상 제작 옵션 최적화
        clip = ImageSequenceClip(final_frames, fps=1)
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            logger=None,
            # threads=4: CPU 병렬 처리로 속도 향상
            # preset='ultrafast': 압축률 포기하고 속도 몰빵 (파일 크기는 조금 커지지만 속도는 짱)
            preset='ultrafast', 
            threads=4,
            # -g 1: 탐색(Seek) 반응 속도 최적화 (깜빡임 방지)
            ffmpeg_params=['-g', '1', '-bf', '0', '-pix_fmt', 'yuv420p']
        )
        
        # 청소
        doc.close()
        for f in frame_files:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False