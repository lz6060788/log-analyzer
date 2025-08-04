import * as monaco from 'monaco-editor';
import { registerClientLogLanguage, registerClientLogTheme } from './clientLogLanguage';
import { registerAdvancedLogLanguage, registerAdvancedLogTheme } from './advancedLogLanguage';

/**
 * 日志语言类型枚举
 */
export enum LogLanguageType {
  CLIENT = 'client-log',
  ADVANCED = 'advanced-log'
}

/**
 * 日志主题类型枚举
 */
export enum LogThemeType {
  CLIENT = 'client-log-theme',
  ADVANCED = 'advanced-log-theme'
}

/**
 * 日志语言配置管理器
 * 提供统一的日志语言注册和管理功能
 */
export class LogLanguageManager {
  private static instance: LogLanguageManager;
  private isInitialized = false;

  private constructor() {}

  /**
   * 获取单例实例
   */
  public static getInstance(): LogLanguageManager {
    if (!LogLanguageManager.instance) {
      LogLanguageManager.instance = new LogLanguageManager();
    }
    return LogLanguageManager.instance;
  }

  /**
   * 初始化所有日志语言和主题
   */
  public initialize(): void {
    if (this.isInitialized) {
      return;
    }

    try {
      // 注册基础日志语言
      registerClientLogLanguage();
      registerClientLogTheme();

      // 注册高级日志语言
      registerAdvancedLogLanguage();
      registerAdvancedLogTheme();

      this.isInitialized = true;
      console.log('日志语言管理器初始化完成');
    } catch (error) {
      console.error('日志语言管理器初始化失败:', error);
    }
  }

  /**
   * 获取可用的日志语言列表
   */
  public getAvailableLanguages(): Array<{ id: string; name: string; description: string }> {
    return [
      {
        id: LogLanguageType.CLIENT,
        name: '客户端日志',
        description: '支持基本的日志格式高亮（时间戳、UUID、日志级别等）'
      },
      {
        id: LogLanguageType.ADVANCED,
        name: '操作日志',
        description: '支持更复杂的日志格式高亮（IP地址、文件路径、异常类型等）'
      }
    ];
  }

  /**
   * 获取可用的日志主题列表
   */
  public getAvailableThemes(): Array<{ id: string; name: string; description: string }> {
    return [
      {
        id: LogThemeType.CLIENT,
        name: '客户端日志主题',
        description: '适合客户端日志格式的深色主题'
      },
      {
        id: LogThemeType.ADVANCED,
        name: '高级日志主题',
        description: '适合复杂日志格式的深色主题，颜色更丰富'
      }
    ];
  }

  /**
   * 验证语言是否已注册
   */
  public isLanguageRegistered(languageId: string): boolean {
    return monaco.languages.getLanguages().some(lang => lang.id === languageId);
  }

  /**
   * 验证主题是否已注册
   */
  public isThemeRegistered(themeId: string): boolean {
    // Monaco Editor没有直接的方法检查主题是否注册
    // 这里我们通过尝试获取主题来验证
    try {
      monaco.editor.defineTheme(themeId, { base: 'vs-dark', inherit: true, rules: [], colors: {} });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 获取推荐的语言和主题组合
   */
  public getRecommendedConfig(): { language: string; theme: string } {
    return {
      language: LogLanguageType.ADVANCED,
      theme: LogThemeType.ADVANCED
    };
  }
}

/**
 * 便捷函数：初始化日志语言管理器
 */
export function initializeLogLanguages(): void {
  LogLanguageManager.getInstance().initialize();
}

/**
 * 便捷函数：获取推荐配置
 */
export function getRecommendedLogConfig(): { language: string; theme: string } {
  return LogLanguageManager.getInstance().getRecommendedConfig();
}
