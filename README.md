# LactoSim 시각화 웹앱

락타아제 처리 조건에 따른 유당분해율을 예측하는 Streamlit 웹앱입니다.

## 구성 파일

- `lactase_visual_app.py`: 앱 메인 파일
- `requirements.txt`: 필요한 라이브러리
- `assets/`: 앱에 들어가는 SVG 그림 파일

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run lactase_visual_app.py
```

## Streamlit Community Cloud 배포

1. GitHub에 새 저장소를 만든다.
2. 이 폴더의 파일 전체를 업로드한다.
3. Streamlit Community Cloud에서 새 앱을 만든다.
4. 저장소를 연결하고 메인 파일을 `lactase_visual_app.py`로 지정한다.
5. Deploy를 누른다.

## 보고서용 핵심 설명

이 웹앱은 초기 유당량, 처리 시간, 효소량, 온도 조건을 입력받아 유당 잔존량, 포도당 생성량, 갈락토스 생성량, 유당분해율을 계산하고 그래프로 나타낸다. 
유당 잔존량은 지수감소 모델로 단순화하였으며, 효소량과 온도 조건은 반응속도상수에 반영하였다.
