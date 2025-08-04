<template>
  <el-dialog
    v-model="visible"
    title="日志解析"
    :fullscreen="true"
    :show-close="true"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    :destroy-on-close="true"
    class="log-paste-dialog"
    @close="handleClose"
  >
    <div class="log-paste-content">
      <LogPasteView :log-text="logText" />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import LogPasteView from '../../views/LogPasteView.vue';

const visible = ref(false);
const logText = ref('');

// 打开弹窗的方法
const open = (text: string) => {
  logText.value = text;
  visible.value = true;
};

// 关闭弹窗的方法
const close = () => {
  visible.value = false;
  logText.value = '';
};

// 处理弹窗关闭事件
const handleClose = () => {
  close();
};

// 暴露方法给外部使用
defineExpose({
  open,
  close
});
</script>

<style scoped>
.log-paste-dialog {
  :deep(.el-dialog) {
    margin: 0;
    border-radius: 0;
  }

  :deep(.el-dialog__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #e4e7ed;
  }

  :deep(.el-dialog__body) {
    padding: 0;
    height: calc(100vh - 60px);
    overflow: hidden;
  }
}

.log-paste-content {
  height: 100%;
  padding: 20px;
  overflow-y: auto;
}
</style>