import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict
import plotly.colors as colors


def create_performance_dashboard(evaluation: Dict):
    """创建专业性能仪表板"""

    # 定义配色方案
    color_scale = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    professional_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    categories = ['需求挖掘', '产品匹配', '异议处理', '沟通能力', '专业知识']
    scores = [
        evaluation.get('scores', {}).get('demand_mining', 0),
        evaluation.get('scores', {}).get('product_fit', 0),
        evaluation.get('scores', {}).get('objection_handling', 0),
        evaluation.get('scores', {}).get('communication', 0),
        evaluation.get('scores', {}).get('professional_knowledge', 0)
    ]

    max_scores = [25, 25, 20, 15, 15]  # 各维度满分

    # 创建子图布局
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('能力维度雷达图', '得分分布对比', '综合评分仪表',
                        '完成度分析', '能力平衡性', '绩效等级'),
        specs=[[{"type": "scatterpolar"}, {"type": "bar"}, {"type": "indicator"}],
               [{"type": "bar"}, {"type": "pie"}, {"type": "indicator"}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # 1. 雷达图
    fig.add_trace(
        go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.4)',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=4, color='#1f77b4'),
            name='能力维度',
            hovertemplate='<b>%{theta}</b><br>得分: %{r}/%{customdata}<extra></extra>',
            customdata=max_scores + [max_scores[0]]
        ),
        row=1, col=1
    )

    # 2. 得分分布柱状图
    fig.add_trace(
        go.Bar(
            x=categories,
            y=scores,
            marker_color=professional_colors,
            marker_line=dict(color='rgba(0,0,0,0.4)', width=1),
            text=[f"{score}/{max_score}" for score, max_score in zip(scores, max_scores)],
            textposition='auto',
            textfont=dict(color='white', size=10),
            hovertemplate='<b>%{x}</b><br>得分: %{y}/%{customdata}<extra></extra>',
            customdata=max_scores
        ),
        row=1, col=2
    )

    # 3. 综合评分仪表
    overall_score = evaluation.get('overall_score', 0)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "综合评分", 'font': {'size': 16}},
            number={'font': {'size': 24, 'color': '#1f77b4'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#1f77b4", 'thickness': 0.8},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 60], 'color': '#FF6B6B'},
                    {'range': [60, 80], 'color': '#FFE66D'},
                    {'range': [80, 100], 'color': '#6BCF7F'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=3
    )

    # 4. 完成度分析
    completion_rates = [score / max_score * 100 for score, max_score in zip(scores, max_scores)]
    fig.add_trace(
        go.Bar(
            x=categories,
            y=completion_rates,
            marker_color=completion_rates,
            marker_colorscale='Viridis',
            text=[f"{rate:.1f}%" for rate in completion_rates],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>完成度: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )

    # 5. 能力平衡性饼图
    total_score = sum(scores)
    if total_score > 0:
        score_percentages = [score / total_score * 100 for score in scores]
    else:
        score_percentages = [0] * len(scores)

    fig.add_trace(
        go.Pie(
            labels=categories,
            values=score_percentages,
            marker_colors=professional_colors,
            textinfo='label+percent',
            insidetextorientation='radial',
            hole=0.4,
            hoverinfo='label+value+percent',
            textfont=dict(size=10)
        ),
        row=2, col=2
    )

    # 6. 绩效等级指示器
    performance_level = evaluation.get('performance_level', '未知')
    level_colors = {
        '不及格': '#FF6B6B',
        '及格': '#FFE66D',
        '良好': '#6BCF7F',
        '优秀': '#4ECDC4',
        '卓越': '#45B7D1'
    }
    level_color = level_colors.get(performance_level, '#999999')

    fig.add_trace(
        go.Indicator(
            mode="number+gauge",
            value=overall_score,
            number={'font': {'size': 20, 'color': level_color}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"绩效等级: {performance_level}", 'font': {'size': 14}},
            gauge={
                'shape': "bullet",
                'axis': {'range': [0, 100]},
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 0.75,
                    'value': overall_score
                },
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(255, 107, 107, 0.3)'},
                    {'range': [60, 80], 'color': 'rgba(255, 230, 109, 0.3)'},
                    {'range': [80, 100], 'color': 'rgba(107, 207, 127, 0.3)'}
                ],
                'bar': {'color': level_color, 'thickness': 0.8}
            }
        ),
        row=2, col=3
    )

    # 更新布局
    fig.update_layout(
        height=700,
        showlegend=False,
        title_text="💰 理财经理能力评估仪表板",
        title_x=0.5,
        title_font=dict(size=24, color='#2c3e50'),
        paper_bgcolor='rgba(248,249,250,1)',
        plot_bgcolor='rgba(248,249,250,1)',
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50")
    )

    # 更新子图标题样式
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12, color='#2c3e50')

    return fig


