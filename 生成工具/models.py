import time
import os
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
from config import config, calculate_relative_path
from rest_client import api_get_tc_detail_by_number, api_post_all_tc_with_limit, api_get_sf_detail_by_id, api_post_sf_by_keyword, api_get_ir_detail_by_id, api_post_ir_list_by_id, api_get_sr_detail_by_id, api_post_sr_list_by_id, api_get_ar_detail_by_id


class SF: pass
class IR: pass
class SR: pass
class AR: pass

class DataRegistry:
    """数据注册表 - 用于快速查找"""
    def __init__(self):
        # IR和SR使用req_id作为键
        self.ir_by_req_id: Dict[str, IR] = {}
        self.sr_by_req_id: Dict[str, SR] = {}
        
        # AR有两个字典：一个按id，一个按req_id
        self.ar_by_id: Dict[str, AR] = {}
        self.ar_by_req_id: Dict[str, AR] = {}
        
        # 测试用例按number作为键
        self.test_case_by_number: Dict[str, TestCase] = {}
    
    def register_ir(self, ir: 'IR'):
        """注册IR（使用req_id）"""
        if ir and ir.req_id:
            self.ir_by_req_id[ir.req_id] = ir
    
    def register_sr(self, sr: 'SR'):
        """注册SR（使用req_id）"""
        if sr and sr.req_id:
            self.sr_by_req_id[sr.req_id] = sr
    
    def register_ar(self, ar: 'AR'):
        """注册AR（同时使用id和req_id）"""
        if not ar:
            return
        
        # 按id注册
        if ar.id:
            self.ar_by_id[ar.id] = ar
        
        # 按req_id注册（如果存在）
        if ar.req_id:
            self.ar_by_req_id[ar.req_id] = ar
    
    def register_test_case(self, test_case: 'TestCase'):
        """注册测试用例（使用number）"""
        if test_case and test_case.number:
            self.test_case_by_number[test_case.number] = test_case
    
    def get_ir(self, req_id: str) -> Optional['IR']:
        """通过req_id获取IR"""
        return self.ir_by_req_id.get(req_id)
    
    def get_sr(self, req_id: str) -> Optional['SR']:
        """通过req_id获取SR"""
        return self.sr_by_req_id.get(req_id)
    
    def get_ar_by_id(self, ar_id: str) -> Optional['AR']:
        """通过id获取AR"""
        return self.ar_by_id.get(ar_id)
    
    def get_ar(self, req_id: str) -> Optional['AR']:
        """通过req_id获取AR"""
        return self.ar_by_req_id.get(req_id)
    
    def get_test_case(self, number: str) -> Optional['TestCase']:
        """通过number获取测试用例"""
        return self.test_case_by_number.get(number)
    
    def get_all_ir(self) -> List['IR']:
        """获取所有IR"""
        return list(self.ir_by_req_id.values())
    
    def get_all_sr(self) -> List['SR']:
        """获取所有SR"""
        return list(self.sr_by_req_id.values())
    
    def get_all_ar(self) -> List['AR']:
        """获取所有AR（去重，因为有两个字典）"""
        # 使用ar_by_id作为主要来源，因为id是唯一的
        return list(self.ar_by_id.values())
    
    def get_all_test_cases(self) -> List['TestCase']:
        """获取所有测试用例"""
        return list(self.test_case_by_number.values())

# 全局数据注册表实例
data_registry = DataRegistry()


@dataclass
class TestCaseDetail:
    """测试用例详情类"""
    id: str = ""
    name: str = ""
    number: str = ""
    creator: str = ""
    preparation: str = ""
    test_step: str = ""
    expect_result: str = ""
    description: str = ""
    related_ar_id: str = ""  # 关联的AR的id
    related_ar_name: str = ""  # 关联AR的名称
    html_file: str = ""  # html文件
    owner: Optional['TestCase'] = None  # 隶属于的测试用例类
    
    def load_detail_by_number(self, number: str) -> bool:
        """通过number获取测试用例详情"""
        if not number:
            print("测试用例number为空，无法获取详情")
            return False
        
        data = api_get_tc_detail_by_number(number)
        if not data:
            return False
        
        return self._update_from_data(data)
    
    def _update_from_data(self, data: dict) -> bool:
        """从详情数据更新测试用例详情"""
        try:
            # 根据提供的JSON结构解析数据
            self.id = data.get("testcase_id", "")
            self.number = data.get("testcase_number", "")
            self.name = data.get("name", "")
            
            # 获取扩展信息
            extend_info = data.get("extend_info", {})
            
            # 获取作者信息（直接处理）
            author_info = extend_info.get("author", {})
            if isinstance(author_info, dict):
                self.creator = author_info.get("name", "")
            
            # 获取准备步骤
            self.preparation = extend_info.get("preparation", "")
            
            # 结构化处理测试步骤和期望结果
            self._process_steps_data(extend_info)
            
            # 获取描述
            self.description = extend_info.get("description", "")
            
            # 获取关联的issue信息（直接处理）
            issue_info = extend_info.get("issue", {})
            if isinstance(issue_info, dict):
                self.related_ar_id = issue_info.get("id", "")
                self.related_ar_name = issue_info.get("name", "")
            
            return True
            
        except Exception as e:
            print(f"更新测试用例详情失败: {e}")
            return False
    
    def _process_steps_data(self, extend_info: dict):
        """处理steps数据，生成适合HTML输出的格式"""
        steps = extend_info.get("steps", [])
        if not steps or not isinstance(steps, list):
            return
        
        all_test_steps = []
        all_expect_results = []
        
        for step in steps:
            if isinstance(step, dict):
                test_step = step.get("test_step", "").strip()
                expect_result = step.get("expect_result", "").strip()
                
                # 清理HTML，确保格式正确
                if test_step:
                    # 移除多余的空白字符，但保留HTML标签
                    test_step = " ".join(test_step.split())
                    all_test_steps.append(test_step)
                
                if expect_result:
                    expect_result = " ".join(expect_result.split())
                    all_expect_results.append(expect_result)
        
        # 合并steps，保留HTML标签
        if all_test_steps:
            # 用<br><br>分隔不同的step，便于在HTML中显示为不同段落
            self.test_step = "<br><br>".join(all_test_steps)
        
        if all_expect_results:
            self.expect_result = "<br><br>".join(all_expect_results)
    
    def get_formatted_steps(self) -> List[str]:
        """获取格式化的测试步骤列表（每个step作为单独元素）"""
        if not self.test_step:
            return []
        
        # 根据<br><br>分割回单独的步骤
        steps = self.test_step.split("<br><br>")
        return [step.strip() for step in steps if step.strip()]
    
    def get_formatted_results(self) -> List[str]:
        """获取格式化的期望结果列表（每个结果作为单独元素）"""
        if not self.expect_result:
            return []
        
        # 根据<br><br>分割回单独的结果
        results = self.expect_result.split("<br><br>")
        return [result.strip() for result in results if result.strip()]


@dataclass
class TestCase:
    """测试用例类"""
    id: str = ""
    name: str = ""
    status: str = ""
    number: str = ""
    description: str = ""
    execution_type: str = ""
    test_type: str = ""
    related_ar_name: str = ""
    related_ar_req_id: str = ""
    related_sr_req_id: str = ""
    related_ir_req_id: str = ""
    html_file: str = ""
    test_case_detail: TestCaseDetail = field(default_factory=TestCaseDetail)
    
    def __post_init__(self):
        """初始化"""
        # 使用默认工厂创建时，test_case_detail已经是一个实例
        # 可以直接设置owner
        self.test_case_detail.owner = self
        
        # 注意：这里不注册到data_registry，因为number可能还没有值
        # 注册会在update_from_api_data中完成（当number被赋值后）
    
    def update_from_api_data(self, tc_data: dict) -> bool:
        """从API数据更新测试用例信息，并加载详情"""
        try:
            # 更新基础信息
            self.id = tc_data.get("id", "")
            self.number = tc_data.get("number", "")
            self.name = tc_data.get("name", "")
            self.description = tc_data.get("description", "")
            
            # 检查是否以tc_OS开头（大小写敏感）
            if not self.number.startswith("tc_OS"):
            	  print(f"测试用例number '{self.number}' 不以'tc_OS'开头，跳过")
            	  return False
            # 更新状态
            status_data = tc_data.get("status", {})
            if isinstance(status_data, dict):
                self.status = status_data.get("name", "")
            
            # 更新执行类型
            execution_type_data = tc_data.get("execution_type", {})
            if isinstance(execution_type_data, dict):
                self.execution_type = execution_type_data.get("name", "")
            
            # 更新测试类型
            test_type_data = tc_data.get("test_type", {})
            if isinstance(test_type_data, dict):
                self.test_type = test_type_data.get("name", "")
            
            # 查找关联的AR并添加到其test_cases列表
            associate_info = tc_data.get("associate_issue_info", {})
            if associate_info and associate_info.get("associate") and associate_info.get("tracker_name") == "AR":
                issue_id = associate_info.get("issue_id", "")
                if issue_id:
                    # 通过issue_id在DataRegistry中查找AR
                    ar = data_registry.get_ar_by_id(issue_id)
                    if ar:
                        # 添加到AR的test_cases列表
                        ar.add_test_case(self)
                        self.related_ar_req_id = ar.req_id
                        self.related_ar_name = ar.title
                        
                        # 通过AR的parent追溯SR和IR的req_id
                        if ar.parent:  # SR
                            self.related_sr_req_id = ar.parent.req_id
                            
                            if ar.parent.parent:  # IR
                                self.related_ir_req_id = ar.parent.parent.req_id
                    else:
                        print(f"警告: 未找到issue_id为 {issue_id} 的AR")
            
            # 在设置完基本信息后，立即加载测试用例详情
            if self.number:
                # 现在number有值了，注册到DataRegistry
                data_registry.register_test_case(self)
            
            return True
            
        except Exception as e:
            print(f"更新测试用例信息失败: {e}")
            return False

    def load_detail(self) -> bool:
        """加载测试用例详情"""
        if not self.number:
            print("测试用例number为空，无法获取详情")
            return False
        
        print(f"正在加载测试用例详情: {self.number}")
        return self.test_case_detail.load_detail_by_number(self.number)

@dataclass
class TestSuite:
    """测试套件类 - 管理测试用例集合"""
    test_cases: List[TestCase] = field(default_factory=list)
    html_file: str = ""
    total: int = 0  # 测试用例总数
    act_total: int = 0  # 测试用例总数0
    
    def load_all_test_cases(self, batch_size: int = 100) -> bool:
        """分批获取所有测试用例"""
        print(f"开始分批获取测试用例，每批 {batch_size} 个")
        
        # 先获取第一批，得到总数
        if not self._load_batch(offset=0, limit=batch_size):
            return False
        
        print(f"测试用例总数: {self.total}")
        
        if self.total <= batch_size:
            # 如果总数小于等于批次大小，已经获取完毕
            print("测试用例已全部获取完成")
            return True
        
        # 计算需要获取的批次数量
        total_batches = (self.total + batch_size - 1) // batch_size
        print(f"需要分 {total_batches} 批获取")
        
        # 从第二批次开始获取（第一批已经获取过了）
        for batch_num in range(1, total_batches):
            offset = batch_num * batch_size
            print(f"正在获取第 {batch_num + 1}/{total_batches} 批，offset={offset}")
            
            if not self._load_batch(offset=offset, limit=batch_size):
                print(f"第 {batch_num + 1} 批获取失败")
                # 可以继续尝试获取下一批
            
        self.act_total = len(self.test_cases)
        print(f"测试用例获取完成，共获取 {self.act_total} 个测试用例")
        return self._load_all_test_case_details()
    
    def _load_batch(self, offset: int, limit: int) -> bool:
        """获取单批测试用例数据"""
        data = api_post_all_tc_with_limit(offset=offset, limit=limit)
        
        if not data:
            print(f"获取第 {offset//limit + 1} 批测试用例数据失败")
            return False
        
        # 更新总数（只在第一次获取时设置）
        if offset == 0:
            self.total = data.get("total", 0)
        
        values = data.get("values", [])
        print(f"第 {offset//limit + 1} 批获取到 {len(values)} 个测试用例数据")
        
        success_count = 0
        for tc_data in values:
            if self._create_and_add_test_case(tc_data):
                success_count += 1
        
        print(f"第 {offset//limit + 1} 批成功创建 {success_count}/{len(values)} 个测试用例")
        return success_count > 0
    
    def _create_and_add_test_case(self, tc_data: dict) -> bool:
        """创建测试用例并添加到列表"""
        try:
            # 创建测试用例对象
            test_case = TestCase()
            
            # 从API数据更新测试用例信息（会自动加载详情）
            if test_case.update_from_api_data(tc_data):
                # 添加到测试套件列表
                self.test_cases.append(test_case)
                return True
            else:
                print(f"创建测试用例失败，数据: {tc_data.get('number', '未知')}")
                del test_case
                return False
                
        except Exception as e:
            print(f"创建测试用例异常: {e}, 数据: {tc_data}")
            return False

    def _load_all_test_case_details(self) -> bool:
        """批量加载所有测试用例的详情"""
        if not self.test_cases:
            print("没有测试用例需要加载详情")
            return False
        
        print(f"\n开始批量加载所有测试用例的详情...")
        success_count = 0
        total_count = len(self.test_cases)
        
        for i, test_case in enumerate(self.test_cases, 1):
            # 显示进度
            if i % 10 == 0 or i == total_count:
                print(f"进度: {i}/{total_count}")
            
            if test_case.load_detail():
                success_count += 1
            time.sleep(0.1) 
        
        print(f"测试用例详情加载完成: {success_count}/{total_count} 成功")
        return success_count > 0


    def sort_test_cases_by_number(self):
        """按number对测试用例进行排序，number格式：tc_OS_XX_XX_XX_XX"""
        if not self.test_cases:
            print("没有测试用例需要排序")
            return
        
        print(f"开始对 {len(self.test_cases)} 个测试用例进行排序...")
        
        def extract_numbers(number_str):
            """从tc_OS_XX_XX_XX_XX格式中提取数字"""
            if not number_str:
                return (0, 0, 0, 0)  # 返回默认值
            
            # 移除前缀"tc_OS_"
            if number_str.startswith("tc_OS_"):
                number_part = number_str[6:]  # 移除"tc_OS_"
            else:
                # 如果不是标准格式，返回默认值
                print(f"警告: 测试用例number格式异常: {number_str}")
                return (0, 0, 0, 0)
            
            # 按"_"分割并转换为整数
            parts = number_part.split("_")
            numbers = []
            
            for part in parts:
                try:
                    numbers.append(int(part))
                except ValueError:
                    numbers.append(0)  # 如果无法转换为整数，使用0
            
            # 确保有4个数字（不足的补0）
            while len(numbers) < 4:
                numbers.append(0)
            
            # 只取前4个数字
            return tuple(numbers[:4])
        
        # 对测试用例进行排序
        self.test_cases.sort(key=lambda tc: extract_numbers(tc.number))
        print("测试用例排序完成")
    
    def get_test_cases(self) -> List[TestCase]:
        """获取所有测试用例"""
        return self.test_cases
    
    def print_summary(self):
        """打印测试套件摘要"""
        print(f"\n测试套件摘要:")
        print(f"  HTML文件: {self.html_file}")
        print(f"  测试用例总数: {self.total}")
        print(f"  已获取测试用例数: {len(self.test_cases)}")
        
        if self.test_cases:
            # 统计状态分布
            status_count = {}
            for tc in self.test_cases:
                status = tc.status or "未知"
                status_count[status] = status_count.get(status, 0) + 1
            
            print(f"  状态分布:")
            for status, count in status_count.items():
                print(f"    {status}: {count}")
    

