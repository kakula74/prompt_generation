"""
基于LangGraph的提示词创建Agent
采用ReAct方式迭代优化，生成结构清晰、目标明确且简洁的提示词
"""

from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator
import os
from dotenv import load_dotenv
from role_types import RoleType

# 加载.env配置
load_dotenv()


class PromptState(TypedDict):
    """状态定义"""
    user_requirement: str  # 用户需求
    role_type: str  # 角色类型
    role_config: dict  # 角色配置
    current_prompt: str  # 当前提示词
    analysis: str  # 需求分析
    evaluation: dict  # 评估结果
    optimization_suggestions: list  # 优化建议
    iteration_count: int  # 迭代次数
    is_complete: bool  # 是否完成
    auto_create_role: bool  # 是否自动创建角色


class PromptCreatorAgent:
    """提示词创建Agent"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_iterations: Optional[int] = None
    ):
        # 从环境变量或参数获取配置
        self.model_name = model_name or os.getenv("MODEL", "gpt-5.4-mini")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.max_iterations = max_iterations or int(os.getenv("MAX_ITERATIONS", "3"))

        # 初始化LLM

        self.llm = ChatOpenAI(model=self.model_name,
                            base_url=self.base_url,
                            api_key=self.api_key,
                            temperature=0.7,
                            extra_body={"thinking": {"type": "enabled"}})

        self.graph = self._build_graph()

    def _clean_response(self, content: str) -> str:
        """清理模型响应，移除思考标签内容

        如果响应包含</think>标签，只保留标签之后的内容
        """
        import re

        # 查找</think>标签
        think_end = re.search(r'</think>', content, re.IGNORECASE)
        if think_end:
            # 返回</think>之后的内容，去除前后空白
            return content[think_end.end():].strip()

        # 如果没有</think>标签，返回原内容
        return content

    def _build_graph(self) -> StateGraph:
        """构建状态图"""
        workflow = StateGraph(PromptState)

        # 添加节点
        workflow.add_node("create_role", self.create_role)
        workflow.add_node("analyze_requirement", self.analyze_requirement)
        workflow.add_node("generate_prompt", self.generate_prompt)
        workflow.add_node("evaluate_prompt", self.evaluate_prompt)
        workflow.add_node("optimize_prompt", self.optimize_prompt)

        # 设置入口点
        workflow.set_entry_point("create_role")

        # 添加边
        workflow.add_edge("create_role", "analyze_requirement")
        workflow.add_edge("analyze_requirement", "generate_prompt")
        workflow.add_edge("generate_prompt", "evaluate_prompt")
        workflow.add_conditional_edges(
            "evaluate_prompt",
            self.should_continue,
            {
                "optimize": "optimize_prompt",
                "end": END
            }
        )
        workflow.add_edge("optimize_prompt", "evaluate_prompt")

        return workflow.compile()

    def create_role(self, state: PromptState) -> PromptState:
        """根据需求创建或选择角色"""
        # 如果已经指定了角色类型且不需要自动创建，直接使用
        if state.get('role_type') and not state.get('auto_create_role', True):
            state['role_config'] = RoleType.get_role_info(state['role_type'])
            return state

        # 根据需求自动创建角色
        print("🤖 正在根据需求分析最适合的角色...")

        messages = [
            SystemMessage(content="""你是一个角色设计专家。根据用户的任务需求，设计一个最适合的AI角色。

输出JSON格式：
{
    "role_key": "角色唯一标识（英文小写+下划线）",
    "name": "角色名称（中文）",
    "description": "角色描述（一句话说明角色定位和专长）",
    "focus": ["关注点1", "关注点2", "关注点3", "关注点4"],
    "output_style": "输出风格描述",
    "constraints": ["约束条件1", "约束条件2", "约束条件3"]
}