def create_simple_dashboard(evaluation: Dict):
    """创建简化但专业的性能仪表板"""

    categories = ['需求挖掘', '产品匹配', '异议处理', '沟通能力', '专业知识']
    scores = [
        evaluation.get('scores', {}).get('demand_mining', 0),
        evaluation.get('scores', {}).get('product_fit', 0),
        evaluation.get('scores', {}).get('objection_handling', 0),
        evaluation.get('scores', {}).get('communication', 0),
        evaluation.get('scores', {}).get('professional_knowledge', 0)
    ]

    # 所有维度满分都改为20
    max_scores = [20, 20, 20, 20, 20]
    overall_score = evaluation.get('overall_score', 0)

    # 创建3个主要图表
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('能力维度得分', '综合评分', '能力完成度', ''),
        specs=[[{"type": "bar"}, {"type": "indicator"}],
               [{"type": "scatterpolar"}, {"type": "bar"}]],
        vertical_spacing=0.15
    )

    # 1. 能力维度柱状图
    fig.add_trace(
        go.Bar(
            x=categories,
            y=scores,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            marker_line=dict(color='rgba(0,0,0,0.4)', width=1),
            text=[f"{score}/{max_score}" for score, max_score in zip(scores, max_scores)],
            textposition='auto',
            textfont=dict(color='white', size=10),
            hovertemplate='<b>%{x}</b><br>得分: %{y}/%{customdata}<extra></extra>',
            customdata=max_scores
        ),
        row=1, col=1
    )

    # 2. 综合评分仪表
    performance_level = evaluation.get('performance_level', '未知')
    level_colors = {
        '不及格': '#FF6B6B',
        '及格': '#FFE66D',
        '良好': '#6BCF7F',
        '优秀': '#4ECDC4',
        '卓越': '#45B7D1'
    }
    level_color = level_colors.get(performance_level, '#999999')

    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"综合评分<br><span style='font-size:0.8em;color:{level_color}'>{performance_level}</span>",
                   'font': {'size': 14}},
            number={'font': {'size': 20, 'color': level_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': level_color},
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(255, 107, 107, 0.3)'},
                    {'range': [60, 80], 'color': 'rgba(255, 230, 109, 0.3)'},
                    {'range': [80, 100], 'color': 'rgba(107, 207, 127, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.8,
                    'value': 90
                }
            }
        ),
        row=1, col=2
    )

    # 3. 雷达图
    fig.add_trace(
        go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(78, 205, 196, 0.3)',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=4),
            name='能力维度',
            hovertemplate='<b>%{theta}</b><br>得分: %{r}/%{customdata}<extra></extra>',
            customdata=max_scores + [max_scores[0]]
        ),
        row=2, col=1
    )

    # 4. 完成度水平条
    completion_rates = [score / max_score * 100 for score, max_score in zip(scores, max_scores)]
    fig.add_trace(
        go.Bar(
            y=categories,
            x=completion_rates,
            orientation='h',
            marker_color=completion_rates,
            marker_colorscale='Viridis',
            text=[f"{rate:.0f}%" for rate in completion_rates],
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=10),
            hovertemplate='<b>%{y}</b><br>完成度: %{x:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="能力评估概览",
        title_x=0.5,
        paper_bgcolor='rgba(248,249,250,1)',
        font=dict(family="Arial, sans-serif")
    )

    return fig


