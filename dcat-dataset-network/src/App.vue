<script setup>
import { ref } from 'vue';
import DataUpload from "@/components/DataUpload.vue";
import DcatKeywordGraph from "@/components/DcatKeywordGraph.vue";

// 상태 관리
const currentView = ref('upload'); // 'upload' | 'analysis'
const uploadedData = ref([]);

// 업로드 완료 후 분석 화면으로 전환
const handleDataUpload = (data) => {
  uploadedData.value = data;
  currentView.value = 'analysis';
};

// 업로드 화면으로 돌아가기
const goBackToUpload = () => {
  currentView.value = 'upload';
  uploadedData.value = [];
};
</script>

<template>
  <main>
    <!-- 업로드 화면 -->
    <div v-if="currentView === 'upload'">
      <DataUpload @data-uploaded="handleDataUpload" />
    </div>

    <!-- 분석 결과 화면 -->
    <div v-if="currentView === 'analysis'" class="analysis-view">
      <div class="analysis-header">
        <button @click="goBackToUpload" class="back-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="m15 18-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          새 데이터 업로드
        </button>
        <h2>네트워크 분석 결과</h2>
        <div class="data-info">
          총 {{ uploadedData.length }}개 데이터셋
        </div>
      </div>
      <DcatKeywordGraph :data="uploadedData" />
    </div>
  </main>
</template>

<style scoped>
.analysis-view {
  width: 100%;
}

.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.analysis-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.data-info {
  font-size: 0.9rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .analysis-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .back-btn {
    align-self: flex-start;
  }
}
</style>
