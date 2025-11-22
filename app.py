import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder  # 增强型表格
import os

# -------------------------- 初始化配置 --------------------------
# 设置页面标题和布局（宽屏模式，更适合表格展示）
st.set_page_config(page_title="团队复盘打卡追踪", layout="wide", page_icon="📝")

# 初始化复盘数据文件（CSV格式，免费版无数据库时用，提交后自动更新）
DATA_FILE = "review_records.csv"
# 初始化表格字段（表头）
DEFAULT_COLUMNS = [
    "姓名", "复盘日期", "复盘主题", "完成情况",
    "核心成长点", "待改进项", "连续打卡天数", "打卡状态", "评论"
]

# 如果CSV文件不存在，创建空文件（首次运行时）
if not os.path.exists(DATA_FILE):
    df_empty = pd.DataFrame(columns=DEFAULT_COLUMNS)
    df_empty.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


# 读取复盘数据（每次刷新页面都会重新读取最新数据）
def load_data():
    return pd.read_csv(DATA_FILE, encoding="utf-8-sig")


# 保存新的复盘记录
def save_data(new_record):
    df = load_data()
    new_df = pd.DataFrame([new_record])
    df_updated = pd.concat([df, new_df], ignore_index=True)
    df_updated.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


# -------------------------- 页面UI设计 --------------------------
# 标题+副标题（精致排版）
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #2c3e50; font-size: 2.5rem;">📝 团队复盘打卡 & 成长追踪</h1>
        <p style="color: #7f8c8d; font-size: 1.1rem;">记录复盘、互相学习、养成持续成长的习惯</p>
    </div>