要求：
1. 角色定位要明确，与任务高度相关
2. 关注点要具体，3-5个
3. 输出风格要清晰描述期望的输出格式和特点
4. 约束条件要实用，2-4个
5. role_key要简洁且有意义"""),
            HumanMessage(content=f"任务需求：{state['user_requirement']}")
        ]

        response = self.llm.invoke(messages)

        # 清理响应内容
        cleaned_content = self._clean_response(response.content)

        import json
        import re

        try:
            # 尝试直接解析
            role_config = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            try:
                # 查找JSON代码块
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_content, re.DOTALL)
                if json_match:
                    role_config = json.loads(json_match.group(1))
                else:
                    # 尝试查找第一个完整的JSON对象
                    json_match = re.search(r'\{.*?\}', cleaned_content, re.DOTALL)
                    if json_match:
                        role_config = json.loads(json_match.group(0))
                    else:
                        raise json.JSONDecodeError("No JSON found", cleaned_content, 0)
            except (json.JSONDecodeError, AttributeError) as e:
                # 解析失败，使用默认角色
                print(f"⚠️  角色创建失败（JSON解析错误），使用通用角色")
                print(f"   原始响应：{cleaned_content[:200]}...")
                state['role_type'] = 'general'
                state['role_config'] = RoleType.get_role_info('general')
                return state

        # 解析成功
        state['role_type'] = role_config['role_key']
        state['role_config'] = role_config

        print(f"✅ 已创建角色：{role_config['name']} ({role_config['role_key']})")
        print(f"   描述：{role_config['description']}")

        return state

    def analyze_requirement(self, state: PromptState) -> PromptState:
        """分析用户需求"""
        role_config = state['role_config']

        messages = [
            SystemMessage(content=f"""需求分析专家。提取关键信息：
1. 核心任务
2. 输出格式
3. 关键约束

目标角色：{role_config['name']} - {role_config['description']}
关注：{', '.join(role_config['focus'][:3])}

输出简洁分析（≤150字）。"""),
            HumanMessage(content=f"需求：{state['user_requirement']}")
        ]

        response = self.llm.invoke(messages)
        state["analysis"] = self._clean_response(response.content)
        state["iteration_count"] = 0
        return state

    def generate_prompt(self, state: PromptState) -> PromptState:
        """生成提示词"""
        role_config = state['role_config']

        # 精简的角色上下文
        role_summary = f"{role_config['name']} - {role_config['description']}"
        key_focuses = ', '.join(role_config['focus'][:3])  # 只取前3个关注点

        if state["iteration_count"] == 0:
            # 首次生成
            messages = [
                SystemMessage(content=f"""你是提示词工程专家。你的目标是：把“用户需求”改写成一段让LLM可直接执行、无歧义、且**不遗漏任何信息**的高质量提示词。目标角色：{role_summary}

**工作原则（必须遵守）**：
1. **信息不遗漏**：用户输入中的每一条信息（目标、背景、条件、示例、字段、格式、边界、偏好、限制）都必须被显式吸收进最终提示词；不得忽略、淡化或自行删改。
2. **逐条覆盖**：先在心中把用户需求拆成要点清单，再在提示词中逐条映射到“任务/输入/输出格式/约束条件”。如果某条信息无法归类，放入“约束条件-其他”并保留。
3. **强可执行**：使用明确动词与可检验要求（例如“必须/仅/禁止/按…输出/字段为…”）。避免“尽量/可能/适当”等模糊词。
4. **结构化且精炼**：信息完整优先，其次才是简洁；删除空洞话术与重复描述，但保留执行所需的全部细节。
5. **冲突处理**：若用户信息存在冲突/缺口，**不得擅自补写**；在“约束条件”中写明“缺失项/待确认项”，并给出最少量澄清问题（最多3个）。
6. 关注重点：{key_focuses}

**输出要求**：
- 仅输出最终提示词正文（不要输出你的分析过程）。
- 提示词要能直接粘贴给LLM使用。

输出结构（严格按此结构输出）：
# 角色
[用1-2句定义角色与专长，与用户需求强相关]

# 任务
[用要点列出核心任务与完成标准，逐条覆盖用户需求]

# 输入
[说明用户将提供什么信息/字段；如何理解示例；对缺失/异常输入如何处理]

# 输出格式
[用列表形式定义输出格式：语言、结构、JSON字段/示例格式要求、顺序、是否允许额外字段等]

# 约束条件
[列出所有关键约束：不得遗漏任何用户信息、不得编造、必须遵循示例/格式、边界条件、质量要求；如有待确认项，列出并给出≤3个澄清问题]

最后自检一句（写进提示词中）：在输出前，逐条核对已覆盖用户需求的所有要点，确保无遗漏。"""),
                HumanMessage(content=f"需求：{state['user_requirement']}\n\n分析：{state['analysis']}")
            ]
        else:
            # 优化迭代
            messages = [
                SystemMessage(content="""你是一位顶级的提示词工程师，你的任务是根据“当前版本”的提示词和“优化建议”，进行一次深度重构和优化，输出一个质量更高的新版提示词。

