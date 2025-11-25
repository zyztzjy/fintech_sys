import dashscope
from dashscope import Generation
import os
from typing import List, Dict
import re
import json


class SessionEvaluator:
    def __init__(self):
        # 配置 Qwen API
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "sk-f048c8f9134d42058be81012f5cffb23")
        dashscope.api_key = self.api_key

        self.evaluation_criteria = {
            "demand_mining": {
                "weight": 0.20,
                "max_score": 20,
                "description": "深度挖掘客户需求的能力",
                "strict_indicators": [
                    "是否使用5W2H提问法全面了解客户情况",
                    "是否挖掘客户完整的财务状况（资产、负债、收入、支出）",
                    "是否准确评估客户风险承受能力等级",
                    "是否了解客户投资目标、期限和偏好",
                    "是否询问客户过往投资经验和教训",
                    "是否了解客户家庭情况和未来规划",
                    "是否识别客户的隐性需求和真实痛点",
                    "是否建立完整的客户画像和需求档案"
                ],
                "deduction_rules": [
                    "未使用开放式提问：-3分",
                    "仅表面询问需求：-2分",
                    "未了解完整财务状况：-3分",
                    "未评估风险承受能力：-3分",
                    "未明确投资目标期限：-2分",
                    "未了解过往投资经验：-2分",
                    "未挖掘家庭背景信息：-2分",
                    "未识别隐性需求：-2分",
                    "提问缺乏逻辑性和系统性：-2分"
                ],
                "excellent_threshold": 16,
                "good_threshold": 12,
                "pass_threshold": 8
            },
            "product_fit": {
                "weight": 0.20,
                "max_score": 20,
                "description": "产品与客户需求的精准匹配度",
                "strict_indicators": [
                    "风险等级是否与客户风险承受能力完全匹配",
                    "流动性安排是否满足客户资金使用需求",
                    "收益水平是否与客户预期合理对应",
                    "投资期限是否与客户时间要求一致",
                    "产品特点是否针对客户特殊情况优化",
                    "是否提供完整的资产配置方案",
                    "是否考虑税收优惠和成本优化",
                    "是否进行竞品对比分析",
                    "是否提供数据支撑和案例参考"
                ],
                "deduction_rules": [
                    "风险错配：-4分",
                    "流动性不匹配：-3分",
                    "收益预期不合理：-3分",
                    "期限不匹配：-3分",
                    "未个性化定制：-3分",
                    "未提供完整方案：-2分",
                    "未考虑税务成本：-2分",
                    "推荐理由不充分：-2分",
                    "缺乏数据支撑：-2分"
                ],
                "excellent_threshold": 16,
                "good_threshold": 12,
                "pass_threshold": 8
            },
            "objection_handling": {
                "weight": 0.20,
                "max_score": 20,
                "description": "专业处理客户异议和质疑的能力",
                "strict_indicators": [
                    "是否及时有效回应所有质疑点",
                    "是否提供数据和案例支持观点",
                    "是否展现深度同理心和专业耐心",
                    "是否提供可行的替代解决方案",
                    "是否将反对意见转化为销售机会",
                    "是否在压力下保持专业形象",
                    "是否有效化解情绪化质疑",
                    "是否使用FABE法则进行产品说明",
                    "是否主动预判并解决潜在异议"
                ],
                "deduction_rules": [
                    "回避关键质疑：-3分",
                    "缺乏数据支持：-3分",
                    "缺乏同理心：-3分",
                    "未提供替代方案：-2分",
                    "未转化销售机会：-2分",
                    "情绪失控：-3分",
                    "未化解情绪质疑：-2分",
                    "解释过于理论化：-2分",
                    "被动应对而非主动引导：-2分"
                ],
                "excellent_threshold": 16,
                "good_threshold": 12,
                "pass_threshold": 8
            },
            "communication": {
                "weight": 0.20,
                "max_score": 20,
                "description": "专业沟通表达和客户关系维护",
                "strict_indicators": [
                    "语言是否精准专业无歧义",
                    "表达是否逻辑清晰有层次",
                    "是否保持适度亲和力和信任感",
                    "是否使用客户易懂的专业术语",
                    "沟通节奏和控场能力是否恰当",
                    "非语言沟通是否专业得体",
                    "是否建立长期信任关系",
                    "是否主动确认客户理解程度",
                    "是否使用结构化表达方式"
                ],
                "deduction_rules": [
                    "专业术语使用不当：-2分",
                    "表达逻辑混乱：-2分",
                    "亲和力不足：-1分",
                    "沟通节奏失控：-1分",
                    "非语言沟通不当：-1分",
                    "未建立信任关系：-2分",
                    "语言啰嗦不简洁：-1分",
                    "未确认客户理解：-1分",
                    "缺乏结构化表达：-1分"
                ],
                "excellent_threshold": 16,
                "good_threshold": 12,
                "pass_threshold": 8
            },
            "professional_knowledge": {
                "weight": 0.20,
                "max_score": 20,
                "description": "金融产品和市场知识的专业深度",
                "strict_indicators": [
                    "产品条款和细节是否完全准确",
                    "风险提示是否完整且重点突出",
                    "法规合规要求是否严格遵守",
                    "市场趋势和机会判断是否专业",
                    "数据计算和演示是否精确无误",
                    "竞品对比分析是否客观全面",
                    "专业资质和认证是否恰当展示",
                    "是否了解最新监管政策",
                    "是否能够解释复杂金融概念"
                ],
                "deduction_rules": [
                    "产品信息错误：-4分",
                    "风险提示遗漏：-3分",
                    "违反合规要求：-8分（严重）",
                    "市场判断错误：-3分",
                    "计算演示错误：-3分",
                    "竞品分析偏颇：-2分",
                    "资质展示不当：-1分",
                    "政策理解错误：-3分",
                    "概念解释不清：-2分"
                ],
                "excellent_threshold": 16,
                "good_threshold": 12,
                "pass_threshold": 8
            }
        }

        # 平庸回答的特征模式
        self.mediocre_patterns = [
            "模板化回复", "缺乏个性化", "回避关键问题", "理论堆砌",
            "缺乏数据支撑", "情绪管理差", "沟通节奏混乱", "专业深度不足"
        ]

        # 新增亮点识别标准
        self.positive_indicators = {
            "demand_mining": [
                "使用开放式提问深入了解客户",
                "系统性收集客户完整信息",
                "挖掘到客户的隐性需求和痛点",
                "建立完整的客户画像",
                "提问逻辑清晰有层次",
                "使用5W2H等专业提问方法"
            ],
            "product_fit": [
                "产品推荐与客户需求高度匹配",
                "提供个性化定制方案",
                "考虑客户特殊情况优化方案",
                "提供完整的资产配置建议",
                "有数据支撑的产品对比分析",
                "考虑税务和成本优化"
            ],
            "objection_handling": [
                "有效化解客户关键质疑",
                "提供具体数据和案例支撑",
                "展现深度同理心和耐心",
                "将反对意见转化为机会",
                "在压力下保持专业形象",
                "使用FABE等专业销售方法"
            ],
            "communication": [
                "语言精准且通俗易懂",
                "表达逻辑清晰层次分明",
                "建立良好的信任关系",
                "沟通节奏把控得当",
                "使用客户能理解的语言",
                "展现专业亲和力"
            ],
            "professional_knowledge": [
                "产品信息准确无误",
                "风险提示完整清晰",
                "法规合规严格遵守",
                "市场分析专业到位",
                "概念解释通俗准确",
                "提供专业数据支撑"
            ]
        }

    def comprehensive_evaluation(self, messages: List[Dict], client_type: str, difficulty: int = 3) -> Dict:
        """平衡型综合评估 - 严格但公平"""

        # 提取理财经理的发言
        manager_messages = [msg['content'] for msg in messages if msg['role'] == 'user']
        conversation_text = "\n".join(manager_messages)

        # 检测亮点和平庸特征
        positive_score = self._detect_positive_indicators(manager_messages, client_type)
        mediocrity_score = self._detect_mediocrity(manager_messages)

        # 根据客户类型调整评估重点
        evaluation_focus = self._get_evaluation_focus(client_type, difficulty)

        evaluation_prompt = f"""
作为金融行业资深教练，请对以下理财经理与{client_type}的对话进行平衡评估。难度级别：{difficulty}/5。

对话记录：
{conversation_text}

{evaluation_focus}

## 📊 平衡评估标准（总分100分）

### 核心原则：
1. **严格但不苛刻**：要求专业但认可努力
2. **亮点加分制**：优秀表现给予额外加分  
3. **进步导向**：重点指出可改进的方向
4. **客户适配**：根据客户类型调整评估重点
5. **鼓励为主**：在指出问题的同时给予鼓励

### 1. 需求挖掘（20分）
{self._format_balanced_criteria('demand_mining')}

### 2. 产品匹配（20分）  
{self._format_balanced_criteria('product_fit')}

### 3. 异议处理（20分）
{self._format_balanced_criteria('objection_handling')}

### 4. 沟通能力（20分）
{self._format_balanced_criteria('communication')}

### 5. 专业知识（20分）
{self._format_balanced_criteria('professional_knowledge')}

## 🌟 亮点加分项（每项+1-2分）：
- 使用客户能理解的通俗语言解释复杂概念
- 主动挖掘客户的隐性需求和真实痛点
- 提供个性化定制的解决方案
- 有效处理情绪化质疑并建立信任
- 展现深度专业知识和数据支撑
- 沟通节奏把控得当，引导对话进程
- 展现耐心和同理心
- 提供清晰的步骤指导

## 📈 评分等级标准：
- 🟢 卓越 (90-100分)：专业表现突出，有多处亮点
- 🔵 优秀 (80-89分)：表现良好，有明显亮点
- 🟡 良好 (70-79分)：基本达标，有进步空间  
- 🟠 及格 (60-69分)：存在不足但无重大错误
- 🔴 需改进 (50-59分)：需要重点改进

请以JSON格式返回评估结果：
{{
    "overall_score": 75,
    "scores": {{
        "demand_mining": 15,
        "product_fit": 16,
        "objection_handling": 14, 
        "communication": 16,
        "professional_knowledge": 14
    }},
    "strengths": ["具体亮点描述，至少找出2-3个积极方面"],
    "improvements": ["具体改进建议，3-4个关键点"],
    "critical_errors": ["重大错误列表，如无则留空"],
    "positive_highlights": ["检测到的具体亮点"],
    "suggested_phrases": ["针对性提升话术"],
    "detailed_feedback": {{
        "demand_mining": "具体评价和改进建议",
        "product_fit": "具体评价和改进建议",
        "objection_handling": "具体评价和改进建议", 
        "communication": "具体评价和改进建议",
        "professional_knowledge": "具体评价和改进建议"
    }},
    "performance_level": "需改进/及格/良好/优秀/卓越",
    "encouragement": "一句鼓励性话语"
}}

请确保找出对话中的亮点，给予建设性反馈。
"""

        try:
            # 使用 Qwen API
            response = Generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.3,  # 适度随机性以识别亮点
                max_tokens=4000,
                result_format='message'
            )

            if response.status_code == 200:
                result_text = response.output.choices[0].message.content
                evaluation_data = self.parse_evaluation_result(result_text)

                # 应用亮点加分
                evaluation_data = self._apply_positive_adjustment(evaluation_data, positive_score)
                # 应用平庸检测调整（更温和）
                evaluation_data = self._apply_mediocrity_adjustment(evaluation_data, mediocrity_score)
                # 根据难度调整
                evaluation_data = self._apply_difficulty_adjustment(evaluation_data, difficulty, client_type)

                return evaluation_data
            else:
                print(f"Qwen API错误: {response.status_code}")
                return self.get_balanced_evaluation(difficulty, client_type)

        except Exception as e:
            print(f"评估过程出错: {str(e)}")
            return self.get_balanced_evaluation(difficulty, client_type)

    def _detect_positive_indicators(self, manager_messages: List[str], client_type: str) -> float:
        """检测回答中的亮点"""
        if not manager_messages:
            return 0.0

        text = " ".join(manager_messages).lower()

        positive_count = 0
        total_indicators = 0

        for dimension, indicators in self.positive_indicators.items():
            total_indicators += len(indicators)
            for indicator in indicators:
                # 简单的关键词匹配
                keywords = self._get_indicator_keywords(indicator)
                if any(keyword in text for keyword in keywords):
                    positive_count += 1

        # 特殊客户类型的额外亮点检测
        if "小白" in client_type:
            # 检测对小白客户的友好表现
            friendly_indicators = ["不用着急", "慢慢来", "我理解", "不用担心", "简单说", "举个例子", "从基础开始",
                                   "一步一步"]
            if any(indicator in text for indicator in friendly_indicators):
                positive_count += 2

        if "蛮横" in client_type:
            # 检测对蛮横客户的耐心表现
            patience_indicators = ["我理解您的顾虑", "您说得对", "感谢您提出", "我们来看数据", "保持冷静", "专业应对"]
            if any(indicator in text for indicator in patience_indicators):
                positive_count += 2

        return positive_count / total_indicators if total_indicators > 0 else 0.0

    def _get_indicator_keywords(self, indicator: str) -> List[str]:
        """获取指标对应的关键词"""
        keyword_map = {
            "使用开放式提问深入了解客户": ["什么", "如何", "为什么", "能不能聊聊", "您觉得", "哪些方面"],
            "系统性收集客户完整信息": ["收入", "支出", "资产", "负债", "家庭", "规划", "工作情况"],
            "挖掘到客户的隐性需求和痛点": ["其实您", "我理解您", "真正需要", "核心需求", "深层需求"],
            "建立完整的客户画像": ["整体情况", "全面了解", "综合评估", "客户画像"],
            "产品推荐与客户需求高度匹配": ["适合您", "根据您的", "匹配", "符合您", "针对您的"],
            "提供个性化定制方案": ["为您定制", "个性化", "专门为您", "量身定做", "个性化方案"],
            "有效化解客户关键质疑": ["数据表明", "案例显示", "实际上", "您看这样", "我们可以"],
            "展现深度同理心和耐心": ["我理解", "不用担心", "慢慢来", "不着急", "有道理"],
            "语言精准且通俗易懂": ["简单说", "举个例子", "就像", "通俗讲", "说白了"],
            "建立良好的信任关系": ["我们一起", "长期", "信任", "放心", "合作"],
            "产品信息准确无误": ["年化收益", "期限", "风险等级", "保本", "收益率"],
            "风险提示完整清晰": ["风险", "可能亏损", "不保证", "需要注意", "风险提示"]
        }
        return keyword_map.get(indicator, [indicator.split()[0].lower()])

    def _apply_positive_adjustment(self, evaluation_data: Dict, positive_score: float) -> Dict:
        """根据亮点检测调整分数"""
        if positive_score > 0.2:  # 有亮点就加分
            bonus_points = int(positive_score * 8)  # 最高加8分
            evaluation_data['overall_score'] = min(100, evaluation_data['overall_score'] + bonus_points)

            # 确保各维度分数也相应调整
            for key in evaluation_data['scores']:
                dimension_bonus = int(positive_score * 1.5)  # 各维度最高加1.5分
                evaluation_data['scores'][key] = min(20, evaluation_data['scores'][key] + dimension_bonus)

        return evaluation_data

    def _apply_mediocrity_adjustment(self, evaluation_data: Dict, mediocrity_score: float) -> Dict:
        """更温和的平庸检测调整"""
        if mediocrity_score > 0.6:  # 只有比较平庸才扣分
            adjustment_factor = 1.0 - ((mediocrity_score - 0.6) * 0.3)  # 最高降低12%
            evaluation_data['overall_score'] = int(evaluation_data['overall_score'] * adjustment_factor)

        return evaluation_data

    def _apply_difficulty_adjustment(self, evaluation_data: Dict, difficulty: int, client_type: str) -> Dict:
        """根据难度应用分数调整"""
        base_score = evaluation_data['overall_score']

        # 难度调整系数（更温和）
        if difficulty == 4:
            adjustment = 0.92  # 降低8%
        elif difficulty == 5:
            adjustment = 0.85  # 降低15%
        elif "蛮横" in client_type:
            adjustment = 0.95  # 蛮横客户降低5%
        else:
            adjustment = 1.0

        # 应用调整
        evaluation_data['overall_score'] = max(0, int(base_score * adjustment))
        for key in evaluation_data['scores']:
            original_score = evaluation_data['scores'][key]
            evaluation_data['scores'][key] = max(0, int(original_score * adjustment))

        # 设置表现等级
        evaluation_data['performance_level'] = self._get_performance_level(evaluation_data['overall_score'])

        return evaluation_data

    def _get_performance_level(self, score: int) -> str:
        """获取表现等级"""
        if score >= 90:
            return "卓越"
        elif score >= 80:
            return "优秀"
        elif score >= 70:
            return "良好"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"

    def _format_balanced_criteria(self, criteria_key: str) -> str:
        """格式化平衡评估标准"""
        criteria = self.evaluation_criteria[criteria_key]
        positive = "\n".join([f"   ✅ {indicator}" for indicator in self.positive_indicators[criteria_key][:3]])
        improvements = "\n".join([f"   📝 {rule}" for rule in criteria['deduction_rules'][:3]])

        return f"优秀表现：\n{positive}\n常见不足：\n{improvements}"

    def _get_evaluation_focus(self, client_type: str, difficulty: int) -> str:
        """获取评估重点说明"""
        focus_map = {
            "小白型新手客户": "🎓 重点评估耐心引导和通俗解释能力，认可基础教育的努力。对于通俗易懂的解释要给予加分。",
            "蛮横型高净值客户": "⚠️ 重点评估情绪控制和专业权威展现，认可压力下的稳定表现。对于保持专业冷静要给予认可。",
            "稳健型中年客户": "🏠 重点评估风险匹配和家庭规划，认可全面性考虑。对于稳健建议要给予肯定。",
            "进取型年轻客户": "🚀 重点评估收益机会把握，认可创新思维。对于进取型建议要适当认可。",
            "保守型退休客户": "🛡️ 重点评估安全保障，认可风险意识。对于保守建议要给予理解。",
            "企业主客户": "💼 重点评估税务和企业需求，认可商业思维。对于企业角度思考要加分。",
            "白领上班族": "📱 重点评估便捷方案，认可效率考虑。对于便捷性建议要认可。"
        }

        base_focus = focus_map.get(client_type, "采用标准平衡评估，重点找出亮点和进步空间。")

        if difficulty >= 4:
            base_focus += f"\n🔴 高难度模式：适当提高优秀标准，但仍要认可努力和亮点。"

        return base_focus

    def _detect_mediocrity(self, manager_messages: List[str]) -> float:
        """检测回答的平庸程度"""
        if not manager_messages:
            return 0.0

        text = " ".join(manager_messages).lower()

        mediocrity_indicators = 0
        total_indicators = len(self.mediocre_patterns)

        # 检测模板化语言
        template_phrases = ["很高兴为您服务", "这是一个很好的问题", "根据您的需求", "我们推荐", "建议您"]
        if any(phrase in text for phrase in template_phrases):
            mediocrity_indicators += 1

        # 检测缺乏数据支撑
        data_indicators = ["数据显示", "统计表明", "案例显示", "历史回报", "年化收益", "具体数据"]
        if not any(indicator in text for indicator in data_indicators):
            mediocrity_indicators += 1

        # 检测回避问题
        evasion_phrases = ["这个要看具体情况", "很难一概而论", "建议您考虑", "我们可以进一步讨论"]
        if any(phrase in text for phrase in evasion_phrases):
            mediocrity_indicators += 1

        # 检测理论堆砌
        theory_words = ["首先", "其次", "然后", "最后", "综上所述"]
        if len([word for word in theory_words if word in text]) > 3:
            mediocrity_indicators += 1

        return mediocrity_indicators / total_indicators

    def _get_strictness_modifier(self, client_type: str, difficulty: int) -> str:
        """获取严格程度修饰语"""
        modifiers = []

        if "小白" in client_type:
            modifiers.extend([
                "🎓 对此类理财小白客户重点评估：",
                "- 解释的通俗易懂程度权重加倍",
                "- 耐心和引导能力重点评估",
                "- 基础概念解释的准确性严格打分",
                "- 必须提供清晰的步骤指导",
                "- 避免使用专业术语，或用后立即解释",
                "- 情绪安抚和信心建立能力重点考察"
            ])
        elif "蛮横" in client_type:
            modifiers.extend([
                "⚠️ 对此类客户实行较严格标准：",
                "- 情绪控制能力权重加倍",
                "- 专业形象维护能力重点评估",
                "- 应对挑战性问题的技巧严格打分",
                "- 必须展现专业权威和自信",
                "- 对质疑必须提供数据支撑的反驳"
            ])

        if difficulty >= 4:
            modifiers.extend([
                f"🔴 高难度模式（{difficulty}/5）：",
                "- 评分标准适度提高严格度",
                "- 优秀标准适当提高",
                "- 但仍要认可努力和亮点"
            ])

        return "\n".join(modifiers) if modifiers else "采用标准平衡评估，重点找出亮点。"

    def parse_evaluation_result(self, result_text: str) -> Dict:
        """解析评估结果"""
        try:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # 验证必要字段是否存在
                required_fields = ['overall_score', 'scores']
                if all(field in result for field in required_fields):
                    return result
                else:
                    return self.get_balanced_evaluation(3, "普通客户")
            else:
                return self.get_balanced_evaluation(3, "普通客户")
        except:
            return self.get_balanced_evaluation(3, "普通客户")

    def get_balanced_evaluation(self, difficulty: int = 3, client_type: str = "普通客户") -> Dict:
        """获取平衡的默认评估结果"""
        # 更合理的基准分数
        base_score = 68 - (difficulty - 3) * 4  # 难度影响更温和

        # 根据客户类型微调基准分
        if "小白" in client_type:
            base_score += 2  # 对小白客户更宽容
        elif "蛮横" in client_type:
            base_score -= 3  # 对蛮横客户稍严格

        return {
            "overall_score": max(55, base_score),
            "scores": {
                "demand_mining": max(12, 15 - (difficulty - 3) * 1.5),
                "product_fit": max(12, 15 - (difficulty - 3) * 1.5),
                "objection_handling": max(11, 14 - (difficulty - 3) * 1.2),
                "communication": max(13, 16 - (difficulty - 3) * 1.2),
                "professional_knowledge": max(12, 15 - (difficulty - 3) * 1.2)
            },
            "strengths": [
                "基本沟通能力良好",
                "展现了服务客户的意愿",
                "对客户问题做出了积极回应",
                "具备基本的专业知识"
            ],
            "improvements": [
                "可以更深度挖掘客户需求",
                "产品推荐可以更个性化",
                "沟通表达可以更结构化",
                "可以更多使用数据支撑观点"
            ],
            "critical_errors": [],
            "positive_highlights": ["积极回应客户问题", "展现服务意识"],
            "suggested_phrases": [
                "尝试使用更多开放式提问了解客户深层需求",
                "在推荐产品时提供具体的数据支撑",
                "用更结构化的方式组织沟通内容",
                "针对客户特点提供更个性化的建议"
            ],
            "detailed_feedback": {
                "demand_mining": "基本需求了解到位，可以进一步挖掘隐性需求和建立完整客户画像",
                "product_fit": "产品推荐基本合理，匹配精度可以提升，建议更多个性化定制",
                "objection_handling": "对客户疑虑有所回应，处理技巧可以加强，建议更多使用数据支撑",
                "communication": "沟通表达清晰，可以更好引导对话节奏和建立信任关系",
                "professional_knowledge": "专业知识掌握良好，可以更多结合案例和数据说明"
            },
            "performance_level": "良好" if base_score >= 70 else "及格",
            "encouragement": "表现不错！继续努力，每一次对话都是进步的机会！"
        }

    def format_feedback(self, evaluation: Dict) -> str:
        """格式化反馈信息"""
        scores = evaluation.get('scores', {})
        detailed_feedback = evaluation.get('detailed_feedback', {})
        critical_errors = evaluation.get('critical_errors', [])
        positive_highlights = evaluation.get('positive_highlights', [])
        performance_level = evaluation.get('performance_level', '未知')
        encouragement = evaluation.get('encouragement', '继续加油！')

        # 根据分数设置表情
        score_emoji = "🔴" if evaluation['overall_score'] < 60 else "🟡" if evaluation['overall_score'] < 70 else "🟢" if \
        evaluation['overall_score'] < 85 else "⭐"

        feedback = f"""
## 📊 专业评估报告 {score_emoji}

### 综合评分：{evaluation['overall_score']}/100 · 等级：**{performance_level}**

**各维度评分：**
- 🎯 需求挖掘：{scores.get('demand_mining', 0)}/20
- 📈 产品匹配：{scores.get('product_fit', 0)}/20  
- 🛡️ 异议处理：{scores.get('objection_handling', 0)}/20
- 💬 沟通能力：{scores.get('communication', 0)}/20
- 🎓 专业知识：{scores.get('professional_knowledge', 0)}/20

### 🌟 亮点表现
{chr(10).join(['- ✅ ' + strength for strength in evaluation.get('strengths', [])])}

### 🔍 具体亮点
{chr(10).join(['- ✨ ' + highlight for highlight in positive_highlights]) if positive_highlights else "- 💡 展现了基本的专业素养"}

### ⚠️ 关键问题
{chr(10).join(['- ❌ ' + error for error in critical_errors]) if critical_errors else "- ✅ 未发现重大错误"}

### 📋 详细分析
**🎯 需求挖掘：** {detailed_feedback.get('demand_mining', '暂无详细反馈')}
**📈 产品匹配：** {detailed_feedback.get('product_fit', '暂无详细反馈')}
**🛡️ 异议处理：** {detailed_feedback.get('objection_handling', '暂无详细反馈')}
**💬 沟通能力：** {detailed_feedback.get('communication', '暂无详细反馈')}
**🎓 专业知识：** {detailed_feedback.get('professional_knowledge', '暂无详细反馈')}

### 🎯 改进建议  
{chr(10).join(['- 📝 ' + improvement for improvement in evaluation.get('improvements', [])])}

### 💬 话术提升
{chr(10).join(['- 🗣️ ' + phrase for phrase in evaluation.get('suggested_phrases', [])])}

### 💪 鼓励话语
**{encouragement}**

---
**评估标准：** 60分及格 · 70分良好 · 80分优秀 · 90分卓越
**评估理念：** 平衡评估，认可亮点，指导进步
        """

        return feedback