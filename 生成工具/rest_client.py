import requests
import json
import logging
from typing import Dict, Any, Optional
from config import config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_token() -> Optional[str]:
    """获取认证token"""
    # 如果已经获取过token，直接返回
    if config.has_token:
        logger.info("Token已存在，直接返回")
        return config.token
    
    logger.info("开始获取token...")
    
    # 构建请求体
    auth_data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": config.USERNAME,
                        "password": config.PASSWORD,
                        "domain": {
                            "name": config.DOMAIN_NAME
                        }
                    }
                }
            },
            "scope": {
                "project": {
                    "id": config.PROJECT_ID
                }
            }
        }
    }
    
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    
    try:
        response = requests.post(
            url=config.IAM_URL,
            headers=headers,
            json=auth_data,
            timeout=config.TIMEOUT,
            verify=False  # 跳过SSL证书验证
        )
        
        if response.status_code == 201:
            token = response.headers.get('X-Subject-Token')
            if token:
                config.token = token
                config.has_token = True
                logger.info("Token获取成功")
                print(token)
                return token
            else:
                logger.error("响应头中未找到X-Subject-Token")
        else:
            logger.error(f"Token获取失败，状态码: {response.status_code}")
            
    except Exception as e:
        logger.error(f"获取token失败: {e}")
    
    return None

def api_get(url: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """发送GET请求"""
    return _make_request('GET', url, params=params)

def api_post(url: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """发送POST请求"""
    return _make_request('POST', url, data, params)

def _make_request(method: str, url: str, data: Dict[str, Any] = None, 
                 params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """发送HTTP请求"""
    # 如果没有token，先获取token
    if not config.has_token:
        logger.info("未获取token，先获取token")
        if not get_token():
            logger.error("获取token失败，无法发送请求")
            return None
    
    # 构建请求头
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Auth-Token': config.token
    }
    
    try:
        logger.info(f"发送请求: {method} {url}")
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=config.TIMEOUT,
            verify=False  # 跳过SSL证书验证
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        
        # 如果token过期，重新获取token并重试
        if response.status_code == 401:
            logger.warning("Token可能已过期，重新获取token并重试")
            config.has_token = False  # 重置token状态
            if get_token():  # 重新获取token
                # 使用新token重新发送请求
                headers['X-Auth-Token'] = config.token
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=config.TIMEOUT,
                    verify=False  # 跳过SSL证书验证
                )
                logger.info(f"重试后响应状态码: {response.status_code}")
            else:
                logger.error("重新获取token失败")
                return None
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        logger.error(f"请求失败: {e}")
    
    return None



#TC related function

def api_get_tc_detail_by_number(tc_num: str)-> Optional[Dict[str, Any]]:
    params = {
        "testcase_number": tc_num
    }
    return api_get(config.TC_DETAIL_URL, params)

def api_post_all_tc_with_limit(offset: int, limit: int) -> Optional[Dict[str, Any]]:
    data = {
        "offset": offset,
        "limit": limit,
        "execution_type_id": config.EXECUTION_TYPE_ID
    }
    return api_post(config.TC_ALL_URL, data=data)
    

#SF related function
def api_get_sf_detail_by_id(issue_id: str)-> Optional[Dict[str, Any]]:
    url = config.IPD_DETAIL_URL + issue_id
    params = {
        "issue_type": "SF"
    }
    return api_get(url, params)

def api_post_sf_by_keyword() -> Optional[Dict[str, Any]]:
    data = {
        "keyword": config.SF_KEYWORD
    }
    params = {
        "category": "SF"
    }
    return api_post(config.IPD_TREE_URL, data, params)


#IR related function
def api_get_ir_detail_by_id(issue_id: str)-> Optional[Dict[str, Any]]:
    url = config.IPD_DETAIL_URL + issue_id
    params = {
        "issue_type": "IR"
    }
    return api_get(url, params)

def api_post_ir_list_by_id(issue_id: str) -> Optional[Dict[str, Any]]:
    data = {
        "filter": [
            {
                "id": {
                    "values": [
                        issue_id
                    ],
                    "operator": "||"
                }
            }
        ]
    }
    params = {
        "issue_type": "IR"
    }
    return api_post(config.IPD_LIST_URL, data, params)

#SR related function
def api_get_sr_detail_by_id(issue_id: str)-> Optional[Dict[str, Any]]:
    url = config.IPD_DETAIL_URL + issue_id
    params = {
        "issue_type": "SR"
    }
    return api_get(url, params)

def api_post_sr_list_by_id(issue_id: str) -> Optional[Dict[str, Any]]:
    data = {
        "filter": [
            {
                "id": {
                    "values": [
                        issue_id
                    ],
                    "operator": "||"
                }
            }
        ]
    }
    params = {
        "issue_type": "SR"
    }
    return api_post(config.IPD_LIST_URL, data, params)


#AR related function
def api_get_ar_detail_by_id(issue_id: str)-> Optional[Dict[str, Any]]:
    url = config.IPD_DETAIL_URL + issue_id
    params = {
        "issue_type": "AR"
    }
    return api_get(url, params)