**第一步：分析与思考（在脑海中进行）**

1.  **分析当前版本**：
    *   它的核心目标是什么？
    *   结构是否清晰？指令是否明确？
    *   是否存在模糊、冗余或矛盾的表述？
    *   是否缺少必要的上下文或约束？

2.  **解读优化建议**：
    *   这些建议具体指向哪些问题？
    *   它们的核心改进方向是什么（例如，要求更简洁、要求更详细、要求改变格式）？

3.  **制定优化计划**：
    *   我需要如何重写角色定义，使其更精准？
    *   我应该如何调整任务描述，使其更具可操作性？
    *   我应该如何改进格式或约束，以满足建议的要求？
    *   我需要补充哪些被遗漏的关键信息？

**第二步：执行优化与输出**

根据你的分析和计划，重写并输出一个完美的新版提示词。

**优化准则：**
1.  **角色和目标**：角色定义必须非常清晰，目标必须明确。
2.  **结构化**：使用Markdown（如`#`、`##`、`*`、`1.`）来构建清晰的层次结构。
3.  **指令明确**：指令必须是具体、无歧义、可执行的。避免使用“可能”、“也许”等模糊词汇。
4.  **内容完整**：确保提供了LLM完成任务所需的所有背景信息、上下文、示例和约束。
5.  **精炼无冗余**：删除所有不必要的词语、重复的指令和空洞的描述，做到“字字珠玑”。