def create_radar_dashboard(evaluation: Dict):
    """创建专业雷达图"""

    categories = ['需求挖掘', '产品匹配', '异议处理', '沟通能力', '专业知识']
    scores = [
        evaluation.get('scores', {}).get('demand_mining', 0),
        evaluation.get('scores', {}).get('product_fit', 0),
        evaluation.get('scores', {}).get('objection_handling', 0),
        evaluation.get('scores', {}).get('communication', 0),
        evaluation.get('scores', {}).get('professional_knowledge', 0)
    ]

    # 所有维度满分都改为20
    max_scores = [20, 20, 20, 20, 20]

    fig = go.Figure()

    # 添加满分参考区域
    fig.add_trace(go.Scatterpolar(
        r=max_scores + [max_scores[0]],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='rgba(200,200,200,0.5)', width=1, dash='dash'),
        name='满分参考',
        hoverinfo='skip'
    ))

    # 添加实际得分区域
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.4)',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4, color='#1f77b4'),
        name='实际得分',
        hovertemplate='<b>%{theta}</b><br>得分: %{r}/%{customdata}<extra></extra>',
        customdata=max_scores + [max_scores[0]]
    ))

    # 添加目标线（80%完成度）
    target_scores = [max_score * 0.8 for max_score in max_scores]
    fig.add_trace(go.Scatterpolar(
        r=target_scores + [target_scores[0]],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='rgba(255, 107, 107, 0.7)', width=1, dash='dot'),
        name='目标线(80%)',
        hoverinfo='skip'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max_scores)],
                tickfont=dict(size=10),
                gridcolor='rgba(200,200,200,0.5)',
                linecolor='rgba(200,200,200,0.8)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
                gridcolor='rgba(200,200,200,0.5)',
                linecolor='rgba(200,200,200,0.8)',
                rotation=90
            ),
            bgcolor='rgba(248,249,250,0.5)'
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        title="能力维度雷达分析",
        title_x=0.5,
        title_font=dict(size=16),
        height=450,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='white'
    )

    return fig


