import fitz  # PyMuPDF
import os
import shutil
import gc
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "final_no_bframes"
    try:
        # 1. 폴더 초기화
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"🔥 [B-프레임 제거 모드] 총 {len(doc)}페이지", flush=True)

        frame_files = []
        
        # 2. 이미지 추출 (메모리 폭발 방지)
        for i, page in enumerate(doc):
            # 해상도 1.2배 (서버 타협점)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2))
            
            # 파일명 강제 정렬 (frame_0000.png)
            filename = f"frame_{i:04d}.png"
            path = os.path.join(temp_dir, filename)
            
            pix.save(path)
            frame_files.append(path)
            
            # 메모리 청소
            pix = None
            if i % 3 == 0: gc.collect()

        doc.close()
        
        # 3. 정렬 (문자열 정렬이어도 0000 포맷이라 100% 정확함)
        frame_files.sort()

        print("🎬 영상 굽는 중... (예측 프레임 삭제)", flush=True)

        # 4. 영상 변환 설정 (여기가 핵심)
        # 소스는 fps=1로 읽지만...
        clip = ImageSequenceClip(frame_files, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=30,  # [수정] 표준 30프레임으로 늘려서 저장 (호환성 확보)
            codec='libx264', 
            audio=False, 
            
            # [★잔상/튀는 현상 완벽 제거 옵션★]
            ffmpeg_params=[
                "-bf", "0",               # [핵심] B-프레임 0개 (앞뒤 참조 절대 금지)
                "-profile:v", "baseline", # [핵심] 베이스라인 프로필 (가장 단순한 재생 방식)
                "-g", "30",               # 1초마다 키프레임 (탐색 최적화)
                "-pix_fmt", "yuv420p"
            ],
            preset='ultrafast',
            threads=1,
            logger=None
        )
        
        print("✅ [완료] B-프레임 제거됨. 이제 절대 안 튑니다.", flush=True)
        return True

    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)
        return False
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        gc.collect()