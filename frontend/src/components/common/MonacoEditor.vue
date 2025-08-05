<template>
  <div class="monaco-editor-wrapper" :style="{height}">
    <div ref="editorContainer" class="editor-container" style="width:100%;height:100%"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import * as monaco from 'monaco-editor';
import { initializeLogLanguages } from '@/utils/logLanguageManager';

// 全局类型声明
declare global {
  interface Window {
    __logLanguagesInitialized?: boolean;
  }
}

interface Props {
  modelValue: string;
  height?: string;
  readonly?: boolean;
  language?: string;
  theme?: string;
  showMinimap?: boolean; // 新增：控制minimap显示
  showPasteDialog?: boolean; // 新增：控制粘贴对话框显示
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue', 'scroll', 'contextmenu', 'parse-log']);

const editorContainer = ref<HTMLDivElement | null>(null);
let editor: monaco.editor.IStandaloneCodeEditor | null = null;

// 横向滚动条状态
const isWordWrap = ref(true);

// 暴露给父组件的方法
const getSelectedText = (): string => {
  if (!editor) return '';
  const selection = editor.getSelection();
  if (!selection) return '';
  return editor.getModel()?.getValueInRange(selection) || '';
};

const getEditor = () => editor;

// 切换横向滚动条显示状态
const toggleHorizontalScrollbar = () => {
  if (!editor) return;

  isWordWrap.value = !isWordWrap.value;

  // 更新编辑器配置
  editor.updateOptions({
    wordWrap: isWordWrap.value ? 'off' : 'on'
  });
};

// 暴露方法给父组件
defineExpose({
  getSelectedText,
  getEditor,
  toggleHorizontalScrollbar
});

onMounted(() => {
  // 初始化日志语言管理器 - 只在第一次初始化时执行
  if (!window.__logLanguagesInitialized) {
    initializeLogLanguages();
    window.__logLanguagesInitialized = true;
  }

  if (editorContainer.value) {
    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue,
      language: props.language || 'plaintext',
      theme: props.theme || 'vs-dark',
      readOnly: props.readonly || false,
      automaticLayout: true,
      minimap: {
        enabled: props.showMinimap !== false, // 默认启用，可通过props控制
        size: 'proportional',
        side: 'right',
        showSlider: 'mouseover',
        maxColumn: 120
      },
      scrollBeyondLastLine: false,
      fontSize: 14,
      lineNumbers: 'on',
      roundedSelection: false,
      wordWrap: isWordWrap.value ? 'off' : 'on',
      scrollbar: {
        vertical: 'visible',
        horizontal: 'visible'
      },
      // 配置右键菜单
      contextmenu: true,
      // 自定义右键菜单
      quickSuggestions: false,
      suggestOnTriggerCharacters: false
    });

    // 自定义右键菜单
    if (props.showPasteDialog) {
      editor.addAction({
        id: 'parse-log',
        label: '解析选中日志',
        keybindings: [],
        contextMenuGroupId: '1_modification',
        contextMenuOrder: 1.5,
        run: (editor) => {
          const selection = editor.getSelection();
          if (selection) {
            const selectedText = editor.getModel()?.getValueInRange(selection) || '';
            if (selectedText.trim()) {
              // 触发自定义事件
              emit('parse-log', selectedText);
            }
          }
        }
      });
    }

    editor.addAction({
      id: 'copy-selection',
      label: '复制选中内容',
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyC],
      contextMenuGroupId: '1_modification',
      contextMenuOrder: 1.0,
      run: (editor) => {
        const selection = editor.getSelection();
        if (selection) {
          const selectedText = editor.getModel()?.getValueInRange(selection) || '';
          if (selectedText.trim()) {
            navigator.clipboard.writeText(selectedText);
          }
        }
      }
    });

    // 添加横向滚动条控制菜单项
    editor.addAction({
      id: 'toggle-horizontal-scrollbar',
      label: '切换横向滚动条',
      keybindings: [],
      contextMenuGroupId: '2_view',
      contextMenuOrder: 1.0,
      run: (editor) => {
        toggleHorizontalScrollbar();
      }
    });

    editor.onDidChangeModelContent(() => {
      if (editor) {
        emit('update:modelValue', editor.getValue());
      }
    });

    // 监听滚动事件
    editor.onDidScrollChange((e) => {
      // 获取编辑器的视口高度
      const viewportHeight = editor!.getLayoutInfo().height;

      emit('scroll', {
        target: {
          scrollTop: e.scrollTop,
          scrollHeight: e.scrollHeight,
          clientHeight: viewportHeight
        }
      });
    });

    // 监听右键菜单事件
    editor.onContextMenu((e) => {
      emit('contextmenu', e);
    });
  }
});

watch(() => props.modelValue, (val) => {
  if (editor && editor.getValue() !== val) {
    editor.setValue(val);
  }
});

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose();
  }
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
