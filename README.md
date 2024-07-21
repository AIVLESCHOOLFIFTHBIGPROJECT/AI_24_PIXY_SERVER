# PIXY Project

## 개요
PIXY는 KT Aivle 5기 과정에서 개발된 혁신적인 AI 기반 예측 및 모니터링 시스템입니다. 이 프로젝트는 프론트엔드, 백엔드, Custom LLM, 그리고 세 가지 AI 모델링 (시계열 데이터 예측, 이상 행동 예측, 화재 예측)을 통합하여 실시간 데이터 분석과 예측 기능을 제공합니다.

## 프로젝트 구조
- `/frontend`: React 기반 사용자 인터페이스
- `/backend`: Django REST Framework 기반 API 서버
- `/custom-llm`: BERT 기반 커스텀 언어 모델
- `/ai-models`: 머신러닝 및 딥러닝 모델
  - `/sales-prediction`: RandomForest 기반 시계열 데이터 예측 모델
  - `/anomaly-detection`: Isolation Forest 기반 이상 행동 예측 모델
  - `/fire-prediction`: XGBoost 기반 화재 예측 모델

## 주요 기능
- 대시보드를 통한 실시간 데이터 시각화 및 분석
- RESTful API를 통한 효율적인 데이터 처리 및 모델 결과 제공
- 자연어 처리 기반의 사용자 쿼리 해석 및 응답 생성
- 시계열 데이터를 활용한 미래 트렌드 예측
- 실시간 이상 행동 감지 및 즉각적인 알림 시스템
- 다양한 요인을 고려한 정확한 화재 위험 예측 및 조기 경보 시스템

## 기술 스택
- 프론트엔드: React, Redux, Material-UI
- 백엔드: Django, Django REST Framework, Celery
- 데이터베이스: PostgreSQL, Redis
- AI/ML: TensorFlow, PyTorch, Scikit-learn, RandomForest
- 인프라: Docker, Kubernetes, AWS

## 설치 및 실행
각 컴포넌트별 설치 및 실행 방법은 해당 디렉토리의 README.md 파일을 참조하세요.
