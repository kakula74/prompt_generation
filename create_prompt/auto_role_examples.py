"""
自动角色创建示例
演示如何根据需求自动创建角色并生成提示词
"""

from create_prompt import PromptCreatorAgent
from dotenv import load_dotenv

load_dotenv()


def example_auto_create_role():
    """示例：自动创建角色"""
    print("=" * 80)
    print("示例1：自动创建角色 - 财务分析")
    print("=" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    我需要一个提示词，让AI帮我分析公司的年度财务报表。
    要求能够识别财务风险、评估盈利能力、给出投资建议。
    输出要包含关键财务指标分析和风险提示。
    """

    # auto_create_role=True（默认），会根据需求自动创建角色
    result = agent.create_prompt(requirement, auto_create_role=True)

    print(f"\n📋 需求分析：\n{result['analysis']}\n")
    print(f"🎭 创建的角色：{result['role_info']['name']}")
    print(f"   描述：{result['role_info']['description']}\n")
    print(f"✨ 最终提示词：\n{result['prompt']}\n")
    print(f"📊 评估：总分 {result['evaluation'].get('total_score', 'N/A')}/40，迭代 {result['iterations']} 次\n")


def example_auto_vs_manual():
    """对比：自动创建 vs 手动指定角色"""
    print("=" * 80)
    print("示例2：对比自动创建和手动指定角色")
    print("=" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    创建一个提示词，让AI帮我设计一个电商网站的用户注册流程。
    需要考虑用户体验、安全性、转化率。
    """

    print("\n方式1：自动创建角色")
    print("-" * 40)
    result1 = agent.create_prompt(requirement, auto_create_role=True)
    print(f"创建的角色：{result1['role_info']['name']}")
    print(f"角色标识：{result1['role_info']['role_key']}\n")

    print("\n方式2：手动指定角色（产品经理）")
    print("-" * 40)
    result2 = agent.create_prompt(requirement, role_type="product_manager", auto_create_role=False)
    print(f"使用角色：{result2['role_info']['name']}")
    print(f"角色标识：{result2['role_info']['role_key']}\n")

    print("\n对比结果：")
    print(f"自动创建角色更贴合具体需求，手动指定角色使用预定义配置")


def example_complex_task():
    """示例：复杂任务自动创建角色"""
    print("\n" + "=" * 80)
    print("示例3：复杂任务 - 自动创建专业角色")
    print("=" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    我需要一个提示词，让AI帮我审查智能合约代码的安全性。
    要求：
    1. 识别常见的安全漏洞（重入攻击、整数溢出等）
    2. 检查权限控制和访问控制
    3. 评估gas优化
    4. 给出修复建议和改进代码
    输出要包含风险等级和详细的安全报告。
    """

    result = agent.create_prompt(requirement, auto_create_role=True)

    print(f"\n🎭 自动创建的角色：{result['role_info']['name']}")
    print(f"   标识：{result['role_info']['role_key']}")
    print(f"   描述：{result['role_info']['description']}\n")
    print(f"✨ 生成的提示词：\n{result['prompt']}\n")
    print(f"📊 质量评分：{result['evaluation'].get('total_score', 'N/A')}/40")


def interactive_auto_create():
    """交互模式：输入需求自动创建角色"""
    print("\n" + "=" * 80)
    print("🎯 交互模式：自动创建角色")
    print("=" * 80)

    agent = PromptCreatorAgent()

    print("\n请描述你的需求（可以多行，空行结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    requirement = "\n".join(lines)

    if not requirement.strip():
        print("❌ 需求不能为空")
        return

    print("\n🚀 正在自动创建角色并生成提示词...\n")
    result = agent.create_prompt(requirement, auto_create_role=True)

    print("=" * 80)
    print("🎭 自动创建的角色：")
    print(f"  • 名称：{result['role_info']['name']}")
    print(f"  • 标识：{result['role_info']['role_key']}")
    print(f"  • 描述：{result['role_info']['description']}")
    print("\n" + "=" * 80)
    print("📋 需求分析：")
    print(result['analysis'])
    print("\n" + "=" * 80)
    print("✨ 最终提示词：")
    print(result['prompt'])
    print("\n" + "=" * 80)
    print("📊 评估结果：")
    eval_data = result['evaluation']
    print(f"  • 目标明确性：{eval_data.get('clarity_score', 'N/A')}/10")
    print(f"  • 结构清晰度：{eval_data.get('structure_score', 'N/A')}/10")
    print(f"  • 简洁性：{eval_data.get('conciseness_score', 'N/A')}/10")
    print(f"  • 可执行性：{eval_data.get('executability_score', 'N/A')}/10")
    print(f"  • 总分：{eval_data.get('total_score', 'N/A')}/40")
    print(f"  • 迭代次数：{result['iterations']}")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_auto_create()
    else:
        # 运行所有示例
        example_auto_create_role()
        print("\n\n")
        example_auto_vs_manual()
        print("\n\n")
        example_complex_task()
        print("\n\n")
        print("💡 提示：运行 'python auto_role_examples.py interactive' 进入交互模式")
