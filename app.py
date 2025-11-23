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
        /* 英文/数字专属字体：Inter（现代简洁，提升科技感） */
        .en, .num, .score, .rank {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
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
    </style>
""", unsafe_allow_html=True)
warnings.filterwarnings("ignore")

# ---------------------- 核心配置（用户后续需填写的内容）----------------------
# 1. 本月新成员名单（用户稍后填写，格式：["成员1", "成员2", ...]）
THIS_MONTH_NEW_MEMBERS = ["李韫","豆皮","Libby","陈庚","阿龙","二月","七公主","匆匆","拈指花开","姜姜好","自由之花","白了个白","阿成","浅夏"]

# 2. 复盘质量分（用户稍后填写，格式：{成员姓名: 最新质量分, ...}，10分制）
REVIEW_QUALITY_SCORES = {}  # 示例：{"光影": 8.5, "小妮": 9.2, "小马哥": 7.8}

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
                                                                                                        1) - timedelta(
    days=1)

# ---------------------- 【每日数据录入区】（原有数据不变）----------------------
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

    # 11月16日（周日）：主持人光影
    {"date_str": "2025-11-16", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-16", "member": "桃子", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "王永涛", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "阿成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "鱼大爷", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "姜姜好", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},

    # 11月15日（周六）：主持人阳州
    {"date_str": "2025-11-15", "member": "鱼鱼", "is_participate": 1, "host": "阳州", "review": ""},
    {"date_str": "2025-11-15", "member": "阿成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "拈指花开", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "姜姜好", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-15", "member": "光影", "is_participate": 1, "host": "", "review": ""},

    # 11月14日（周五）：主持人miss恩
    {"date_str": "2025-11-14", "member": "光影", "is_participate": 1, "host": "miss恩", "review": ""},
    {"date_str": "2025-11-14", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "Libby", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "时成成", "is_participate": 1, "host": "", "review": ""},

    # 11月13日（周四）：主持人小马哥
    {"date_str": "2025-11-13", "member": "光影", "is_participate": 1, "host": "小马哥", "review": ""},
    {"date_str": "2025-11-13", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "团子", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "Libby", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "小金", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "时成成", "is_participate": 1, "host": "", "review": ""},

    # 11月12日（周三）：主持人花满天
    {"date_str": "2025-11-12", "member": "光影", "is_participate": 1, "host": "花满天", "review": ""},
    {"date_str": "2025-11-12", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "花满天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "时成成", "is_participate": 1, "host": "", "review": ""},

    # 11月11日（周二）：主持人光影
    {"date_str": "2025-11-11", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-11", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-11", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-11", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-11", "member": "拈指花开", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-11", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},

    # 11月10日（周一）：主持人小妮
    {"date_str": "2025-11-10", "member": "阿成", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-10", "member": "Sora", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "拈指花开", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "阿童", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "曾律师", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},

# 1号（2025-11-01）：主持人小妮
    {"date_str": "2025-11-01", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-01", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-01", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-01", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-01", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},

    # 2号（2025-11-02）：主持人小妮
    {"date_str": "2025-11-02", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-02", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "花满天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "李理", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-02", "member": "Betty", "is_participate": 1, "host": "", "review": ""},

    # 3号（2025-11-03）：主持人光影
    {"date_str": "2025-11-03", "member": "莫非", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-03", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-03", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-03", "member": "阿童", "is_participate": 1, "host": "", "review": ""},

    # 4号（2025-11-04）：主持人小妮
    {"date_str": "2025-11-04", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-04", "member": "Sora", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "马梓航", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "Libby", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "李韫", "is_participate": 1, "host": "", "review": ""},

    # 5号（2025-11-05）：主持人小妮
    {"date_str": "2025-11-05", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-05", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "Libby", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},

    # 6号（2025-11-06）：主持人小妮
    {"date_str": "2025-11-06", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-06", "member": "桃桃", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "二月", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},

    # 7号（2025-11-07）：主持人光影
    {"date_str": "2025-11-07", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-07", "member": "小妍", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "桃桃", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "花满天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "李理", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "小金", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "二月", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},

    # 8号（2025-11-08）：主持人小妮
    {"date_str": "2025-11-08", "member": "光影", "is_participate": 1, "host": "小妮", "review": ""},
    {"date_str": "2025-11-08", "member": "Libby", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "miss恩", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},

    # 9号（2025-11-09）：主持人光影
    {"date_str": "2025-11-09", "member": "Betty", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-09", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "白了个白", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "拈指花开", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "自由之花", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "阿信", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "姜姜好", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "九月", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},

    # 11-09（主持人光影）
    {"date_str": "2025-11-09", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-09", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "九月", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "Isa", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "Betty", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "小金", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "阿成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-09", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},

    # 11-16（主持人光影）
    {"date_str": "2025-11-16", "member": "光影", "is_participate": 1, "host": "光影", "review": ""},
    {"date_str": "2025-11-16", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "陈庚", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "阿成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "Betty", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "九月", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "阿龙", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "Isa", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "姜姜好", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "小妮", "is_participate": 1, "host": "", "review": ""},

    {"date_str": "2025-11-01", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-01", "member": "平平", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-03", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-03", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-04", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-05", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-06", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "平平", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-07", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-08", "member": "平平", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-10", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-11", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-12", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-13", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-14", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-16", "member": "桃子", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-17", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-18", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-19", "member": "echo", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-20", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-21", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-22", "member": "夏天", "is_participate": 1, "host": "", "review": ""},

    # 11-23（主持人miss恩）
    {"date_str": "2025-11-23", "member": "miss恩", "is_participate": 1, "host": "miss恩", "review": ""},
    {"date_str": "2025-11-23", "member": "光影", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "夏天", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "鱼鱼", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "小马哥", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "小妮", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "时成成", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "李韫", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "阳州", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "匆匆", "is_participate": 1, "host": "", "review": ""},
    {"date_str": "2025-11-23", "member": "浅夏", "is_participate": 1, "host": "", "review": ""},
    # 新增日期数据示例（复制下面一行，修改日期、成员、主持人即可）
    # {"date_str": "2025-11-23", "member": "成员姓名", "is_participate": 1, "host": "", "review": ""},
    # 每个新日期只需在第一条记录填写主持人，其他成员留空
]

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
    """直接处理DAILY_DATA为DataFrame，不依赖外部文件"""
    df = pd.DataFrame(DAILY_DATA)
    # 转换日期格式
    df["日期"] = pd.to_datetime(df["date_str"]).dt.date
    # 提取每日主持人（每个日期的第一个非空host）
    def get_daily_host(group):
        hosts = group["host"].dropna().unique()
        return hosts[0] if len(hosts) > 0 else "无"
    daily_hosts = df.groupby("日期").apply(get_daily_host).to_dict()
    df["主持人"] = df["日期"].map(daily_hosts)
    # 重命名并筛选列
    df = df.rename(columns={
        "member": "成员姓名",
        "is_participate": "是否参与",
        "review": "微复盘"
    })[["日期", "成员姓名", "是否参与", "主持人", "微复盘"]]
    return df

# 直接处理数据，不读写CSV
df = process_daily_data()

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

# ---------------------- 新增：核心分数计算函数 ----------------------
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

        # 1. 参与次数统计（使用筛选后的数据）
    member_participation = filtered_df[filtered_df["是否参与"] == 1]["成员姓名"].value_counts().reset_index()
    member_participation.columns = ["成员姓名", "参与次数"]

    # 2. 补充质量分、点赞数（无数据时默认0）
    member_participation["复盘质量分"] = member_participation["成员姓名"].map(REVIEW_QUALITY_SCORES).fillna(0)
    member_participation["被点赞数"] = member_participation["成员姓名"].map(LIKE_COUNTS).fillna(0)

    # 3. 计算首月进步分（逻辑不变，但基于筛选后参与的成员）
    def get_first_month_progress(member):
        if member not in FIRST_REVIEW_INFO:
            return 0
        first_info = FIRST_REVIEW_INFO[member]
        first_score = first_info.get("首次质量分", 0)
        current_score = member_participation[member_participation["成员姓名"] == member]["复盘质量分"].iloc[0]
        return max(0, current_score - first_score)  # 进步分不低于0

    member_participation["首月进步分"] = member_participation["成员姓名"].apply(get_first_month_progress)

    # 4. 每周质量分/进步分（基于当前筛选周期内的逻辑，此处保持原逻辑，如需关联筛选周期可进一步调整）
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

    member_participation["本周质量分"] = member_participation["成员姓名"].apply(
        lambda x: get_week_quality_score(x, "this_week"))
    member_participation["上周质量分"] = member_participation["成员姓名"].apply(
        lambda x: get_week_quality_score(x, "last_week"))
    member_participation["每周进步分"] = member_participation["本周质量分"] - member_participation["上周质量分"]

    # 5. 标记是否为本月新成员
    member_participation["是否本月新成员"] = member_participation["成员姓名"].isin(THIS_MONTH_NEW_MEMBERS)

    return member_participation


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
    """新锐成长榜：参与次数≤5的用户，参与次数×30% + 首月进步分×70%"""
    df = metrics_df.copy()
    # 筛选参与次数≤5的用户
    newbie_df = df[df["参与次数"] <= 5].copy()
    if len(newbie_df) == 0:
        return pd.DataFrame(columns=df.columns.tolist() + ["新锐成长分"])

    # 计算成长分（标准化）
    max_participate = newbie_df["参与次数"].max() if newbie_df["参与次数"].max() > 0 else 1
    max_progress = newbie_df["首月进步分"].max() if newbie_df["首月进步分"].max() > 0 else 1

    newbie_df["参与次数标准化"] = newbie_df["参与次数"] / max_participate * 10
    newbie_df["进步分标准化"] = newbie_df["首月进步分"] / max_progress * 10

    newbie_df["新锐成长分"] = (
            newbie_df["参与次数标准化"] * 0.3 +
            newbie_df["进步分标准化"] * 0.7
    ).round(2)

    return newbie_df.sort_values("新锐成长分", ascending=False).reset_index(drop=True)


def get_weekly_progress_ranking(metrics_df):
    """每周进步榜：所有用户，本周质量分-上周质量分，正增长Top10"""
    df = metrics_df.copy()
    # 筛选正增长用户
    progress_df = df[df["每周进步分"] > 0].copy()
    if len(progress_df) == 0:
        return pd.DataFrame(columns=df.columns.tolist())

    # 按进步分降序，取Top10
    return progress_df.sort_values("每周进步分", ascending=False).head(10).reset_index(drop=True)

# ---------------------- 新增：本月黑马计算函数 ----------------------
def get_this_month_dark_horse(metrics_df):
    """本月黑马：本月新成员中综合实力分最高的前六名成员（精致卡片展示，修复HTML渲染）"""
    if not THIS_MONTH_NEW_MEMBERS:
        return '<div style="background: #f8f9fa; border-radius: 12px; padding: 2rem; text-align: center; border: 1px solid #eee; margin: 1rem 0;"><span style="color: #6c757d; font-size: 1.1rem;">暂无（请补充本月新成员名单）</span></div>'

    new_member_df = metrics_df[metrics_df["是否本月新成员"]].copy()
    if len(new_member_df) == 0:
        return '<div style="background: #f8f9fa; border-radius: 12px; padding: 2rem; text-align: center; border: 1px solid #eee; margin: 1rem 0;"><span style="color: #6c757d; font-size: 1.1rem;">暂无（新成员暂无参与记录）</span></div>'

    # 计算新成员综合实力分（同综合实力榜规则，增加空值保护）
    max_participate = new_member_df["参与次数"].max() if new_member_df["参与次数"].max() > 0 else 1
    max_quality = new_member_df["复盘质量分"].max() if new_member_df["复盘质量分"].max() > 0 else 1
    max_like = new_member_df["被点赞数"].max() if new_member_df["被点赞数"].max() > 0 else 1

    new_member_df["参与次数标准化"] = (new_member_df["参与次数"] / max_participate * 10).round(2)
    new_member_df["质量分标准化"] = (new_member_df["复盘质量分"] / max_quality * 10).round(2)
    new_member_df["点赞数标准化"] = (new_member_df["被点赞数"] / max_like * 10).round(2)

    new_member_df["综合实力分"] = (
            new_member_df["参与次数标准化"] * 0.4 +
            new_member_df["质量分标准化"] * 0.5 +
            new_member_df["点赞数标准化"] * 0.1
    ).round(2)

    # 按综合实力分降序排序，取前六名（若不足六名则返回全部，去重避免重复成员）
    top_new_members = new_member_df.drop_duplicates("成员姓名").sort_values(
        by="综合实力分",
        ascending=False
    ).head(6).reset_index(drop=True)

    # 生成紧凑格式HTML（关键：去掉所有多余换行和缩进）
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
            rank_text = f"第{idx+1}名"

        # 紧凑格式卡片HTML（无换行，无多余缩进）
        card_html = f'<div style="background:{card_bg};border:2px solid {border_color};border-radius:12px;padding:1rem;text-align:center;display:inline-block;width:140px;margin:0.8rem;box-shadow:0 2px 6px rgba(0,0,0,0.08);"><div style="background:{rank_bg};color:{rank_color};font-size:0.8rem;font-weight:bold;padding:0.2rem 0.8rem;border-radius:20px;margin-bottom:0.8rem;display:inline-block;">{rank_text}</div><div style="font-size:1.2rem;font-weight:700;color:#2d3748;margin-bottom:0.5rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{row["成员姓名"]}</div><div style="font-size:0.9rem;color:#718096;margin-bottom:0.4rem;">参与 {row["参与次数"]} 次</div><div style="font-size:1rem;font-weight:600;color:#e53e3e;">{row["综合实力分"]} 分</div></div>'
        cards_html.append(card_html)

    # 紧凑格式容器HTML
    result_html = f'<div style="text-align:center;width:100%;margin:1rem 0;overflow-x:auto;padding:0.5rem 0;">{"".join(cards_html)}</div>'

    return result_html

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

# ---------------------- 主页面：顶部天数显示（原有不变）----------------------
st.markdown(f"""
    <div class='day-count-title'>
        复盘实验室第
        <span class='day-count-number'>{days_passed}</span>
        天
    </div>
""", unsafe_allow_html=True)

# ---------------------- 新增：本月黑马称号展示 ----------------------
metrics_df = calculate_member_metrics()

st.subheader("🏆 本月黑马（新成员前6名）")
dark_horse = get_this_month_dark_horse(metrics_df)
st.markdown(dark_horse, unsafe_allow_html=True)
st.caption("基于新成员的参与次数、复盘质量分综合评选")

# ---------------------- 主页面：头部信息（原有不变）----------------------
st.markdown("<h1 class='warm-title'>✨ 公益复盘群 · 成长记录</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B9093; margin-bottom: 2rem;'>记录参与情况，留存成长足迹～</p>", unsafe_allow_html=True)


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
                <span class='rank-desc'>面向头部/活跃用户 | 参与次数×40% + 质量分×50% + 点赞数×10%</span>
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
                <span class='rank-desc'>面向参与≤5次新人 | 参与次数×30% + 首月进步分×70%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if len(newbie_rank) == 0:
        st.markdown("<p style='color: #6B9093; text-align: center; padding: 2rem 0;'>暂无符合条件的新人用户～</p>",
                    unsafe_allow_html=True)
    else:
        display_cols = ["排名", "成员姓名", "参与次数", "首月进步分", "新锐成长分"]
        rank_df = newbie_rank[["成员姓名", "参与次数", "首月进步分", "新锐成长分"]].copy()
        rank_df["排名"] = range(1, len(rank_df) + 1)
        rank_df = rank_df[display_cols]

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("排名", format="%d"),
                "参与次数": st.column_config.NumberColumn("参与次数", format="%d"),
                "首月进步分": st.column_config.NumberColumn("首月进步分", format="%.1f"),
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
        display_cols = ["排名", "成员姓名", "上周质量分", "本周质量分", "每周进步分"]
        rank_df = weekly_progress_rank[["成员姓名", "上周质量分", "本周质量分", "每周进步分"]].copy()
        rank_df["排名"] = range(1, len(rank_df) + 1)
        rank_df = rank_df[display_cols]

        st.dataframe(
            rank_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "排名": st.column_config.NumberColumn("排名", format="%d"),
                "上周质量分": st.column_config.NumberColumn("上周质量分", format="%.1f"),
                "本周质量分": st.column_config.NumberColumn("本周质量分", format="%.1f"),
                "每周进步分": st.column_config.NumberColumn("每周进步分", format="%.1f")
            }
        )

# ---------------------- 原有页面其他内容（参与情况统计、每日详情等）----------------------
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


# ---------------------- 页脚（原有不变）----------------------
st.markdown("---")
st.markdown(f"""
    <p style='text-align: center; color: #6B9093; font-size: 0.9rem; margin: 1rem 0;'>
    🌱 公益复盘群 | 数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
""", unsafe_allow_html=True)