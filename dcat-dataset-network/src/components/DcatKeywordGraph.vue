<template>
  <div>
    <h1>데이터셋 간 키워드 유사도 네트워크</h1>
    <div id="cy" style="width: 1000px; height: 600px;"></div>
  </div>
  <div class="legend">
    <div v-for="(color, category) in categoryColorMap" :key="category" class="legend-item">
      <span class="color-box" :style="{ backgroundColor: color }"></span>
      <span class="label">{{ category }}</span>
    </div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape';

export default {
  name: 'DcatDatasetGraph',
  
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      cy: null,
      categoryColorMap: {
        '의료/보건': '#1f77b4',
        '복지/돌봄': '#ff7f0e',
        '교육': '#2ca02c',
        '환경/기후': '#d62728',
        '문화/예술': '#9467bd',
        '방송/콘텐츠': '#8c564b',
        '교통/안전': '#e377c2',
        '행정/정책': '#7f7f7f',
        '기타': '#cccccc'
      }
    };
  },


  async mounted() {
    // props로 전달받은 데이터 사용, 없으면 기본 데이터 로드
    let data = this.data;
    
    if (!data || data.length === 0) {
      try {
        const res = await fetch('/dcat_sample.json');
        data = await res.json();
      } catch (error) {
        console.error('기본 데이터 로드 실패:', error);
        data = [];
      }
    }

    if (data.length === 0) {
      console.warn('표시할 데이터가 없습니다.');
      return;
    }

    this.initializeGraph(data);
  },

  watch: {
    data: {
      handler(newData) {
        if (newData && newData.length > 0) {
          this.initializeGraph(newData);
        }
      },
      deep: true
    }
  },

  methods: {
    initializeGraph(data) {
      // 기존 그래프가 있다면 제거
      const container = document.getElementById('cy');
      if (container && this.cy) {
        this.cy.destroy();
      }

      // 카테고리별 색상 지정
      const categoryColorMap = this.categoryColorMap;

      // 노드: 데이터셋 하나
      const nodes = data.map((entry, idx) => ({
        data: {
          id: `D${idx}`,
          label: entry.title,
          category: entry.category
        }
      }));

      // 엣지: keyword 교집합 수 ≥ 1
      const edges = [];
      for (let i = 0; i < data.length; i++) {
        for (let j = i + 1; j < data.length; j++) {
          const k1 = new Set(data[i].keyword);
          const k2 = new Set(data[j].keyword);
          const common = [...k1].filter(k => k2.has(k));
          const weight = common.length;
          if (weight >= 1) {
            edges.push({
              data: {
                source: `D${i}`,
                target: `D${j}`,
                weight: weight
              }
            });
          }
        }
      }

      // 노드 weight 계산 (엣지 연결 강도 총합)
      const nodeWeights = {};
      edges.forEach(edge => {
        nodeWeights[edge.data.source] = (nodeWeights[edge.data.source] || 0) + edge.data.weight;
        nodeWeights[edge.data.target] = (nodeWeights[edge.data.target] || 0) + edge.data.weight;
      });

      // Cytoscape 시각화
      this.cy = cytoscape({
        container: document.getElementById('cy'),
        elements: [...nodes, ...edges],
        style: [
          {
            selector: 'node',
            style: {
              'label': 'data(label)',
              'background-color': ele => {
                const cat = ele.data('category');
                return categoryColorMap[cat] || '#999';
              },
              'color': '#000',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '10px',
              'width': ele => {
                const id = ele.data('id');
                const size = nodeWeights[id] || 1;
                return Math.min(60, 20 + size * 3);
              },
              'height': ele => {
                const id = ele.data('id');
                const size = nodeWeights[id] || 1;
                return Math.min(60, 20 + size * 3);
              }
            }
          },
          {
            selector: 'edge',
            style: {
              'width': ele => 1 + ele.data('weight'),
              'line-color': '#ccc',
              'curve-style': 'bezier'
            }
          }
        ],
        layout: {
          name: 'cose',
          animate: true
        },
        minZoom: 0.5,
        maxZoom: 2.5,
        wheelSensitivity: 0.2
      });
    }
  }
};
</script>

<style scoped>
h1 {
  text-align: center;
  margin: 20px;
}
#cy {
  border: 1px solid #ddd;
  margin: 0 auto;
  background-color: #fafafa;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 4px 12px;
}

.color-box {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  border: 1px solid #999;
  border-radius: 3px;
}

.label {
  font-size: 13px;
  color: #fff;
}

</style>
