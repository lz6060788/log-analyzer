export type ClientLogLine = {
  content: string;
  req_id: string;
  time: string;
  req_type: string;
  isError: boolean;
  isTimeout: boolean;
  isSkip: boolean;
  isNewTransmit: boolean;
  isResponseWithoutReqId: boolean;
};
