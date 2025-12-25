from config import config
from models import SF, IR, SR, AR,TestCaseDetail,TestCase,TestSuite
from rest_client import api_get_tc_detail_by_number, api_post_all_tc_with_limit, api_get_sf_detail_by_id,api_post_sf_by_keyword,api_get_ir_detail_by_id,api_post_ir_list_by_id,api_get_sr_detail_by_id,api_post_sr_list_by_id,api_get_ar_detail_by_id

def print_test_cases_summary(test_suite: TestSuite):
    """打印测试用例摘要"""
    print("\n" + "="*80)
    print("测试用例列表:")
    print("="*80)
    
    # 打印测试套件基本信息
    print(f"测试用例总数: {test_suite.total}")
    print(f"已获取测试用例数: {len(test_suite.test_cases)}")
    print(f"HTML文件: {test_suite.html_file}")
    
    # 打印所有测试用例的详细信息
    if test_suite.test_cases:
        print(f"\n所有测试用例详情 ({len(test_suite.test_cases)} 个):")
        print("-" * 120)
        
        for i, test_case in enumerate(test_suite.test_cases, 1):
            print(f"\n[{i}] Number: {test_case.number}")
            print(f"    Name: {test_case.name}")
            
            # 打印关联的AR名称
            if test_case.related_ar_name:
                print(f"    Related AR: {test_case.related_ar_name}")
            else:
                print(f"    Related AR: 无")
            
            # 打印测试用例详情中的preparation
            if test_case.test_case_detail and test_case.test_case_detail.preparation:
                preparation = test_case.test_case_detail.preparation
                # 处理换行符，使其在控制台中显示更美观
                preparation = preparation.replace('\n', ' ').replace('\\n', ' ')
                print(f"    Preparation: {preparation}")
            else:
                print(f"    Preparation: 无")
            
            # 分隔线（每5个测试用例加一条分隔线）
            if i % 5 == 0 and i < len(test_suite.test_cases):
                print("-" * 80)
    else:
        print("没有测试用例数据")

def print_hierarchical_data(sf):
    """按层级打印数据"""
    print("\n" + "="*80)
    print("按层级打印数据:")
    print("="*80)
    
    # 打印SF信息
    print(f"\n[SF层级]")
    sf.print_info()
    
    # 打印每个IR及其下的SR和AR
    for ir in sf.irs:
        print(f"\n  [IR层级] {ir.number} - {ir.title}")
        ir.print_info()
        
        for sr in ir.srs:
            print(f"\n    [SR层级] {sr.number} - {sr.title}")
            sr.print_info()
            
            for ar in sr.ars:
                print(f"\n      [AR层级] {ar.number} - {ar.title}")
                ar.print_info()

def main():
    # 创建空的SF实例
    sf = SF()
    
    print("="*80)
    print("开始加载SF信息...")
    print("="*80)
    
    # 使用一个函数加载完整SF信息（从配置读取关键词）
    if not sf.load_sf_by_keyword():
        print("加载SF信息失败")
        return
    
    print(f"\n? SF基本信息加载成功")
    print(f"  SF标题: {sf.title} ({sf.number})")
    
    # 更新SF的所有IR的详细信息
    print("\n" + "="*80)
    print("开始更新所有IR的详细信息...")
    print("="*80)
    sf.update_all_irs()
    
    # 更新所有SR的详细信息
    print("\n" + "="*80)
    print("开始更新所有SR的详细信息...")
    print("="*80)
    sf.update_all_srs()
    
    # 更新所有AR的详细信息
    print("\n" + "="*80)
    print("开始更新所有AR的详细信息...")
    print("="*80)
    sf.update_all_ars()
    
    # 统计信息
    print("\n" + "="*80)
    print("数据加载完成，统计信息:")
    print("="*80)
    
    total_irs = len(sf.irs)
    total_srs = sum(len(ir.srs) for ir in sf.irs)
    total_ars = sum(len(sr.ars) for sr in [sr for ir in sf.irs for sr in ir.srs])
    
    print(f"SF: {sf.title}")
    print(f"  总IR数量: {total_irs}")
    print(f"  总SR数量: {total_srs}")
    print(f"  总AR数量: {total_ars}")
    
    # 按层级打印数据
    #print_hierarchical_data(sf)

    # ==================== 新增：获取所有测试用例 ====================
    print("\n" + "="*80)
    print("开始获取所有测试用例...")
    print("="*80)
    
    # 创建测试套件
    test_suite = TestSuite(html_file="test_report.html")
    
    # 分批获取所有测试用例
    if test_suite.load_all_test_cases(batch_size=100):
        print("\n✓ 测试用例获取成功")
        
        # 打印测试用例摘要
        print("\n 开始对测试用例列表进行排序")
        test_suite.sort_test_cases_by_number()
        print_test_cases_summary(test_suite)        
        
    else:
        print("\n✗ 测试用例获取失败")

    sf.generate_all_html()    
    print("\n程序执行完成！")
if __name__ == "__main__":
    main()