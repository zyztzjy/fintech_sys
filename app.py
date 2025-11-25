import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import datetime
from models.coach_agent import FinancialCoachAgent
from models.evaluator import SessionEvaluator
from utils.visualization import create_radar_dashboard, create_simple_dashboard, create_trend_analysis

# 页面配置
st.set_page_config(
    page_title="理财经理实战陪练系统",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


class FinancialCoachApp:
    def __init__(self):
        self.coach = FinancialCoachAgent()
        self.evaluator = SessionEvaluator()
        self.init_session_state()

    def init_session_state(self):
        """初始化会话状态"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'session_started' not in st.session_state:
            st.session_state.session_started = False
        if 'client_type' not in st.session_state:
            st.session_state.client_type = None
        if 'session_history' not in st.session_state:
            st.session_state.session_history = []
        if 'evaluation_data' not in st.session_state:
            st.session_state.evaluation_data = {}

    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.title("💰 理财经理陪练系统")
            st.markdown("---")

            # 客户类型选择
            st.subheader("选择客户类型")
            client_type = st.selectbox(
                "请选择要练习的客户类型:",
                ["小白型新手客户","稳健型中年客户", "进取型年轻客户", "保守型退休客户", "企业主客户", "白领上班族","蛮横型高净值客户"]
            )

            # 练习场景选择
            st.subheader("练习场景")
            scenario = st.selectbox(
                "选择练习场景:",
                ["新产品推荐", "客户需求挖掘", "异议处理", "资产配置建议", "风险教育"]
            )

            # 难度设置
            difficulty = st.slider("难度级别", 1, 5, 3)

            # 开始/结束会话按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✔️ 开始新会话", use_container_width=True):
                    self.start_new_session(client_type, scenario, difficulty)
            with col2:
                if st.button("❌️️ 结束会话", use_container_width=True):
                    self.end_session()

            st.markdown("---")

            # 历史会话统计
            if st.session_state.session_history:
                st.subheader("历史统计")
                total_sessions = len(st.session_state.session_history)

                # 安全地计算平均分
                scores = []
                for session in st.session_state.session_history:
                    # 检查评估数据是否存在且包含 overall_score
                    if (session.get('evaluation') and
                            isinstance(session['evaluation'], dict) and
                            'overall_score' in session['evaluation']):
                        scores.append(session['evaluation']['overall_score'])

                if scores:
                    avg_score = sum(scores) / len(scores)
                    st.metric("总练习次数", total_sessions)
                    st.metric("平均得分", f"{avg_score:.1f}")
                else:
                    st.metric("总练习次数", total_sessions)
                    st.metric("平均得分", "暂无")

    def start_new_session(self, client_type, scenario, difficulty):
        """开始新会话"""
        st.session_state.session_started = True
        st.session_state.client_type = client_type
        st.session_state.session_difficulty = difficulty  # 保存难度
        st.session_state.messages = []
        st.session_state.evaluation_data = {}

        # 添加欢迎消息
        welcome_msg = f"""
        开始新的陪练会话！
        - 客户类型: {client_type}
        - 练习场景: {scenario}  
        - 难度级别: {difficulty}/5

        请开始与客户对话吧！
        """
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def end_session(self):
        """结束当前会话"""
        if st.session_state.session_started:
            # 生成最终评估
            if st.session_state.messages:
                evaluation = self.evaluator.comprehensive_evaluation(
                    st.session_state.messages,
                    st.session_state.client_type,
                    st.session_state.get('session_difficulty', 3)  # 传递难度
                )

                # 确保评估数据格式正确
                if not isinstance(evaluation, dict):
                    evaluation = self.evaluator.get_default_evaluation()

                st.session_state.evaluation_data = evaluation

                # 保存到历史
                session_record = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "client_type": st.session_state.client_type,
                    "messages": st.session_state.messages,
                    "evaluation": evaluation,
                    "duration_minutes": self.calculate_session_duration()
                }
                st.session_state.session_history.append(session_record)

        st.session_state.session_started = False
        st.session_state.messages = []
        st.rerun()

    def calculate_session_duration(self):
        """计算会话时长"""
        if len(st.session_state.messages) >= 2:
            start_time = datetime.datetime.fromisoformat(st.session_state.messages[0]['timestamp'])
            end_time = datetime.datetime.fromisoformat(st.session_state.messages[-1]['timestamp'])
            return (end_time - start_time).total_seconds() / 60
        return 0

    def render_chat_interface(self):
        """渲染聊天界面"""
        st.header(f"💬 与{st.session_state.client_type}对话")

        # 聊天消息显示
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with st.chat_message("user", avatar="👨‍💼"):
                        st.markdown(message["content"])
                        st.caption(message.get("timestamp", ""))
                else:
                    with st.chat_message("assistant", avatar="👥"):
                        st.markdown(message["content"])
                        st.caption(message.get("timestamp", ""))

        # 聊天输入
        if st.session_state.session_started:
            if prompt := st.chat_input("请输入您的回复..."):
                # 添加用户消息
                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": datetime.datetime.now().isoformat()
                })

                # 检查是否请求反馈
                if "请求反馈" in prompt or "评估" in prompt:
                    evaluation = self.evaluator.comprehensive_evaluation(
                        st.session_state.messages,
                        st.session_state.client_type
                    )
                    st.session_state.evaluation_data = evaluation
                    feedback_msg = self.evaluator.format_feedback(evaluation)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": feedback_msg,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "is_feedback": True
                    })
                else:
                    # 获取AI回复
                    with st.spinner("客户正在思考..."):
                        ai_response = self.coach.get_response(
                            prompt,
                            st.session_state.messages,
                            st.session_state.client_type
                        )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.datetime.now().isoformat()
                    })

                st.rerun()

    def render_evaluation_dashboard(self):
        """渲染评估仪表板"""
        if st.session_state.evaluation_data:
            st.header("会话评估报告")

            evaluation = st.session_state.evaluation_data

            # 确保评估数据格式正确
            if not isinstance(evaluation, dict):
                st.error("评估数据格式错误")
                return

            # 使用默认值防止 KeyError
            overall_score = evaluation.get('overall_score', 0)
            scores = evaluation.get('scores', {})
            strengths = evaluation.get('strengths', [])
            improvements = evaluation.get('improvements', [])
            suggested_phrases = evaluation.get('suggested_phrases', [])

            # 关键指标
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            # 在 render_evaluation_dashboard 方法中修改指标显示
            with col1:
                st.metric("综合评分", f"{overall_score}/100")
            with col2:
                st.metric("需求挖掘", f"{scores.get('demand_mining', 0)}/20")
            with col3:
                st.metric("产品匹配", f"{scores.get('product_fit', 0)}/20")
            with col4:
                st.metric("沟通能力", f"{scores.get('communication', 0)}/20")
            with col5:
                st.metric("专业知识", f"{scores.get('professional_knowledge', 0)}/20")
            with col6:
                st.metric("异议处理", f"{scores.get('objection_handling', 0)}/20")
            # 可视化图表 - 使用新的简化版本

            # 额外显示雷达图
            st.subheader("能力维度雷达图")
            radar_fig = create_radar_dashboard(evaluation)
            st.plotly_chart(radar_fig, use_container_width=True)

            # 详细反馈
            st.subheader("详细分析")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🟢 亮点")
                for strength in strengths:
                    st.success(f"✅ {strength}")

            with col2:
                st.markdown("#### 🟡 改进建议")
                for improvement in improvements:
                    st.warning(f"📝 {improvement}")

            # 话术建议
            if suggested_phrases:
                st.markdown("#### 🗣️ 推荐话术")
                for example in suggested_phrases:
                    st.info(f"💬 {example}")

    def render_analytics(self):
        """渲染数据分析页面"""
        st.header("训练数据分析")

        if not st.session_state.session_history:
            st.info("暂无历史数据，请先完成一些练习会话。")
            return

        # 转换为DataFrame便于分析
        history_df = self.prepare_analytics_data()

        # 额外检查DataFrame是否为空
        if len(history_df) == 0:
            st.info("暂无有效的历史数据进行分析。")
            return

        # 整体趋势分析 - 使用新的折线图
        st.subheader("综合得分趋势")
        trend_fig = create_trend_analysis(history_df)
        st.plotly_chart(trend_fig, use_container_width=True)

        # 其他图表
        col1, col2 = st.columns(2)

        with col1:
            # 客户类型分布
            fig2 = px.pie(history_df, names='client_type',
                          title='客户类型分布')
            st.plotly_chart(fig2, use_container_width=True)


        # 详细数据表
        st.subheader("历史会话记录")
        st.dataframe(history_df[['session_date', 'client_type', 'overall_score',
                                 'duration_minutes']], use_container_width=True)

    def prepare_analytics_data(self):
        """准备分析数据"""
        data = []
        for i, session in enumerate(st.session_state.session_history):
            evaluation = session.get('evaluation', {})
            scores = evaluation.get('scores', {})

            data.append({
                'session_date': i + 1,  # 使用序号而不是日期，便于显示
                'client_type': session['client_type'],
                'overall_score': evaluation.get('overall_score', 0),
                'demand_mining': scores.get('demand_mining', 0),
                'product_fit': scores.get('product_fit', 0),
                'objection_handling': scores.get('objection_handling', 0),
                'communication': scores.get('communication', 0),
                'professional_knowledge': scores.get('professional_knowledge', 0),
                'duration_minutes': session.get('duration_minutes', 0)
            })

        # 如果数据为空，返回空的DataFrame
        if not data:
            return pd.DataFrame(columns=['session_date', 'client_type', 'overall_score',
                                         'demand_mining', 'product_fit', 'objection_handling',
                                         'communication', 'professional_knowledge', 'duration_minutes'])

        return pd.DataFrame(data)



    def run(self):
        """运行主应用"""
        self.render_sidebar()

        # 主内容区域
        tab1, tab2, tab3 = st.tabs(["💬 实时陪练", "📊 会话评估", "📈 成长分析"])

        with tab1:
            if st.session_state.session_started:
                self.render_chat_interface()
            else:
                st.info("👈 请在侧边栏选择客户类型并开始新会话")

        with tab2:
            self.render_evaluation_dashboard()

        with tab3:
            self.render_analytics()


# 运行应用
if __name__ == "__main__":
    app = FinancialCoachApp()
    app.run()