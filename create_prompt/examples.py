"""
使用示例：演示如何使用提示词创建Agent
"""

from create_prompt import PromptCreatorAgent
from dotenv import load_dotenv

# 加载.env配置
load_dotenv()


def example_1():
    """示例1：代码分析提示词"""
    print("=" * 80)
    print("示例1：创建代码性能分析提示词")
    print("=" * 80)

    # 使用.env配置，也可以手动指定参数覆盖
    agent = PromptCreatorAgent()

    requirement = """
    我需要一个提示词，让AI帮我分析Python代码的性能瓶颈。
    要求能够识别出耗时的操作，给出优化建议，并提供改进后的代码示例。
    """

    result = agent.create_prompt(requirement, role_type="code_expert")

    print(f"\n📋 需求分析：\n{result['analysis']}\n")
    print(f"✨ 最终提示词：\n{result['prompt']}\n")
    print(f"📊 评估：总分 {result['evaluation'].get('total_score', 'N/A')}/40，迭代 {result['iterations']} 次\n")


def example_2():
    """示例2：文档生成提示词"""
    print("=" * 80)
    print("示例2：创建API文档生成提示词")
    print("=" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    创建一个提示词，让AI根据代码自动生成API文档。
    需要包含：接口描述、参数说明、返回值、示例代码。
    输出格式要符合OpenAPI 3.0规范。
    """

    result = agent.create_prompt(requirement, role_type="technical_writer")

    print(f"\n📋 需求分析：\n{result['analysis']}\n")
    print(f"✨ 最终提示词：\n{result['prompt']}\n")
    print(f"📊 评估：总分 {result['evaluation'].get('total_score', 'N/A')}/40，迭代 {result['iterations']} 次\n")


def example_3():
    """示例3：数据分析提示词"""
    print("=" * 80)
    print("示例3：创建数据分析报告提示词")
    print("=" * 80)

    agent = PromptCreatorAgent()

    requirement = """
    需要一个提示词让AI分析CSV数据并生成报告。
    要求：
    1. 自动识别数据类型和分布
    2. 发现异常值和缺失值
    3. 生成可视化建议
    4. 输出markdown格式的分析报告
    保持简洁，不要过于冗长。
    """

    result = agent.create_prompt(requirement, role_type="data_analyst")

    print(f"\n📋 需求分析：\n{result['analysis']}\n")
    print(f"✨ 最终提示词：\n{result['prompt']}\n")
    print(f"📊 评估：总分 {result['evaluation'].get('total_score', 'N/A')}/40，迭代 {result['iterations']} 次\n")


def interactive_mode():
    """交互模式：用户输入需求"""
    print("=" * 80)
    print("🎯 交互模式：输入你的需求")
    print("=" * 80)

    agent = PromptCreatorAgent()

    print("\n请描述你需要的提示词（输入多行，空行结束）：")
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

    print("\n🚀 正在创建提示词...\n")
    result = agent.create_prompt(requirement)

    print("=" * 80)
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
        interactive_mode()
    else:
        # 运行所有示例
        example_1()
        print("\n\n")
        example_2()
        print("\n\n")
        example_3()
        print("\n\n")
        print("💡 提示：运行 'python examples.py interactive' 进入交互模式")