@dataclass
class DetailedDescription:
    """详细描述类"""
    content: str = ""
    owner: Optional[Union[SF, IR, SR, AR]] = None
    html_file: str = ""
    
    def generate_html(self):
        """
        生成详细描述的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            print("错误: DetailedDescription的html_file未设置")
            return
        
        if not self.owner or not hasattr(self.owner, 'html_file'):
            print("错误: DetailedDescription的owner未设置或无效")
            return
        
        # 计算返回上一级的相对路径
        back_link = "#"
        if self.owner.html_file:
            back_link = calculate_relative_path(self.html_file, self.owner.html_file)
        
        # 构建HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>需求描述</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}
        
        h1 {{
              font-size: 28px;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #3498db;
        }}
        
        .text-box {{
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 25px;
            margin: 0;
            white-space: pre-line;
            font-size: 14px;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
          <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回上一级</a>
    <div class="container">
        <h1>需求描述</h1>
        
        <div class="text-box">
{self.content if self.content else "暂无内容"}
        </div>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成详细描述HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")

@dataclass
class ReviewRecord:
    """评审记录类"""
    title: str = ""
    req_id: str = ""
    req_name: str = ""
    plan_start_date: str = ""
    plan_end_date: str = ""
    reviewer: str = ""
    cc_name: str = ""
    approver: str = ""
    result: str = ""
    owner: Optional[Union['SF', 'IR', 'SR', 'AR']] = None
    html_file: str = ""

    def generate_html(self):
        """
        生成评审记录的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            return
        
        # 计算返回上一级的相对路径
        back_link = "#"
        if self.owner and self.owner.html_file:
            back_link = calculate_relative_path(self.html_file, self.owner.html_file)
        
        # 获取需求ID和名称（owner里肯定存在req_id和title）
        req_id = self.owner.req_id if (self.owner and self.owner.req_id) else "无"
        req_name = self.owner.title if (self.owner and self.owner.title) else "无"
        
        # 构建HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>评审记录</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        h1 {{
        	  font-size: 28px;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #3498db;
        }}

        h2 {{
            color: #34495e;
            margin: 25px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}
        
        /* 信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 120px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}

        .modification-list {{
            margin: 20px 0;
        }}        
        .modification-list {{
            margin: 20px 0;
        }}
        
        .modification-item {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: flex-start;
        }}
        
        .modification-item:last-child {{
            border-bottom: none;
        }}
        
        .modification-time {{
            min-width: 180px;
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .modification-user {{
            min-width: 80px;
            color: #2c3e50;
            font-weight: 500;
            margin: 0 15px;
        }}
        
        .modification-action {{
            color: #666;
            flex: 1;
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px 15px;
            margin: 5px 0;
            border-radius: 0 4px 4px 0;
        }}
        
        .action-highlight {{
            color: #0066cc;
            font-weight: 500;
        }}
    </style>
</head>
<body>
	  	      <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回上一级</a>
    <div class="container">
        <h1>评审记录</h1>
        <h2>1. 需求信息</h2>
        <div class="description-box">
            <div class="info-list">
                <div class="info-row">
                    <span class="info-label">需求ID：</span>
                    <span class="info-value">{req_id}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">需求名称：</span>
                    <span class="info-value">{req_name}</span>
                </div>
            </div>
        </div>
        <h2>2. 评审历史记录</h2>
        <span class="info-value">无</span>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成详细描述HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")

@dataclass
class HistoryRecord:
    """历史记录类"""
    req_id: str = ""
    req_name: str = ""
    changes: dict = field(default_factory=dict)
    owner: Optional[Union['SF', 'IR', 'SR', 'AR']] = None
    html_file: str = ""

    def generate_html(self):
        """
        生成历史记录的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            return
        
        # 计算返回上一级的相对路径
        back_link = "SF.html"
        if self.owner and self.owner.html_file:
            back_link = calculate_relative_path(self.html_file, self.owner.html_file)
        
        # 获取需求ID和名称
        req_id = self.owner.req_id if (self.owner and self.owner.req_id) else "无"
        req_name = self.owner.title if (self.owner and self.owner.title) else "无"
        
        # 构建HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>修改记录</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        h1 {{
        	  font-size: 28px;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #3498db;
        }}

        h2 {{
            color: #34495e;
            margin: 25px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #3498db;
        }}
        
        /* 信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 120px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}

        .modification-list {{
            margin: 20px 0;
        }}        
        .modification-list {{
            margin: 20px 0;
        }}
        
        .modification-item {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: flex-start;
        }}
        
        .modification-item:last-child {{
            border-bottom: none;
        }}
        
        .modification-time {{
            min-width: 180px;
            color: #666;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .modification-user {{
            min-width: 80px;
            color: #2c3e50;
            font-weight: 500;
            margin: 0 15px;
        }}
        
        .modification-action {{
            color: #666;
            flex: 1;
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 12px 15px;
            margin: 5px 0;
            border-radius: 0 4px 4px 0;
        }}
        
        .action-highlight {{
            color: #0066cc;
            font-weight: 500;
        }}
    </style>
</head>
<body>
	  	      <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回上一级</a>
    <div class="container">
        <h1>修改记录</h1>
        <h2>1. 需求信息</h2>
        <div class="description-box">
            <div class="info-list">
                <div class="info-row">
                    <span class="info-label">需求ID：</span>
                    <span class="info-value">{req_id}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">需求名称：</span>
                    <span class="info-value">{req_name}</span>
                </div>
            </div>
        </div>
        <h2>2. 修改历史记录</h2>
        <span class="info-value">无</span>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成修改记录HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")

@dataclass
class AR:
    """AR (Action Request) - 最底层"""
    id: str = ""
    req_id: str = ""
    number: str = ""
    title: str = ""
    category: str = ""
    status: str = ""
    workload: float = 0.0
    act_workload: float = 0.0
    creator: str = ""
    domain_value: str = ""
    assignee: str = ""
    status_value: str = ""
    plan_start_date: str = ""
    plan_end_date: str = ""
    plan_dev_end_date: str = ""
    plan_test_end_date: str = ""
    html_file: str = ""
    parent: Optional['SR'] = None
    detailed_description: DetailedDescription = field(default_factory=DetailedDescription)
    review_record: ReviewRecord = field(default_factory=ReviewRecord)
    history_record: HistoryRecord = field(default_factory=HistoryRecord)
    test_cases: List[TestCase] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后自动注册到数据注册表"""
        self.detailed_description.owner = self
        self.review_record.owner = self
        self.history_record.owner = self
        pass

    #创建AR html文件
    def create_ar_html_files(self):
        """为当前AR创建HTML空文件"""
        if not self.title:
            print("AR title为空，无法创建文件")
            return
        
        if not self.parent or not self.parent.title:
            print("AR没有关联的SR或SR title为空")
            return
        
        if not self.parent.parent or not self.parent.parent.title:
            print("SR没有关联的IR或IR title为空")
            return
        
        # 获取IR和SR的title
        ir_title = self.parent.parent.title
        sr_title = self.parent.title
        
        # 构建目录路径
        ar_dir = os.path.join(config.BASE_DIR_NAME, config.REQ_DIR_NAME, ir_title, sr_title, self.title)
        
        # 创建AR专属目录
        if not os.path.exists(ar_dir):
            os.makedirs(ar_dir)
        
        # 设置文件路径
        self.html_file = os.path.join(ar_dir, f"{self.title}.html")
        self.detailed_description.html_file = os.path.join(ar_dir, f"{self.title}描述.html")
        self.review_record.html_file = os.path.join(ar_dir, f"{self.title}评审记录.html")
        self.history_record.html_file = os.path.join(ar_dir, f"{self.title}修改记录.html")
        
        # 创建四个空文件
        for file_path in [
            self.html_file,
            self.detailed_description.html_file,
            self.review_record.html_file,
            self.history_record.html_file
        ]:
            try:
                open(file_path, 'w', encoding='utf-8').close()
                print(f"创建AR文件: {file_path}")
            except Exception as e:
                print(f"创建失败 {file_path}: {e}")

    def _extract_req_ids_from_title(self):
        """从title中提取AR、SR、IR的req_id"""
        if not self.title:
            return None, None, None
        
        # 查找 "LLR_OS_" 关键字
        keyword = "LLR_OS_"
        start_idx = self.title.find(keyword)
        if start_idx == -1:
            return None, None, None
        
        # 提取 LLR_OS_xx_xx_xx 部分
        # 格式为 LLR_OS_xx_xx_xx，xx是两位数字，共5部分
        expected_length = len("LLR_OS_xx_xx_xx")  # 15个字符
        
        # 从关键字开始，取15个字符
        ar_req_id = self.title[start_idx:start_idx + expected_length]
        
        # 验证格式
        parts = ar_req_id.split('_')
        if len(parts) != 5 or parts[0] != "LLR" or parts[1] != "OS":
            return None, None, None
        
        # 生成SR的req_id：LLR_OS_01_02_03 -> HLR_OS_01_02
        sr_parts = ["HLR", "OS", parts[2], parts[3]]
        sr_req_id = '_'.join(sr_parts)
        
        # 生成IR的req_id：HLR_OS_01_02 -> HLR_OS_01
        ir_parts = ["HLR", "OS", parts[2]]
        ir_req_id = '_'.join(ir_parts)
        
        return ar_req_id, sr_req_id, ir_req_id
    
    def _update_req_id_chain(self):
        """更新AR、SR、IR的req_id链,并注册到DataRegistry"""
        if not self.title:
            return False
        
        # 从AR的title提取req_id
        ar_req_id, sr_req_id, ir_req_id = self._extract_req_ids_from_title()
        
        if not ar_req_id:
            return False
        
        # 1. 更新AR的req_id（直接设置）
        self.req_id = ar_req_id
        # 注册AR到DataRegistry
        data_registry.register_ar(self)
        
        # 2. 更新父级SR的req_id（如果为空）
        if self.parent and not self.parent.req_id:
            self.parent.req_id = sr_req_id
            # 注册SR到DataRegistry
            data_registry.register_sr(self.parent)
            
            # 3. 更新父级IR的req_id（如果为空）
            if self.parent.parent and not self.parent.parent.req_id:
                self.parent.parent.req_id = ir_req_id
                # 注册IR到DataRegistry
                data_registry.register_ir(self.parent.parent)
        
        return True

    def load_detail_by_id(self) -> bool:
        """通过ID加载AR详情"""
        if not self.id:
            print("AR ID为空，无法加载详情")
            return False
        
        data = api_get_ar_detail_by_id(self.id)
        if not data:
            return False
        
        return self._extract_detail_info(data)
    
    def _extract_detail_info(self, data: dict) -> bool:
        """从详情数据中提取信息"""
        try:
            result = data.get("result", [])
            if not result:
                return False
            
            detail = result[0]
            
            # 填充各个字段
            self.number = detail.get("number", "")
            self.title = detail.get("title", "")
            self.category = detail.get("category", "")
            
            # status对应的status下面的name
            status_data = detail.get("status", {})
            if isinstance(status_data, dict):
                self.status = status_data.get("name", "")
            
            # workload对应的workload_man_day
            workload_str = detail.get("workload_man_day", "0.0")
            try:
                self.workload = float(workload_str)
            except:
                self.workload = 0.0
            
            # act_workload对应的sum_workload_man_day
            sum_workload = detail.get("sum_workload_man_day")
            if sum_workload is None:
                self.act_workload = 0.0
            else:
                try:
                    self.act_workload = float(sum_workload)
                except:
                    self.act_workload = 0.0
            
            # creator对应的created_by中的nick_name
            created_by_data = detail.get("created_by", {})
            if isinstance(created_by_data, dict):
                creator_name = created_by_data.get("nick_name", "")
                if not creator_name:
                    creator_name = created_by_data.get("user_name", "")
                self.creator = creator_name
            
            # domain_value对应的business_domain下的display_value
            business_domain_data = detail.get("business_domain", {})
            if isinstance(business_domain_data, dict):
                self.domain_value = business_domain_data.get("display_value", "")
            
            # assignee对应的assignee下的nick_name
            assignee_data = detail.get("assignee", {})
            if isinstance(assignee_data, dict):
                assignee_name = assignee_data.get("nick_name", "")
                if not assignee_name:
                    assignee_name = assignee_data.get("user_name", "")
                self.assignee = assignee_name
            
            # status_value对应的status下面的code
            if isinstance(status_data, dict):
                self.status_value = status_data.get("code", "")
            
            # plan_start_date和plan_end_date（注意：JSON中字段名是反的）
            self.plan_start_date = detail.get("plan_end_date", "")
            self.plan_end_date = detail.get("plan_start_date", "")
            
            # plan_dev_end_date
            plan_dev_end_date = detail.get("plan_dev_end_date")
            if plan_dev_end_date is None:
                self.plan_dev_end_date = ""
            else:
                self.plan_dev_end_date = plan_dev_end_date
            
            # plan_test_end_date
            plan_test_end_date = detail.get("plan_test_end_date")
            if plan_test_end_date is None:
                self.plan_test_end_date = ""
            else:
                self.plan_test_end_date = plan_test_end_date
            
            # 设置详细描述
            self._set_detailed_description(detail)
            
            # 在所有字段提取完成后，更新req_id链
            self._update_req_id_chain()
            
            return True
            
        except Exception as e:
            print(f"提取AR详情信息出错: {e}")
            return False
    
    def _set_detailed_description(self, detail_data: dict):
        """设置详细描述"""
        description = detail_data.get("description", "")
        self.detailed_description.content = description
        self.detailed_description.owner = self
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def print_info(self):
        """打印AR的所有元素信息"""
        print("\n" + "="*60)
        print("AR 详细信息:")
        print("="*60)
        print(f"id: {self.id}")
        print(f"req_id: {self.req_id}")
        print(f"number: {self.number}")
        print(f"title: {self.title}")
        print(f"category: {self.category}")
        print(f"status: {self.status}")
        print(f"workload: {self.workload}")
        print(f"act_workload: {self.act_workload}")
        print(f"creator: {self.creator}")
        print(f"domain_value: {self.domain_value}")
        print(f"assignee: {self.assignee}")
        print(f"status_value: {self.status_value}")
        print(f"plan_start_date: {self.plan_start_date}")
        print(f"plan_end_date: {self.plan_end_date}")
        print(f"plan_dev_end_date: {self.plan_dev_end_date}")
        print(f"plan_test_end_date: {self.plan_test_end_date}")
        print(f"html_file: {self.html_file}")
        
        # 打印父级信息（如果有）
        if self.parent:
            print(f"parent (SR): {self.parent.id} - {self.parent.title}")
        else:
            print("parent: None")
        
        # 打印详细描述的owner id
        if self.detailed_description and self.detailed_description.owner:
            print(f"detailed_description.owner_id: {self.detailed_description.owner.id}")
        
        # 打印测试用例数量
        print(f"test_cases count: {len(self.test_cases)}")


    def generate_html(self):
        """
        生成AR的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            return
        
        # 计算返回父需求的相对路径
        back_link = "../OSTaskChangePrio()-任务优先级设置.html"
        if self.parent and self.parent.html_file:
            back_link = calculate_relative_path(self.html_file, self.parent.html_file)
        
        # 计算返回根需求的相对路径
        root_link = "../../任务管理.html"
        if self.parent and self.parent.parent and self.parent.parent.html_file:
            root_link = calculate_relative_path(self.html_file, self.parent.parent.html_file)
        
        # 计算详细描述链接的相对路径
        desc_href = "LLR_OS_01_01_01任务状态有效性判断描述.html"
        if self.detailed_description.html_file:
            desc_href = calculate_relative_path(self.html_file, self.detailed_description.html_file)
        
        # 计算评审记录链接的相对路径
        review_href = "LLR_OS_01_01_01任务状态有效性判断评审记录.html"
        if self.review_record.html_file:
            review_href = calculate_relative_path(self.html_file, self.review_record.html_file)
        
        # 计算修改记录链接的相对路径
        history_href = "LLR_OS_01_01_01任务状态有效性判断修改记录.html"
        if self.history_record.html_file:
            history_href = calculate_relative_path(self.html_file, self.history_record.html_file)
        
        # 计算父需求链接的相对路径（复用之前计算的back_link）
        parent_href = back_link
        parent_title = self.parent.title if (self.parent and self.parent.title) else "无"
        
        # 生成测试用例链接HTML
        test_case_links_html = ""
        for test_case in self.test_cases:
            if test_case.html_file or test_case.name:  # 只处理有HTML文件和标题的测试用例
                test_case_relative_path = calculate_relative_path(self.html_file, test_case.html_file)
                test_case_link = f"""
            <div class="requirement-item">
                <a href="{test_case_relative_path}" class="requirement-link">{test_case.name}</a>
            </div>"""
                test_case_links_html += test_case_link
        
        # 构建完整的HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}


        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        
        .subsection-title {{
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            margin: 20px 0 10px 0;
        }}
        
        /* 新的信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 140px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}
        
        /* CM信息网格布局 - 一行两列 */
        .cm-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 15px 0;
            position: relative;
        }}
        
        .cm-info-grid::before {{
            content: "";
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 1px;
            height: 100%;
            background-color: #e0e0e0;
        }}
        
        .cm-column {{
            display: flex;
            flex-direction: column;
        }}
        
        .link-group {{
            display: flex;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        .link-item {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }}
        
        .link-item:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
        }}
        
        .requirement-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .requirement-item {{
            margin: 8px 0;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        
        .requirement-link {{
            color: #0066cc;
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }}
        
        .requirement-link:hover {{
            color: #004499;
            text-decoration: underline;
        }}
        
        /* 需求详情样式 */
        .requirement-detail {{
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
          <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回父需求</a>
    <a href="{root_link}" class="back-left-link">返回根需求</a>
    <div class="container">
        <h1 style="text-align: center; color: #2c3e50; margin-bottom: 30px; font-size: 28px;">{self.title}</h1>
        
        <!-- 1. 基本信息 -->
        <div class="section-title">1. 基本信息</div>
    
        <div class="info-list">
            <div class="info-row">
                <span class="info-label">需求级别：</span>
                <span class="info-value">AR(低层)</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求ID：</span>
                <span class="info-value">{self.req_id if self.req_id else "无"}</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求名称：</span>
                <span class="info-value">{self.title}</span>
            </div>
        </div>
        
        <div class="section-title">2. 需求描述</div>
        <div class="requirement-detail">
            <a href="{desc_href}" class="link-item">详细描述</a>
        </div>
        
        <!-- 3. CM信息 - 一行两列网格布局 -->
        <div class="section-title">3. CM信息</div>
        
        <div class="cm-info-grid">
            <!-- 左侧列 -->
            <div class="cm-column">
                <div class="info-list">
                    <div class="info-row">
                        <span class="info-label">提出人：</span>
                        <span class="info-value">{self.creator if self.creator else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">状态：</span>
                        <span class="info-value">{self.status if self.status else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开始时间：</span>
                        <span class="info-value">{self.plan_start_date if self.plan_start_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开发结束：</span>
                        <span class="info-value">{self.plan_dev_end_date if self.plan_dev_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划工时：</span>
                        <span class="info-value">{self.workload} 人天</span>
                    </div>
                </div>
            </div>
            
            <!-- 右侧列 -->
            <div class="cm-column">
                <div class="info-list">
                      <div class="info-row">
                        <span class="info-label">负责人：</span>
                        <span class="info-value">{self.assignee if self.assignee else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">领域：</span>
                        <span class="info-value">{self.domain_value if self.domain_value else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划完成时间：</span>
                        <span class="info-value">{self.plan_end_date if self.plan_end_date else "无"}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">计划测试结束：</span>
                        <span class="info-value">{self.plan_test_end_date if self.plan_test_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">实际工时：</span>
                        <span class="info-value">{self.act_workload} 人天</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 评审和修改记录链接 -->
        <div class="link-group">
            <a href="{review_href}" class="link-item">评审记录</a>
            <a href="{history_href}" class="link-item">修改记录</a>
        </div>
        
        <!-- 4. 关联项 -->
        <div class="section-title">4. 关联项</div>
        
        <div class="subsection-title">4.1 上一层级需求(SR级)：</div>
        <div class="requirement-list">
            <div class="requirement-item">
                <a href="{parent_href}" class="requirement-link">{parent_title}</a>
            </div>
        </div>
        
        <div class="subsection-title">4.2 关联测试用例：</div>
        <div class="requirement-list">
            {test_case_links_html if test_case_links_html else '<div class="requirement-item">无</div>'}
        </div>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成AR HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")


@dataclass
class SR:
    """SR (Service Request) - 第三层"""
    id: str = ""
    req_id: str = ""
    number: str = ""
    title: str = ""
    category: str = ""
    status: str = ""
    workload: float = 0.0
    act_workload: float = 0.0
    creator: str = ""
    domain_value: str = ""
    assignee: str = ""
    status_value: str = ""
    plan_start_date: str = ""
    plan_end_date: str = ""
    plan_dev_end_date: str = ""
    plan_test_end_date: str = ""
    html_file: str = ""
    req_table_html_file: str = ""
    parent: Optional['IR'] = None
    detailed_description: DetailedDescription = field(default_factory=DetailedDescription)
    review_record: ReviewRecord = field(default_factory=ReviewRecord)
    history_record: HistoryRecord = field(default_factory=HistoryRecord)
    ars: List[AR] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后自动注册到数据注册表"""
        self.detailed_description.owner = self
        self.review_record.owner = self
        self.history_record.owner = self
        pass

    #创建sr的html文件
    def create_sr_html_files(self):
        """为当前SR创建HTML空文件"""
        if not self.title:
            print("SR title为空，无法创建文件")
            return
        
        if not self.parent or not self.parent.title:
            print("SR没有关联的IR或IR title为空")
            return
        
        # 构建目录路径
        sr_dir = os.path.join(config.BASE_DIR_NAME, config.REQ_DIR_NAME, self.parent.title, self.title)
        
        # 创建SR专属目录
        if not os.path.exists(sr_dir):
            os.makedirs(sr_dir)
        
        # 设置文件路径
        self.html_file = os.path.join(sr_dir, f"{self.title}.html")
        self.req_table_html_file = os.path.join(sr_dir, f"{self.title}_table.html")
        self.detailed_description.html_file = os.path.join(sr_dir, f"{self.title}描述.html")
        self.review_record.html_file = os.path.join(sr_dir, f"{self.title}评审记录.html")
        self.history_record.html_file = os.path.join(sr_dir, f"{self.title}修改记录.html")
        
        # 创建四个空文件
        for file_path in [
            self.html_file,
            self.req_table_html_file,
            self.detailed_description.html_file,
            self.review_record.html_file,
            self.history_record.html_file
        ]:
            try:
                open(file_path, 'w', encoding='utf-8').close()
                print(f"创建SR文件: {file_path}")
            except Exception as e:
                print(f"创建失败 {file_path}: {e}")


    #使用req_id对ars进行排序
    def sort_ars_by_req_id(self):
        """按照req_id对ars列表进行排序"""
        if not self.ars or len(self.ars) <= 1:
            print(f"  AR列表为空或只有一个元素，无需排序")
            return
        
        # 检查AR是否有req_id
        ars_without_req_id = [ar for ar in self.ars if ar and not ar.req_id]
        if ars_without_req_id:
            print(f"  警告：{len(ars_without_req_id)}个AR没有req_id")
        
        def get_sort_key(ar):
            """获取AR的排序键"""
            if not ar or not ar.req_id:
                return (999, 999, 999, "zzz")  # 没有req_id的放在最后
            
            # 处理req_id格式：LLR_OS_01_02_03
            parts = ar.req_id.split('_')
            if len(parts) < 5:
                return (999, 999, 999, ar.req_id)  # 格式不正确的放在最后
            
            try:
                # 解析数字部分
                num1 = int(parts[2]) if parts[2].isdigit() else 0
                num2 = int(parts[3]) if parts[3].isdigit() else 0
                num3 = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
                return (num1, num2, num3, ar.req_id)
            except (ValueError, IndexError):
                return (999, 999, 999, ar.req_id or "")
        
        # 使用稳定排序
        self.ars.sort(key=get_sort_key)
        
        print(f"  AR排序完成，顺序如下：")
        for i, ar in enumerate(self.ars, 1):
            if ar:
                print(f"    {i}. {ar.req_id or '无req_id'} - {ar.title[:30]}...")
        
        return True

    
    def load_detail_by_id(self) -> bool:
        """通过ID加载SR详情"""
        if not self.id:
            print("SR ID为空，无法加载详情")
            return False
        
        data = api_get_sr_detail_by_id(self.id)
        if not data:
            return False
        
        return self._extract_detail_info(data)
    
    def _extract_detail_info(self, data: dict) -> bool:
        """从详情数据中提取信息"""
        try:
            result = data.get("result", [])
            if not result:
                return False
            
            detail = result[0]
            
            # 填充各个字段
            self.number = detail.get("number", "")
            self.title = detail.get("title", "")
            self.category = detail.get("category", "")
            
            # status对应的status下面的name
            status_data = detail.get("status", {})
            if isinstance(status_data, dict):
                self.status = status_data.get("name", "")
            
            # workload对应的workload_man_day
            workload_str = detail.get("workload_man_day", "0.0")
            try:
                self.workload = float(workload_str)
            except:
                self.workload = 0.0
            
            # act_workload对应的sum_workload_man_day
            sum_workload = detail.get("sum_workload_man_day")
            if sum_workload is None:
                self.act_workload = 0.0
            else:
                try:
                    self.act_workload = float(sum_workload)
                except:
                    self.act_workload = 0.0
            
            # creator对应的created_by中的nick_name
            created_by_data = detail.get("created_by", {})
            if isinstance(created_by_data, dict):
                creator_name = created_by_data.get("nick_name", "")
                if not creator_name:
                    creator_name = created_by_data.get("user_name", "")
                self.creator = creator_name
            
            # domain_value对应的business_domain下的display_value
            business_domain_data = detail.get("business_domain", {})
            if isinstance(business_domain_data, dict):
                self.domain_value = business_domain_data.get("display_value", "")
            
            # assignee对应的assignee下的nick_name
            assignee_data = detail.get("assignee", {})
            if isinstance(assignee_data, dict):
                assignee_name = assignee_data.get("nick_name", "")
                if not assignee_name:
                    assignee_name = assignee_data.get("user_name", "")
                self.assignee = assignee_name
            
            # status_value对应的status下面的code
            if isinstance(status_data, dict):
                self.status_value = status_data.get("code", "")
            
            # plan_start_date和plan_end_date（注意：JSON中字段名是反的）
            self.plan_start_date = detail.get("plan_end_date", "")
            self.plan_end_date = detail.get("plan_start_date", "")
            
            # plan_dev_end_date
            plan_dev_end_date = detail.get("plan_dev_end_date")
            if plan_dev_end_date is None:
                self.plan_dev_end_date = ""
            else:
                self.plan_dev_end_date = plan_dev_end_date
            
            # plan_test_end_date
            plan_test_end_date = detail.get("plan_test_end_date")
            if plan_test_end_date is None:
                self.plan_test_end_date = ""
            else:
                self.plan_test_end_date = plan_test_end_date
            
            # 设置详细描述
            self._set_detailed_description(detail)
            
            # 从children字段创建AR
            children_str = detail.get("children", "")
            if children_str:
                self._create_ars_from_string(children_str)
            
            return True
            
        except Exception as e:
            print(f"提取SR详情信息出错: {e}")
            return False
    
    def _set_detailed_description(self, detail_data: dict):
        """设置详细描述"""
        description = detail_data.get("description", "")
        self.detailed_description.content = description
        self.detailed_description.owner = self
    
    def _create_ars_from_string(self, children_str: str):
        """根据children字符串创建AR"""
        ar_ids = [ar_id.strip() for ar_id in children_str.split(",") if ar_id.strip()]
        
        for ar_id in ar_ids:
            ar = AR(id=ar_id)
            self.add_ar(ar)
    
    def add_ar(self, ar: AR):
        """添加AR并设置父子关系"""
        ar.parent = self
        self.ars.append(ar)
    
    def update_all_ars(self) -> bool:
        """更新SR的所有AR的详细信息"""
        if not self.ars:
            print(f"SR {self.title} 没有AR需要更新")
            return True
        
        print(f"开始更新SR '{self.title}' 的所有AR详情...")
        print(f"共 {len(self.ars)} 个AR需要更新")
        
        success_count = 0
        for i, ar in enumerate(self.ars, 1):
            print(f"  更新AR {i}/{len(self.ars)}: {ar.id}")
            if ar.load_detail_by_id():
                success_count += 1
                ar.create_ar_html_files()
                print(f"    ✓ 成功")
            else:
                print(f"    ✗ 失败")
        
        print(f"AR详情更新完成: {success_count}/{len(self.ars)} 个成功")
        return success_count > 0
    
    def print_info(self):
        """打印SR的所有元素信息"""
        print("\n" + "="*60)
        print("SR 详细信息:")
        print("="*60)
        print(f"id: {self.id}")
        print(f"req_id: {self.req_id}")
        print(f"number: {self.number}")
        print(f"title: {self.title}")
        print(f"category: {self.category}")
        print(f"status: {self.status}")
        print(f"workload: {self.workload}")
        print(f"act_workload: {self.act_workload}")
        print(f"creator: {self.creator}")
        print(f"domain_value: {self.domain_value}")
        print(f"assignee: {self.assignee}")
        print(f"status_value: {self.status_value}")
        print(f"plan_start_date: {self.plan_start_date}")
        print(f"plan_end_date: {self.plan_end_date}")
        print(f"plan_dev_end_date: {self.plan_dev_end_date}")
        print(f"plan_test_end_date: {self.plan_test_end_date}")
        print(f"html_file: {self.html_file}")
        
        # 打印父级信息（如果有）
        if self.parent:
            print(f"parent (IR): {self.parent.id} - {self.parent.title}")
        else:
            print("parent: None")
        
        # 打印详细描述的owner id
        if self.detailed_description and self.detailed_description.owner:
            print(f"detailed_description.owner_id: {self.detailed_description.owner.id}")
        
        # 打印AR数量
        print(f"ars count: {len(self.ars)}")


    def generate_html(self):
        """
        生成SR的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            return
        
        # 计算返回父需求的相对路径
        back_link = "../任务管理.html"
        if self.parent and self.parent.html_file:
            back_link = calculate_relative_path(self.html_file, self.parent.html_file)
        
        # 计算详细描述链接的相对路径
        desc_href = "OSTaskChangePrio()-任务优先级设置描述.html"
        if self.detailed_description.html_file:
            desc_href = calculate_relative_path(self.html_file, self.detailed_description.html_file)
        
        # 计算评审记录链接的相对路径
        review_href = "OSTaskChangePrio()-任务优先级设置评审记录.html"
        if self.review_record.html_file:
            review_href = calculate_relative_path(self.html_file, self.review_record.html_file)
        
        # 计算修改记录链接的相对路径
        history_href = "OSTaskChangePrio()-任务优先级设置修改记录.html"
        if self.history_record.html_file:
            history_href = calculate_relative_path(self.html_file, self.history_record.html_file)
        
        # 计算父需求链接的相对路径（复用之前计算的back_link）
        parent_href = back_link
        parent_title = self.parent.title if (self.parent and self.parent.title) else "无"
        
        # 生成AR链接HTML
        ar_links_html = ""
        for ar in self.ars:
            if ar.html_file and ar.title:  # 只处理有HTML文件和标题的AR
                ar_relative_path = calculate_relative_path(self.html_file, ar.html_file)
                ar_link = f"""
            <div class="requirement-item">
                <a href="{ar_relative_path}" class="requirement-link">{ar.title}</a>
            </div>"""
                ar_links_html += ar_link
        
        # 构建完整的HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}


        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        
        .subsection-title {{
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            margin: 20px 0 10px 0;
        }}
        
        /* 新的信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 140px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}
        
        /* CM信息网格布局 - 一行两列 */
        .cm-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 15px 0;
            position: relative;
        }}
        
        .cm-info-grid::before {{
            content: "";
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 1px;
            height: 100%;
            background-color: #e0e0e0;
        }}
        
        .cm-column {{
            display: flex;
            flex-direction: column;
        }}
        
        .link-group {{
            display: flex;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        .link-item {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }}
        
        .link-item:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
        }}
        
        .requirement-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .requirement-item {{
            margin: 8px 0;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        
        .requirement-link {{
            color: #0066cc;
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }}
        
        .requirement-link:hover {{
            color: #004499;
            text-decoration: underline;
        }}
        
        /* 需求详情样式 */
        .requirement-detail {{
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
          <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回父需求</a>
    <div class="container">
        <h1 style="text-align: center; color: #2c3e50; margin-bottom: 30px; font-size: 28px;">{self.title}</h1>
        
        <!-- 1. 基本信息 -->
        <div class="section-title">1. 基本信息</div>
    
        <div class="info-list">
            <div class="info-row">
                <span class="info-label">需求级别：</span>
                <span class="info-value">SR(高层)</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求ID：</span>
                <span class="info-value">{self.req_id if self.req_id else "无"}</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求名称：</span>
                <span class="info-value">{self.title}</span>
            </div>
        </div>
        
        <div class="section-title">2. 需求描述</div>
        <div class="requirement-detail">
            <a href="{desc_href}" class="link-item">详细描述</a>
        </div>
        
        <!-- 3. CM信息 - 一行两列网格布局 -->
        <div class="section-title">3. CM信息</div>
        
        <div class="cm-info-grid">
            <!-- 左侧列 -->
            <div class="cm-column">
                <div class="info-list">
                    <div class="info-row">
                        <span class="info-label">提出人：</span>
                        <span class="info-value">{self.creator if self.creator else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">状态：</span>
                        <span class="info-value">{self.status if self.status else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开始时间：</span>
                        <span class="info-value">{self.plan_start_date if self.plan_start_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开发结束：</span>
                        <span class="info-value">{self.plan_dev_end_date if self.plan_dev_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划工时：</span>
                        <span class="info-value">{self.workload} 人天</span>
                    </div>
                </div>
            </div>
            
            <!-- 右侧列 -->
            <div class="cm-column">
                <div class="info-list">
                      <div class="info-row">
                        <span class="info-label">负责人：</span>
                        <span class="info-value">{self.assignee if self.assignee else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">领域：</span>
                        <span class="info-value">{self.domain_value if self.domain_value else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划完成时间：</span>
                        <span class="info-value">{self.plan_end_date if self.plan_end_date else "无"}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">计划测试结束：</span>
                        <span class="info-value">{self.plan_test_end_date if self.plan_test_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">实际工时：</span>
                        <span class="info-value">{self.act_workload} 人天</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 评审和修改记录链接 -->
        <div class="link-group">
            <a href="{review_href}" class="link-item">评审记录</a>
            <a href="{history_href}" class="link-item">修改记录</a>
        </div>
        
        <!-- 4. 关联项 -->
        <div class="section-title">4. 关联项</div>
        
        <div class="subsection-title">4.1 上一层级需求(IR级)：</div>
        <div class="requirement-list">
            <div class="requirement-item">
                <a href="{parent_href}" class="requirement-link">{parent_title}</a>
            </div>
        </div>
        
        <div class="subsection-title">4.2 下一层级需求(AR级)：</div>
        <div class="requirement-list">
            {ar_links_html if ar_links_html else '<div class="requirement-item">无</div>'}
        </div>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成SR HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")



    def generate_req_table_html(self):
        """
        生成SR-AR需求表HTML文件，并保存到req_table_html_file指定的路径
        """
        if not self.req_table_html_file:
            print("错误: SR的req_table_html_file未设置")
            return
        
        if not self.html_file:
            print("错误: SR的html_file未设置，无法计算相对路径")
            return
        
        # 计算SR文件的相对路径
        sr_relative_path = calculate_relative_path(self.req_table_html_file, self.html_file)
        
        # 生成AR行HTML
        ar_rows_html = self._generate_ar_rows(sr_relative_path)
        
        # 构建完整的HTML内容
        html_content = self._build_sr_ar_table_html(sr_relative_path, ar_rows_html)
        
        # 写入文件
        try:
            with open(self.req_table_html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成SR-AR需求表HTML文件: {self.req_table_html_file}")
            
        except Exception as e:
            print(f"写入SR-AR需求表HTML文件失败: {e}")
    
    def _generate_ar_rows(self, sr_relative_path: str) -> str:
        """生成AR行的HTML"""
        if not self.ars:
            return f'''
                <tr>
                    <td class="sr-cell" rowspan="1">
                        <a href="{sr_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td colspan="2" style="text-align: center; color: #7f8c8d; font-style: italic;">
                        暂无AR级需求
                    </td>
                </tr>'''
        
        rows_html = ""
        row_count = len(self.ars)
        
        for i, ar in enumerate(self.ars):
            if not ar.req_id:
                continue
                
            # 第一个链接：使用AR的req_table_html_file
            #ar_table_href = calculate_relative_path(self.req_table_html_file, ar.req_table_html_file)
            
            # 第二个链接：使用AR的html_file
            ar_detail_href = calculate_relative_path(self.req_table_html_file, ar.html_file)
            
            # 获取AR的标题
            ar_title = ar.title if ar.title else "无名称"
            
            # 如果是第一行，包含SR单元格
            if i == 0:
                row = f'''
                <tr>
                    <td class="sr-cell" rowspan="{row_count}">
                        <a href="{sr_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td>{ar.req_id}</td>
                    <td><a href="{ar_detail_href}" target="_blank">{ar_title}</a></td>
                </tr>'''
            else:
                row = f'''
                <tr>
                    <td>{ar.req_id}</td>
                    <td><a href="{ar_detail_href}" target="_blank">{ar_title}</a></td>
                </tr>'''
            
            rows_html += row
        
        return rows_html
    
    def _build_sr_ar_table_html(self, sr_relative_path: str, ar_rows_html: str) -> str:
        """构建SR-AR表格HTML文档"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} SR-AR需求表</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            padding: 30px;
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 25px;
            color: #2c3e50;
            font-weight: 600;
            font-size: 24px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eaeaea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            border: 1px solid #ddd;
        }}
        
        th {{
            background-color: #2ecc71;
            color: white;
            font-weight: 500;
            padding: 14px 16px;
            text-align: center;
            border-right: 1px solid #27ae60;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        td {{
            padding: 12px 16px;
            text-align: center;
            border-bottom: 1px solid #eaeaea;
            border-right: 1px solid #eaeaea;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        tr:hover {{
            background-color: #f0f7ff;
        }}
        
        .sr-cell {{
            background-color: #d1fae5;
            font-weight: 500;
            vertical-align: middle;
            color: #065f46;
        }}
        
        a {{
            color: #2980b9;
            text-decoration: none;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        a:hover {{
            background-color: #3498db;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title} SR-AR需求表</h1>
        
        <table>
            <thead>
                <tr>
                    <th>SR</th>
                    <th>AR-低层需求ID</th>
                    <th>AR-需求名称</th>
                </tr>
            </thead>
            <tbody>
{ar_rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>'''

@dataclass
class IR:
    """IR (Incident Request) - 第二层"""
    id: str = ""
    req_id: str = ""
    number: str = ""
    title: str = ""
    category: str = ""
    status: str = ""
    workload: float = 0.0
    act_workload: float = 0.0
    creator: str = ""
    domain_value: str = ""
    assignee: str = ""
    status_value: str = ""
    plan_start_date: str = ""
    plan_end_date: str = ""
    plan_dev_end_date: str = ""
    plan_test_end_date: str = ""
    html_file: str = ""
    req_table_html_file: str = ""
    parent: Optional['SF'] = None
    detailed_description: DetailedDescription = field(default_factory=DetailedDescription)
    review_record: ReviewRecord = field(default_factory=ReviewRecord)
    history_record: HistoryRecord = field(default_factory=HistoryRecord)
    srs: List['SR'] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后自动注册到数据注册表"""
        self.detailed_description.owner = self
        self.review_record.owner = self
        self.history_record.owner = self
        pass

    def create_ir_html_files(self):
        """为当前IR创建HTML空文件"""
        if not self.title:
            print("IR title为空，无法创建文件")
            return
        
        # 构建目录路径
        ir_dir = os.path.join(config.BASE_DIR_NAME, config.REQ_DIR_NAME, self.title)
        
        # 创建IR专属目录
        if not os.path.exists(ir_dir):
            os.makedirs(ir_dir)
        
        # 设置文件路径
        self.html_file = os.path.join(ir_dir, f"{self.title}.html")
        self.req_table_html_file = os.path.join(ir_dir, f"{self.title}_table.html")
        self.detailed_description.html_file = os.path.join(ir_dir, f"{self.title}描述.html")
        self.review_record.html_file = os.path.join(ir_dir, f"{self.title}评审记录.html")
        self.history_record.html_file = os.path.join(ir_dir, f"{self.title}修改记录.html")
      
        # 创建四个空文件
        for file_path in [
            self.html_file,
            self.req_table_html_file,
            self.detailed_description.html_file,
            self.review_record.html_file,
            self.history_record.html_file
        ]:
            try:
                open(file_path, 'w', encoding='utf-8').close()
                print(f"创建: {file_path}")
            except Exception as e:
                print(f"创建失败 {file_path}: {e}")

    #使用req_id对srs进行排序
    def sort_srs_by_req_id(self):
        """按照req_id对srs列表进行排序"""
        if not self.srs or len(self.srs) <= 1:
            print(f"  SR列表为空或只有一个元素，无需排序")
            return
        
        # 检查SR是否有req_id
        srs_without_req_id = [sr for sr in self.srs if sr and not sr.req_id]
        if srs_without_req_id:
            print(f"  警告：{len(srs_without_req_id)}个SR没有req_id")
        
        def get_sort_key(sr):
            """获取SR的排序键"""
            if not sr or not sr.req_id:
                return (999, 999, "zzz")  # 没有req_id的放在最后
            
            # 处理req_id格式：HLR_OS_01_02
            parts = sr.req_id.split('_')
            if len(parts) < 4:
                return (999, 999, sr.req_id)  # 格式不正确的放在最后
            
            try:
                # 解析数字部分
                num1 = int(parts[2]) if parts[2].isdigit() else 0
                num2 = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                return (num1, num2, sr.req_id)
            except (ValueError, IndexError):
                return (999, 999, sr.req_id or "")
        
        # 使用稳定排序
        self.srs.sort(key=get_sort_key)
        
        print(f"  SR排序完成，顺序如下：")
        for i, sr in enumerate(self.srs, 1):
            if sr:
                print(f"    {i}. {sr.req_id or '无req_id'} - {sr.title[:30]}...")
        
        return True


    def load_detail_by_id(self) -> bool:
        """通过ID加载IR详情"""
        if not self.id:
            print("IR ID为空，无法加载详情")
            return False
        
        data = api_get_ir_detail_by_id(self.id)
        if not data:
            return False
        
        return self._extract_detail_info(data)
    
    def _extract_detail_info(self, data: dict) -> bool:
        """从详情数据中提取信息"""
        try:
            result = data.get("result", [])
            if not result:
                return False
            
            detail = result[0]
            
            # 填充各个字段
            self.number = detail.get("number", "")
            self.title = detail.get("title", "")
            self.category = detail.get("category", "")
            
            # status对应的status下面的name
            status_data = detail.get("status", {})
            if isinstance(status_data, dict):
                self.status = status_data.get("name", "")
            
            # workload对应的workload_man_day
            workload_str = detail.get("workload_man_day", "0.0")
            try:
                self.workload = float(workload_str)
            except:
                self.workload = 0.0
            
            # act_workload对应的sum_workload_man_day
            sum_workload = detail.get("sum_workload_man_day")
            if sum_workload is None:
                self.act_workload = 0.0
            else:
                try:
                    self.act_workload = float(sum_workload)
                except:
                    self.act_workload = 0.0
            
            # creator对应的created_by中的nick_name
            created_by_data = detail.get("created_by", {})
            if isinstance(created_by_data, dict):
                creator_name = created_by_data.get("nick_name", "")
                if not creator_name:
                    creator_name = created_by_data.get("user_name", "")
                self.creator = creator_name
            
            # domain_value对应的business_domain下的display_value
            business_domain_data = detail.get("business_domain", {})
            if isinstance(business_domain_data, dict):
                self.domain_value = business_domain_data.get("display_value", "")
            
            # assignee对应的assignee下的nick_name
            assignee_data = detail.get("assignee", {})
            if isinstance(assignee_data, dict):
                assignee_name = assignee_data.get("nick_name", "")
                if not assignee_name:
                    assignee_name = assignee_data.get("user_name", "")
                self.assignee = assignee_name
            
            # status_value对应的status下面的code
            if isinstance(status_data, dict):
                self.status_value = status_data.get("code", "")
            
            # plan_start_date和plan_end_date（注意：JSON中字段名是反的）
            self.plan_start_date = detail.get("plan_end_date", "")
            self.plan_end_date = detail.get("plan_start_date", "")
            
            # plan_dev_end_date
            plan_dev_end_date = detail.get("plan_dev_end_date")
            if plan_dev_end_date is None:
                self.plan_dev_end_date = ""
            else:
                self.plan_dev_end_date = plan_dev_end_date
            
            # plan_test_end_date
            plan_test_end_date = detail.get("plan_test_end_date")
            if plan_test_end_date is None:
                self.plan_test_end_date = ""
            else:
                self.plan_test_end_date = plan_test_end_date
            
            # 设置详细描述
            self._set_detailed_description(detail)
            
            # 从children字段创建SR
            children_str = detail.get("children", "")
            if children_str:
                self._create_srs_from_string(children_str)
            
            return True
            
        except Exception as e:
            print(f"提取IR详情信息出错: {e}")
            return False
    
    def _set_detailed_description(self, detail_data: dict):
        """设置详细描述"""
        description = detail_data.get("description", "")
        self.detailed_description.content = description
        self.detailed_description.owner = self
    
    def _create_srs_from_string(self, children_str: str):
        """根据children字符串创建SR"""
        sr_ids = [sr_id.strip() for sr_id in children_str.split(",") if sr_id.strip()]
        
        for sr_id in sr_ids:
            if sr_id == "1061206331188977665":
        	      continue
            sr = SR(id=sr_id)
            self.add_sr(sr)
    
    def add_sr(self, sr: 'SR'):
        """添加SR并设置父子关系"""
        sr.parent = self
        self.srs.append(sr)
    
    def update_all_srs(self) -> bool:
        """更新IR的所有SR的详细信息"""
        if not self.srs:
            print(f"IR {self.title} 没有SR需要更新")
            return True
        
        print(f"开始更新IR '{self.title}' 的所有SR详情...")
        print(f"共 {len(self.srs)} 个SR需要更新")
        
        success_count = 0
        for i, sr in enumerate(self.srs, 1):
            print(f"  更新SR {i}/{len(self.srs)}: {sr.id}")
            if sr.load_detail_by_id():
                success_count += 1
                sr.create_sr_html_files()
                print(f"    ✓ 成功")
            else:
                print(f"    ✗ 失败")
        
        print(f"SR详情更新完成: {success_count}/{len(self.srs)} 个成功")
        return success_count > 0
    
    def print_info(self):
        """打印IR的所有元素信息"""
        print("\n" + "="*60)
        print("IR 详细信息:")
        print("="*60)
        print(f"id: {self.id}")
        print(f"req_id: {self.req_id}")
        print(f"number: {self.number}")
        print(f"title: {self.title}")
        print(f"category: {self.category}")
        print(f"status: {self.status}")
        print(f"workload: {self.workload}")
        print(f"act_workload: {self.act_workload}")
        print(f"creator: {self.creator}")
        print(f"domain_value: {self.domain_value}")
        print(f"assignee: {self.assignee}")
        print(f"status_value: {self.status_value}")
        print(f"plan_start_date: {self.plan_start_date}")
        print(f"plan_end_date: {self.plan_end_date}")
        print(f"plan_dev_end_date: {self.plan_dev_end_date}")
        print(f"plan_test_end_date: {self.plan_test_end_date}")
        print(f"html_file: {self.html_file}")
        
        # 打印父级信息（如果有）
        if self.parent:
            print(f"parent (SF): {self.parent.id} - {self.parent.title}")
        else:
            print("parent: None")
        
        # 打印详细描述的owner id
        if self.detailed_description and self.detailed_description.owner:
            print(f"detailed_description.owner_id: {self.detailed_description.owner.id}")
        
        # 打印SR数量
        print(f"srs count: {len(self.srs)}")

    def generate_html(self):
        """
        生成IR的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            return
        
        # 计算返回父需求的相对路径
        back_link = "#"
        if self.parent and self.parent.html_file:
            back_link = calculate_relative_path(self.html_file, self.parent.html_file)
        
        # 计算详细描述链接的相对路径
        desc_href = "#"
        if self.detailed_description.html_file:
            desc_href = calculate_relative_path(self.html_file, self.detailed_description.html_file)
        
        # 计算评审记录链接的相对路径
        review_href = "#"
        if self.review_record.html_file:
            review_href = calculate_relative_path(self.html_file, self.review_record.html_file)
        
        # 计算修改记录链接的相对路径
        history_href = "#"
        if self.history_record.html_file:
            history_href = calculate_relative_path(self.html_file, self.history_record.html_file)
        
        # 计算父需求链接的相对路径（复用之前计算的back_link）
        parent_href = back_link
        parent_title = self.parent.title if (self.parent and self.parent.title) else "无"
        
        # 生成SR链接HTML
        sr_links_html = ""
        for sr in self.srs:
            if sr.html_file and sr.title:  # 只处理有HTML文件和标题的SR
                sr_relative_path = calculate_relative_path(self.html_file, sr.html_file)
                sr_link = f"""
            <div class="requirement-item">
                <a href="{sr_relative_path}" class="requirement-link">{sr.title}</a>
            </div>"""
                sr_links_html += sr_link
        
        # 构建完整的HTML内容
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            position: relative;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}


        /* 返回链接样式1 */
        .back-right-link {{
            position: absolute;
            top: 30px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式2 */
        .back-right2-link {{
            position: absolute;
            top: 82px;
            right: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-right2-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}

        /* 返回链接样式3 */
        .back-left-link {{
            position: absolute;
            top: 30px;
            left: 40px;
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
            transition: all 0.3s;
            z-index: 100;
        }}
        
        .back-left-link:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
            text-decoration: none;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        
        .subsection-title {{
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            margin: 20px 0 10px 0;
        }}
        
        /* 新的信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 140px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}
        
        /* CM信息网格布局 - 一行两列 */
        .cm-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 15px 0;
            position: relative;
        }}
        
        .cm-info-grid::before {{
            content: "";
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 1px;
            height: 100%;
            background-color: #e0e0e0;
        }}
        
        .cm-column {{
            display: flex;
            flex-direction: column;
        }}
        
        .link-group {{
            display: flex;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        .link-item {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }}
        
        .link-item:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
        }}
        
        .requirement-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .requirement-item {{
            margin: 8px 0;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        
        .requirement-link {{
            color: #0066cc;
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }}
        
        .requirement-link:hover {{
            color: #004499;
            text-decoration: underline;
        }}
        
        /* 需求详情样式 */
        .requirement-detail {{
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
          <!-- 返回链接 -->
    <a href="{back_link}" class="back-right-link">返回父需求</a>
    <div class="container">
        <h1 style="text-align: center; color: #2c3e50; margin-bottom: 30px; font-size: 28px;">{self.title}</h1>
        
        <!-- 1. 基本信息 -->
        <div class="section-title">1. 基本信息</div>
    
        <div class="info-list">
            <div class="info-row">
                <span class="info-label">需求级别：</span>
                <span class="info-value">IR(高层)</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求ID：</span>
                <span class="info-value">{self.req_id if self.req_id else "无"}</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求名称：</span>
                <span class="info-value">{self.title}</span>
            </div>
        </div>
        
        <div class="section-title">2. 需求描述</div>
        <div class="requirement-detail">
            <a href="{desc_href}" class="link-item">详细描述</a>
        </div>
        
        <!-- 3. CM信息 - 一行两列网格布局 -->
        <div class="section-title">3. CM信息</div>
        
        <div class="cm-info-grid">
            <!-- 左侧列 -->
            <div class="cm-column">
                <div class="info-list">
                    <div class="info-row">
                        <span class="info-label">提出人：</span>
                        <span class="info-value">{self.creator if self.creator else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">状态：</span>
                        <span class="info-value">{self.status if self.status else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开始时间：</span>
                        <span class="info-value">{self.plan_start_date if self.plan_start_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开发结束：</span>
                        <span class="info-value">{self.plan_dev_end_date if self.plan_dev_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划工时：</span>
                        <span class="info-value">{self.workload} 人天</span>
                    </div>
                </div>
            </div>
            
            <!-- 右侧列 -->
            <div class="cm-column">
                <div class="info-list">
                      <div class="info-row">
                        <span class="info-label">负责人：</span>
                        <span class="info-value">{self.assignee if self.assignee else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">领域：</span>
                        <span class="info-value">{self.domain_value if self.domain_value else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划完成时间：</span>
                        <span class="info-value">{self.plan_end_date if self.plan_end_date else "无"}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">计划测试结束：</span>
                        <span class="info-value">{self.plan_test_end_date if self.plan_test_end_date else "无"}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">实际工时：</span>
                        <span class="info-value">{self.act_workload} 人天</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 评审和修改记录链接 -->
        <div class="link-group">
            <a href="{review_href}" class="link-item">评审记录</a>
            <a href="{history_href}" class="link-item">修改记录</a>
        </div>
        
        <!-- 4. 关联项 -->
        <div class="section-title">4. 关联项</div>
        
        <div class="subsection-title">4.1 上一层级需求(SF级)：</div>
        <div class="requirement-list">
            <div class="requirement-item">
                <a href="{parent_href}" class="requirement-link">{parent_title}</a>
            </div>
        </div>
        
        <div class="subsection-title">4.2 下一层级需求(SR级)：</div>
        <div class="requirement-list">
            {sr_links_html if sr_links_html else '<div class="requirement-item">无</div>'}
        </div>
    </div>
</body>
</html>'''
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成IR HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")

    def generate_req_table_html(self):
        """
        生成IR-SR需求表HTML文件，并保存到req_table_html_file指定的路径
        """
        if not self.req_table_html_file:
            print("错误: IR的req_table_html_file未设置")
            return
        
        if not self.html_file:
            print("错误: IR的html_file未设置，无法计算相对路径")
            return
        
        # 计算IR文件的相对路径
        ir_relative_path = calculate_relative_path(self.req_table_html_file, self.html_file)
        
        # 生成SR行HTML
        sr_rows_html = self._generate_sr_rows(ir_relative_path)
        
        # 构建完整的HTML内容
        html_content = self._build_ir_sr_table_html(ir_relative_path, sr_rows_html)
        
        # 写入文件
        try:
            with open(self.req_table_html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成IR-SR需求表HTML文件: {self.req_table_html_file}")
            
        except Exception as e:
            print(f"写入IR-SR需求表HTML文件失败: {e}")
    
    def _generate_sr_rows(self, ir_relative_path: str) -> str:
        """生成SR行的HTML"""
        if not self.srs:
            return f'''
                <tr>
                    <td class="ir-cell" rowspan="1">
                        <a href="{ir_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td colspan="2" style="text-align: center; color: #7f8c8d; font-style: italic;">
                        暂无SR级需求
                    </td>
                </tr>'''
        
        rows_html = ""
        row_count = len(self.srs)
        
        for i, sr in enumerate(self.srs):
            if not sr.req_id:
                continue
                
            # 第一个链接：使用SR的req_table_html_file
            sr_table_href = calculate_relative_path(self.req_table_html_file, sr.req_table_html_file)
            
            # 第二个链接：使用SR的html_file
            sr_detail_href = calculate_relative_path(self.req_table_html_file, sr.html_file)
            
            # 获取SR的标题
            sr_title = sr.title if sr.title else "无名称"
            
            # 如果是第一行，包含IR单元格
            if i == 0:
                row = f'''
                <tr>
                    <td class="ir-cell" rowspan="{row_count}">
                        <a href="{ir_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td><a href="{sr_table_href}" target="_blank">{sr.req_id}</a></td>
                    <td><a href="{sr_detail_href}" target="_blank">{sr_title}</a></td>
                </tr>'''
            else:
                row = f'''
                <tr>
                    <td><a href="{sr_table_href}" target="_blank">{sr.req_id}</a></td>
                    <td><a href="{sr_detail_href}" target="_blank">{sr_title}</a></td>
                </tr>'''
            
            rows_html += row
        
        return rows_html
    
    def _build_ir_sr_table_html(self, ir_relative_path: str, sr_rows_html: str) -> str:
        """构建IR-SR表格HTML文档"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} IR-SR需求表</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            padding: 30px;
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 25px;
            color: #2c3e50;
            font-weight: 600;
            font-size: 24px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eaeaea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            border: 1px solid #ddd;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 500;
            padding: 14px 16px;
            text-align: center;
            border-right: 1px solid #2c81ba;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        td {{
            padding: 12px 16px;
            text-align: center;
            border-bottom: 1px solid #eaeaea;
            border-right: 1px solid #eaeaea;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        tr:hover {{
            background-color: #f0f7ff;
        }}
        
        .ir-cell {{
            background-color: #e0f2fe;
            font-weight: 500;
            vertical-align: middle;
            color: #1e3a8a;
        }}
        
        a {{
            color: #2980b9;
            text-decoration: none;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        a:hover {{
            background-color: #3498db;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title} IR-SR需求表</h1>
        
        <table>
            <thead>
                <tr>
                    <th>IR</th>
                    <th>SR-高层需求ID</th>
                    <th>SR-需求名称</th>
                </tr>
            </thead>
            <tbody>
{sr_rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>'''

@dataclass
class SF:
    """SF (Service Function) - 最顶层"""
    id: str = ""
    req_id: str = ""
    number: str = ""
    title: str = ""
    category: str = ""
    assignee: str = ""
    workload: float = 0.0
    plan_start_date: str = ""
    plan_end_date: str = ""
    status: str = ""
    html_file: str = ""
    req_navga_html_file: str = ""
    req_table_html_file: str = ""
    detailed_description: DetailedDescription = field(default_factory=DetailedDescription)
    review_record: ReviewRecord = field(default_factory=ReviewRecord)
    history_record: HistoryRecord = field(default_factory=HistoryRecord)
    irs: List[IR] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后自动注册到数据注册表"""
        self.detailed_description.owner = self
        self.review_record.owner = self
        self.history_record.owner = self
        pass

    def create_sf_html_files(self):
        """为当前SF创建HTML空文件，路径：verifymaterial/requirement/"""
        import os
        
        # 构建完整路径
        base_dir = config.BASE_DIR_NAME
        requirement_dir = os.path.join(base_dir, config.REQ_DIR_NAME)
        
        # 创建verifymaterial目录（如果不存在）
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            print(f"创建目录: {base_dir}")
        
        # 创建requirement目录（如果不存在）
        if not os.path.exists(requirement_dir):
            os.makedirs(requirement_dir)
            print(f"创建目录: {requirement_dir}")
        
        # 设置文件路径
        self.html_file = os.path.join(requirement_dir, "SF.html")
        self.req_table_html_file = os.path.join(requirement_dir, f"{self.title}_table.html")
        self.req_navga_html_file = os.path.join(requirement_dir, "需求导航.html")
        self.detailed_description.html_file = os.path.join(requirement_dir, "SF描述.html")
        self.review_record.html_file = os.path.join(requirement_dir, "SF评审记录.html")
        self.history_record.html_file = os.path.join(requirement_dir, "SF修改记录.html")
        
        # 创建空文件
        files_to_create = [
            ("SF.html", self.html_file),
            ("SF_IR_table.html", self.req_table_html_file),
            ("需求导航.html", self.req_navga_html_file),
            ("SF描述.html", self.detailed_description.html_file),
            ("SF评审记录.html", self.review_record.html_file),
            ("SF修改记录.html", self.history_record.html_file)
        ]
        
        for file_name, file_path in files_to_create:
            try:
                with open(file_path, 'w', encoding='utf-8'):
                    pass  # 创建空文件
                print(f"创建空文件: {file_path}")
            except Exception as e:
                print(f"创建文件 {file_name} 失败: {e}")

    #使用req_id对irs进行排序
    def sort_irs_by_req_id(self):
        """按照req_id对irs列表进行排序"""
        if not self.irs or len(self.irs) <= 1:
            print("  IR列表为空或只有一个元素，无需排序")
            return
        
        # 检查IR是否有req_id
        irs_without_req_id = [ir for ir in self.irs if ir and not ir.req_id]
        if irs_without_req_id:
            print(f"  警告：{len(irs_without_req_id)}个IR没有req_id")
        
        def get_sort_key(ir):
            """获取IR的排序键"""
            if not ir or not ir.req_id:
                return (999, "zzz")  # 没有req_id的放在最后
            
            # 处理req_id格式：HLR_OS_01
            parts = ir.req_id.split('_')
            if len(parts) < 3:
                return (999, ir.req_id)  # 格式不正确的放在最后
            
            try:
                # 解析数字部分
                num1 = int(parts[2]) if parts[2].isdigit() else 0
                return (num1, ir.req_id)
            except (ValueError, IndexError):
                return (999, ir.req_id or "")
        
        # 使用稳定排序
        self.irs.sort(key=get_sort_key)
        
        print(f"  IR排序完成，顺序如下：")
        for i, ir in enumerate(self.irs, 1):
            if ir:
                print(f"    {i}. {ir.req_id or '无req_id'} - {ir.title[:30]}...")
        
        return True

    #对整个IR，SR，AR列表进行排序
    def _sort_all_hierarchy_after_ars_updated(self):
        """在所有AR更新完成后，排序整个层级"""
        print(f"\n" + "-"*60)
        print(f"开始排序SF '{self.title}' 的所有层级...")
        print("-"*60)
        
        # 1. 先排序IR（此时IR的req_id应该已经被AR推导出来了）
        if self.irs:
            print(f"1. 排序IR列表 ({len(self.irs)}个)")
            self.sort_irs_by_req_id()
            
            # 2. 对每个已排序的IR，排序其SR
            for ir in self.irs:
                if ir and ir.srs:
                    print(f"\n2. 排序IR '{ir.title[:20]}...' 的SR列表 ({len(ir.srs)}个)")
                    ir.sort_srs_by_req_id()
                    
                    # 3. 对每个已排序的SR，排序其AR
                    for sr in ir.srs:
                        if sr and sr.ars:
                            print(f"3. 排序SR '{sr.title[:20]}...' 的AR列表 ({len(sr.ars)}个)")
                            sr.sort_ars_by_req_id()  # 直接调用SR的排序方法
        
        print(f"\nSF '{self.title}' 的所有层级排序完成")
        print("-"*60)

    def load_sf_by_keyword(self) -> bool:
        """通过关键词加载完整SF信息（从配置读取关键词）"""
        # 1. 搜索SF获取基本信息
        if not self._search_by_keyword():
            return False
        
        # 2. 加载SF详情
        if not self._load_detail_by_id():
            return False
        
        self.create_sf_html_files()
        return True
    
    def _search_by_keyword(self) -> bool:
        """通过关键词搜索SF（内部方法）"""
        data = api_post_sf_by_keyword()
        if not data:
            return False
        
        return self._extract_basic_info(data)
    
    def _load_detail_by_id(self) -> bool:
        """通过ID加载SF详情（内部方法）"""
        if not self.id:
            print("SF ID为空，无法加载详情")
            return False
        
        data = api_get_sf_detail_by_id(self.id)
        if not data:
            return False
        
        return self._extract_detail_info(data)
    
    def _extract_basic_info(self, data: dict) -> bool:
        """从搜索结果中提取SF基本信息"""
        try:
            result = data.get("result", {})
            issues = result.get("issues", [])
            if not issues:
                return False
            
            issue = issues[0]
            
            self.id = issue.get("id", "")
            self.number = issue.get("number", "")
            self.title = issue.get("title", "")
            self.category = issue.get("category", "")
            self.status = issue.get("status", "")
            
            assignee_data = issue.get("assignee", {})
            if isinstance(assignee_data, dict):
                self.assignee = assignee_data.get("name", "")
            else:
                self.assignee = str(assignee_data)
            
            workload_str = issue.get("workload", "0.0")
            try:
                self.workload = float(workload_str)
            except:
                self.workload = 0.0
            
            # 获取feature2ir字段，创建IR
            feature2ir_str = issue.get("feature2ir", "")
            if feature2ir_str:
                self._create_irs_from_string(feature2ir_str)
            
            return True
        except Exception as e:
            print(f"提取SF基本信息出错: {e}")
            return False
    
    def _create_irs_from_string(self, feature2ir_str: str):
        """根据feature2ir字符串创建IR"""
        ir_ids = [ir_id.strip() for ir_id in feature2ir_str.split(",") if ir_id.strip()]
        
        for ir_id in ir_ids:
            ir = IR(id=ir_id)
            self.add_ir(ir)
    
    def _extract_detail_info(self, data: dict) -> bool:
        """从详情数据中提取信息"""
        try:
            result = data.get("result", [])
            if not result:
                return False
            
            detail = result[0]
            
            # 获取详细描述
            description = detail.get("description", "")
            self.detailed_description.content = description
            self.detailed_description.owner = self
            
            # 获取plan_start_date和plan_end_date
            self.plan_start_date = detail.get("plan_start_date", "")
            self.plan_end_date = detail.get("plan_end_date", "")
            
            return True
        except Exception as e:
            print(f"提取SF详情信息出错: {e}")
            return False
    
    def update_all_irs(self) -> bool:
        """更新SF的所有IR的详细信息"""
        if not self.irs:
            print(f"SF {self.title} 没有IR需要更新")
            return True
        
        print(f"开始更新SF '{self.title}' 的所有IR详情...")
        print(f"共 {len(self.irs)} 个IR需要更新")
        
        success_count = 0
        for i, ir in enumerate(self.irs, 1):
            print(f"  更新IR {i}/{len(self.irs)}: {ir.id}")
            if ir.load_detail_by_id():
                success_count += 1
                print(f"    ✓ 成功")
                ir.create_ir_html_files()
            else:
                print(f"    ✗ 失败")
        
        print(f"IR详情更新完成: {success_count}/{len(self.irs)} 个成功")
        return success_count > 0
    
    def update_all_srs(self) -> bool:
        """更新SF的所有SR的详细信息（通过IR链）"""
        total_srs = sum(len(ir.srs) for ir in self.irs)
        if total_srs == 0:
            print(f"SF {self.title} 没有SR需要更新")
            return True
        
        print(f"开始更新SF '{self.title}' 的所有SR详情...")
        print(f"共 {total_srs} 个SR需要更新（通过{len(self.irs)}个IR）")
        
        success_count = 0
        for i, ir in enumerate(self.irs, 1):
            print(f"\n通过IR {i}/{len(self.irs)} 更新SR: {ir.title}")
            if ir.update_all_srs():
                success_count += len(ir.srs)
        
        print(f"\nSR详情更新完成: {success_count}/{total_srs} 个成功")
        return success_count > 0
    
    def update_all_ars(self) -> bool:
        """更新SF的所有AR的详细信息（通过SR链）"""
        total_ars = 0
        for ir in self.irs:
            for sr in ir.srs:
                total_ars += len(sr.ars)
        
        if total_ars == 0:
            print(f"SF {self.title} 没有AR需要更新")
            return True
        
        print(f"开始更新SF '{self.title}' 的所有AR详情...")
        print(f"共 {total_ars} 个AR需要更新")
        
        success_count = 0
        for i, ir in enumerate(self.irs, 1):
            for j, sr in enumerate(ir.srs, 1):
                print(f"\n通过SR {j}/{len(ir.srs)} 更新AR: {sr.title}")
                if sr.update_all_ars():
                    success_count += len(sr.ars)
        
        print(f"\nAR详情更新完成: {success_count}/{total_ars} 个成功")
        self._sort_all_hierarchy_after_ars_updated()
        return success_count > 0
    
    def add_ir(self, ir: IR):
        """添加IR"""
        ir.parent = self
        self.irs.append(ir)
    
    def print_info(self):
        """打印SF的所有元素信息"""
        print("\n" + "="*60)
        print("SF 详细信息:")
        print("="*60)
        print(f"id: {self.id}")
        print(f"number: {self.number}")
        print(f"title: {self.title}")
        print(f"category: {self.category}")
        print(f"assignee: {self.assignee}")
        print(f"workload: {self.workload}")
        print(f"plan_start_date: {self.plan_start_date}")
        print(f"plan_end_date: {self.plan_end_date}")
        print(f"status: {self.status}")
        print(f"html_file: {self.html_file}")
        
        # 打印详细描述的owner id
        if self.detailed_description and self.detailed_description.owner:
            print(f"detailed_description.owner_id: {self.detailed_description.owner.id}")
        
        # 打印IR数量
        print(f"irs count: {len(self.irs)}")

    def generate_html(self):
        """
        生成SF的HTML内容并保存到html_file指定的文件中
        """
        if not self.html_file:
            print("错误: SF的html_file未设置")
            return
        
        # 计算各个关联文件的相对路径
        desc_relative_path = calculate_relative_path(self.html_file, self.detailed_description.html_file)
        review_relative_path = calculate_relative_path(self.html_file, self.review_record.html_file)
        history_relative_path = calculate_relative_path(self.html_file, self.history_record.html_file)
        
        # 生成IR链接HTML
        ir_links_html = ""
        for ir in self.irs:
            if ir.html_file and ir.title:  # 只处理有HTML文件和标题的IR
                ir_relative_path = calculate_relative_path(self.html_file, ir.html_file)
                ir_link = f"""
            <div class="requirement-item">
                <a href="{ir_relative_path}" class="requirement-link">{ir.title}</a>
            </div>"""
                ir_links_html += ir_link
        
        # 为空的路径设置默认值
        desc_href = desc_relative_path if desc_relative_path else "#"
        review_href = review_relative_path if review_relative_path else "#"
        history_href = history_relative_path if history_relative_path else "#"
        
        # 构建完整的HTML内容
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        
        .subsection-title {{
            font-size: 16px;
            font-weight: bold;
            color: #34495e;
            margin: 20px 0 10px 0;
        }}
        
        /* 新的信息列表布局 */
        .info-list {{
            margin: 15px 0;
        }}
        
        .info-row {{
            display: flex;
            padding: 12px 0;
            border-bottom: 1px solid #ecf0f1;
            align-items: center;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
            min-width: 140px;
            flex-shrink: 0;
        }}
        
        .info-value {{
            color: #666;
            flex: 1;
        }}
        
        /* 两列信息组 */
        .info-group {{
            display: flex;
            gap: 40px;
            margin: 15px 0;
        }}
        
        .info-column {{
            flex: 1;
        }}
        
        .link-group {{
            display: flex;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        .link-item {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }}
        
        .link-item:hover {{
            color: #004499;
            background-color: #f0f7ff;
            border-color: #0066cc;
        }}
        
        .requirement-list {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        
        .requirement-item {{
            margin: 8px 0;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        
        .requirement-link {{
            color: #0066cc;
            text-decoration: none;
            transition: color 0.3s;
            font-weight: 500;
        }}
        
        .requirement-link:hover {{
            color: #004499;
            text-decoration: underline;
        }}
        
        /* 需求详情样式 */
        .requirement-detail {{
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; color: #2c3e50; margin-bottom: 30px;">{self.title}</h1>
        
        <!-- 1. 基本信息 -->
        <div class="section-title">1. 基本信息</div>
    
        <div class="info-list">
            <div class="info-row">
                <span class="info-label">需求级别：</span>
                <span class="info-value">SF(系统级)</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求ID：</span>
                <span class="info-value">无</span>
            </div>
            <div class="info-row">
                <span class="info-label">需求名称：</span>
                <span class="info-value">{self.title}</span>
            </div>
        </div>
        
        <div class="section-title">2. 需求描述</div>
        <div class="requirement-detail">
            <a href="{desc_href}" class="link-item">详细描述</a>
        </div>
        
        <!-- 3. CM信息 - 使用两列布局 -->
        <div class="section-title">3. CM信息</div>
        
        <div class="info-group">
            <div class="info-column">
                <div class="info-list">
                    <div class="info-row">
                        <span class="info-label">责任人：</span>
                        <span class="info-value">{self.assignee}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划开始时间：</span>
                        <span class="info-value">{self.plan_start_date}</span>
                    </div>
                </div>
            </div>
            <div class="info-column">
                <div class="info-list">
                    <div class="info-row">
                        <span class="info-label">计划工时：</span>
                        <span class="info-value">{self.workload}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">计划结束时间：</span>
                        <span class="info-value">{self.plan_end_date}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 评审和修改记录链接 -->
        <div class="link-group">
            <a href="{review_href}" class="link-item">评审记录</a>
            <a href="{history_href}" class="link-item">修改记录</a>
        </div>
        
        <!-- 4. 关联项 -->
        <div class="section-title">4. 关联项</div>
        
        <div class="subsection-title">4.1 上一层级需求：</div>
        <div class="requirement-list">
            <div class="requirement-item">
                <a href="upper-level-requirement.html" class="requirement-link">无</a>
            </div>
        </div>
        
        <div class="subsection-title">4.2 下一层级需求(IR级)：</div>
        <div class="requirement-list">
            {ir_links_html if ir_links_html else '<div class="requirement-item">无</div>'}
        </div>
    </div>
</body>
</html>"""
        
        # 将HTML内容写入文件
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成SF HTML文件: {self.html_file}")
        except Exception as e:
            print(f"写入HTML文件失败: {e}")

    def generate_req_navigation_html(self):
        """
        生成SF的需求导航HTML文件，并保存到req_navga_html_file指定的路径
        """
        if not self.req_navga_html_file:
            print("错误: SF的req_navga_html_file未设置")
            return
        
        if not self.html_file:
            print("错误: SF的html_file未设置，无法计算相对路径")
            return
        
        # 计算SF节点自身的相对路径（从导航文件到SF详情文件）
        sf_relative_path = calculate_relative_path(self.req_navga_html_file, self.html_file)
        
        # 生成完整的HTML内容
        html_content = self._build_navigation_html(sf_relative_path)
        
        # 写入文件
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.req_navga_html_file), exist_ok=True)
            
            with open(self.req_navga_html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成需求导航HTML文件: {self.req_navga_html_file}")
            
        except Exception as e:
            print(f"写入需求导航HTML文件失败: {e}")
    
    def _build_navigation_html(self, sf_relative_path: str) -> str:
        """构建完整的导航HTML文档"""
        # 生成SF节点的HTML（开始部分）
        sf_node_start = f'''
            <div class="node">
                <div class="node-content">
                    <span class="level-badge level-sf">SF</span>
                    <a href="{sf_relative_path}" class="node-link" target="_blank">{self.title}</a>
                    <div class="toggle">▶</div>
                </div>
                <div class="children">'''
        
        # 生成IR-SR-AR层级结构
        children_html = self._generate_children_hierarchy()
        
        # 完成SF节点
        complete_sf_node = sf_node_start + children_html + '''
                </div>
            </div>'''
        
        # 返回完整的HTML文档
        return self._get_html_template().format(
            title=f"{self.title} 需求导航",
            sf_node=complete_sf_node
        )
    
    def _generate_children_hierarchy(self) -> str:
        """生成IR-SR-AR层级结构的HTML"""
        if not self.irs:
            return '''
                    <div class="empty-message">暂无IR级需求</div>'''
        
        children_html = ""
        
        # 遍历所有IR
        for ir in self.irs:
            if not ir.title or not ir.html_file:
                continue
                
            # 计算IR的相对路径
            ir_relative_path = calculate_relative_path(self.req_navga_html_file, ir.html_file)
            
            # 生成IR节点（开始部分）
            ir_node_start = f'''
                    <div class="node">
                        <div class="node-content">
                            <span class="level-badge level-ir">IR</span>
                            <a href="{ir_relative_path}" class="node-link" target="_blank">{ir.title}</a>
                            <div class="toggle">▶</div>
                        </div>
                        <div class="children">'''
            
            # 生成SR子节点
            sr_children = self._generate_sr_children(ir)
            
            # 完成IR节点
            ir_node = ir_node_start + sr_children + '''
                        </div>
                    </div>'''
            children_html += ir_node
        
        return children_html
    
    def _generate_sr_children(self, ir: 'IR') -> str:
        """生成SR子节点的HTML"""
        if not hasattr(ir, 'srs') or not ir.srs:
            return '''
                            <div class="empty-message">暂无SR级需求</div>'''
        
        sr_children = ""
        
        for sr in ir.srs:
            if not sr.title or not sr.html_file:
                continue
            
            # 计算SR的相对路径
            sr_relative_path = calculate_relative_path(self.req_navga_html_file, sr.html_file)
            
            # 生成SR节点（开始部分）
            sr_node_start = f'''
                            <div class="node">
                                <div class="node-content">
                                    <span class="level-badge level-sr">SR</span>
                                    <a href="{sr_relative_path}" class="node-link" target="_blank">{sr.title}</a>
                                    <div class="toggle">▶</div>
                                </div>
                                <div class="children">'''
            
            # 生成AR子节点
            ar_children = self._generate_ar_children(sr)
            
            # 完成SR节点
            sr_node = sr_node_start + ar_children + '''
                                </div>
                            </div>'''
            sr_children += sr_node
        
        return sr_children
    
    def _generate_ar_children(self, sr: 'SR') -> str:
        """生成AR子节点的HTML"""
        if not hasattr(sr, 'ars') or not sr.ars:
            return '''
                                    <div class="empty-message">暂无AR级需求</div>'''
        
        ar_children = ""
        
        for ar in sr.ars:
            if not ar.title or not ar.html_file:
                continue
            
            # 计算AR的相对路径
            ar_relative_path = calculate_relative_path(self.req_navga_html_file, ar.html_file)
            
            # 生成AR节点
            ar_node = f'''
                                    <div class="node">
                                        <div class="node-content">
                                            <span class="level-badge level-ar">AR</span>
                                            <a href="{ar_relative_path}" class="node-link" target="_blank">{ar.title}</a>
                                        </div>
                                    </div>'''
            ar_children += ar_node
        
        return ar_children
    
    def _get_html_template(self) -> str:
        """返回HTML模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #3498db;
        }}
        
        .description {{
            background-color: #e8f4fd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }}
        
        .traceability-tree {{
            margin-top: 30px;
        }}
        
        .node {{
            margin: 10px 0;
            position: relative;
        }}
        
        .node-content {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background-color: white;
            border-radius: 6px;
            border: 1px solid #e1e8ed;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .node-content:hover {{
            background-color: #f0f7ff;
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
        }}
        
        .toggle {{
            width: 24px;
            height: 24px;
            margin-left: 10px;
            border-radius: 50%;
            background-color: #3498db;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            flex-shrink: 0;
        }}
        
        .toggle:hover {{
            background-color: #2980b9;
            transform: scale(1.1);
        }}
        
        .node-link {{
            color: #2c3e50;
            text-decoration: none;
            font-weight: 500;
            flex-grow: 1;
        }}
        
        .node-link:hover {{
            color: #3498db;
        }}
        
        .level-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
            color: white;
            flex-shrink: 0;
        }}
        
        .level-sf {{
            background-color: #e74c3c;
        }}
        
        .level-ir {{
            background-color: #3498db;
        }}
        
        .level-sr {{
            background-color: #2ecc71;
        }}
        
        .level-ar {{
            background-color: #f39c12;
        }}
        
        .children {{
            margin-left: 30px;
            display: none;
            border-left: 2px dashed #bdc3c7;
            padding-left: 20px;
        }}
        
        .children.show {{
            display: block;
        }}
        
        .empty-message {{
            color: #7f8c8d;
            font-style: italic;
            padding: 10px 0;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .btn-expand {{
            background-color: #3498db;
            color: white;
        }}
        
        .btn-expand:hover {{
            background-color: #2980b9;
        }}
        
        .btn-collapse {{
            background-color: #95a5a6;
            color: white;
        }}
        
        .btn-collapse:hover {{
            background-color: #7f8c8d;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 14px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="description">
            <p>需求导航可按SF-IR-SR-AR层级进行追溯浏览。点击需求名称可查看详细信息，点击右侧箭头可展开/折叠下级需求。</p>
            <p>点击"展开全部"可查看完整层级结构，点击"折叠全部"可重新折叠所有节点。</p>
        </div>
        
        <div class="traceability-tree" id="traceabilityTree">
{sf_node}
        </div>
        
        <div class="action-buttons">
            <button class="btn btn-expand" id="expandAll">展开全部</button>
            <button class="btn btn-collapse" id="collapseAll">折叠全部</button>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #e74c3c;"></div>
                <span>SF - 系统需求</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #3498db;"></div>
                <span>IR - 高层需求</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #2ecc71;"></div>
                <span>SR - 高层需求</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #f39c12;"></div>
                <span>AR - 低层需求</span>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 切换节点展开/折叠
            const toggles = document.querySelectorAll('.toggle');
            toggles.forEach(toggle => {{
                toggle.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    const children = this.parentElement.nextElementSibling;
                    if (children && children.classList.contains('children')) {{
                        children.classList.toggle('show');
                        this.textContent = children.classList.contains('show') ? '▼' : '▶';
                    }}
                }});
            }});
            
            // 展开全部
            document.getElementById('expandAll').addEventListener('click', function() {{
                const allChildren = document.querySelectorAll('.children');
                const allToggles = document.querySelectorAll('.toggle');
                
                allChildren.forEach(child => {{
                    child.classList.add('show');
                }});
                
                allToggles.forEach(toggle => {{
                    toggle.textContent = '▼';
                }});
            }});
            
            // 折叠全部
            document.getElementById('collapseAll').addEventListener('click', function() {{
                const allChildren = document.querySelectorAll('.children');
                const allToggles = document.querySelectorAll('.toggle');
                
                allChildren.forEach(child => {{
                    child.classList.remove('show');
                }});
                
                allToggles.forEach(toggle => {{
                    toggle.textContent = '▶';
                }});
            }});
        }});
    </script>
</body>
</html>'''

    def generate_req_table_html(self):
        """
        生成SF-IR需求表HTML文件，并保存到req_table_html_file指定的路径
        """
        if not self.req_table_html_file:
            print("错误: SF的req_table_html_file未设置")
            return
        
        if not self.html_file:
            print("错误: SF的html_file未设置，无法计算相对路径")
            return
        
        # 计算SF文件的相对路径
        sf_relative_path = calculate_relative_path(self.req_table_html_file, self.html_file)
        
        # 生成IR行HTML
        ir_rows_html = self._generate_ir_rows(sf_relative_path)
        
        # 构建完整的HTML内容
        html_content = self._build_table_html(sf_relative_path, ir_rows_html)
        
        # 写入文件
        try:
            with open(self.req_table_html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"已成功生成SF-IR需求表HTML文件: {self.req_table_html_file}")
            
        except Exception as e:
            print(f"写入SF-IR需求表HTML文件失败: {e}")
    
    def _generate_ir_rows(self, sf_relative_path: str) -> str:
        """生成IR行的HTML"""
        if not self.irs:
            return f'''
                <tr>
                    <td class="sf-cell" rowspan="1">
                        <a href="{sf_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td colspan="2" style="text-align: center; color: #7f8c8d; font-style: italic;">
                        暂无IR级需求
                    </td>
                </tr>'''
        
        rows_html = ""
        row_count = len(self.irs)
        
        for i, ir in enumerate(self.irs):
            if not ir.req_id:
                continue
                
            # 第一个链接：使用IR的req_table_html_file（对应示例中的"任务管理/任务管理.html"）
            # 这是IR自己的需求表文件
            ir_table_href = calculate_relative_path(self.req_table_html_file, ir.req_table_html_file)
            
            # 第二个链接：使用IR的html_file（对应示例中的"../SF/任务管理/任务管理.html"）
            # 这是IR的详情文件
            ir_detail_href = calculate_relative_path(self.req_table_html_file, ir.html_file)
            
            # 获取IR的标题，如果没有则显示"无名称"
            ir_title = ir.title if ir.title else "无名称"
            
            # 如果是第一行，包含SF单元格
            if i == 0:
                row = f'''
                <tr>
                    <td class="sf-cell" rowspan="{row_count}">
                        <a href="{sf_relative_path}" target="_blank">{self.title}</a>
                    </td>
                    <td><a href="{ir_table_href}" target="_blank">{ir.req_id}</a></td>
                    <td><a href="{ir_detail_href}" target="_blank">{ir_title}</a></td>
                </tr>'''
            else:
                row = f'''
                <tr>
                    <td><a href="{ir_table_href}" target="_blank">{ir.req_id}</a></td>
                    <td><a href="{ir_detail_href}" target="_blank">{ir_title}</a></td>
                </tr>'''
            
            rows_html += row
        
        return rows_html
    
    def _build_table_html(self, sf_relative_path: str, ir_rows_html: str) -> str:
        """构建完整的表格HTML文档"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title} SF-IR需求表</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            padding: 30px;
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 25px;
            color: #2c3e50;
            font-weight: 600;
            font-size: 24px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eaeaea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            border: 1px solid #ddd;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 500;
            padding: 14px 16px;
            text-align: center;
            border-right: 1px solid #2c81ba;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        td {{
            padding: 12px 16px;
            text-align: center;
            border-bottom: 1px solid #eaeaea;
            border-right: 1px solid #eaeaea;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        tr:hover {{
            background-color: #f0f7ff;
        }}
        
        .sf-cell {{
            background-color: #e8f4fc;
            font-weight: 500;
            vertical-align: middle;
            color: #2c3e50;
        }}
        
        a {{
            color: #2980b9;
            text-decoration: none;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        a:hover {{
            background-color: #3498db;
            color: white;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 25px;
            color: #7f8c8d;
            font-size: 14px;
            padding-top: 15px;
            border-top: 1px solid #eaeaea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{self.title} SF-IR需求表</h1>
        
        <table>
            <thead>
                <tr>
                    <th>SF</th>
                    <th>IR-高层需求ID</th>
                    <th>IR-需求名称</th>
                </tr>
            </thead>
            <tbody>
{ir_rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>'''

    def generate_all_html(self):
        self.generate_html()
        self.detailed_description.generate_html()
        self.review_record.generate_html()
        self.history_record.generate_html()
        self.generate_req_navigation_html()
        self.generate_req_table_html()
        for ir in self.irs:
            ir.generate_html()
            ir.detailed_description.generate_html()
            ir.review_record.generate_html()
            ir.history_record.generate_html()
            ir.generate_req_table_html()
            for sr in ir.srs:
                sr.generate_html()
                sr.detailed_description.generate_html()
                sr.review_record.generate_html()
                sr.history_record.generate_html()
                sr.generate_req_table_html()
                for ar in sr.ars:
                    ar.generate_html()
                    ar.detailed_description.generate_html()
                    ar.review_record.generate_html()
                    ar.history_record.generate_html()
