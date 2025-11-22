import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta, date
from pathlib import Path
import warnings

# 导入字体（增强IP质感）
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@500;700;900&family=Montserrat:wght@600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

warnings.filterwarnings("ignore")

# ---------------------- 核心新增：计算复盘实验室天数 ----------------------
# 起始日期：2025年7月7日
start_date = date(2025, 7, 7)
# 今日日期（本地日期，自动获取）
today = datetime.now().date()
# 计算天数差（确保不出现负数，若起始日期在今日之后则显示0）
days_passed = max(0, (today - start_date).days)

# ---------------------- 【每日数据录入区】----------------------
# ！！！你只需修改这里的数据，运行代码即可自动保存 ！！！
# 格式说明：
# - date_str: 日期（格式：YYYY-MM-DD）
# - member: 成员姓名（直接填写，无需引号）
# - is_participate: 是否参与（1=是，0=否）
# - host: 当日主持人（每个日期只需在一条记录中填写，其他可留空，自动去重）
# - review: 固定为空字符串（已移除微复盘功能）
DAILY_DATA = [
    # 本周六（2025-11-22）：主持人李韫
    {"date_str": "2025-11-22", "member": "陈庚", "is_participate": 1, "host": "李韫", "review": ""},
    {"date_str": "2025-11-22", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "自由之花", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "echo", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "州州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "李姐", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "姜姜好", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "李韫", "is_participate": 1, "host": "", "review": ""},  # 主持人自身也在参与列表
    # 本周五（2025-11-21）：主持人小妮
    {"date_str": "2025-11-21", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-21", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "七公主", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    # 本周四（2025-11-20）：主持人小马哥
    {"date_str": "2025-11-20", "member": "陈庚", "is_participate": 1, "host": "小马哥", "review": ""},
    {"date_str": "2025-11-20", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "echo", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "七公主", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    # 本周三（2025-11-19）：主持人浅夏
    {"date_str": "2025-11-19", "member": "光影", "is_participate": 1, "host": "浅夏", "review": ""},
    {"date_str": "2025-11-19", "member": "sora", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "echo", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "七公主", "is_participate": 1, "host": "", "review": ""},
    # 本周二（2025-11-18）：主持人光影
    {"date_str": "2025-11-18", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-18", "member": "sora", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "拈指花开", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "七公主", "is_participate": 1, "host": "", "review": ""},
    # 本周一（2025-11-17）：主持人时成成
    {"date_str": "2025-11-17", "member": "光影", "is_participate": 1, "host": "时成成", "review": ""},
    {"date_str": "2025-11-17", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "echo", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "七公主", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    # 新增日期数据示例（复制下面一行，修改日期、成员、主持人即可）
    # {"date_str": "2025-11-23", "member": "成员姓名", "is_participate": 1, "host": "", "review": ""},
    # 每个新日期只需在第一条记录填写主持人，其他成员留空
]

# ---------------------- 基础配置 ----------------------
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# Streamlit页面配置（温馨风格）
st.set_page_config(
    page_title="成长实验室 · 复盘成长",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据文件路径（持久化存储，录入后自动保存）
DATA_PATH = Path("review_group_data.csv")


# ---------------------- 数据处理核心函数 ----------------------
def init_data():
    """初始化数据文件（若不存在则创建，新增host字段）"""
    if not DATA_PATH.exists():
        init_df = pd.DataFrame({
            "日期": [],
            "成员姓名": [],
            "是否参与": [],
            "主持人": [],  # 新增主持人字段
            "微复盘": []
        })
        init_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


def save_new_data(new_data_list):
    """保存新录入数据到CSV（自动去重，处理主持人字段）"""
    if not new_data_list:
        return
    # 转换新数据为DataFrame
    new_df = pd.DataFrame(new_data_list)
    new_df["日期"] = pd.to_datetime(new_df["date_str"]).dt.date
    # 核心修复：强制转换host字段为字符串，避免空值识别异常
    new_df["host"] = new_df["host"].astype(str).str.strip()

    # 提取每日主持人（优先获取非空、非空白字符串的值）
    def get_daily_host(host_series):
        # 过滤空字符串和纯空白字符串
        valid_hosts = host_series[host_series != ""].drop_duplicates()
        return valid_hosts.iloc[0] if len(valid_hosts) > 0 else "无"

    daily_host = new_df.groupby("日期")["host"].apply(get_daily_host).to_dict()
    # 为每条记录填充当日主持人
    new_df["主持人"] = new_df["日期"].map(daily_host)
    # 选择最终字段
    new_df = new_df[["日期", "member", "is_participate", "主持人", "review"]]
    new_df.columns = ["日期", "成员姓名", "是否参与", "主持人", "微复盘"]
    # 加载历史数据
    history_df = init_data()
    history_df["日期"] = pd.to_datetime(history_df["日期"]).dt.date
    # 去重：同一日期+同一成员只保留最新一条
    combined_df = pd.concat([history_df, new_df]).drop_duplicates(
        subset=["日期", "成员姓名"], keep="last"
    )
    # 保存到CSV
    combined_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    # print(f"[成功] 保存 {len(new_df)} 条数据（自动去重后总数据量：{len(combined_df)}）")


# 运行代码时自动保存新数据（首次运行会创建CSV，重复运行会自动去重）
save_new_data(DAILY_DATA)

# 加载最终数据（包含历史+新录入）
df = init_data()
df["日期"] = pd.to_datetime(df["日期"]).dt.date  # 统一日期格式
# 处理主持人字段空值（确保没有nan）
df["主持人"] = df["主持人"].fillna("无").astype(str).str.strip()


# ---------------------- 页面样式定制（温馨风格+主持人高光） ----------------------
def set_warm_style():
    st.markdown("""
        <style>
            /* 全局温馨背景 */
            body {
                background-color: #FFF9F5;
            }
            .main {
                padding: 0rem 1rem;
            }
            /* 顶部天数标题样式 */
            /* 顶部天数标题样式（高端IP感） */
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
            /* 标题底部装饰线 */
            .day-count-title::after {
                content: "";
                display: block;
                width: 180px;
                height: 3px;
                background: linear-gradient(90deg, transparent, #FFD700, transparent);
                margin: 0.8rem auto 0;
                border-radius: 3px;
            }
            /* 天数单独强调 */
            .day-count-number {
                font-family: 'Montserrat', sans-serif;
                font-weight: 700;
                font-size: 3rem;
                letter-spacing: 0;
                margin: 0 0.3rem;
                text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
            }
            /* 标题样式（暖橙+活泼字体） */
            .warm-title {
                color: #FF7A45;
                font-weight: 700;
                margin-bottom: 1rem;
                font-size: 1.8rem;
                text-shadow: 0 2px 4px rgba(255, 122, 69, 0.1);
            }
            /* 子标题样式 */
            .warm-subtitle {
                color: #488286;
                font-weight: 600;
                margin: 1.5rem 0 1rem 0;
                font-size: 1.3rem;
            }
            /* 卡片样式（柔和圆角+暖阴影） */
            .warm-card {
                background-color: white;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
                border-left: 4px solid #FF7A45;
            }
            /* 主持人高光样式 */
            .host-highlight {
                background: linear-gradient(90deg, #FFE8CC 0%, #FFD5B8 100%);
                color: #D9534F;
                font-weight: 700;
                padding: 0.2rem 0.5rem;
                border-radius: 6px;
                display: inline-block;
            }
            /* 数据指标卡片 */
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
            /* 每日参与列表样式 */
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
        </style>
    """, unsafe_allow_html=True)


set_warm_style()

# ---------------------- 主页面：顶部天数显示（新增，居中） ----------------------
# 主页面：顶部天数显示（高端IP感）
st.markdown(f"""
    <div class='day-count-title'>
        复盘实验室
        <span class='day-count-number'>{days_passed}</span>
        天
    </div>
""", unsafe_allow_html=True)

# ---------------------- 主页面：头部信息 ----------------------
st.markdown("<h1 class='warm-title'>✨ 公益复盘群 · 成长记录</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B9093; margin-bottom: 2rem;'>记录参与情况，留存成长足迹～</p>", unsafe_allow_html=True)

# ---------------------- 侧边栏（周期筛选） ----------------------
with st.sidebar:
    st.markdown("<h3 style='color: #FF7A45; margin: 1rem 0;'>📅 周期筛选</h3>", unsafe_allow_html=True)
    # 周期类型选择
    period_type = st.radio(
        "选择统计周期",
        options=["本周", "上周", "自定义周", "月度"],
        index=0,
        key="period_type"
    )
    # 按周期类型生成筛选条件
    today_sidebar = datetime.now().date()
    if period_type == "本周":
        # 本周：周一到今日
        monday = today_sidebar - timedelta(days=today_sidebar.weekday())
        start_date = monday
        end_date = today_sidebar
    elif period_type == "上周":
        # 上周：周一到周日
        last_monday = today_sidebar - timedelta(days=today_sidebar.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_date = last_monday
        end_date = last_sunday
    elif period_type == "自定义周":
        # 自定义周：用户选择起止日期
        start_date = st.date_input("开始日期", value=today_sidebar - timedelta(days=7))
        end_date = st.date_input("结束日期", value=today_sidebar)
    else:  # 月度
        # 月度：用户选择月份
        selected_month = st.date_input(
            "选择月份",
            value=today_sidebar,
            format="YYYY-MM"
        ).replace(day=1)  # 取当月第一天
        # 计算当月最后一天
        if selected_month.month == 12:
            next_month = selected_month.replace(year=selected_month.year + 1, month=1)
        else:
            next_month = selected_month.replace(month=selected_month.month + 1)
        start_date = selected_month
        end_date = next_month - timedelta(days=1)
    # 显示当前筛选周期
    st.markdown(f"""
        <p style='color: #6B9093; margin: 1rem 0;'>
        当前筛选：{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}
        </p>
    """, unsafe_allow_html=True)
    # 刷新数据按钮
    if st.button("🔄 刷新数据", type="primary"):
        df = init_data()
        df["日期"] = pd.to_datetime(df["日期"]).dt.date
        df["主持人"] = df["主持人"].fillna("无").astype(str).str.strip()
        st.success("数据已刷新！")
    # 侧边栏底部说明
    st.markdown("---")
    st.markdown("<p style='color: #6B9093; font-size: 0.9rem;'>🌱 公益复盘群成长记录平台</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #999; font-size: 0.8rem;'>数据存储：review_group_data.csv</p>", unsafe_allow_html=True)

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

# ---------------------- 主页面：周期参与情况统计 ----------------------
st.markdown("<h2 class='warm-subtitle'>📊 周期参与情况</h2>", unsafe_allow_html=True)

# 统计指标卡片（4列布局）
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{len(period_members)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>周期参与成员数</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{total_participations}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>周期总参与人次</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{round(avg_daily_participants, 1)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>日均参与人数</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    overall_rate = round((len(period_members) / len(all_members)) * 100, 1) if len(all_members) > 0 else 0
    st.markdown(f"<div class='metric-value'>{overall_rate}%</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>成员参与覆盖率</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 周期参与趋势图（简化样式，适配所有Plotly版本）
st.markdown("<div class='warm-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #488286; font-size: 1.1rem; margin-bottom: 1rem;'>每日参与人数趋势</h3>",
            unsafe_allow_html=True)

# 计算每日参与人数
daily_participants = filtered_df.groupby("日期")["成员姓名"].nunique().reset_index()
daily_participants.columns = ["日期", "参与人数"]

# 补全周期内所有日期（避免漏填日期导致图表断层）
date_range = pd.date_range(start=start_date, end=end_date).date
date_df = pd.DataFrame({"日期": date_range})
daily_participants_complete = pd.merge(
    date_df, daily_participants, on="日期", how="left"
).fillna(0)
daily_participants_complete["参与人数"] = daily_participants_complete["参与人数"].astype(int)

# 绘制兼容版柱状图（移除高版本参数，保留核心样式）
fig_trend = px.bar(
    daily_participants_complete,
    x="日期",
    y="参与人数",
    color="参与人数",
    color_continuous_scale=["#FFE8F0", "#FFC1D5", "#FF9EB8", "#FF7A9E"],  # 温馨粉橙色渐变
    height=350,
    template="plotly_white"
)
fig_trend.update_layout(
    xaxis_title="日期",
    yaxis_title="参与人数",
    coloraxis_showscale=False,
    plot_bgcolor="white",
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(
        tickformat="%m-%d",  # 日期格式简化为月-日
        gridcolor="#F5F5F5"
    ),
    yaxis=dict(
        gridcolor="#F5F5F5"
    )
)
# 简化update_traces，只保留hover提示（兼容低版本Plotly）
fig_trend.update_traces(
    hovertemplate="日期: %{x}<br>参与人数: %{y}人<extra></extra>"
)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- 主页面：每日参与详情（含主持人高光） ----------------------
st.markdown("<h2 class='warm-subtitle'>📝 每日参与详情</h2>", unsafe_allow_html=True)

st.markdown("<div class='warm-card'>", unsafe_allow_html=True)
if len(daily_summary) == 0:
    st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>该周期暂无参与数据～</p>",
                unsafe_allow_html=True)
else:
    for _, row in daily_summary.iterrows():
        date_str = row["日期"].strftime("%Y-%m-%d")
        weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        weekday = weekday_map[row["日期"].weekday()]
        host = row["主持人"] if row["主持人"] != "无" else "未指定"
        participants = row["参与成员"]

        # 日期+主持人标题（主持人高光）
        st.markdown(f"""
            <h4 style='color: #488286; margin-top: 1.5rem;'>
                {date_str}（{weekday}）| 主持人：<span class='host-highlight'>{host}</span>
            </h4>
        """, unsafe_allow_html=True)

        # 参与成员标签列表
        st.markdown("<div class='daily-participants'>", unsafe_allow_html=True)
        for member in participants:
            # 主持人标签额外标注
            if member == host:
                st.markdown(f"<span class='participant-tag host-highlight'>{member}（主持人）</span>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='participant-tag'>{member}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- 主页面：成员参与排名 ----------------------
st.markdown("<h2 class='warm-subtitle'>🏅 周期参与排名</h2>", unsafe_allow_html=True)

# 排名表格（温馨风格染色，主持人标注）
st.markdown("<div class='warm-card'>", unsafe_allow_html=True)
if len(member_participation) == 0:
    st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>该周期暂无参与数据～</p>",
                unsafe_allow_html=True)
else:
    # 合并主持次数（确保每个主持人只统计日期去重后的次数）
    member_participation = pd.merge(
        member_participation, host_count, on="成员姓名", how="left"
    ).fillna({"主持次数": 0})
    member_participation["主持次数"] = member_participation["主持次数"].astype(int)


    # 表格样式：前三名染色+主持人标注
    def color_rank(row):
        if row["排名"] == 1:
            return ["background-color: #FFF0E6"] * len(row)
        elif row["排名"] == 2:
            return ["background-color: #F0FFF4"] * len(row)
        elif row["排名"] == 3:
            return ["background-color: #F0F8FF"] * len(row)
        else:
            return [""] * len(row)


    # 显示排名表格（新增主持次数列）
    st.dataframe(
        member_participation[["排名", "成员姓名", "参与次数", "参与率(%)", "主持次数"]].style.apply(color_rank, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "排名": st.column_config.NumberColumn("排名", format="%d"),
            "成员姓名": st.column_config.TextColumn("成员姓名"),
            "参与次数": st.column_config.NumberColumn("参与次数", format="%d"),
            "参与率(%)": st.column_config.NumberColumn("参与率(%)", format="%.1f"),
            "主持次数": st.column_config.NumberColumn("主持次数", format="%d")
        }
    )
st.markdown("</div>", unsafe_allow_html=True)

# 前三名卡片展示（温馨风格）
if len(member_participation) >= 3:
    st.markdown("<div style='display: flex; justify-content: center; gap: 1.5rem; margin: 1.5rem 0; flex-wrap: wrap;'>",
                unsafe_allow_html=True)

    # 第一名
    top1 = member_participation.iloc[0]
    host_text = f"（主持{top1['主持次数']}次）" if top1['主持次数'] > 0 else ""
    st.markdown(f"""
        <div class='warm-card' style='flex: 1; min-width: 220px; border-left-color: #FF7A45;'>
            <div style='font-size: 2rem; font-weight: 700; color: #FF7A45; text-align: center; margin-bottom: 0.5rem;'>🥇 第1名</div>
            <div style='font-size: 1.3rem; font-weight: 600; color: #488286; text-align: center;'>{top1['成员姓名']}{host_text}</div>
            <div style='text-align: center; margin-top: 1rem;'>
                <p style='color: #6B9093;'>参与次数：{top1['参与次数']}次</p>
                <p style='color: #6B9093;'>参与率：{top1['参与率(%)']}%</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 第二名
    top2 = member_participation.iloc[1]
    host_text = f"（主持{top2['主持次数']}次）" if top2['主持次数'] > 0 else ""
    st.markdown(f"""
        <div class='warm-card' style='flex: 1; min-width: 220px; border-left-color: #488286;'>
            <div style='font-size: 2rem; font-weight: 700; color: #488286; text-align: center; margin-bottom: 0.5rem;'>🥈 第2名</div>
            <div style='font-size: 1.3rem; font-weight: 600; color: #488286; text-align: center;'>{top2['成员姓名']}{host_text}</div>
            <div style='text-align: center; margin-top: 1rem;'>
                <p style='color: #6B9093;'>参与次数：{top2['参与次数']}次</p>
                <p style='color: #6B9093;'>参与率：{top2['参与率(%)']}%</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 第三名
    top3 = member_participation.iloc[2]
    host_text = f"（主持{top3['主持次数']}次）" if top3['主持次数'] > 0 else ""
    st.markdown(f"""
        <div class='warm-card' style='flex: 1; min-width: 220px; border-left-color: #6B9093;'>
            <div style='font-size: 2rem; font-weight: 700; color: #6B9093; text-align: center; margin-bottom: 0.5rem;'>🥉 第3名</div>
            <div style='font-size: 1.3rem; font-weight: 600; color: #488286; text-align: center;'>{top3['成员姓名']}{host_text}</div>
            <div style='text-align: center; margin-top: 1rem;'>
                <p style='color: #6B9093;'>参与次数：{top3['参与次数']}次</p>
                <p style='color: #6B9093;'>参与率：{top3['参与率(%)']}%</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- 页脚（温馨提示） ----------------------
st.markdown("---")
st.markdown(f"""
    <p style='text-align: center; color: #6B9093; font-size: 0.9rem; margin: 1rem 0;'>
    🌱 公益复盘群 | 数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据存储：{DATA_PATH}
    </p>
""", unsafe_allow_html=True)