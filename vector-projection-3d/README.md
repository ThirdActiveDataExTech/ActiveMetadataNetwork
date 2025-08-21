# vector-projection-3d

임베딩된 데이터를 3차원으로 축소하여 Node로 표현하고,
데이터의 카테고리 정보를 Link로 하여
3차원 공간에 데이터를 표현하는 프로그램

## 사용된 데이터 셋
- 인천공항공사의 보도자료

## 구성 방식

### frontend
- 언어: vue3

3d-force-graph 를활용하여 3차원 공간에 그래프를 표현하는 방식을 사용

### backend
- 언어: python3

- embedding 결과를 UMAP을 이용하여 3차원으로 축소 진행
- MST를 이용하여 링크 생성

## 실행 방법

backend의 host/port는 0.0.0.0:8800 으로 고정하여 동작하도록 설정됨

- backend 실행 방법

```
cd backend
pip install -r requirements.txt
sh run.sh
```
