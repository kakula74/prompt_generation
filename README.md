# 提示词创建Agent

基于LangGraph的智能提示词生成工具，采用ReAct方式迭代优化，自动生成结构清晰、目标明确且简洁的提示词。

## 特性

- 🎯 **智能需求分析**：自动提取关键信息和约束条件
- 🤖 **自动角色创建**：根据需求AI自动创建最适合的角色（默认模式）
- 🔄 **ReAct迭代优化**：通过推理-行动循环不断改进
- 📊 **多维度评估**：从明确性、结构、简洁性、可执行性四个维度评分
- 🎭 **双模式支持**：自动创建角色 + 10种预定义角色
- ⚡ **自动收敛**：达到质量阈值或最大迭代次数后自动停止

## 工作流程

```
用户需求 → 需求分析 → 生成提示词 → 评估质量 → [优化] → 最终提示词
                                    ↑_________|
```

## requirements
langgraph>=0.0.20
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-core>=0.1.0
openai>=1.0.0
python-dotenv>=1.0.0

## 配置

自行创建.env文件：

```bash
touch .env
```

编辑 `.env` 文件：

```bash
# 基础配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL=gpt-4
MAX_ITERATIONS=3
```

**extra**：可以在.env文件中加入langsmith用于监控输出结果

```
## 使用示例

### 自动创建角色（推荐）

系统会根据你的需求自动创建最适合的角色：

```python
from create_prompt import PromptCreatorAgent

agent = PromptCreatorAgent()

requirement = """
我需要一个提示词，让AI帮我分析公司财务报表，
识别风险，评估盈利能力，给出投资建议。
"""

# auto_create_role=True（默认），自动创建角色
result = agent.create_prompt(requirement)

print(f"创建的角色：{result['role_info']['name']}")
print(f"角色描述：{result['role_info']['description']}")
print(f"提示词：{result['prompt']}")
```

**工作流程**：
```
用户需求 → AI分析需求 → 自动创建角色 → 生成提示词 → 迭代优化 → 最终提示词
```

### 手动指定角色

如果你想使用预定义角色：

```python
# 使用预定义的代码专家角色
result = agent.create_prompt(
    "分析Python代码性能",
    role_type="code_expert",
    auto_create_role=False  # 不自动创建，使用指定角色
)
```

### 可用角色类型

| 角色类型 | 名称 | 适用场景 |
|---------|------|---------|
| `code_expert` | 代码专家 | 代码分析、优化、重构 |
| `data_analyst` | 数据分析师 | 数据处理、统计分析、可视化 |
| `technical_writer` | 技术写作者 | 技术文档、教程编写 |
| `educator` | 教育导师 | 概念讲解、教学内容 |
| `product_manager` | 产品经理 | 需求分析、功能设计 |
| `system_architect` | 系统架构师 | 架构设计、技术选型 |
| `qa_engineer` | 测试工程师 | 测试策略、质量保证 |
| `devops_engineer` | DevOps工程师 | 部署、运维、监控 |
| `security_expert` | 安全专家 | 安全审计、漏洞分析 |
| `general` | 通用助手 | 通用任务（默认） |

### 运行示例

```bash
# 自动创建角色示例（推荐）
python auto_role_examples.py

# 交互模式（自动创建角色）
python auto_role_examples.py interactive

# 预定义角色示例
python examples.py

# 查看所有预定义角色
python role_examples.py roles
```

## 评估维度

| 维度 | 说明 | 分值范围 |
|------|------|----------|
| 目标明确性 | 任务目标是否清晰明确 | 1-10 |
| 结构清晰度 | 组织结构是否清晰易懂 | 1-10 |
| 简洁性 | 是否简洁精炼，无冗余 | 1-10 |
| 可执行性 | LLM是否容易理解和执行 | 1-10 |

总分 ≥ 36 分（平均9分）视为优质提示词。

## 输出格式

生成的提示词采用标准化结构：

```markdown
# 角色
[定义AI的角色]

# 任务
[明确的任务描述]

# 输出格式
[期望的输出格式]

# 约束条件
[必要的约束]
```

## 高级用法

### 手动指定参数

```python
# 参数会覆盖.env配置
agent = PromptCreatorAgent(
    model_name="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key="your-key",
    max_iterations=5
)

result = agent.create_prompt(requirement, role_type="code_expert")
```

### 自定义评估标准

```python
# 修改should_continue方法中的阈值
def should_continue(self, state: PromptState) -> Literal["optimize", "end"]:
    if state["iteration_count"] >= self.max_iterations:
        return "end"
    
    total_score = state["evaluation"].get("total_score", 0)
    if total_score >= 38:  # 提高质量要求
        return "end"
    
    return "optimize"
```

### 调整模型参数

```python
agent = PromptCreatorAgent(
    model_name="gpt-4-turbo-preview",
    max_iterations=5  # 增加迭代次数
)
```

## 注意事项

- 首次运行需要联网访问OpenAI API
- 建议使用GPT-4以获得更好的提示词质量
- 迭代次数建议设置为3-5次，避免过度优化
- 生成的提示词需要根据实际使用场景微调

## License

MIT
