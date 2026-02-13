import fitz  # PyMuPDF
import os
import shutil
from moviepy.editor import ImageSequenceClip

def convert_pdf_to_video(pdf_path, output_path):
    temp_dir = "final_frames"
    try:
        # 1. 기존 임시 폴더 싹 지우고 새로 만들기 (잔상 방지)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        doc = fitz.open(pdf_path)
        print(f"🔥 [최종] 총 {len(doc)}페이지 변환 시작", flush=True)

        frame_files = []
        
        # 2. 이미지 추출 (이름을 0001.png 처럼 만들어서 강제 정렬 준비)
        for i, page in enumerate(doc):
            # 해상도 1.0 (메모리 안전빵)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))
            
            # 파일명을 0000, 0001, 0002... 로 저장
            filename = f"frame_{i:04d}.png"
            frame_path = os.path.join(temp_dir, filename)
            
            pix.save(frame_path)
            frame_files.append(frame_path)
            
            print(f"  - {i+1}페이지 저장됨", flush=True)

        doc.close()

        # 3. ★핵심★ 파일 이름 순서대로 강제 정렬 (1, 10, 2 사태 방지)
        frame_files.sort()
        print(f"📑 정렬된 파일 목록 확인: {frame_files[0]} ... {frame_files[-1]}", flush=True)

        # 4. 영상 제작 (1초 = 1페이지)
        print("🎬 영상 굽는 중... (VRChat 최적화)", flush=True)
        clip = ImageSequenceClip(frame_files, fps=1)
        
        clip.write_videofile(
            output_path, 
            fps=1, 
            codec='libx264', 
            audio=False, 
            # [VRChat 전용 옵션]
            # -g 1 : 모든 프레임을 키프레임으로 (탐색 시 화면 깨짐/섞임 100% 방지)
            # -pix_fmt yuv420p : 비디오 플레이어 호환성 확보
            ffmpeg_params=["-g", "1", "-pix_fmt", "yuv420p"],
            preset='ultrafast',
            threads=1,
            logger=None # 로그 지저분해지는 것 방지
        )
        
        print("✅ [성공] 변환 완료! 이제 뒤죽박죽 안 됩니다.", flush=True)
        return True

    except Exception as e:
        # 에러가 나면 뭔지 정확히 알려줌
        print(f"❌ [치명적 오류]: {e}", flush=True)
        import traceback
        traceback.print_exc() # 상세 에러 위치 출력
        return False
        
    finally:
        # 청소
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)