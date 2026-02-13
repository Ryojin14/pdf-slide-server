import fitz  # PyMuPDF
import os
from moviepy.editor import ImageSequenceClip
import shutil

def convert_pdf_to_video(pdf_path, output_path):
    # 매번 깨끗한 임시 폴더 사용
    temp_dir = "absolute_order_frames"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"📦 [순서 고정] 총 {len(doc)}페이지 변환 시작", flush=True)

        # ★ 핵심: 생성되는 즉시 리스트에 넣어 '절대 순서'를 보장합니다.
        ordered_frame_files = []
        
        for i in range(len(doc)):
            page = doc[i]
            # 해상도를 1.0으로 고정하여 서버 메모리 안정성 확보
            pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
            
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            pix.save(frame_path)
            
            # 여기서 리스트에 바로 추가하므로 os.listdir()를 쓸 필요가 없습니다.
            ordered_frame_files.append(frame_path)
            print(f"📝 {i+1}페이지 저장 완료", flush=True)
        
        doc.close()

        # 영상 제작: 1초당 1프레임 (1페이지 = 1초)
        # ordered_frame_files 리스트는 이미 0, 1, 2, 3 순서가 완벽합니다.
        clip = ImageSequenceClip(ordered_frame_files, fps=1)
        
        # [VRChat 탐색 최적화]
        # -g 1: 모든 프레임을 독립된 사진으로 만듦 (이전/다음 버튼 클릭 시 즉시 반응)
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            ffmpeg_params=["-g", "1", "-keyint_min", "1", "-pix_fmt", "yuv420p"],
            preset='ultrafast',
            threads=1,
            logger=None
        )
        
        print(f"✅ [최종 성공] {len(doc)}페이지 영상 제작 완료!", flush=True)
        return True

    except Exception as e:
        print(f"❌ 치명적 에러: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)