def create_trend_analysis(history_data):
    """创建专业的综合得分趋势折线图"""
    # 正确检查 DataFrame 是否为空
    if history_data is None or len(history_data) == 0:
        # 返回一个友好的空状态图表
        fig = go.Figure()
        fig.add_annotation(
            text="📊 暂无足够的历史数据进行分析<br>请完成更多练习会话",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="综合得分趋势分析",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            paper_bgcolor='rgba(248,249,250,1)'
        )
        return fig

    # 确保数据按时间排序
    history_data = history_data.sort_values('session_date')

    # 计算关键指标
    current_score = history_data['overall_score'].iloc[-1]
    max_score = history_data['overall_score'].max()
    min_score = history_data['overall_score'].min()
    avg_score = history_data['overall_score'].mean()

    # 计算进步情况
    if len(history_data) > 1:
        first_score = history_data['overall_score'].iloc[0]
        improvement = current_score - first_score
        improvement_percent = (improvement / first_score * 100) if first_score > 0 else 0
    else:
        improvement = 0
        improvement_percent = 0

    # 创建简洁的折线图
    fig = go.Figure()

    # 1. 主趋势线 - 综合得分折线
    fig.add_trace(
        go.Scatter(
            x=history_data['session_date'],
            y=history_data['overall_score'],
            mode='lines+markers',
            name='综合得分',
            line=dict(color='#1f77b4', width=4),
            marker=dict(
                size=8,
                color='#1f77b4',
                line=dict(width=2, color='white')
            ),
            hovertemplate=(
                    '<b>第%{x}次练习</b><br>' +
                    '综合得分: <b>%{y}</b>/100<br>' +
                    '<extra></extra>'
            )
        )
    )

    # 2. 移动平均线 (3期)
    if len(history_data) >= 3:
        moving_avg = history_data['overall_score'].rolling(window=3, min_periods=1).mean()
        fig.add_trace(
            go.Scatter(
                x=history_data['session_date'],
                y=moving_avg,
                mode='lines',
                name='移动平均(3期)',
                line=dict(color='#ff7f0e', width=3, dash='dash'),
                hovertemplate='移动平均: <b>%{y:.1f}</b>/100<extra></extra>'
            )
        )

    # 3. 添加目标区域背景色
    # 优秀区域 (80-100)
    fig.add_hrect(
        y0=80, y1=100,
        fillcolor="rgba(107, 207, 127, 0.2)",
        line_width=0,
        annotation_text="优秀区域",
        annotation_position="top left"
    )

    # 良好区域 (60-80)
    fig.add_hrect(
        y0=60, y1=80,
        fillcolor="rgba(255, 230, 109, 0.2)",
        line_width=0,
        annotation_text="良好区域",
        annotation_position="top left"
    )

    # 不及格区域 (0-60)
    fig.add_hrect(
        y0=0, y1=60,
        fillcolor="rgba(255, 107, 107, 0.1)",
        line_width=0,
        annotation_text="需改进区域",
        annotation_position="top left"
    )

    # 4. 添加关键参考线
    fig.add_hline(y=60, line_dash="dot", line_color="#FF6B6B",
                  annotation_text="及格线", annotation_position="bottom right")
    fig.add_hline(y=80, line_dash="dot", line_color="#4ECDC4",
                  annotation_text="优秀线", annotation_position="bottom right")

    # 更新布局
    fig.update_layout(
        height=500,
        title=dict(
            text=f"📈 综合得分趋势分析 | 当前得分: {current_score}分 | 进步: {improvement:+.1f}分 ({improvement_percent:+.1f}%)",
            x=0.5,
            font=dict(size=18, color='#2c3e50')
        ),
        xaxis_title="练习次数",
        yaxis_title="综合得分",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        paper_bgcolor='rgba(248,249,250,1)',
        plot_bgcolor='rgba(248,249,250,1)',
        font=dict(family="Arial, sans-serif"),
        hovermode='x unified'
    )

    # 设置y轴范围
    fig.update_yaxes(range=[0, 100])

    return fig