""", unsafe_allow_html=True)

# 分栏布局（左：提交复盘/打卡；右：数据统计）
col1, col2 = st.columns([2, 1])

# -------------------------- 左侧：提交复盘+打卡表单 --------------------------
with col1:
    st.subheader("📥 今日复盘打卡")
    st.markdown("---")  # 分隔线

    # 表单：收集复盘信息
    with st.form(key="review_form", clear_on_submit=True):
        # 1. 基础信息
        name = st.text_input("你的姓名", placeholder="请输入真实姓名（方便大家互相学习）")
        review_date = st.date_input("复盘日期", value=datetime.now(), max_value=datetime.now())

        # 2. 复盘核心内容
        theme = st.text_input("复盘主题", placeholder="比如：项目开发复盘、学习Python复盘、工作效率复盘")
        progress = st.selectbox("完成情况", ["✅ 全部完成", "⚠️ 部分完成", "❌ 未完成"], index=0)
        growth = st.text_area("核心成长点", placeholder="本次复盘最大的收获（1-3句话，方便他人借鉴）", height=80)
        improvement = st.text_area("待改进项", placeholder="下次需要优化的地方（明确可执行）", height=80)

        # 3. 打卡相关（自动计算连续天数，无需手动输入）
        st.markdown("🔄 打卡状态（自动统计，无需手动修改）")

        # 提交按钮
        submit_btn = st.form_submit_button("提交复盘 & 完成打卡", type="primary")

        # 表单提交逻辑
        if submit_btn:
            # 验证必填项
            if not name or not theme or not growth:
                st.error("姓名、复盘主题、核心成长点为必填项，请补充完整！")
            else:
                # 自动计算连续打卡天数（查询该用户上一次打卡日期）
                df = load_data()
                user_prev_records = df[df["姓名"] == name].sort_values("复盘日期", ascending=False)

                if user_prev_records.empty:
                    consecutive_days = 1  # 首次打卡，连续1天
                else:
                    prev_date = pd.to_datetime(user_prev_records.iloc[0]["复盘日期"]).date()
                    today_date = review_date
                    # 判断是否连续（前一天或当天，避免重复打卡）
                    if today_date == prev_date:
                        st.warning("你今天已经打卡过啦，请勿重复提交！")
                        st.stop()
                    elif today_date == prev_date + timedelta(days=1):
                        consecutive_days = int(user_prev_records.iloc[0]["连续打卡天数"]) + 1
                    else:
                        consecutive_days = 1  # 中断后重新开始计数

                # 打卡状态（连续≥7天标为“优秀”）
                if consecutive_days >= 7:
                    check_status = "🌟 优秀（连续≥7天）"
                elif consecutive_days >= 3:
                    check_status = "📈 良好（连续≥3天）"
                else:
                    check_status = "🌱 起步（连续1-2天）"

                # 组装新记录
                new_record = {
                    "姓名": name,
                    "复盘日期": str(review_date),
                    "复盘主题": theme,
                    "完成情况": progress,
                    "核心成长点": growth,
                    "待改进项": improvement,
                    "连续打卡天数": consecutive_days,
                    "打卡状态": check_status,
                    "评论": ""  # 初始评论为空，后续可编辑
                }

                # 保存数据
                save_data(new_record)
                st.success(f"✅ 复盘提交成功！你的连续打卡天数：{consecutive_days}天")
                st.balloons()  # 动画效果，增强互动感

# -------------------------- 右侧：数据统计+成长可视化 --------------------------
with col2:
    st.subheader("📊 成长数据统计")
    st.markdown("---")

    df = load_data()
    total_people = df["姓名"].nunique()  # 参与人数
    total_records = len(df)  # 总复盘次数

    # 统计卡片（精致排版）
    col_stats1, col_stats2 = st.columns(2)
    with col_stats1:
        st.markdown(f"""
            <div style="background-color: #f0f8fb; padding: 15px; border-radius: 8px; text-align: center;">
                <h3 style="color: #2196f3; margin: 0;">{total_people}</h3>
                <p style="color: #666; margin: 5px 0 0 0;">参与人数</p>
            </div>
        """, unsafe_allow_html=True)
    with col_stats2:
        st.markdown(f"""
            <div style="background-color: #fef7fb; padding: 15px; border-radius: 8px; text-align: center;">
                <h3 style="color: #9c27b0; margin: 0;">{total_records}</h3>
                <p style="color: #666; margin: 5px 0 0 0;">总复盘次数</p>
            </div>
        """, unsafe_allow_html=True)

    # 连续打卡TOP3（激励用户）
    st.markdown("### 🏆 连续打卡排行榜")
    if not df.empty:
        top_users = df.groupby("姓名")["连续打卡天数"].max().sort_values(ascending=False).head(3)
        for i, (name, days) in enumerate(top_users.items(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f"{medal} {name}：{days}天")
    else:
        st.text("暂无打卡数据，快来提交你的第一次复盘吧！")

    # 成长曲线（可视化每人的打卡趋势）
    st.markdown("### 📈 个人打卡趋势")
    if total_people > 0:
        selected_user = st.selectbox("选择查看用户", df["姓名"].unique())
        user_data = df[df["姓名"] == selected_user].sort_values("复盘日期")

        if len(user_data) >= 2:
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(user_data["复盘日期"], user_data["连续打卡天数"],
                    marker="o", color="#2196f3", linewidth=2)
            ax.set_xlabel("复盘日期", fontsize=10)
            ax.set_ylabel("连续打卡天数", fontsize=10)
            ax.set_title(f"{selected_user} 的打卡趋势", fontsize=12)
            ax.grid(alpha=0.3)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.text(f"{selected_user} 暂无足够数据生成趋势图（需至少2次复盘）")

# -------------------------- 下方：精致复盘表格+互动功能 --------------------------
st.markdown("---")
st.subheader("📋 团队复盘总览（可筛选/评论）")

# 加载数据并处理日期格式
df = load_data()
if not df.empty:
    df["复盘日期"] = pd.to_datetime(df["复盘日期"]).dt.strftime("%Y-%m-%d")  # 格式化日期

    # 增强型表格配置（精致、可交互）
    gb = GridOptionsBuilder.from_dataframe(df)
    # 1. 表格样式
    gb.configure_default_column(
        resizable=True,  # 列宽可调整
        sortable=True,  # 可排序
        filter=True  # 可筛选
    )
    # 2. 条件格式化（突出显示关键信息）
    gb.configure_column("完成情况",
                        cellStyle=lambda params: {
                            "color": "green" if params.value == "✅ 全部完成" else
                            "orange" if params.value == "⚠️ 部分完成" else "red"
                        }
                        )
    gb.configure_column("连续打卡天数",
                        cellStyle=lambda params: {
                            "backgroundColor": "#e3f2fd" if params.value >= 7 else
                            "#fff3e0" if params.value >= 3 else "white"
                        }
                        )
    # 3. 评论列支持编辑（互动功能）
    gb.configure_column("评论", editable=True)

    # 生成表格
    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        height=400,  # 表格高度
        theme="streamlit",  # 适配Streamlit主题
        allow_unsafe_jscode=True,
        update_mode="value_changed"  # 编辑评论后自动更新
    )

    # 保存编辑后的评论（互动功能核心）
    updated_df = grid_response["data"]
    if not updated_df.equals(df):
        updated_df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        st.success("💬 评论已保存！")

    # 导出功能（下载完整复盘数据）
    csv_data = updated_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 下载复盘数据（CSV格式）",
        data=csv_data,
        file_name=f"团队复盘记录_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    # 无数据时的引导提示
    st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f8f9fa; border-radius: 10px;">
            <h3 style="color: #666;">暂无复盘数据</h3>
            <p style="color: #999; margin: 20px 0;">点击左侧「今日复盘打卡」提交你的第一条记录吧！</p>
        </div>
    """, unsafe_allow_html=True)

# -------------------------- 底部：习惯养成引导 --------------------------
st.markdown("---")
st.subheader("🌱 养成复盘习惯的小建议")
tips = [
    "1. 每天固定时间复盘（比如晚上8点），形成肌肉记忆；",
    "2. 成长点尽量具体（比如“学会了Streamlit表格交互”，而非“有进步”）；",
    "3. 多给他人评论点赞，互相鼓励，形成正向循环；",
    "4. 每周下载数据复盘，看看自己的成长趋势～"
]
for tip in tips:
    st.markdown(f"<p style='color: #34495e;'>{tip}</p>", unsafe_allow_html=True)