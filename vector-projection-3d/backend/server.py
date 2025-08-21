from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os, json, pickle
from pathlib import Path
import psycopg
import numpy as np
import pandas as pd

from umap import UMAP
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
import networkx as nx

# ================== 설정 ==================
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB   = os.getenv("PGDATABASE", "db")
PG_USER = os.getenv("PGUSER", "user")
PG_PASS = os.getenv("PGPASSWORD", "passwd")

# 캐시 설정
CACHE_PATH = Path(os.getenv("CACHE_PATH", "./cache/news_rows.pkl"))
CACHE_REFRESH = os.getenv("CACHE_REFRESH", "0") == "1"

# UMAP 하이퍼파라미터 (필요시 조정)
UMAP_N_NEIGHBORS = 20
UMAP_MIN_DIST = 0.05
UMAP_RANDOM_STATE = 42

# (옵션) 원공간 코사인 기준 kNN 링크 생성
USE_KNN_LINKS = False
K_FOR_LINKS = 8

# ================== 데이터 로드 (캐시 + DB) ==================
def fetch_rows_from_pg():
    with psycopg.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT embedding::text, num, summary, report_type
                FROM third.news_report
                WHERE embedding IS NOT NULL
            """)
            return cur.fetchall()

def load_rows_with_cache() -> list:
    """피클 캐시가 있으면 로드, 없거나 강제 갱신이면 DB에서 가져와 저장."""
    if not CACHE_REFRESH and CACHE_PATH.exists():
        with CACHE_PATH.open("rb") as f:
            rows = pickle.load(f)
        # rows 형식 점검(옵션)
        return rows

    # 캐시 미존재 또는 강제 갱신
    rows = fetch_rows_from_pg()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("wb") as f:
        pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)
    return rows

rows = load_rows_with_cache()

# ===== 파싱 → 행렬 구성 =====
ids: List[int] = []
summaries: List[str] = []
report_types: List[str] = []
embeddings: List[List[float]] = []

for emb_txt, num, summary, rtype in rows:
    vec = json.loads(emb_txt)                 # "[...]" → List[float]
    embeddings.append(vec)
    ids.append(num)
    summaries.append((summary or "").replace("\n", " ").strip())
    report_types.append(str(rtype) if rtype is not None else "unknown")

if not embeddings:
    raise RuntimeError("임베딩이 비어 있습니다. third.news_report.embedding을 확인하세요.")

# numpy 행렬
X = np.asarray(embeddings, dtype=float)

# ===== 코사인 일관성: L2 정규화 후 UMAP(3D) =====
Xn = normalize(X)  # 각 벡터 길이 1로 → cosine metric과 일관성
umap = UMAP(
    n_components=3,
    n_neighbors=UMAP_N_NEIGHBORS,
    min_dist=UMAP_MIN_DIST,
    metric="cosine",
    random_state=UMAP_RANDOM_STATE
)
X3 = umap.fit_transform(Xn)  # (n_samples, 3)

df_out = pd.DataFrame(X3, columns=["x", "y", "z"])
df_out["id"] = ids
df_out["summary"] = summaries
df_out["report_type"] = report_types

# ================== 스케일링 유틸 ==================
def robust_scale_to_range(series: pd.Series, low=-1000.0, high=1000.0,
                          q_low=1, q_high=99):
    s = series.astype(float).replace([np.inf, -np.inf], np.nan)
    s = s.fillna(s.median())
    lo, hi = np.percentile(s, [q_low, q_high])
    if hi == lo:
        s_clip = np.zeros_like(s)
    else:
        s_clip = np.clip(s, lo, hi)
        s_clip = (s_clip - lo) / (hi - lo)
    return s_clip * (high - low) + low

# 좌표 스케일링 (3d-force-graph 보기 좋은 범위로)
df_scaled = pd.DataFrame({
    "id": df_out["id"],
    "summary": df_out["summary"],
    "report_type": df_out["report_type"],
    "fx": robust_scale_to_range(df_out["x"], -1000, 1000),
    "fy": robust_scale_to_range(df_out["y"], -1000, 1000),
    "fz": robust_scale_to_range(df_out["z"], -1000, 1000),
})

# ================== nodes 생성 ==================
nodes: List[Dict[str, Any]] = []
for _, row in df_scaled.iterrows():
    label = row["summary"] or ""
    if len(label) > 180:
        label = label[:180] + "…"
    nodes.append({
        "id": int(row["id"]),
        "group": row["report_type"],   # report_type을 색상 그룹으로 사용
        "fx": float(row["fx"]),
        "fy": float(row["fy"]),
        "fz": float(row["fz"]),
        "summary": label,
        "report_type": row["report_type"],
    })

# ================== MST 링크: report_type별로 생성 ==================
def build_mst_links_by_report_type(ids_list: List[int],
                                   types_list: List[str],
                                   X_norm: np.ndarray) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []
    # 타입별 인덱스 모으기
    by_type: Dict[str, List[int]] = {}
    for idx, t in enumerate(types_list):
        by_type.setdefault(t, []).append(idx)

    for rtype, idxs in by_type.items():
        if len(idxs) < 2:
            continue  # 노드 1개면 MST 불가
        # 해당 타입의 코사인 거리 행렬 (1 - cosine_similarity)
        D = pairwise_distances(X_norm[idxs], metric="cosine")  # shape (m, m)
        # 네트워크X 그래프 구성
        G = nx.Graph()
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                dist_ij = float(D[i, j])
                sim_ij = 1.0 - dist_ij
                G.add_edge(i, j, weight=dist_ij, sim=sim_ij)  # 가중치는 거리, sim은 보조속성

        # MST 계산
        T = nx.minimum_spanning_tree(G, weight="weight")
        for u, v, data in T.edges(data=True):
            a = int(ids_list[idxs[u]])
            b = int(ids_list[idxs[v]])
            links.append({
                "source": a,
                "target": b,
                "type": "mst",
                "report_type": rtype,
                "weight": float(data.get("sim", 1.0 - D[u, v]))  # 코사인 유사도(0~1)
            })
    return links

links = build_mst_links_by_report_type(ids, report_types, Xn)

# ================== FastAPI ==================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sample_graph() -> Dict[str, List[Dict[str, Any]]]:
    # 3d-force-graph는 fx/fy/fz가 있으면 해당 위치에 고정됨
    return {"nodes": nodes, "links": links}

@app.get("/graph")
def get_graph():
    return sample_graph()