def create_performance_metrics(history_data):
    """创建关键绩效指标卡片"""
    if not history_data or len(history_data) == 0:
        return None

    current_score = history_data['overall_score'].iloc[-1]
    max_score = history_data['overall_score'].max()
    min_score = history_data['overall_score'].min()
    avg_score = history_data['overall_score'].mean()
    total_sessions = len(history_data)

    # 计算连续进步次数
    if len(history_data) > 1:
        improvements = history_data['overall_score'].diff().fillna(0)
        consecutive_improvements = 0
        for change in improvements.iloc[::-1]:
            if change > 0:
                consecutive_improvements += 1
            else:
                break
    else:
        consecutive_improvements = 0

    # 计算稳定性（标准差）
    stability = history_data['overall_score'].std()

    # 创建指标卡片
    metrics_fig = make_subplots(
        rows=1, cols=4,
        specs=[[{"type": "indicator"}, {"type": "indicator"},
                {"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=('当前得分', '历史最高', '平均表现', '进步 streak')
    )

    # 当前得分
    metrics_fig.add_trace(
        go.Indicator(
            mode="number",
            value=current_score,
            number=dict(
                font=dict(size=24, color='#1f77b4'),
                suffix="/100"
            ),
            title=dict(text="当前得分", font=dict(size=14))
        ),
        row=1, col=1
    )

    # 历史最高
    metrics_fig.add_trace(
        go.Indicator(
            mode="number",
            value=max_score,
            number=dict(
                font=dict(size=24, color='#2ca02c'),
                suffix="/100"
            ),
            title=dict(text="历史最高", font=dict(size=14))
        ),
        row=1, col=2
    )

    # 平均表现
    metrics_fig.add_trace(
        go.Indicator(
            mode="number",
            value=avg_score,
            number=dict(
                font=dict(size=24, color='#ff7f0e'),
                suffix="/100"
            ),
            title=dict(text="平均表现", font=dict(size=14))
        ),
        row=1, col=3
    )

    # 连续进步
    metrics_fig.add_trace(
        go.Indicator(
            mode="number",
            value=consecutive_improvements,
            number=dict(
                font=dict(size=24, color='#9467bd'),
                suffix="次"
            ),
            title=dict(text="连续进步", font=dict(size=14))
        ),
        row=1, col=4
    )

    metrics_fig.update_layout(
        height=150,
        paper_bgcolor='rgba(248,249,250,1)',
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return metrics_fig


def create_performance_breakdown(history_data):
    """创建能力维度趋势分解"""
    if not history_data or len(history_data) < 2:
        return None

    # 提取各维度得分
    dimensions = ['demand_mining', 'product_fit', 'objection_handling', 'communication', 'professional_knowledge']
    dimension_names = ['需求挖掘', '产品匹配', '异议处理', '沟通能力', '专业知识']

    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (dim, name) in enumerate(zip(dimensions, dimension_names)):
        # 计算每个维度的趋势线
        scores = history_data[dim] if dim in history_data.columns else [0] * len(history_data)

        fig.add_trace(
            go.Scatter(
                x=history_data['session_date'],
                y=scores,
                mode='lines+markers',
                name=name,
                line=dict(color=colors[i], width=3),
                marker=dict(size=6),
                hovertemplate=f'<b>{name}</b><br>得分: %{{y}}<br>时间: %{{x}}<extra></extra>'
            )
        )

    fig.update_layout(
        title="📊 能力维度趋势分解",
        xaxis_title="练习时间",
        yaxis_title="维度得分",
        height=400,
        paper_bgcolor='rgba(248,249,250,1)',
        plot_bgcolor='rgba(248,249,250,1)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def create_comparison_chart(current_eval, previous_eval=None):
    """创建对比分析图表"""
    categories = ['需求挖掘', '产品匹配', '异议处理', '沟通能力', '专业知识']

    current_scores = [
        current_eval.get('scores', {}).get('demand_mining', 0),
        current_eval.get('scores', {}).get('product_fit', 0),
        current_eval.get('scores', {}).get('objection_handling', 0),
        current_eval.get('scores', {}).get('communication', 0),
        current_eval.get('scores', {}).get('professional_knowledge', 0)
    ]

    fig = go.Figure()

    # 当前得分
    fig.add_trace(go.Bar(
        name='当前表现',
        x=categories,
        y=current_scores,
        marker_color='#1f77b4',
        text=current_scores,
        textposition='auto',
    ))

    # 如果有历史数据，添加对比
    if previous_eval:
        previous_scores = [
            previous_eval.get('scores', {}).get('demand_mining', 0),
            previous_eval.get('scores', {}).get('product_fit', 0),
            previous_eval.get('scores', {}).get('objection_handling', 0),
            previous_eval.get('scores', {}).get('communication', 0),
            previous_eval.get('scores', {}).get('professional_knowledge', 0)
        ]

        fig.add_trace(go.Bar(
            name='上次表现',
            x=categories,
            y=previous_scores,
            marker_color='#ff7f0e',
            text=previous_scores,
            textposition='auto',
        ))

    fig.update_layout(
        title='能力维度对比分析',
        barmode='group',
        xaxis_tickangle=-45,
        paper_bgcolor='rgba(248,249,250,1)',
        plot_bgcolor='rgba(248,249,250,1)'
    )

    return fig