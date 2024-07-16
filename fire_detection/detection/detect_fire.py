
import torch
import cv2
from ultralytics import YOLO
import os

def detect_fire(video_path, output_dir, model_path='fire_yolov8n_v2.pt'):
    model = YOLO(model_path)

    # cv로 비디오 열기
    cap = cv2.VideoCapture(video_path)
    
    # 비디오 열리지 않을 시 에러 메시지 출력
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return False

    # 비디오 속성
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # 영상 너비
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 영상 높이
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 코덱 설정 & 영상 생성 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'avc1') # 동영상 파일 코덱 포맷 지정
    output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_detected.mp4' # 결과 파일 이름 지정
    output_path = os.path.join(output_dir, output_filename) # 결과파일 들어갈 경로 지정
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height)) # VideoWriter 객체 생성

    # 화재 감지 연속 5번으로 되어야 True 반환하기
    cons_frame_count = 0 # 화재 감지된 프레임 수 (연속)
    fire_detected = False

    # 비디오 열어서 프레임 가져오기
    while cap.isOpened():
        # ret: 동영상 열기 성공 여부, frame: 현재 프레임 (np.ndarray)
        ret, frame = cap.read()
        # 동영상 못 열었으면 멈추기
        if not ret:
            break

        # 현재 프레임에 대해 모델 run
        results = model(frame)
        
        # 각 프레임 감지 결과 확인
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls)
                    class_name = model.names[class_id]
                    # 화재 감지 시 화재 감지 카운트 1씩 증가
                    if class_name == 'fire':
                        cons_frame_count += 1
                        if cons_frame_count >= 5:
                            fire_detected = True
                    else:
                        cons_frame_count = 0

            # 프레임에 bounding box 그리기
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            
    cap.release()
    out.release()
    
    return fire_detected, output_path
