"""
账户查询处理器模块
负责账户信息查询和处理
"""

import json
import re
from typing import Dict, List, Any, Optional
import pandas as pd

from .models import AccountInfo, ProcessingState, RequestPairsDict


class AccountProcessor:
    """账户查询处理器类"""
    
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        self.query_accounts = {}
        self.query_accounts_df = {}
    
    def parse_account_query(self) -> None:
        """
        解析账户查询数据
        """
        # 处理账户查询结果
        for query_time, user_account_str in self.query_accounts.items():
            user_account_dict = json.loads(user_account_str)["result"]["data"]["account_fn"]["list_account_portfolio"]["edges"]
            df_user_account = self._handle_once_account_query(user_account_dict)
            self.query_accounts_df[query_time] = df_user_account
            self._update_fund_mappings(df_user_account)
        
        # 处理upload_fund_info请求
        self._process_upload_fund_info()
        
        # 处理list_account_portfolio请求
        self._process_list_account_portfolio()
    
    def _handle_once_account_query(self, query_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        处理单次账户查询数据
        
        Args:
            query_data: 查询数据
            
        Returns:
            账户信息DataFrame
        """
        result = []
        for item in query_data:
            fund_token = item["portfolios"][0]["fund_token"]
            if fund_token in self.state.client_fundtoken_mapping.keys():
                fund_token = self.state.client_fundtoken_mapping[fund_token]
            
            result.append({
                "user_id": item["user_id"],
                "fund_token": fund_token,
                "account_code": item["account_code"],
                "account_name": item["account_name"],
                "alias": item["alias"],
                "broker_name": item["broker_name"],
                "broker_id": item["qsid"],
                "trade_type": item["trade_type"],
            })
        
        df_user_account = pd.DataFrame(result, columns=[
            "user_id", "fund_token", "account_code", "account_name", 
            "alias", "broker_id", "broker_name", "trade_type"
        ])
        return df_user_account
    
    def _update_fund_mappings(self, df_user_account: pd.DataFrame) -> None:
        """
        更新资金映射关系
        
        Args:
            df_user_account: 用户账户DataFrame
        """
        # 更新fundtoken_dict
        fundtoken_dict = {}
        for _, row in df_user_account.iterrows():
            value_str = f"{row['account_code']}:{row['broker_name']}:{row['trade_type']}"
            fundtoken_dict[row["fund_token"]] = value_str
        self.state.fundtoken_dict.update(fundtoken_dict)
        
        # 更新fund_dict
        fund_dict = {}
        for _, row in df_user_account.iterrows():
            value_str = f"{row['account_code']}:{row['broker_name']}:{row['trade_type']}"
            value_key = f"{row['account_code']}:{row['trade_type']}"
            fund_dict[value_key] = value_str
        self.state.fund_dict.update(fund_dict)
    
    def _process_upload_fund_info(self) -> None:
        """
        处理upload_fund_info请求
        """
        for key, value in self.req_pairs.items():
            if "upload_fund_info" in json.dumps(value["request"]):
                request = value["request"]
                response = value["response"]
                
                if "error" not in response.keys():
                    query_string = request["params"]["query"]
                    match = re.search(r',fund_token:"([^"]+)"', query_string)
                    token_a = ""
                    if match:
                        token_a = match.group(1)
                    
                    token_b = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["fund_token"]
                    permission_code = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["permission_code"]
                    fund_name = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["account_name"]
                    
                    self.state.client_fundtoken_mapping[token_b] = token_a
                    self.state.client_permissioncode_mapping[token_b] = f'fund_name:{fund_name},permission_code:{permission_code}'
    
    def _process_list_account_portfolio(self) -> None:
        """
        处理list_account_portfolio请求
        """
        for key, value in self.req_pairs.items():
            checkstr = json.dumps(value["request"])
            # 不带with_permission的list_account_portfolio请求是投后分析发起的，需要过滤
            if "list_account_portfolio" in checkstr and "with_permission" in checkstr:
                request = value["request"]
                response = value["response"]
                rsp_time = value["rsp_time"]
                
                user_account_dict = response["result"]["data"]["account_fn"]["list_account_portfolio"]["edges"]
                df_user_account = self._handle_once_account_query(user_account_dict)
                self.query_accounts_df[rsp_time] = df_user_account
                self._update_fund_mappings(df_user_account)
    
    def handle_account_query(self, req_time: str = "") -> Optional[pd.DataFrame]:
        """
        处理账户查询
        
        Args:
            req_time: 请求时间
            
        Returns:
            账户查询结果DataFrame
        """
        if req_time in self.query_accounts_df.keys():
            return self.query_accounts_df[req_time]
        return None
    
    def get_fund_by_fund_token(self, fund_token: str) -> str:
        """
        根据fund_token获取账户名称
        
        Args:
            fund_token: 资金令牌
            
        Returns:
            账户名称
        """
        if fund_token in self.state.fundtoken_dict.keys():
            return self.state.fundtoken_dict[fund_token]
        else:
            return fund_token
    
    def get_all_accounts(self) -> List[str]:
        """
        获取所有账户列表
        
        Returns:
            账户列表
        """
        accounts = []
        for df in self.query_accounts_df.values():
            if not df.empty:
                accounts.extend(df["fund_token"].tolist())
        return list(set(accounts))
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        获取账户汇总信息
        
        Returns:
            账户汇总字典
        """
        total_accounts = 0
        unique_accounts = set()
        
        for df in self.query_accounts_df.values():
            if not df.empty:
                total_accounts += len(df)
                unique_accounts.update(df["fund_token"].tolist())
        
        return {
            "total_account_queries": len(self.query_accounts_df),
            "total_accounts": total_accounts,
            "unique_accounts": len(unique_accounts),
            "account_list": list(unique_accounts)
        }
    
    def show_account_summary(self) -> None:
        """
        显示账户汇总信息
        """
        summary = self.get_account_summary()
        
        print("\n=== 账户查询汇总 ===")
        print(f"账户查询次数: {summary['total_account_queries']}")
        print(f"总账户数: {summary['total_accounts']}")
        print(f"唯一账户数: {summary['unique_accounts']}")
        print(f"账户列表: {summary['account_list']}")
        print("=" * 30)
    
    def export_accounts_to_dataframe(self) -> pd.DataFrame:
        """
        导出账户信息到DataFrame
        
        Returns:
            账户信息DataFrame
        """
        all_accounts = []
        for df in self.query_accounts_df.values():
            if not df.empty:
                all_accounts.append(df)
        
        if all_accounts:
            return pd.concat(all_accounts, ignore_index=True)
        else:
            return pd.DataFrame() 
