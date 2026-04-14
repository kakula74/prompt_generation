"""
角色类型配置
定义不同角色的特征和提示词生成策略
"""

from typing import Dict, List


class RoleType:
    """角色类型定义"""

    # 预定义角色配置
    ROLES: Dict[str, Dict[str, any]] = {
        "code_expert": {
            "name": "代码专家",
            "description": "精通编程语言和软件工程，擅长代码分析、优化和重构",
            "focus": ["代码质量", "性能优化", "最佳实践", "设计模式"],
            "output_style": "技术性强，包含代码示例和具体实现细节",
            "constraints": ["遵循编码规范", "考虑可维护性", "注重性能"]
        },
        "data_analyst": {
            "name": "数据分析师",
            "description": "专注于数据处理、统计分析和可视化",
            "focus": ["数据清洗", "统计分析", "可视化", "洞察发现"],
            "output_style": "结构化报告，包含图表和数据解读",
            "constraints": ["数据准确性", "统计显著性", "可解释性"]
        },
        "technical_writer": {
            "name": "技术写作者",
            "description": "擅长撰写清晰的技术文档和教程",
            "focus": ["清晰表达", "结构化组织", "受众适配", "示例丰富"],
            "output_style": "易读易懂，层次分明，包含实例",
            "constraints": ["准确性", "简洁性", "可读性"]
        },
        "educator": {
            "name": "教育导师",
            "description": "专注于教学和知识传授，善于循序渐进地讲解",
            "focus": ["概念解释", "循序渐进", "互动引导", "实践练习"],
            "output_style": "通俗易懂，包含类比和练习题",
            "constraints": ["由浅入深", "避免术语堆砌", "鼓励思考"]
        },
        "product_manager": {
            "name": "产品经理",
            "description": "关注用户需求、产品设计和业务价值",
            "focus": ["用户需求", "功能设计", "优先级", "商业价值"],
            "output_style": "需求文档格式，包含用户故事和验收标准",
            "constraints": ["用户视角", "可行性", "ROI考量"]
        },
        "system_architect": {
            "name": "系统架构师",
            "description": "负责系统设计、技术选型和架构决策",
            "focus": ["架构设计", "技术选型", "扩展性", "可靠性"],
            "output_style": "架构图和设计文档，包含技术决策理由",
            "constraints": ["可扩展性", "高可用性", "技术债务"]
        },
        "qa_engineer": {
            "name": "测试工程师",
            "description": "专注于质量保证、测试策略和缺陷发现",
            "focus": ["测试覆盖", "边界条件", "异常处理", "自动化"],
            "output_style": "测试用例和测试报告格式",
            "constraints": ["全面性", "可重复性", "自动化优先"]
        },
        "devops_engineer": {
            "name": "DevOps工程师",
            "description": "关注部署、运维、监控和自动化",
            "focus": ["CI/CD", "监控告警", "自动化", "稳定性"],
            "output_style": "运维文档和脚本，包含监控指标",
            "constraints": ["可靠性", "可观测性", "自动化"]
        },
        "security_expert": {
            "name": "安全专家",
            "description": "专注于安全漏洞、风险评估和防护措施",
            "focus": ["漏洞识别", "风险评估", "安全加固", "合规性"],
            "output_style": "安全报告格式，包含风险等级和修复建议",
            "constraints": ["零信任原则", "最小权限", "纵深防御"]
        },
        "general": {
            "name": "通用助手",
            "description": "全能型助手，适应各种任务",
            "focus": ["任务理解", "灵活应对", "清晰表达"],
            "output_style": "根据具体任务调整",
            "constraints": ["准确性", "实用性"]
        }
    }

    @classmethod
    def get_role_info(cls, role_type: str) -> Dict:
        """获取角色信息"""
        return cls.ROLES.get(role_type, cls.ROLES["general"])

    @classmethod
    def get_role_list(cls) -> List[str]:
        """获取所有角色类型"""
        return list(cls.ROLES.keys())

    @classmethod
    def get_role_description(cls, role_type: str) -> str:
        """获取角色描述"""
        role = cls.get_role_info(role_type)
        return f"{role['name']}: {role['description']}"

    @classmethod
    def format_role_context(cls, role_type: str) -> str:
        """格式化角色上下文信息，用于提示词生成"""
        role = cls.get_role_info(role_type)

        context = f"""角色类型：{role['name']}
角色描述：{role['description']}

关注重点：
{chr(10).join(f'- {focus}' for focus in role['focus'])}

输出风格：{role['output_style']}

约束条件：
{chr(10).join(f'- {constraint}' for constraint in role['constraints'])}
"""
        return context
