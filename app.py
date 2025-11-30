from member_data import DAILY_DATA,daily_speeches

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta, date
from pathlib import Path
import warnings

# 强化IP质感：字体组合+全局样式统一
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Sans+SC:wght@400;600;800&family=Inter:wght@500;700;900&display=swap" rel="stylesheet">
    <style>
        /* 全局基础样式：统一IP质感 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        /* 中文主体字体：Noto Sans SC（清晰专业）+ 马善政（手写感点缀） */
        body, div, p, span, table, input {
            font-family: 'Noto Sans SC', sans-serif;
            font-weight: 500;
            line-height: 1.6;
            color: #2d3748; /* 深灰主色，专业不压抑 */
        }
        /* 标题专属字体：马善政（手写感，强化成长温度）+ 加粗强调 */
        h1, h2, h3, h4, .title {
            font-family: 'Ma Shan Zheng', 'Noto Sans SC', cursive;
            font-weight: 800;
            color: #2e7d32; /* 主题绿，呼应成长实验室🌱 */
            letter-spacing: 0.5px;
            text-shadow: 0 2px 4px rgba(46, 125, 50, 0.1);
        }
        /* 英文/数字专属字体：Inter（现代简洁，提升科技感）+ 深绿配色（清晰易读） */
        .en, .num, .score, .rank {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1b5e20; /* 深绿色，呼应主题且对比度更高，解决看不清问题 */
        }
        /* 强调文本样式（标签、重点数据） */
        .highlight {
            font-family: 'Noto Sans SC', sans-serif;
            font-weight: 800;
            color: #ff7a45; /* 暖橙 accent色，吸睛不刺眼 */
        }
        /* 卡片类文本优化 */
        .card-text {
            font-size: 1rem;
            color: #4a5568;
        }
        .card-title {
            font-family: 'Ma Shan Zheng', 'Noto Sans SC', cursive;
            font-size: 1.2rem;
            color: #2e7d32;
        }
        /* 确保表格/输入框中的数字也能继承样式 */
        table .num, input[type="number"] {
            color: #1b5e20 !important;
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)
warnings.filterwarnings("ignore")
# ---------------------- 核心配置（用户后续需填写的内容）----------------------
# 1. 本月新成员名单（用户稍后填写，格式：["成员1", "成员2", ...]）
THIS_MONTH_NEW_MEMBERS = ["李韫","Libby","陈庚","阿龙","二月","七公主","匆匆","拈指花开","姜姜好","自由之花","阿成","浅夏"]

# 2. 复盘质量分（用户稍后填写，格式：{成员姓名: 最新质量分, ...}，10分制）
#REVIEW_QUALITY_SCORES = {}  # 示例：{"光影": 8.5, "小妮": 9.2, "小马哥": 7.8}


# 3. 被点赞数（用户稍后填写，格式：{成员姓名: 点赞数, ...}）
LIKE_COUNTS = {}  # 示例：{"光影": 25, "小妮": 32, "小马哥": 18}

# 4. 成员首次复盘信息（用户稍后补充，格式：{成员姓名: {"首次日期": "2025-11-01", "首次质量分": 6.5}, ...}）
FIRST_REVIEW_INFO = {}  # 示例：{"新成员A": {"首次日期": "2025-11-05", "首次质量分": 6.0}}

# ---------------------- 基础配置 ----------------------
# 起始日期：2025年7月7日
start_date = date(2025, 7, 7)
# 今日日期（本地日期，自动获取）
today = datetime.now().date()
# 计算天数差
days_passed = max(0, (today - start_date).days)
# 本月时间范围（用于黑马筛选）
this_month_start = date(today.year, today.month, 1)
this_month_end = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year + 1,
                                                                                                        1,
                                                                                                        1) - timedelta(days=1)

