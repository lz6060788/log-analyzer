<template>
  <div class="monaco-editor-wrapper" :style="{height}">
    <div ref="editorContainer" class="editor-container" style="width:100%;height:100%"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
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
  defaultWordWrap?: boolean;
  showMinimap?: boolean; // 新增：控制minimap显示
  showPasteDialog?: boolean; // 新增：控制粘贴对话框显示
  enableInteractive?: boolean; // 新增：启用交互功能
  enableHoverLineHighlight?: boolean; // 新增：启用鼠标悬浮行高亮
}

const props = withDefaults(defineProps<Props>(), {
  defaultWordWrap: true,
  enableHoverLineHighlight: true
});
const emit = defineEmits(['update:modelValue', 'scroll', 'contextmenu', 'parse-log', 'log-click']);

const editorContainer = ref<HTMLDivElement | null>(null);
let editor: monaco.editor.IStandaloneCodeEditor | null = null;
let decorations: string[] = [];

// 横向滚动条状态
const isWordWrap = ref(props.defaultWordWrap ?? true);

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

// 处理双击事件
const handleMouseDoubleClick = (e: monaco.editor.IEditorMouseEvent) => {
  if (!props.enableInteractive || !editor) return;
  
  const position = e.target.position;
  if (!position) return;
  
  const lineNumber = position.lineNumber;
  
  // 只向外层抛出双击事件和行数，不进行日志解析
  emit('log-click', { type: 'double-click', lineNumber });
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
      suggestOnTriggerCharacters: false,
      // 启用悬浮提示
      hover: {
        enabled: true,
        delay: 300
      },
      // 行高亮配置
      renderLineHighlight: 'all', // 当前行高亮
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

    // 添加交互功能
    if (props.enableInteractive) {
      // 监听鼠标双击事件
      editor.onMouseDown((e) => {
        // 检查是否为双击事件
        if (e.event && e.event.detail === 2) {
          handleMouseDoubleClick(e);
        }
      });
    }

    // 鼠标悬浮行高亮功能
    if (props.enableHoverLineHighlight) {
      let currentHoverLine: number | null = null;
      editor.onMouseMove((e) => {
        const position = e.target.position;
        if (position) {
          const lineNumber = position.lineNumber;
          if (currentHoverLine !== lineNumber) {
            // 清除之前的高亮
            if (currentHoverLine) {
              decorations = editor!.deltaDecorations(decorations, []);
            }
            // 添加新的高亮
            currentHoverLine = lineNumber;
            const range = new monaco.Range(lineNumber, 1, lineNumber, 1);
            decorations = editor!.deltaDecorations(decorations, [{
              range: range,
              options: {
                className: 'hover-line-highlight',
                isWholeLine: true
              }
            }]);
          }
        }
      });

      // 鼠标离开编辑器时清除高亮
      editor.onMouseLeave(() => {
        if (currentHoverLine) {
          decorations = editor!.deltaDecorations(decorations, []);
          currentHoverLine = null;
        }
      });
    }

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

/* 交互式行的样式 */
:deep(.log-interactive-line) {
  background-color: rgba(0, 122, 204, 0.1) !important;
  cursor: pointer !important;
}

:deep(.log-interactive-line:hover) {
  background-color: rgba(0, 122, 204, 0.2) !important;
}

/* 鼠标悬浮行高亮样式 */
:deep(.hover-line-highlight) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  border-left: 2px solid rgba(0, 122, 204, 0.5) !important;
}
</style>
