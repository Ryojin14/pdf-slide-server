import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip
import shutil

def convert_pdf_to_video(pdf_path, output_path):
    # 매번 완전히 새로운 임시 폴더를 사용해서 잔상을 방지합니다.
    temp_dir = "temp_frames_clean"
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        frame_files = []
        
        print(f"📄 정밀 변환 시작: {len(doc)}페이지")

        for i, page in enumerate(doc):
            # 해상도를 1.2로 살짝 올려 가독성을 확보합니다.
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
            # 파일명을 0001, 0002 식으로 정렬하기 좋게 만듭니다.
            frame_path = os.path.join(temp_dir, f"f_{i:04d}.png")
            pix.save(frame_path)
            frame_files.append(frame_path)
        
        doc.close()

        # [중요] 파일 리스트를 다시 한번 이름순으로 정렬해서 뒤섞임 방지
        frame_files.sort()

        # 영상 제작 (durations를 명시해서 한 페이지당 정확히 1초씩 할당)
        clip = ImageSequenceClip(frame_files, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio=False, 
            preset='medium', # 'ultrafast'보다 안정적인 압축 방식 사용
            threads=1,
            logger=None
        )
        
        print("✅ 정밀 변환 및 정렬 완료!")
        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        # 작업 종료 후 임시 파일 즉시 삭제
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)