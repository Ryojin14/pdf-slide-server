import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    try:
        doc = fitz.open(pdf_path)
        frame_files = []
        
        # 1. 모든 페이지를 이미지로 추출
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(matrix=fitz.Matrix(1, 1)) # 화질을 높이려면 (2, 2)로 변경
            path = f"f_{i}.png"
            pix.save(path)
            frame_files.append(path)
        
        # [수정 1] 복사본 생성 코드 삭제
        # 이제 영상은 [1쪽, 2쪽, 3쪽...] 순서대로 정직하게 들어갑니다.
        final_frames = frame_files
        
        # 3. 영상 제작
        # [수정 2] ffmpeg_params=['-g', '1'] 추가 (핵심!)
        # '-g 1'은 "모든 프레임을 원본 그대로 저장해라(키프레임 간격 1)"라는 뜻입니다.
        # 이렇게 하면 VRChat에서 0.1초 단위로 이동해도 깜빡임 없이 칼같이 이동합니다.
        clip = ImageSequenceClip(final_frames, fps=1)
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            logger=None,
            ffmpeg_params=['-g', '1'] 
        )
        
        # 4. 임시 파일 삭제
        doc.close()
        for f in frame_files:
            if os.path.exists(f): os.remove(f)
            
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False