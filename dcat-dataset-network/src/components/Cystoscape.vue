<template>
  <div>
    <h1>Cytoscape</h1>
    <div id="cy" style="width: 800px; height: 600px; margin-top: 20px;"></div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import cytoscape from 'cytoscape';

export default {
  setup() {
    const cy = ref(null);

    const parseCSVLine = (line) => {
      const result = [];
      let current = '';
      let insideQuotes = false;

      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          insideQuotes = !insideQuotes;
        } else if (char === ',' && !insideQuotes) {
          result.push(current.trim().replace(/^"|"$/g, ''));
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim().replace(/^"|"$/g, ''));
      return result;
    };

    const loadCSVData = async () => {
      try {
        const response = await fetch('/test4.csv');
        const text = await response.text();
        const lines = text.trim().split('\n');
        const elements = new Set();
        const edges = [];

        const headers = parseCSVLine(lines[0])
        const indexA1 = headers.indexOf('분류');
        const indexB3 = headers.indexOf('특성추출');

        if (indexA1 === -1 || indexB3 === -1) {
          throw new Error('Required columns 분류 or 특성추출 not found in CSV file');
        }

        lines.slice(1).forEach(line => {
          const columns = parseCSVLine(line);
          const source = columns[indexA1]?.split('>')[0]?.trim();
          const targets = columns[indexB3]?.trim().split(',');

          if (source && source.length > 0 && targets) {
            elements.add(source);
            targets.forEach(target => {
              const trimmedTarget = target.trim();
              if (trimmedTarget.length > 0) {
                elements.add(trimmedTarget);
                edges.push({ data: { id: `${source}-${trimmedTarget}`, source, target: trimmedTarget } });
              }
            });
          }
        });

        const nodes = Array.from(elements).map(node => ({ data: { id: node, label: node } }));

        console.log(edges)
        console.log(nodes)

        // 노드 크기를 연결된 엣지 수에 따라 설정
        const nodeSizes = {};
        edges.forEach(edge => {
          nodeSizes[edge.data.source] = (nodeSizes[edge.data.source] || 0) + 1;
          nodeSizes[edge.data.target] = (nodeSizes[edge.data.target] || 0) + 1;
        });

        cy.value = cytoscape({
          container: document.getElementById('cy'),
          elements: [...nodes, ...edges],
          // elements: elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'background-color': '#0074D9',
                'color': '#fff',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': ele => 10 + (nodeSizes[ele.data('id')] || 0) * 2,
                'height': ele => 10 + (nodeSizes[ele.data('id')] || 0) * 2
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 2,
                'line-color': '#AAAAAA',
                'target-arrow-shape': 'triangle'
              }
            }
          ],
          layout: {
            name: 'cose',
            directed: true,
            padding: 10,
            avoidOverlap: true    // 겹침 방지
          }
        });
      } catch (error) {
        console.error('Error loading CSV file:', error);
      }
    };

    onMounted(() => {
      loadCSVData();
    });

    return {};
  },
};
</script>

<style>
#cy {
  width: 100%;
  height: 500px;
  border: 1px solid #ccc;
}
</style>
