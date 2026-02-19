import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # 1. 페이지 추출 (가장 가벼운 1,1 유지)
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(1, 1))
            path = f"f_{i}.png"
            pix.save(path)
            frame_files.append(path)
        
        # [필수] 마지막 페이지 복사 (영상 끝남 방지)
        if frame_files:
            frame_files.append(frame_files[-1])
            
        final_frames = frame_files
        
        # 2. 영상 제작 (가성비 세팅)
        # fps=1 (입력) -> fps=4 (출력) : 4배만 뻥튀기 (24배는 너무 무거움)
        clip = ImageSequenceClip(final_frames, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=4,  # [핵심] 4프레임이면 VRChat도 속고 서버도 버팁니다.
            codec='libx264', 
            audio=False, 
            logger=None,
            preset='ultrafast', # 속도 최우선
            threads=4,          # 멀티코어 사용
            # [마법의 옵션 설명]
            # -tune stillimage: "이거 PPT니까 쓸데없는 계산 하지마" (속도 대폭 향상)
            # -g 4: 1초(4프레임)마다 키프레임 박기 -> 탐색 오류 해결
            # -bf 0: 예측 프레임 끄기 -> 깜빡임 완전 제거
            ffmpeg_params=['-tune', 'stillimage', '-g', '4', '-bf', '0', '-pix_fmt', 'yuv420p']
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