<template>
  <div class="monaco-editor-wrapper" :style="{height}">
    <div ref="editorContainer" class="editor-container" style="width:100%;height:100%"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import * as monaco from 'monaco-editor';

interface Props {
  modelValue: string;
  height?: string;
  readonly?: boolean;
  language?: string;
  theme?: string;
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue']);

const editorContainer = ref<HTMLDivElement | null>(null);
let editor: monaco.editor.IStandaloneCodeEditor | null = null;

onMounted(() => {
  if (editorContainer.value) {
    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue,
      language: props.language || 'plaintext',
      theme: props.theme || 'vs-dark',
      readOnly: props.readonly || false,
      automaticLayout: true,
      minimap: { enabled: false },
    });
    editor.onDidChangeModelContent(() => {
      emit('update:modelValue', editor!.getValue());
    });
  }
});

watch(() => props.modelValue, (val) => {
  if (editor && editor.getValue() !== val) {
    editor.setValue(val);
  }
});

onBeforeUnmount(() => {
  editor?.dispose();
});
</script>

<style scoped>
.monaco-editor-wrapper {
  width: 100%;
  min-height: 100px;
}
.editor-container {
  width: 100%;
  height: 100%;
}
</style> 
