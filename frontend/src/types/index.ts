export enum LogAnalyserType {
  Client = 'client',
  Operation = 'operation'
}

export enum LogAnalyserStatusType {
  None = 'None',
  Running = 'Running',
  Ready = 'Ready',
  Error = 'Error'
}

declare global {
  interface Window {
    electronAPI: {
      [index: string]: void;
    };
  }
}
