import fitz  # PyMuPDF
import os
import shutil
import gc # 메모리 청소부 호출
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "final_optimization"
    try:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"📉 [메모리 절약 모드] 총 {len(doc)}페이지 변환 시작", flush=True)

        frame_files = []
        
        for i, page in enumerate(doc):
            # [중요] 해상도 1.2배 (서버 안 죽는 선에서 최대 화질)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
            
            # 파일명 0001, 0002 강제 (순서 꼬임 방지)
            filename = f"frame_{i:04d}.png"
            path = os.path.join(temp_dir, filename)
            
            pix.save(path)
            frame_files.append(path)
            
            # 한 장 처리할 때마다 메모리 청소 (제발 죽지 마라)
            pix = None
            if i % 3 == 0: gc.collect()

        doc.close()
        frame_files.sort() # 순서 2차 확인

        print("🎬 영상 굽는 중... (키프레임 강제 모드)", flush=True)

        # 1초에 1장 (메모리 살리기)
        clip = ImageSequenceClip(frame_files, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            # [★여기가 핵심★]
            # -g 1 : GOP 사이즈를 1로 설정 -> 모든 프레임이 키프레임이 됨
            # -keyint_min 1 : 최소 키프레임 간격 1
            # -tune stillimage : 슬라이드 이미지에 최적화된 인코딩
            ffmpeg_params=["-g", "1", "-keyint_min", "1", "-tune", "stillimage", "-pix_fmt", "yuv420p"],
            preset='ultrafast',
            threads=1, # 쓰레드 1개만 써서 메모리 폭발 방지
            logger=None
        )
        
        print("✅ [생존] 변환 완료! 화면 튐 없음.", flush=True)
        return True

    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        gc.collect()