**输出要求：**
*   **仅输出**优化后最终的、完整的提示词文本。
*   **严禁**包含任何解释、评论、分析过程或Markdown代码块标记（如` ``` `）。"""),
                HumanMessage(content=f"""当前版本：
{state['current_prompt']}

优化建议：{', '.join(state['optimization_suggestions'][:3])}

请输出优化后的新版提示词。""")
            ]

        response = self.llm.invoke(messages)
        state["current_prompt"] = self._clean_response(response.content)
        return state

    def evaluate_prompt(self, state: PromptState) -> PromptState:
        """评估提示词质量"""
        messages = [
            SystemMessage(content="""评估提示词质量，输出JSON：

{
    "clarity_score": 1-10,
    "structure_score": 1-10,
    "conciseness_score": 1-10,
    "executability_score": 1-10,
    "total_score": 总分,
    "should_continue": true/false,
    "continue_reason": "需要继续的原因（如果should_continue为true）",
    "issues": ["问题"],
    "suggestions": ["建议"]
}

评分标准：
- clarity_score: 指令是否清晰明确，无歧义
- structure_score: 结构是否合理，层次是否清晰
- conciseness_score: 是否简洁适中，无冗余重复，也不过于简短缺失信息
- executability_score: LLM是否能直接执行，信息是否完整

should_continue判断标准：
- 如果总分<36分，或存在明显问题（不清晰/结构混乱/过于冗长/过于简短/信息不完整），设为true
- 如果总分≥36分且质量良好、长度适中，设为false
- 综合考虑质量和可优化空间

检查要点：
1. 是否有冗余、重复的内容
2. 信息是否完整，能否让LLM理解并执行任务
3. 长度是否适中（不要过长导致冗余，也不要过短导致信息不足）"""),
            HumanMessage(content=f"""当前迭代：{state['iteration_count'] + 1}次

{state['current_prompt']}

需求：{state['user_requirement'][:150]}""")
        ]

        response = self.llm.invoke(messages)

        # 清理响应内容
        cleaned_content = self._clean_response(response.content)

        import json
        import re
        try:
            eval_result = json.loads(cleaned_content)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_content, re.DOTALL)
                if json_match:
                    eval_result = json.loads(json_match.group(1))
                else:
                    json_match = re.search(r'\{.*?\}', cleaned_content, re.DOTALL)
                    if json_match:
                        eval_result = json.loads(json_match.group(0))
                    else:
                        raise json.JSONDecodeError("No JSON found", cleaned_content, 0)
            except (json.JSONDecodeError, AttributeError):
                eval_result = {
                    "total_score": 32,
                    "should_continue": True,
                    "continue_reason": "评估解析失败，需要继续优化",
                    "issues": ["需要精简"],
                    "suggestions": ["删除冗余"]
                }

        # 确保必要字段存在
        if "issues" not in eval_result:
            eval_result["issues"] = []
        if "suggestions" not in eval_result:
            eval_result["suggestions"] = []
        if "should_continue" not in eval_result:
            # 如果LLM没有返回should_continue，根据分数判断
            total_score = eval_result.get("total_score", 0)
            eval_result["should_continue"] = total_score < 36
            eval_result["continue_reason"] = f"总分{total_score}分，低于36分阈值" if total_score < 36 else ""

        state["evaluation"] = eval_result
        state["optimization_suggestions"] = eval_result.get("suggestions", [])
        state["iteration_count"] += 1

        return state

    def should_continue(self, state: PromptState) -> Literal["optimize", "end"]:
        """判断是否继续优化（基于LLM判断）"""
        # 达到最大迭代次数，强制停止
        if state["iteration_count"] >= self.max_iterations:
            print(f"⏸️  已达到最大迭代次数（{self.max_iterations}次），停止优化")
            return "end"

        # 获取LLM的判断
        should_continue = state["evaluation"].get("should_continue", False)
        continue_reason = state["evaluation"].get("continue_reason", "")

        if should_continue:
            print(f"🔄 LLM判断需要继续优化：{continue_reason}")
            return "optimize"
        else:
            print(f"✅ LLM判断质量已达标，停止优化")
            return "end"

    def optimize_prompt(self, state: PromptState) -> PromptState:
        """优化提示词（通过重新生成实现）"""
        return self.generate_prompt(state)

    def create_prompt(self, user_requirement: str, role_type: str = None, auto_create_role: bool = True) -> dict:
        """创建提示词的主入口

        Args:
            user_requirement: 用户需求描述
            role_type: 角色类型（可选）。如果不提供且auto_create_role=True，会自动创建角色
            auto_create_role: 是否自动创建角色。True=根据需求自动创建，False=使用指定的role_type

        Returns:
            包含prompt、analysis、evaluation、iterations、role_info、state的字典
        """
        # 如果指定了role_type但不在已知角色中，且不自动创建，则使用general
        if role_type and not auto_create_role:
            if role_type not in RoleType.get_role_list():
                print(f"⚠️  未知角色类型 '{role_type}'，使用默认角色 'general'")
                role_type = "general"

        initial_state = {
            "user_requirement": user_requirement,
            "role_type": role_type or "general",
            "role_config": {},
            "auto_create_role": auto_create_role,
            "current_prompt": "",
            "analysis": "",
            "evaluation": {},
            "optimization_suggestions": [],
            "iteration_count": 0,
            "is_complete": False
        }

        # 运行图
        final_state = self.graph.invoke(initial_state)

        return {
            "prompt": final_state["current_prompt"],
            "analysis": final_state["analysis"],
            "evaluation": final_state["evaluation"],
            "iterations": final_state["iteration_count"],
            "role_info": {
                "role_key": final_state["role_type"],
                "name": final_state["role_config"]["name"],
                "description": final_state["role_config"]["description"]
            },
            "_state": final_state  # 保存完整状态，用于后续优化
        }

    def continue_optimize(self, result: dict, max_extra_iterations: int = 2) -> dict:
        """继续优化已有提示词（当达到最大迭代次数但质量仍不理想时）

        Args:
            result: create_prompt返回的结果字典
            max_extra_iterations: 额外的优化迭代次数（默认2次）

        Returns:
            优化后的结果字典
        """
        print(f"\n🔄 手动继续优化提示词（额外{max_extra_iterations}轮迭代）...")

        state = result["_state"].copy()

        # 保存原始迭代次数
        original_iterations = state["iteration_count"]

        # 临时增加最大迭代次数
        original_max = self.max_iterations
        self.max_iterations = original_iterations + max_extra_iterations

        print(f"📊 当前状态：已完成{original_iterations}次迭代，新增{max_extra_iterations}次机会")

        # 继续优化循环
        for i in range(max_extra_iterations):
            print(f"\n--- 第{original_iterations + i + 1}次迭代 ---")

            state = self.optimize_prompt(state)
            state = self.evaluate_prompt(state)

            # 检查LLM是否判断可以停止
            decision = self.should_continue(state)
            if decision == "end":
                print(f"✅ 优化完成（额外迭代{i+1}次后达标）")
                break
        else:
            # 用完所有额外迭代次数
            print(f"⏸️  已完成{max_extra_iterations}次额外迭代")

        # 恢复原始设置
        self.max_iterations = original_max

        return {
            "prompt": state["current_prompt"],
            "analysis": state["analysis"],
            "evaluation": state["evaluation"],
            "iterations": state["iteration_count"],
            "role_info": result["role_info"],
            "_state": state
        }

    def refine_with_feedback(self, result: dict, feedback: str, max_iterations: int = 2) -> dict:
        """根据用户反馈补充需求和限制

        Args:
            result: create_prompt返回的结果字典
            feedback: 用户的反馈和补充要求
            max_iterations: 优化迭代次数（默认2次）

        Returns:
            优化后的结果字典
        """
        print(f"\n📝 根据反馈优化提示词（最多{max_iterations}次迭代）...")
        print(f"反馈内容：{feedback}\n")

        state = result["_state"].copy()

        # 将用户反馈整合到优化建议中
        state["optimization_suggestions"] = [
            f"用户反馈：{feedback}",
            "根据反馈调整提示词内容和结构",
            "确保满足新增的需求和限制"
        ]

        # 更新需求描述（追加反馈）
        state["user_requirement"] = f"{state['user_requirement']}\n\n补充要求：{feedback}"

        # 保存原始迭代次数
        original_iterations = state["iteration_count"]

        # 临时设置最大迭代次数
        original_max = self.max_iterations
        self.max_iterations = original_iterations + max_iterations

        # 执行优化
        for i in range(max_iterations):
            print(f"\n--- 第{original_iterations + i + 1}次迭代 ---")

            state = self.generate_prompt(state)
            state = self.evaluate_prompt(state)

            # 检查LLM是否判断可以停止
            decision = self.should_continue(state)
            if decision == "end":
                print(f"✅ 优化完成（迭代{i+1}次后达标）")
                break
        else:
            print(f"⏸️  已完成{max_iterations}次迭代")

        # 恢复设置
        self.max_iterations = original_max

        return {
            "prompt": state["current_prompt"],
            "analysis": state["analysis"],
            "evaluation": state["evaluation"],
            "iterations": state["iteration_count"],
            "role_info": result["role_info"],
            "_state": state
        }


def show_result(result, detailed=False):
    """显示提示词结果

    Args:
        result: 提示词生成结果
        detailed: 是否显示详细信息（包括需求分析和问题列表）
    """
    print("\n" + "=" * 60)
    print("✨ 当前提示词：")
    print(result["prompt"])
    print("\n" + "=" * 60)
    print("📊 评估结果：")
    eval_result = result['evaluation']
    print(f"总分：{eval_result.get('total_score', 'N/A')}/40")
    print(f"  - 明确性：{eval_result.get('clarity_score', 'N/A')}/10")
    print(f"  - 结构性：{eval_result.get('structure_score', 'N/A')}/10")
    print(f"  - 简洁性：{eval_result.get('conciseness_score', 'N/A')}/10")
    print(f"  - 可执行性：{eval_result.get('executability_score', 'N/A')}/10")
    print(f"迭代次数：{result['iterations']} | 长度：{len(result['prompt'])}字")

    if detailed:
        if result.get('analysis'):
            print(f"\n📋 需求分析：")
            print(result['analysis'])
        if eval_result.get('issues'):
            print(f"\n⚠️  发现问题：")
            for issue in eval_result['issues']:
                print(f"  • {issue}")
    elif eval_result.get('issues'):
        print(f"问题：{', '.join(eval_result['issues'])}")

    print("=" * 60)


def save_prompt(result, filename=None):
    """保存提示词到文件

    Args:
        result: 提示词生成结果
        filename: 文件名（可选，默认为prompt.txt）
    """
    if filename is None:
        filename = input("\n保存文件名（默认：prompt.txt）: ").strip() or "prompt.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result["prompt"])
    print(f"✅ 已保存到 {filename}")


def optimization_loop(agent, result):
    """优化循环 - 提供继续优化和补充需求的选项

    Args:
        agent: PromptCreatorAgent实例
        result: 当前提示词结果

    Returns:
        优化后的结果
    """
    while True:
        print("\n💡 选项：")
        print("  1. 继续优化（提高质量）")
        print("  2. 补充需求（添加要求）")
        print("  3. 完成并保存")
        print("  4. 退出")

        choice = input("\n请选择 (1/2/3/4): ").strip()

        if choice == "1":
            result = agent.continue_optimize(result, max_extra_iterations=2)
            show_result(result)

        elif choice == "2":
            print("\n请输入补充需求（支持多行输入，输入空行结束）：")
            lines = []
            while True:
                line = input("> " if not lines else "  ")
                if not line:  # 空行表示结束
                    break
                lines.append(line)

            feedback = "\n".join(lines).strip()
            if feedback:
                result = agent.refine_with_feedback(result, feedback, max_iterations=2)
                show_result(result)
            else:
                print("未输入内容，跳过。")

        elif choice == "3":
            save_prompt(result)
            return result

        elif choice == "4":
            print("👋 退出")
            return result

        else:
            print("❌ 无效选择")


def demo_mode():
    """示例演示模式"""
    agent = PromptCreatorAgent()

    print("=" * 60)
    print("🤖 提示词创建Agent - 示例演示")
    print("=" * 60)

    # 示例需求
    requirement = """
请帮我写一个提示词，用于指导LLM生成一个数据分析的提示词。要求：
1. 角色定位：数据分析专家，专长于从复杂数据中提取洞见，能够指导LLM进行数据分析任务。
2. 任务描述：生成一个提示词，能够让LLM理解并执行一个数据分析任务。提示词需要明确要求LLM分析数据集中的趋势、异常值和相关性，并提供可视化建议。
    """

    print(f"\n📝 示例需求：{requirement}\n")
    print("🚀 开始创建提示词...\n")

    result = agent.create_prompt(requirement, auto_create_role=True)
    show_result(result, detailed=True)

    result = optimization_loop(agent, result)
    print("\n🎉 完成！")


def interactive_mode():
    """交互式模式"""
    agent = PromptCreatorAgent()

    print("=" * 60)
    print("🤖 提示词创建Agent - 交互式模式")
    print("=" * 60)

    print("\n请描述您的提示词需求（支持多行输入，输入空行结束）：")
    lines = []
    while True:
        line = input("> " if not lines else "  ")
        if not line:  # 空行表示结束
            break
        lines.append(line)

    requirement = "\n".join(lines).strip()

    if not requirement:
        print("❌ 需求不能为空")
        return

    print("\n🚀 开始创建提示词...\n")
    result = agent.create_prompt(requirement, auto_create_role=True)
    show_result(result)

    result = optimization_loop(agent, result)
    print("\n🎉 完成！")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="提示词创建Agent - 基于LangGraph的智能提示词生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  # 直接输入需求生成提示词
  python create_prompt.py "帮我写一个数据分析的提示词"

  # 指定输出文件
  python create_prompt.py "生成代码审查提示词" -o review.txt

  # 设置最大迭代次数
  python create_prompt.py "生成翻译提示词" --max-iterations 5

  # 进入交互式模式
  python create_prompt.py --interactive

  # 运行示例
  python create_prompt.py --demo
        """
    )

    parser.add_argument(
        "requirement",
        nargs="?",
        help="提示词需求描述（直接输入需求文本）"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="进入交互式模式"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="输出文件路径（默认：prompt.txt）"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        help="最大迭代次数（默认：从环境变量读取或3）"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="运行示例演示"
    )

    args = parser.parse_args()

    # 模式选择
    if args.demo:
        # 运行示例
        demo_mode()
    elif args.interactive:
        # 交互式模式
        interactive_mode()
    elif args.requirement:
        # 命令行模式
        agent = PromptCreatorAgent(max_iterations=args.max_iterations)

        print("=" * 60)
        print("🤖 提示词创建Agent")
        print("=" * 60)
        print(f"\n📝 需求：{args.requirement}\n")
        print("🚀 开始创建提示词...\n")

        result = agent.create_prompt(args.requirement, auto_create_role=True)
        show_result(result)

        # 如果指定了输出文件，直接保存；否则进入优化循环
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result["prompt"])
            print(f"\n✅ 已保存到 {args.output}")
            print("\n🎉 完成！")
        else:
            result = optimization_loop(agent, result)
            print("\n🎉 完成！")
    else:
        # 没有参数，显示帮助
        parser.print_help()
