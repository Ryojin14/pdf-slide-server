import fitz  # PyMuPDF
import os
import shutil
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "standard_frames"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"🔥 [표준 규격] 총 {len(doc)}페이지 변환 시작", flush=True)

        frame_files = []
        
        # 1. 이미지 추출 (0000, 0001 이름 강제)
        for i, page in enumerate(doc):
            # 해상도 1.5배 (화질 약간 복구)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            filename = f"frame_{i:04d}.png"
            path = os.path.join(temp_dir, filename)
            pix.save(path)
            frame_files.append(path)

        doc.close()
        frame_files.sort() # 순서 절대 보장

        # 2. 영상 제작 (여기가 핵심)
        # fps=1로 클립을 만들지만...
        clip = ImageSequenceClip(frame_files, fps=1)
        
        print("🎬 영상 인코딩 중 (30fps 표준 포맷)...", flush=True)
        
        # ★ 쓸 때는 fps=30으로 늘려서 저장합니다.
        # 이렇게 하면 사진 1장을 30프레임동안 계속 보여주므로
        # 중간에 다른 페이지가 끼어들 틈이 0.0001초도 없습니다.
        clip.write_videofile(
            output_path, 
            fps=30,  # [수정] 1초에 30장 (표준 동영상 규격)
            codec='libx264', 
            audio=False, 
            # -g 30 : 1초(30프레임)마다 키프레임 박기
            ffmpeg_params=["-g", "30", "-pix_fmt", "yuv420p"],
            preset='ultrafast',
            threads=1,
            logger=None
        )
        
        print("✅ [완료] 이제 진짜 안 튑니다.", flush=True)
        return True

    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)