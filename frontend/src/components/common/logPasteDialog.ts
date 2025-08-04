import { createApp, h } from 'vue';
import LogPasteDialog from './LogPasteDialog.vue';

interface LogPasteDialogInstance {
  open: (text: string) => void;
  close: () => void;
}

let dialogInstance: LogPasteDialogInstance | null = null;
let currentContainer: HTMLElement | null = null;
let currentApp: any = null;

/**
 * 清理当前弹窗实例
 */
function cleanupDialog(): void {
  if (dialogInstance) {
    dialogInstance = null;
  }
  
  if (currentApp) {
    try {
      currentApp.unmount();
    } catch (error) {
      console.warn('卸载应用时出错:', error);
    }
    currentApp = null;
  }

  if (currentContainer && document.body.contains(currentContainer)) {
    try {
      document.body.removeChild(currentContainer);
    } catch (error) {
      console.warn('移除容器时出错:', error);
    }
    currentContainer = null;
  }
}

/**
 * 打开日志解析弹窗
 * @param text 要解析的日志文本
 */
export function openLogPasteDialog(text: string): void {
  if (dialogInstance) {
    // 如果已经存在实例，直接打开
    dialogInstance.open(text);
    return;
  }

  // 确保清理之前的实例
  cleanupDialog();

  // 创建新的弹窗实例
  const container = document.createElement('div');
  container.id = 'log-paste-dialog-container';
  document.body.appendChild(container);
  currentContainer = container;

  const app = createApp({
    render() {
      return h(LogPasteDialog, {
        ref: (el: any) => {
          if (el) {
            dialogInstance = el;
            currentApp = app;

            // 打开弹窗
            el.open(text);

            // 重写close方法以处理清理
            const originalClose = el.close;
            el.close = () => {
              originalClose();
              // 延迟清理，确保弹窗动画完成
              setTimeout(() => {
                cleanupDialog();
              }, 100);
            };
          }
        }
      });
    }
  });

  app.mount(container);
}

/**
 * 关闭日志解析弹窗
 */
export function closeLogPasteDialog(): void {
  if (dialogInstance) {
    dialogInstance.close();
  } else {
    // 如果没有实例，直接清理
    cleanupDialog();
  }
}
