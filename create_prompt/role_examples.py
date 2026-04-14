"""
角色类型使用示例
"""

from create_prompt import PromptCreatorAgent
from role_types import RoleType
from dotenv import load_dotenv

load_dotenv()


def show_available_roles():
    """显示所有可用角色"""
    print("=" * 80)
    print("📋 可用角色类型")
    print("=" * 80)

    for role_key in RoleType.get_role_list():
        role = RoleType.get_role_info(role_key)
        print(f"\n🎭 {role_key}")
        print(f"   名称：{role['name']}")
        print(f"   描述：{role['description']}")
        print(f"   关注：{', '.join(role['focus'][:3])}")
    print("\n" + "=" * 80)


def example_code_expert():
    """示例：代码专家角色"""
    print("\n示例1：代码专家 - 性能分析")
    print("-" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    创建一个提示词，让AI分析Python代码的性能瓶颈，
    识别耗时操作，给出优化建议和改进代码。
    """

    result = agent.create_prompt(requirement, role_type="code_expert")

    print(f"✨ 生成的提示词：\n{result['prompt']}\n")
    print(f"📊 评分：{result['evaluation'].get('total_score', 'N/A')}/40")


def example_data_analyst():
    """示例：数据分析师角色"""
    print("\n示例2：数据分析师 - 数据报告")
    print("-" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    需要一个提示词让AI分析CSV数据并生成报告。
    包括数据分布、异常值检测、可视化建议。
    """

    result = agent.create_prompt(requirement, role_type="data_analyst")

    print(f"✨ 生成的提示词：\n{result['prompt']}\n")
    print(f"📊 评分：{result['evaluation'].get('total_score', 'N/A')}/40")


def example_educator():
    """示例：教育导师角色"""
    print("\n示例3：教育导师 - 概念讲解")
    print("-" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    创建一个提示词，让AI讲解Python装饰器的概念。
    要求通俗易懂，包含实例和练习题。
    """

    result = agent.create_prompt(requirement, role_type="educator")

    print(f"✨ 生成的提示词：\n{result['prompt']}\n")
    print(f"📊 评分：{result['evaluation'].get('total_score', 'N/A')}/40")


def example_system_architect():
    """示例：系统架构师角色"""
    print("\n示例4：系统架构师 - 架构设计")
    print("-" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    需要一个提示词让AI设计微服务架构。
    包括服务拆分、技术选型、通信方式、数据一致性方案。
    """

    result = agent.create_prompt(requirement, role_type="system_architect")

    print(f"✨ 生成的提示词：\n{result['prompt']}\n")
    print(f"📊 评分：{result['evaluation'].get('total_score', 'N/A')}/40")


def interactive_with_role():
    """交互模式：选择角色并输入需求"""
    print("\n" + "=" * 80)
    print("🎯 交互模式：选择角色并创建提示词")
    print("=" * 80)

    # 显示角色列表
    roles = RoleType.get_role_list()
    print("\n可用角色：")
    for i, role_key in enumerate(roles, 1):
        role = RoleType.get_role_info(role_key)
        print(f"{i}. {role_key} - {role['name']}")

    # 选择角色
    while True:
        try:
            choice = input("\n请选择角色编号（直接回车使用general）：").strip()
            if not choice:
                role_type = "general"
                break
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(roles):
                role_type = roles[choice_idx]
                break
            else:
                print("❌ 无效的选择，请重新输入")
        except ValueError:
            print("❌ 请输入数字")

    print(f"\n✅ 已选择角色：{RoleType.get_role_info(role_type)['name']}")

    # 输入需求
    print("\n请描述你的需求（输入多行，空行结束）：")
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

    # 创建提示词
    print("\n🚀 正在创建提示词...\n")
    agent = PromptCreatorAgent()
    result = agent.create_prompt(requirement, role_type=role_type)

    # 显示结果
    print("=" * 80)
    print("📋 需求分析：")
    print(result['analysis'])
    print("\n" + "=" * 80)
    print("✨ 最终提示词：")
    print(result['prompt'])
    print("\n" + "=" * 80)
    print("📊 评估结果：")
    eval_data = result['evaluation']
    print(f"  • 角色类型：{RoleType.get_role_info(result['role_type'])['name']}")
    print(f"  • 目标明确性：{eval_data.get('clarity_score', 'N/A')}/10")
    print(f"  • 结构清晰度：{eval_data.get('structure_score', 'N/A')}/10")
    print(f"  • 简洁性：{eval_data.get('conciseness_score', 'N/A')}/10")
    print(f"  • 可执行性：{eval_data.get('executability_score', 'N/A')}/10")
    print(f"  • 总分：{eval_data.get('total_score', 'N/A')}/40")
    print(f"  • 迭代次数：{result['iterations']}")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "roles":
            show_available_roles()
        elif sys.argv[1] == "interactive":
            interactive_with_role()
        else:
            print("用法：")
            print("  python role_examples.py roles       - 显示所有角色")
            print("  python role_examples.py interactive - 交互模式")
            print("  python role_examples.py             - 运行所有示例")
    else:
        # 运行所有示例
        show_available_roles()
        example_code_expert()
        example_data_analyst()
        example_educator()
        example_system_architect()
        print("\n💡 提示：")
        print("  • python role_examples.py roles       - 查看所有角色")
        print("  • python role_examples.py interactive - 交互式创建")
