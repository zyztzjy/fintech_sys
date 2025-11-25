import dashscope
from dashscope import Generation
import os
from typing import List, Dict
import json


class FinancialCoachAgent:
    def __init__(self):
        # 配置 Qwen API - 请替换为您的 API_KEY
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "sk-f048c8f9134d42058be81012f5cffb23")
        dashscope.api_key = self.api_key

        self.client_types = {
            "稳健型中年客户": {
                "profile": "45岁企业中层，有房贷和子女教育压力，关注本金安全和流动性",
                "concerns": ["保本吗", "急用钱", "收益稳定性", "风险等级"],
                "questions": ["这个产品保本吗？", "急用钱时好赎回吗？", "收益比定期存款高多少？"],
                "difficulty": "中等"
            },
            "进取型年轻客户": {
                "profile": "28岁互联网从业者，追求高收益，能承受较高风险",
                "concerns": ["年化收益", "增长潜力", "投资门槛", "市场机会"],
                "questions": ["年化收益能到多少？", "有什么高收益产品？", "风险大没关系"],
                "difficulty": "中等"
            },
            "保守型退休客户": {
                "profile": "65岁退休教师，极度风险厌恶，主要需求是资金安全和流动性",
                "concerns": ["绝对安全", "随时取用", "本金保障", "简单易懂"],
                "questions": ["这个绝对安全吗？", "能不能随时取出来？", "我只要保本的"],
                "difficulty": "中等"
            },
            "蛮横型高净值客户": {
                "profile": "50岁企业主，资产雄厚但性格强势，缺乏耐心，喜欢质疑专业人士",
                "concerns": ["服务效率", "专业权威", "定制方案", "特权待遇"],
                "questions": ["你懂不懂啊？", "我认识你们行长！", "别跟我讲这些理论", "直接说能赚多少钱"],
                "difficulty": "困难",
                "behavior_traits": [
                    "频繁打断理财经理的讲解",
                    "质疑理财经理的专业能力",
                    "要求特殊待遇和更高收益",
                    "缺乏耐心听完整的产品介绍",
                    "喜欢用身份地位施压",
                    "对风险提示不屑一顾"
                ]
            },
            "小白型新手客户": {
                "profile": "25岁职场新人，第一次接触理财，对金融知识几乎为零，容易迷茫和犹豫",
                "concerns": ["完全不懂", "害怕风险", "钱会不会没", "怎么开始", "需要学习"],
                "questions": [
                    "理财是什么意思？我完全不懂这些",
                    "我的钱会不会亏没啊？好害怕",
                    "应该从多少钱开始投资？",
                    "这些专业术语我都听不懂，能说简单点吗？",
                    "别人都说理财有风险，是真的吗？",
                    "我每个月就几千块工资，也能理财吗？",
                    "能不能一步一步教我该怎么做？"
                ],
                "difficulty": "简单但需要耐心",
                "behavior_traits": [
                    "频繁表示自己什么都不懂",
                    "需要反复解释基本概念",
                    "对专业术语感到困惑",
                    "容易犹豫不决",
                    "需要大量 reassurance",
                    "提问非常基础但重要的问题",
                    "害怕做出错误决定",
                    "需要简单明了的步骤指导",
                    "对数字和计算感到头疼"
                ]
            },
            "企业主客户": {
                "profile": "45岁中小企业主，资金流动性要求高，关注税务优化和资产隔离",
                "concerns": ["税务筹划", "资产隔离", "资金周转", "企业理财"],
                "questions": ["这个能省税吗？", "和企业资产能分开吗？", "急用钱时怎么办？"],
                "difficulty": "中等"
            },
            "白领上班族": {
                "profile": "32岁外企白领，工作稳定但忙碌，偏好便捷的理财方式",
                "concerns": ["操作便捷", "自动续投", "手机银行", "定期定额"],
                "questions": ["手机能操作吗？", "能设置自动投资吗？", "每月定投怎么样？"],
                "difficulty": "简单"
            }
        }

    def get_response(self, user_input: str, message_history: List[Dict], client_type: str, difficulty: int = 3) -> str:
        """获取AI陪练回复"""

        client_profile = self.client_types.get(client_type, self.client_types["稳健型中年客户"])

        # 根据难度调整客户行为
        difficulty_modifier = ""
        if difficulty >= 4:
            difficulty_modifier = "适当增加提问的尖锐性和质疑程度，但保持合理性。"
        elif difficulty == 5:
            difficulty_modifier = "显著增加质疑和挑战性，可以适当表现出不耐烦和强势态度。"

        system_prompt = f"""
        你是一名真实的{client_type}，正在与理财经理咨询理财产品。

        你的个人情况：{client_profile['profile']}
        你的主要关注点：{', '.join(client_profile['concerns'])}
        你的典型问题：{', '.join(client_profile['questions'])}

        {f"你的行为特点：{', '.join(client_profile.get('behavior_traits', []))}" if client_profile.get('behavior_traits') else ""}

        对话规则：
        1. 以真实客户的身份自然对话，表达真实的疑虑和需求
        2. 根据理财经理的回复提出合理的后续问题
        3. 可以适当表现出犹豫、担心或兴趣
        4. 不要主动结束对话，持续互动直到理财经理明显推动流程
        5. 如果理财经理的话术很好，可以表现出被说服的倾向
        6. 如果理财经理的推荐不合适，要明确表达顾虑
        7. {difficulty_modifier}

        请用自然、口语化的中文回复，展现真实客户的思考过程。
        """

        try:
            # 构建对话历史
            messages = [{"role": "system", "content": system_prompt}]
            for msg in message_history[-6:]:  # 最近6轮对话作为上下文
                if msg["role"] == "user":
                    messages.append({"role": "user", "content": msg["content"]})
                else:
                    messages.append({"role": "assistant", "content": msg["content"]})

            # 调用 Qwen API
            response = Generation.call(
                model="qwen-max",
                messages=messages,
                temperature=0.7 + (difficulty * 0.06),  # 难度越高，回复越不可预测
                max_tokens=500,
                result_format='message'
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"抱歉，Qwen服务暂时不可用。错误码：{response.status_code}"

        except Exception as e:
            return f"抱歉，我现在无法回复。错误信息：{str(e)}"