# ---------------------- 基础配置（原有配置不变）----------------------
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(
    page_title="成长实验室 · 复盘成长",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


def process_daily_data():
    """直接处理DAILY_DATA为DataFrame，不依赖外部文件
    修复：列名校验 + 数据类型转换 + 空值处理，解决groupby求和报错
    新增：统计每个成员的主持次数并合并到数据中
    """
    # 1. 基础数据转换 & 空值过滤
    df = pd.DataFrame(DAILY_DATA)
    if df.empty:
        raise ValueError("DAILY_DATA 为空，请检查数据来源")

    # 2. 核心修复1：强制校验/转换关键列（避免列名错误）
    required_cols = ["date_str", "member", "is_participate", "host"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"DAILY_DATA 缺少必要列：{col}")

    # 3. 转换日期格式（统一为date对象）
    df["日期"] = pd.to_datetime(df["date_str"], errors="coerce").dt.date  # 错误日期转为NaT
    df = df.dropna(subset=["日期"])  # 过滤无效日期行

    # 4. 提取每日主持人（每个日期的第一个非空host）
    def get_daily_host(group):
        hosts = group["host"].dropna().unique()
        return hosts[0] if len(hosts) > 0 else "无"

    daily_hosts = df.groupby("日期").apply(get_daily_host).to_dict()  # {日期: 主持人}
    df["主持人"] = df["日期"].map(daily_hosts)

    # 5. 核心修复2：重命名列 + 确保"是否参与"为数值类型
    df = df.rename(columns={
        "member": "成员姓名",
        "is_participate": "是否参与",  # 确保列名统一
        "review": "微复盘"
    })
    # 强制转换"是否参与"为整数（处理布尔值/字符串等异常类型）
    df["是否参与"] = pd.to_numeric(df["是否参与"], errors="coerce").fillna(0).astype(int)

    # 6. 统计每个成员的主持次数（核心新增）
    # 步骤1：将每日主持人映射表转为DataFrame，排除"无"主持人
    host_df = pd.DataFrame({
        "日期": list(daily_hosts.keys()),
        "成员姓名": list(daily_hosts.values())
    })
    host_df = host_df[host_df["成员姓名"] != "无"]  # 过滤无效主持人

    # 步骤2：统计每个成员的主持次数
    host_counts = host_df.groupby("成员姓名").size().reset_index(name="主持次数")

    # 7. 核心修复3：统计参与次数（确保列存在且为数值）
    participation_counts = df.groupby("成员姓名")["是否参与"].sum().reset_index()
    participation_counts.rename(columns={"是否参与": "参与次数"}, inplace=True)

    # 8. 筛选最终列 + 合并数据
    df = df[["日期", "成员姓名", "是否参与", "主持人", "微复盘"]]
    # 合并参与次数 + 主持次数（左连接，未参与/未主持的填充0）
    df = df.merge(participation_counts, on="成员姓名", how="left")
    df = df.merge(host_counts, on="成员姓名", how="left")

    # 9. 空值填充（未主持/未参与的成员设为0）
    df["参与次数"] = df["参与次数"].fillna(0).astype(int)
    df["主持次数"] = df["主持次数"].fillna(0).astype(int)

    return df

# 直接处理数据，不读写CSV
df = process_daily_data()

all_members = list(set(df['成员姓名'].tolist() + THIS_MONTH_NEW_MEMBERS))
REVIEW_QUALITY_SCORES = {member: 6 for member in all_members}
# 初始化首次复盘信息中的质量分为6分
for member in all_members:
    if member not in FIRST_REVIEW_INFO:
        # 假设首次日期为系统起始日期或成员首次出现日期
        first_date = start_date.strftime("%Y-%m-%d")
        FIRST_REVIEW_INFO[member] = {"首次日期": first_date, "首次质量分": 6}
    else:
        FIRST_REVIEW_INFO[member]["首次质量分"] = 6


# 在现有代码的基础配置部分添加以下数据结构
# ---------------------- 新增：评分与点赞数据存储 ----------------------
# 存储格式: {日期: {成员: {评分: score, 点赞: [被点赞成员列表]}}}
if 'review_data' not in st.session_state:
    st.session_state.review_data = {}

# 获取所有成员列表（从现有数据中提取）
all_members = list(set(df['成员姓名'].tolist() + THIS_MONTH_NEW_MEMBERS))
all_members.sort()

# ---------------------- 第一步：定义用户专属密码（管理员提前分配）----------------------
# 格式：{成员姓名: 专属密码}，建议密码统一为6位数字或自定义，由管理员分发给成员
USER_PASSWORD = {
    "张三": "123456",
    "李四": "654321",
    "王五": "888888",
    # 请补充所有 all_members 中的成员及对应密码
}

def render_daily_review_interface():
    st.markdown("### 📝 今日复盘互动")

    # 获取当前日期字符串
    today_str = datetime.now().date().strftime("%Y-%m-%d")

    # 1. 选择当前用户（仅展示姓名，需后续验证）
    current_user = st.selectbox("选择你的名字", all_members)

    # 2. 身份验证：输入专属密码
    password = st.text_input(
        f"请输入 {current_user} 的专属密码",
        type="password",  # 密码隐藏输入
        placeholder="输入后点击验证"
    )

    # 验证按钮（单独验证，避免频繁校验）
    is_authenticated = False
    if st.button("验证身份"):
        # 检查密码是否匹配（忽略大小写，可选）
        if USER_PASSWORD.get(current_user) == password.strip():
            is_authenticated = True
            st.success(f"身份验证通过！欢迎 {current_user}～")
        else:
            st.error("密码错误！请输入正确的专属密码（联系管理员获取）")

    # 未验证通过，不显示后续内容
    if not is_authenticated:
        return

    # 3. 检查是否已提交（验证通过后再校验提交状态）
    has_submitted = False
    if today_str in st.session_state.review_data:
        if current_user in st.session_state.review_data[today_str]:
            has_submitted = True

    if has_submitted:
        st.info("你今天已经提交过复盘评分和点赞啦！明天再来吧～")
        # 显示已提交的信息
        submitted_data = st.session_state.review_data[today_str][current_user]
        st.write(f"你的自评分数：{submitted_data['评分']}分")
        st.write(f"你点赞的成员：{', '.join(submitted_data['点赞'])}")
        return

    # 4. 自评质量分选择（6-10分）
    score = st.radio(
        "请为你的今日复盘质量评分",
        options=[6, 7, 8, 9, 10],
        format_func=lambda x: f"{x}分"
    )

    # 5. 给其他用户点赞（可多选，限制1-3位）
    liked_members = st.multiselect(
        "请选择你想点赞的成员（可多选，最少1位，最多3位）",
        options=[m for m in all_members if m != current_user],  # 不能给自己点赞
        max_selections=3
    )

    # 6. 提交按钮（含点赞数量校验）
    if st.button("提交", type="primary"):
        if len(liked_members) == 0:
            st.error("请至少选择1位成员进行点赞！")
        else:
            # 初始化数据结构
            if today_str not in st.session_state.review_data:
                st.session_state.review_data[today_str] = {}

            # 保存数据（绑定验证通过的用户）
            st.session_state.review_data[today_str][current_user] = {
                "评分": score,
                "点赞": liked_members
            }

            st.success("提交成功！感谢你的参与～")

            # 数据持久化
            import json
            with open("review_data.json", "w", encoding="utf-8") as f:
                json.dump(st.session_state.review_data, f, ensure_ascii=False, indent=2)

# ---------------------- 主页面：顶部天数显示（原有不变）----------------------
st.markdown(f"""
    <div class='day-count-title'>
        复盘实验室第
        <span class='day-count-number'>{days_passed}</span>
        天
    </div>
""", unsafe_allow_html=True)

# ---------------------- 主页面：头部信息（原有不变）----------------------
st.markdown("<h1 class='warm-title'>✨ 公益复盘群 · 成长记录</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B9093; margin-bottom: 2rem;'>（可在左上方选择时间范围）记录参与情况，留存成长足迹～</p>", unsafe_allow_html=True)

# ---------------------- 侧边栏（原有不变）----------------------
with st.sidebar:
    st.markdown("<h3 style='color: #FF7A45; margin: 1rem 0;'>📅 周期筛选</h3>", unsafe_allow_html=True)
    period_type = st.radio(
        "选择统计周期",
        options=["本周", "上周", "月度"],
        index=0,
        key="period_type"
    )
    today_sidebar = datetime.now().date()
    if period_type == "本周":
        monday = today_sidebar - timedelta(days=today_sidebar.weekday())
        start_date = monday
        end_date = today_sidebar
    elif period_type == "上周":
        last_monday = today_sidebar - timedelta(days=today_sidebar.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_date = last_monday
        end_date = last_sunday
    else:
        selected_month = st.date_input("选择月份", value=today_sidebar).replace(day=1)
        if selected_month.month == 12:
            next_month = selected_month.replace(year=selected_month.year + 1, month=1)
        else:
            next_month = selected_month.replace(month=selected_month.month + 1)
        start_date = selected_month
        if selected_month.month == today_sidebar.month and selected_month.year == today_sidebar.year:
            end_date = today_sidebar
        else:
            end_date = next_month - timedelta(days=1)

    st.markdown(f"""
        <p style='color: #6B9093; margin: 1rem 0;'>
        当前筛选：{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}
        </p>
    """, unsafe_allow_html=True)

    if st.button("🔄 刷新数据", type="primary"):
        df = init_data()
        df["日期"] = pd.to_datetime(df["日期"]).dt.date
        df["主持人"] = df["主持人"].fillna("无").astype(str).str.strip()
        st.success("数据已刷新！")

    st.markdown("---")
    st.markdown("<p style='color: #6B9093; font-size: 0.9rem;'>🌱 公益复盘群成长记录平台</p>", unsafe_allow_html=True)


# ---------------------- 新增：本月黑马计算函数 ----------------------
def get_this_month_dark_horse(metrics_df):
    """本月黑马：本月新成员中综合实力分最高的前六名成员（精致卡片展示，修复HTML渲染）
    新增：主持次数权重占30%，调整权重分配：参与次数0.25、复盘质量0.35、被点赞数0.1、主持次数0.3
    修复：DataFrame 误用字典.get() 方法的报错
    """
    # 先定义 THIS_MONTH_NEW_MEMBERS（若未定义，需补充，示例值如下）
    global THIS_MONTH_NEW_MEMBERS
    if 'THIS_MONTH_NEW_MEMBERS' not in globals():
        THIS_MONTH_NEW_MEMBERS = []  # 实际使用时替换为真实新成员列表

    if not THIS_MONTH_NEW_MEMBERS:
        return '<div style="background: #f8f9fa; border-radius: 12px; padding: 2rem; text-align: center; border: 1px solid #eee; margin: 1rem 0;"><span style="color: #6c757d; font-size: 1.1rem;">暂无（请补充本月新成员名单）</span></div>'

    # 筛选本月新成员数据（先校验列存在性）
    if "是否本月新成员" not in metrics_df.columns:
        return '<div style="background: #f8f9fa; border-radius: 12px; padding: 2rem; text-align: center; border: 1px solid #eee; margin: 1rem 0;"><span style="color: #6c757d; font-size: 1.1rem;">暂无（数据缺少「是否本月新成员」列）</span></div>'

    new_member_df = metrics_df[metrics_df["是否本月新成员"]].copy()
    if len(new_member_df) == 0:
        return '<div style="background: #f8f9fa; border-radius: 12px; padding: 2rem; text-align: center; border: 1px solid #eee; margin: 1rem 0;"><span style="color: #6c757d; font-size: 1.1rem;">暂无（新成员暂无参与记录）</span></div>'

    # ========== 1. 空值填充 + 列存在性校验（核心修复） ==========
    # 基础列填充
    new_member_df["参与次数"] = new_member_df["参与次数"].fillna(0)
    new_member_df["复盘质量分"] = new_member_df["复盘质量分"].fillna(0)

    #st.write("DataFrame list is:", new_member_df.columns.tolist())

    new_member_df["被点赞数"] = new_member_df["被点赞数"].fillna(0)

    # 修复：DataFrame 列读取（替代字典.get()）
    if "主持次数" in new_member_df.columns:
        new_member_df["主持次数"] = new_member_df["主持次数"].fillna(0)
    else:
        new_member_df["主持次数"] = 0  # 无该列则默认0

    # ========== 2. 指标标准化 ==========
    # 参与次数标准化
    max_participate = new_member_df["参与次数"].max() if new_member_df["参与次数"].max() > 0 else 1
    new_member_df["参与次数标准化"] = (new_member_df["参与次数"] / max_participate * 10).round(2)

    # 复盘质量分标准化
    max_quality = new_member_df["复盘质量分"].max() if new_member_df["复盘质量分"].max() > 0 else 1
    new_member_df["质量分标准化"] = (new_member_df["复盘质量分"] / max_quality * 10).round(2)

    # 被点赞数标准化
    max_like = new_member_df["被点赞数"].max() if new_member_df["被点赞数"].max() > 0 else 1
    new_member_df["点赞数标准化"] = (new_member_df["被点赞数"] / max_like * 10).round(2)

    # 主持次数标准化
    max_host = new_member_df["主持次数"].max() if new_member_df["主持次数"].max() > 0 else 1
    new_member_df["主持次数标准化"] = (new_member_df["主持次数"] / max_host * 10).round(2)

    # ========== 3. 综合实力分计算（主持占30%权重） ==========
    new_member_df["综合实力分"] = (
            new_member_df["参与次数标准化"] * 0.25 +  # 参与次数权重25%
            new_member_df["质量分标准化"] * 0.35 +  # 复盘质量权重35%
            new_member_df["点赞数标准化"] * 0.1 +  # 被点赞数权重10%
            new_member_df["主持次数标准化"] * 0.3  # 主持次数权重30%
    ).round(2)

    # 按综合实力分降序排序，取前六名（去重避免重复成员）
    top_new_members = new_member_df.drop_duplicates("成员姓名").sort_values(
        by="综合实力分",
        ascending=False
    ).head(6).reset_index(drop=True)

    # 生成紧凑格式HTML卡片
    cards_html = []
    for idx, row in top_new_members.iterrows():
        # 简化颜色方案
        if idx == 0:
            card_bg = "#fff8e1"
            border_color = "#ffc107"
            rank_bg = "#ffc107"
            rank_color = "#fff"
            rank_text = "第1名"
        elif idx == 1:
            card_bg = "#f5f5f5"
            border_color = "#9e9e9e"
            rank_bg = "#9e9e9e"
            rank_color = "#fff"
            rank_text = "第2名"
        elif idx == 2:
            card_bg = "#ffe0b2"
            border_color = "#ff9800"
            rank_bg = "#ff9800"
            rank_color = "#fff"
            rank_text = "第3名"
        else:
            card_bg = "#f0f8fb"
            border_color = "#2196f3"
            rank_bg = "#2196f3"
            rank_color = "#fff"
            rank_text = f"第{idx + 1}名"

        # 卡片HTML（新增「主持X次」展示）
        card_html = f'<div style="background:{card_bg};border:2px solid {border_color};border-radius:12px;padding:1rem;text-align:center;display:inline-block;width:140px;margin:0.8rem;box-shadow:0 2px 6px rgba(0,0,0,0.08);"><div style="background:{rank_bg};color:{rank_color};font-size:0.8rem;font-weight:bold;padding:0.2rem 0.8rem;border-radius:20px;margin-bottom:0.8rem;display:inline-block;">{rank_text}</div><div style="font-size:1.2rem;font-weight:700;color:#2d3748;margin-bottom:0.5rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["成员姓名"]}</div><div style="font-size:0.9rem;color:#718096;margin-bottom:0.2rem;">参与 {row["参与次数"]} 次</div><div style="font-size:0.9rem;color:#718096;margin-bottom:0.4rem;">主持 {int(row["主持次数"])} 次</div><div style="font-size:1rem;font-weight:600;color:#e53e3e;">{row["综合实力分"]} 分</div></div>'
        cards_html.append(card_html)

    # 紧凑格式容器HTML
    result_html = f'<div style="text-align:center;width:100%;margin:1rem 0;overflow-x:auto;padding:0.5rem 0;">{"".join(cards_html)}</div>'

    return result_html
# ---------------------- 新增：核心分数计算函数 ----------------------
def get_week_participation_count(member, week_type):
    """
    获取指定成员在指定周的参与次数
    :param member: 成员姓名
    :param week_type: "this_week"（本周） / "last_week"（上周）
    :return: 该成员在指定周的参与次数（int）
    """
    today = datetime.now().date()
    # 计算本周/上周的时间范围（周一至周日）
    if week_type == "this_week":
        # 本周：周一 00:00 至 今天
        week_start = today - timedelta(days=today.weekday())
        week_end = today
    else:  # last_week
        # 上周：上周一 00:00 至上周日 23:59
        last_monday = today - timedelta(days=today.weekday() + 7)
        week_start = last_monday
        week_end = last_monday + timedelta(days=6)

    # 筛选该成员在指定周内的有效参与记录（是否参与=1）
    member_records = df[
        (df["成员姓名"] == member) &
        (df["是否参与"] == 1) &
        (df["日期"] >= week_start) &
        (df["日期"] <= week_end)
    ]
    # 返回参与次数（记录数），无记录则返回0
    return len(member_records)

def get_week_quality_score(member, week_type):
    today = datetime.now().date()
    if week_type == "this_week":
        monday = today - timedelta(days=today.weekday())
        week_start = monday
        week_end = today
    else:  # last_week
        last_monday = today - timedelta(days=today.weekday() + 7)
        week_start = last_monday
        week_end = last_monday + timedelta(days=6)

    # 注意：此处仍用原df，如需限定在筛选周期内可改为 filtered_df
    member_records = df[
        (df["成员姓名"] == member) &
        (df["是否参与"] == 1) &
        (df["日期"] >= week_start) &
        (df["日期"] <= week_end)
        ]
    if len(member_records) == 0:
        return 0
    return REVIEW_QUALITY_SCORES.get(member, 0)

def calculate_member_metrics():
    """计算每个成员的核心指标（参与次数、质量分、点赞数、进步分等）"""
    # 新增：根据侧边栏选择的周期筛选数据
    today = datetime.now().date()
    if period_type == "本周":
        # 本周：周一至今天
        week_start = today - timedelta(days=today.weekday())
        filtered_df = df[(df["日期"] >= week_start) & (df["日期"] <= today)]
    elif period_type == "上周":
        # 上周：上周一至上周日
        last_week_end = today - timedelta(days=today.weekday() + 1)
        last_week_start = last_week_end - timedelta(days=6)
        filtered_df = df[(df["日期"] >= last_week_start) & (df["日期"] <= last_week_end)]
    elif period_type == "月度":
        # 本月：月初至今天
        month_start = date(today.year, today.month, 1)
        filtered_df = df[(df["日期"] >= month_start) & (df["日期"] <= today)]

    # 1. 参与次数统计（使用筛选后的数据）- 先定义参与次数统计
    member_participation = filtered_df[filtered_df["是否参与"] == 1]["成员姓名"].value_counts().reset_index()
    member_participation.columns = ["成员姓名", "参与次数"]
    member_participation["本周参与次数"] = member_participation["成员姓名"].apply(
        lambda x: get_week_participation_count(x, "this_week"))
    # 计算上周参与次数
    member_participation["上周参与次数"] = member_participation["成员姓名"].apply(
        lambda x: get_week_participation_count(x, "last_week"))

    # 处理点赞数合并（现在member_participation已定义）
    like_counts_df = pd.DataFrame(list(LIKE_COUNTS.items()), columns=["成员姓名", "被点赞数"])
    member_participation = member_participation.merge(
        like_counts_df,
        on="成员姓名",
        how="left"  # 左连接确保所有成员都保留
    )
    # 填充未被点赞的成员为0
    member_participation["被点赞数"] = member_participation["被点赞数"].fillna(0).astype(int)

    # 【新增】3. 补充主持次数（从原始df中提取每个成员的总主持次数）
    # 由于df中每个成员的"主持次数"字段已在process_daily_data中计算为总次数，直接取每个成员的最大值即可
    host_counts = df.groupby("成员姓名")["主持次数"].max().reset_index()
    member_participation = member_participation.merge(host_counts, on="成员姓名", how="left")
    # 填充未主持过的成员为0
    member_participation["主持次数"] = member_participation["主持次数"].fillna(0).astype(int)

    member_participation["复盘质量分"] = member_participation["成员姓名"].apply(
        lambda x: REVIEW_QUALITY_SCORES.get(x, 0)  # 从质量分字典获取，默认0
    )

    # 4. 计算首月进步分（逻辑不变，但基于筛选后参与的成员）
    def get_first_month_progress(member):
        if member not in FIRST_REVIEW_INFO:
            return 0
        first_info = FIRST_REVIEW_INFO[member]
        first_score = first_info.get("首次质量分", 0)
        current_score = member_participation[member_participation["成员姓名"] == member]["复盘质量分"].iloc[0]
        return max(0, current_score - first_score)  # 进步分不低于0

    # 新增：从原始df中提取每个成员最新的参与记录（日期和是否参与）
    def get_latest_participation(df):
        # 按成员分组，取每个成员最新的记录（按日期排序）
        df_sorted = df.sort_values(by=["成员姓名", "日期"], ascending=[True, False])
        # 每个成员只保留最新一条记录
        latest_records = df_sorted.drop_duplicates(subset=["成员姓名"], keep="first")
        # 提取需要的字段
        return latest_records[["成员姓名", "是否参与", "日期"]]

    # 获取每个成员最新的参与信息
    latest_participation = get_latest_participation(df)

    # 合并到member_participation中
    member_participation = member_participation.merge(
        latest_participation,
        on="成员姓名",
        how="left"  # 左连接确保所有成员都保留
    )

    member_participation["首月进步分"] = member_participation["成员姓名"].apply(get_first_month_progress)

    # ========== 每周进步分 = 本周参与次数 - 上周参与次数 ==========
    member_participation["每周进步分"] = member_participation["本周参与次数"] - member_participation["上周参与次数"]

    # 6. 标记是否为本月新成员
    member_participation["是否本月新成员"] = member_participation["成员姓名"].isin(THIS_MONTH_NEW_MEMBERS)

    return member_participation

# ---------------------- 新增：本月黑马称号展示 ----------------------
metrics_df = calculate_member_metrics()

st.subheader("🏆 本期黑马（新成员前6名）")
dark_horse = get_this_month_dark_horse(metrics_df)
st.markdown(dark_horse, unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>基于本月新成员的参与次数、复盘质量分综合评选</p>", unsafe_allow_html=True)

# ---------------------- 在主界面添加新功能入口 ----------------------
# 在现有代码的主界面部分（如侧边栏下方或主内容区）添加
#st.markdown("## 🌟 今日互动区")
#render_daily_review_interface()

# ---------------------- 新增：三种榜单计算函数 ----------------------
def get_comprehensive_ranking(metrics_df):
    """综合实力榜：参与次数×40% + 复盘质量分×50% + 被点赞数×10%"""
    df = metrics_df.copy()
    # 计算综合分（标准化得分，避免数值范围差异影响）
    max_participate = df["参与次数"].max() if df["参与次数"].max() > 0 else 1
    max_quality = df["复盘质量分"].max() if df["复盘质量分"].max() > 0 else 1
    max_like = df["被点赞数"].max() if df["被点赞数"].max() > 0 else 1

    df["参与次数标准化"] = df["参与次数"] / max_participate * 10
    df["质量分标准化"] = df["复盘质量分"] / max_quality * 10
    df["点赞数标准化"] = df["被点赞数"] / max_like * 10

    df["综合实力分"] = (
            df["参与次数标准化"] * 0.4 +
            df["质量分标准化"] * 0.5 +
            df["点赞数标准化"] * 0.1
    ).round(2)

    return df.sort_values("综合实力分", ascending=False).reset_index(drop=True)

def get_newbie_ranking(metrics_df):
    """新锐成长榜：参与次数≤5的用户，参与次数×30% + 本周较上周增长次数×70%"""
    # 深拷贝避免修改原数据
    df = metrics_df.copy()

    if len(df) == 0:
        return df

    # ---------------------- 增强字段检查与兼容 ----------------------
    # 检查必要字段，给出明确报错提示
    required_cols = ["成员姓名", "参与次数", "是否参与", "日期"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"metrics_df缺少必要字段：{', '.join(missing_cols)}。请确保传入包含这些字段的DataFrame（原始df直接传入即可）")

    # 自动转换日期格式（兼容date/str类型）
    if df["日期"].dtype != "object" or not isinstance(df["日期"].iloc[0], date):
        try:
            df["日期"] = pd.to_datetime(df["日期"]).dt.date
        except Exception as e:
            raise ValueError(f"日期字段格式错误，无法转换为date类型：{str(e)}")

    # ---------------------- 原逻辑保留：筛选参与次数≤5的用户 ----------------------
    newbie_df = df[df["参与次数"] <= 5].copy()
    if len(newbie_df) == 0:
        return pd.DataFrame(
            columns=df.columns.tolist() + ["本周参与次数", "上周参与次数", "本周较上周增长次数", "参与次数标准化",
                                           "增长次数标准化", "新锐成长分"])

    # ---------------------- 计算本周/上周参与次数及增长次数 ----------------------
    today = datetime.now().date()
    today_weekday = today.weekday()  # 0=周一，6=周日
    this_week_start = today - timedelta(days=today_weekday)  # 本周一
    last_week_start = this_week_start - timedelta(days=7)  # 上周一
    last_week_end = this_week_start - timedelta(days=1)  # 上周日

    # 统计每个新锐用户的时段参与次数
    user_time_stats = []
    for user in newbie_df["成员姓名"].unique():
        # 该用户所有参与记录（是否参与=1）
        user_participate_df = df[(df["成员姓名"] == user) & (df["是否参与"] == 1)]

        # 本周参与次数（本周一至今日）
        this_week_participate = user_participate_df[
            (user_participate_df["日期"] >= this_week_start) &
            (user_participate_df["日期"] <= today)
            ].shape[0]

        # 上周参与次数（上周一至上周日）
        last_week_participate = user_participate_df[
            (user_participate_df["日期"] >= last_week_start) &
            (user_participate_df["日期"] <= last_week_end)
            ].shape[0]

        # 增长次数（最小为0，避免负增长）
        growth = max(0, this_week_participate - last_week_participate)

        user_time_stats.append({
            "成员姓名": user,
            "本周参与次数": this_week_participate,
            "上周参与次数": last_week_participate,
            "本周较上周增长次数": growth
        })

    # 合并统计结果
    time_stats_df = pd.DataFrame(user_time_stats)
    newbie_df = newbie_df.merge(time_stats_df, on="成员姓名", how="left")

    # ---------------------- 标准化计算（保持原逻辑） ----------------------
    max_participate = newbie_df["参与次数"].max() if newbie_df["参与次数"].max() > 0 else 1
    max_growth = newbie_df["本周较上周增长次数"].max() if newbie_df["本周较上周增长次数"].max() > 0 else 1

    newbie_df["参与次数标准化"] = (newbie_df["参与次数"] / max_participate * 10).round(2)
    newbie_df["增长次数标准化"] = (newbie_df["本周较上周增长次数"] / max_growth * 10).round(2)

    # ---------------------- 计算新锐成长分 ----------------------
    newbie_df["新锐成长分"] = (
            newbie_df["参与次数标准化"] * 0.3 +
            newbie_df["增长次数标准化"] * 0.7
    ).round(2)

    # 按成长分降序排序
    return newbie_df.sort_values("新锐成长分", ascending=False).reset_index(drop=True)


def get_weekly_progress_ranking(metrics_df):
    """每周进步榜：所有用户，本周参与次数-上周参与次数，正增长Top10"""
    df = metrics_df.copy()

    # 确保参与次数字段存在
    if "本周参与次数" not in df.columns or "上周参与次数" not in df.columns:
        # 计算本周和上周参与次数（兼容旧数据）
        df["本周参与次数"] = df["成员姓名"].apply(lambda x: get_week_participation_count(x, "this_week"))
        df["上周参与次数"] = df["成员姓名"].apply(lambda x: get_week_participation_count(x, "last_week"))

    # 计算每周进步分（本周参与次数 - 上周参与次数）
    df["每周进步分"] = df["本周参与次数"] - df["上周参与次数"]

    # 筛选正增长用户
    progress_df = df[df["每周进步分"] > 0].copy()
    if len(progress_df) == 0:
        # 确保返回包含所需列的空数据框
        return pd.DataFrame(columns=["成员姓名", "上周参与次数", "本周参与次数", "每周进步分"])

    # 按进步分降序，取Top10
    return progress_df.sort_values("每周进步分", ascending=False).head(10).reset_index(drop=True)

# ---------------------- 页面样式定制（原有样式不变，新增榜单样式）----------------------
def set_warm_style():
    st.markdown("""
        <style>
            /* 原有样式不变 */
            body { background-color: #FFF9F5; }
            .main { padding: 0rem 1rem; }
            .day-count-title {
                font-family: 'Noto Sans SC', 'Montserrat', sans-serif;
                font-weight: 900;
                font-size: 2.5rem;
                text-align: center;
                margin: 2rem 0 1rem;
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 30%, #FF6B6B 70%, #4ECDC4 100%);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                text-shadow: 0 4px 15px rgba(255, 215, 0, 0.15);
                letter-spacing: 0.1em;
                padding: 0.5rem 0;
                position: relative;
            }
            .day-count-title::after {
                content: "";
                display: block;
                width: 180px;
                height: 3px;
                background: linear-gradient(90deg, transparent, #FFD700, transparent);
                margin: 0.8rem auto 0;
                border-radius: 3px;
            }
            .day-count-number {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                font-size: 3rem;
                letter-spacing: 0;
                margin: 0 0.3rem;
                text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
            }
            .warm-title {
                color: #FF7A45;
                font-weight: 700;
                margin-bottom: 1rem;
                font-size: 1.8rem;
                text-shadow: 0 2px 4px rgba(255, 122, 69, 0.1);
            }
            .warm-subtitle {
                color: #488286;
                font-weight: 600;
                margin: 1.5rem 0 1rem 0;
                font-size: 1.3rem;
            }
            .warm-card {
                background-color: white;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
                border-left: 4px solid #FF7A45;
            }
            .host-highlight {
                background: linear-gradient(90deg, #FFE8CC 0%, #FFD5B8 100%);
                color: #D9534F;
                font-weight: 700;
                padding: 0.2rem 0.5rem;
                border-radius: 6px;
                display: inline-block;
            }
            .metric-card {
                background-color: #F0FFF4;
                border-radius: 12px;
                padding: 1.2rem;
                text-align: center;
                box-shadow: 0 4px 12px rgba(72, 130, 134, 0.05);
                border: 1px solid #E6FFEF;
            }
            .metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: #488286;
            }
            .metric-label {
                font-size: 0.9rem;
                color: #6B9093;
                margin-top: 0.3rem;
            }
            .daily-participants {
                display: flex;
                flex-wrap: wrap;
                gap: 0.8rem;
                margin-top: 1rem;
            }
            .participant-tag {
                background-color: #F5F5F5;
                color: #488286;
                padding: 0.4rem 0.8rem;
                border-radius: 20px;
                font-size: 0.9rem;
            }
            .stDataFrame { font-size: 0.9rem !important; }
            .stDataFrame td, .stDataFrame th {
                padding: 0.8rem 0.5rem !important;
                white-space: nowrap !important;
            }
            .stDataFrame th {
                color: #488286 !important;
                font-weight: 700 !important;
            }
            /* 新增：黑马称号样式 */
            .dark-horse-card {
                background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
                border-radius: 16px;
                padding: 2rem;
                margin: 2rem 0;
                text-align: center;
                box-shadow: 0 8px 24px rgba(255, 215, 0, 0.1);
                border: 1px solid #FFD700;
            }
            .dark-horse-title {
                font-size: 1.8rem;
                color: #FF8C00;
                font-weight: 700;
                margin-bottom: 1rem;
            }
            .dark-horse-name {
                font-size: 2.2rem;
                color: #FF6B35;
                font-weight: 900;
                margin-bottom: 0.5rem;
            }
            /* 新增：榜单标签样式 */
            .tab-content { margin-top: 1rem; }
            .rank-card {
                margin-bottom: 1.5rem;
                padding: 1rem;
                border-radius: 12px;
                background-color: white;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
            .rank-header {
                display: flex;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #F5F5F5;
            }
            .rank-icon {
                font-size: 1.2rem;
                margin-right: 0.8rem;
                color: #FF7A45;
            }
            .rank-desc {
                font-size: 0.9rem;
                color: #6B9093;
                margin-left: auto;
            }
        </style>
    """, unsafe_allow_html=True)


set_warm_style()


# ---------------------- 数据预处理（按筛选周期过滤） ----------------------
# 按筛选周期过滤数据
filtered_df = df[
    (df["日期"] >= start_date) &
    (df["日期"] <= end_date) &
    (df["是否参与"] == 1)  # 只统计参与的记录
    ].copy()

# 计算核心统计指标
total_days = (end_date - start_date).days + 1  # 周期内总天数
all_members = sorted(df["成员姓名"].unique().tolist())  # 所有成员（历史累计）
period_members = sorted(filtered_df["成员姓名"].unique().tolist())  # 周期内参与过的成员
total_participations = len(filtered_df)  # 周期内总参与人次
avg_daily_participants = total_participations / total_days if total_days > 0 else 0  # 日均参与人数

# 成员周期参与次数统计（用于排名）
member_participation = filtered_df["成员姓名"].value_counts().reset_index()
member_participation.columns = ["成员姓名", "参与次数"]
# 计算参与率（参与次数/周期总天数）
member_participation["参与率(%)"] = round(
    (member_participation["参与次数"] / total_days) * 100, 1
)
# 按参与次数降序排名
member_participation["排名"] = member_participation["参与次数"].rank(ascending=False, method="min").astype(int)


# 提取周期内每日主持人和参与成员（确保主持人无异常）
def get_valid_host(host_series):
    valid_hosts = host_series[host_series != "无"].drop_duplicates()
    return valid_hosts.iloc[0] if len(valid_hosts) > 0 else "无"


daily_summary = filtered_df.groupby("日期").agg({
    "成员姓名": lambda x: sorted(x.tolist()),
    "主持人": get_valid_host
}).reset_index()
daily_summary.columns = ["日期", "参与成员", "主持人"]
daily_summary = daily_summary.sort_values("日期", ascending=False)  # 倒序：最新日期在前

# 修正主持次数统计（按日期去重，每个日期主持人只算1次）
host_daily_unique = filtered_df[filtered_df["主持人"] != "无"][["日期", "主持人"]].drop_duplicates()
host_count = host_daily_unique.groupby("主持人").size().reset_index(name="主持次数")
host_count.columns = ["成员姓名", "主持次数"]

# ---------------------- 新增：三种排名榜单展示 ----------------------
st.markdown("<h2 class='warm-subtitle'>🏅 多维成长排名</h2>", unsafe_allow_html=True)

# 计算三种榜单数据
comprehensive_rank = get_comprehensive_ranking(metrics_df)
newbie_rank = get_newbie_ranking(metrics_df)
weekly_progress_rank = get_weekly_progress_ranking(metrics_df)

# 榜单切换Tabs
tab1, tab2, tab3 = st.tabs(["综合实力榜", "新锐成长榜", "每周进步榜"])

with tab1:
    st.markdown("""
        <div class='rank-card'>
            <div class='rank-header'>
                <span class='rank-icon'>🏆</span>
                <h3 style='color: #488286; margin: 0; font-size: 1.2rem;'>综合实力榜</h3>
                <span class='rank-desc'>面向活跃用户 | 参与次数×40% + 质量分×50% + 点赞数×10%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if len(comprehensive_rank) == 0:
        st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>暂无排名数据～</p>",
                    unsafe_allow_html=True)
    else:
        # 展示前10名表格
        display_cols = ["排名", "成员姓名", "参与次数", "复盘质量分", "被点赞数", "综合实力分"]
        rank_df = comprehensive_rank[["成员姓名", "参与次数", "复盘质量分", "被点赞数", "综合实力分"]].copy()
        rank_df["排名"] = range(1, len(rank_df) + 1)
        rank_df = rank_df[display_cols]

        st.dataframe(
            rank_df.head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("排名", format="%d"),
                "参与次数": st.column_config.NumberColumn("参与次数", format="%d"),
                "复盘质量分": st.column_config.NumberColumn("复盘质量分", format="%.1f"),
                "被点赞数": st.column_config.NumberColumn("被点赞数", format="%d"),
                "综合实力分": st.column_config.NumberColumn("综合实力分", format="%.2f")
            }
        )

with tab2:
    st.markdown("""
        <div class='rank-card'>
            <div class='rank-header'>
                <span class='rank-icon'>🌱</span>
                <h3 style='color: #488286; margin: 0; font-size: 1.2rem;'>新锐成长榜</h3>
                <span class='rank-desc'>面向参与次数≤5的成员 | 参与次数×30% + 本周较上周增长次数×70%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if len(newbie_rank) == 0:
        st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>暂无符合条件的新人用户～</p>",
                    unsafe_allow_html=True)
    else:
        display_cols = ["排名", "成员姓名", "参与次数", "新锐成长分"]
        rank_df = newbie_rank[["成员姓名", "参与次数", "新锐成长分"]].copy()
        rank_df["排名"] = range(1, len(rank_df) + 1)
        rank_df = rank_df[display_cols]

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("排名", format="%d"),
                "参与次数": st.column_config.NumberColumn("参与次数", format="%d"),
                "新锐成长分": st.column_config.NumberColumn("新锐成长分", format="%.2f")
            }
        )

with tab3:
    st.markdown("""
        <div class='rank-card'>
            <div class='rank-header'>
                <span class='rank-icon'>📈</span>
                <h3 style='color: #488286; margin: 0; font-size: 1.2rem;'>每周进步榜</h3>
                <span class='rank-desc'>面向所有用户 | 本周质量分 - 上周质量分（正增长Top10）</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if len(weekly_progress_rank) == 0:
        st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>暂无正增长进步数据～</p>",
                    unsafe_allow_html=True)
    else:
        display_cols = ["排名", "成员姓名", "上周参与次数", "本周参与次数", "每周进步分"]
        rank_df = weekly_progress_rank[["成员姓名", "上周参与次数", "本周参与次数", "每周进步分"]].copy()
        rank_df["排名"] = range(1, len(rank_df) + 1)
        rank_df = rank_df[display_cols]

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("排名", format="%d"),
                "上周参与次数": st.column_config.NumberColumn("上周参与次数", format="%d"),
                "本周参与次数": st.column_config.NumberColumn("本周参与次数", format="%d"),
                "每周进步分": st.column_config.NumberColumn("每周进步分", format="%d")
            }
        )

# ---------------------- 原有页面其他内容（参与情况统计、每日详情等）----------------------
# ---------------------- 主页面：每日参与详情（含主持人高光） ----------------------
daily_summary["日期"] = pd.to_datetime(daily_summary["日期"])
daily_summary["成员发言"] = daily_summary["日期"].dt.strftime("%Y-%m-%d").map(daily_speeches)
daily_summary["成员发言"] = daily_summary["成员发言"].fillna({i: {} for i in daily_summary.index})
# 处理无发言记录的日期（默认空字典）
daily_summary["成员发言"] = daily_summary["成员发言"].fillna({i: {} for i in daily_summary.index})
st.markdown("<h2 class='warm-subtitle'>📝 每日参与详情</h2>", unsafe_allow_html=True)

def extract_core_summary(speech: str) -> str:
    """提取发言核心摘要（默认取前50字+省略号，可自定义）"""
    if len(speech) <= 20:
        return speech
    return speech[:20] + "..."

def highlight_keywords(speech: str) -> str:
    """自动高亮发言中的核心关键词（可根据业务扩展关键词列表）"""
    # 自定义需高亮的关键词（覆盖复盘/工作/学习/休息等场景）
    key_words = [
        "番茄钟", "复盘", "休息", "冥想", "高效", "目标", "节奏","反思","学习"
        "内耗", "理想", "韬光养晦", "锋芒毕露", "知行合一", "长期主义"
    ]
    # 对关键词添加高亮样式（橙色背景+加粗）
    for word in key_words:
        if word in speech:
            speech = speech.replace(
                word,
                f"<span style='background: #FFF3CD; color: #D9822B; font-weight: 600; padding: 0.1rem 0.3rem; border-radius: 4px;'>{word}</span>"
            )
    return speech


st.markdown("<div class='warm-card'>", unsafe_allow_html=True)
if len(daily_summary) == 0:
    st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>该周期暂无参与数据～</p>",
                unsafe_allow_html=True)
else:
    for _, row in daily_summary.iterrows():
        # 2. 基础数据获取（日期、星期、主持人、参与成员）
        date_val = row["日期"]
        weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        if pd.api.types.is_datetime64_any_dtype(date_val):
            date_str = date_val.strftime("%Y-%m-%d")
            weekday = weekday_map[date_val.weekday()]
        else:
            date_str = str(date_val).split(" ")[0]
            try:
                weekday_dt = pd.to_datetime(date_str)
                weekday = weekday_map[weekday_dt.weekday()]
            except:
                weekday = "未知"

        host = row["主持人"] if row["主持人"] != "无" else "未指定"
        participants = row["参与成员"]

        # 3. 成员发言容错处理
        member_speeches = row.get("成员发言", {}) if isinstance(row, dict) else (
            row["成员发言"] if "成员发言" in daily_summary.columns else {})
        if not isinstance(member_speeches, dict):
            member_speeches = {}

        # 4. 渲染日期+主持人标题
        st.markdown(f"""
            <h4 style='color: #488286; margin-top: 1.5rem;'>
                {date_str}（{weekday}）| 主持人：<span class='host-highlight'>{host}</span>
            </h4>
        """, unsafe_allow_html=True)

        # 5. 渲染成员标签+精简发言（核心优化）
        st.markdown(
            "<div class='daily-participants' style='display: flex; flex-wrap: wrap; gap: 1.5rem; margin: 1rem 0;'>",
            unsafe_allow_html=True)

        for member in participants:
            # 5.1 获取发言内容（容错）
            full_speech = member_speeches.get(member, "未记录发言内容")
            # 5.2 提取核心摘要+关键词高亮
            core_summary = extract_core_summary(full_speech)
            highlighted_summary = highlight_keywords(core_summary)
            highlighted_full = highlight_keywords(full_speech)

            # 5.3 区分主持人标签样式
            if member == host:
                tag_html = f"<span class='participant-tag host-highlight'>{member}（主持人）</span>"
            else:
                tag_html = f"<span class='participant-tag'>{member}</span>"

            # 5.4 渲染：标签+高亮摘要 + 折叠面板（完整发言）
            st.markdown(f"""
                <div style='width: calc(33.33% - 1rem); min-width: 250px; margin-bottom: 1rem;'>
                    {tag_html}
                    <!-- 核心摘要（默认展示，含高亮） -->
                    <p style='margin: 0.3rem 0 0.5rem 0; font-size: 0.9rem; color: #374151; line-height: 1.6; padding-left: 0.2rem;'>
                        {highlighted_summary}
                    </p>
                    <!-- 折叠面板（完整发言） -->
                    <details style='font-size: 0.85rem; color: #6b7280; line-height: 1.5;'>
                        <summary style='cursor: pointer; color: #488286;'>查看完整发言</summary>
                        <p style='margin: 0.5rem 0 0 0; padding-left: 0.5rem; border-left: 2px solid #E5E7EB;'>
                            {highlighted_full}
                        </p>
                    </details>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 6. 优化CSS样式（调整字体/行高/高亮样式）
        st.markdown("""
            <style>
                /* 成员标签样式 */
                .participant-tag {
                    background: #f0f8fb; 
                    color: #1b5e20; 
                    padding: 0.4rem 1rem; 
                    border-radius: 20px; 
                    font-size: 0.95rem; 
                    font-weight: 600;
                    display: inline-block;
                }
                /* 主持人标签高亮 */
                .host-highlight {
                    background: linear-gradient(90deg, #FFE8CC 0%, #FFD5B8 100%);
                    color: #D9534F;
                }
                /* 折叠面板样式优化 */
                details > summary {
                    list-style: none; /* 去掉默认箭头 */
                }
                details > summary::before {
                    content: "📝 "; /* 自定义折叠图标 */
                    font-size: 0.8rem;
                }
                details[open] > summary::before {
                    content: "🔍 "; /* 展开后图标变化 */
                }
                /* 全局字体优化 */
                .daily-participants p {
                    letter-spacing: 0.02rem; /* 字间距提升可读性 */
                }
            </style>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------- 页脚（原有不变）----------------------
st.markdown("---")
st.markdown(f"""
    <p style='text-align: center; color: #6B9093; font-size: 0.9rem; margin: 1rem 0;'>
    🌱 公益复盘群 | 数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
""", unsafe_allow_html=True)