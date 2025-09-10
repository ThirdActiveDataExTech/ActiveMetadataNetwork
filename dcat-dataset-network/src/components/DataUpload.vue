<template>
  <div class="upload-container">
    <div class="header">
      <h1>DCAT 메타데이터 네트워크 분석</h1>
      <p class="subtitle">데이터셋 메타데이터를 업로드하여 키워드 기반 네트워크를 시각화하세요</p>
    </div>

    <div class="upload-section">
      <div class="upload-area" :class="{ 'drag-over': isDragOver }" 
           @drop="handleDrop" 
           @dragover="handleDragOver" 
           @dragleave="handleDragLeave"
           @click="triggerFileInput">
        <input 
          ref="fileInput" 
          type="file" 
          multiple 
          accept=".json"
          @change="handleFileSelect"
          style="display: none;"
        />
        
        <div class="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        
        <div class="upload-text">
          <h3>JSON 파일을 드래그하거나 클릭하여 업로드</h3>
          <p>여러 개의 JSON 파일을 한 번에 선택할 수 있습니다</p>
        </div>
      </div>

      <div class="format-info">
        <h4>요구되는 JSON 형식</h4>
        <div class="format-example">
          <pre><code>[
  {
    "title": "데이터셋 제목",
    "description": "데이터셋 설명",
    "keyword": ["키워드1", "키워드2", "키워드3"],
    "category": "카테고리명"
  },
  ...
]</code></pre>
        </div>
      </div>
    </div>

    <div v-if="uploadedFiles.length > 0" class="files-section">
      <h3>업로드된 파일 ({{ uploadedFiles.length }}개)</h3>
      <div class="files-list">
        <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
          <div class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-stats">{{ file.dataCount }}개 데이터셋</div>
          </div>
          <button @click="removeFile(index)" class="remove-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="data-summary">
        <div class="summary-item">
          <span class="label">총 데이터셋:</span>
          <span class="value">{{ totalDatasets }}개</span>
        </div>
        <div class="summary-item">
          <span class="label">카테고리:</span>
          <span class="value">{{ uniqueCategories.length }}개</span>
        </div>
        <div class="summary-item">
          <span class="label">키워드:</span>
          <span class="value">{{ uniqueKeywords.length }}개</span>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="clearAll" class="clear-btn">모두 지우기</button>
        <button @click="startAnalysis" class="analyze-btn" :disabled="totalDatasets === 0">
          네트워크 분석 시작
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataUpload',
  
  data() {
    return {
      uploadedFiles: [],
      isDragOver: false,
      error: null
    };
  },

  computed: {
    totalDatasets() {
      return this.uploadedFiles.reduce((sum, file) => sum + file.dataCount, 0);
    },

    uniqueCategories() {
      const categories = new Set();
      this.uploadedFiles.forEach(file => {
        file.data.forEach(item => {
          if (item.category) categories.add(item.category);
        });
      });
      return Array.from(categories);
    },

    uniqueKeywords() {
      const keywords = new Set();
      this.uploadedFiles.forEach(file => {
        file.data.forEach(item => {
          if (item.keyword && Array.isArray(item.keyword)) {
            item.keyword.forEach(k => keywords.add(k));
          }
        });
      });
      return Array.from(keywords);
    },

    combinedData() {
      const allData = [];
      this.uploadedFiles.forEach(file => {
        allData.push(...file.data);
      });
      return allData;
    }
  },

  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    handleFileSelect(event) {
      const files = Array.from(event.target.files);
      this.processFiles(files);
    },

    handleDrop(event) {
      event.preventDefault();
      this.isDragOver = false;
      const files = Array.from(event.dataTransfer.files);
      this.processFiles(files);
    },

    handleDragOver(event) {
      event.preventDefault();
      this.isDragOver = true;
    },

    handleDragLeave(event) {
      event.preventDefault();
      this.isDragOver = false;
    },

    async processFiles(files) {
      this.error = null;
      
      const jsonFiles = files.filter(file => file.name.endsWith('.json'));
      
      if (jsonFiles.length === 0) {
        this.error = 'JSON 파일만 업로드할 수 있습니다.';
        return;
      }

      for (const file of jsonFiles) {
        try {
          const text = await this.readFileAsText(file);
          const data = JSON.parse(text);
          
          if (!Array.isArray(data)) {
            throw new Error('JSON 파일은 배열 형태여야 합니다.');
          }

          const validData = this.validateAndCleanData(data);
          
          if (validData.length === 0) {
            throw new Error('유효한 데이터가 없습니다.');
          }

          this.uploadedFiles.push({
            name: file.name,
            data: validData,
            dataCount: validData.length
          });

        } catch (error) {
          this.error = `${file.name}: ${error.message}`;
          return;
        }
      }
    },

    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error('파일을 읽을 수 없습니다.'));
        reader.readAsText(file);
      });
    },

    validateAndCleanData(data) {
      return data.filter(item => {
        if (!item.title || !item.description) {
          return false;
        }

        if (!item.keyword || !Array.isArray(item.keyword)) {
          item.keyword = [];
        }

        if (!item.category) {
          item.category = '기타';
        }

        return true;
      });
    },

    removeFile(index) {
      this.uploadedFiles.splice(index, 1);
    },

    clearAll() {
      this.uploadedFiles = [];
      this.error = null;
    },

    startAnalysis() {
      if (this.totalDatasets === 0) {
        this.error = '분석할 데이터가 없습니다.';
        return;
      }

      this.$emit('data-uploaded', this.combinedData);
    }
  }
};
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 3rem;
}

.header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  line-height: 1.6;
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-area {
  border: 3px dashed #bdc3c7;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.upload-area:hover {
  border-color: #3498db;
  background: #e3f2fd;
}

.upload-area.drag-over {
  border-color: #2ecc71;
  background: #e8f5e8;
  transform: scale(1.02);
}

.upload-icon {
  color: #95a5a6;
  margin-bottom: 1rem;
}

.upload-text h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
}

.upload-text p {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.format-info {
  margin-top: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 4px solid #3498db;
}

.format-info h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.format-example {
  background: #2c3e50;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
}

.format-example pre {
  margin: 0;
  color: #ecf0f1;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.4;
}

.files-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.files-section h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 0.5rem;
}

.files-list {
  margin-bottom: 2rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.file-stats {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.remove-btn:hover {
  background: #ffeaea;
}

.data-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.25rem;
}

.summary-item .value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.clear-btn, .analyze-btn {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn {
  background: #95a5a6;
  color: white;
}

.clear-btn:hover {
  background: #7f8c8d;
}

.analyze-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.analyze-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.error-message {
  background: #e74c3c;
  color: white;
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  text-align: center;
}

@media (max-width: 768px) {
  .upload-container {
    padding: 1rem;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .upload-area {
    padding: 2rem 1rem;
  }
  
  .data-summary {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
