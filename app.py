import streamlit as st
import pandas as pd

# 1. 网页标题和说明
st.title("我的第一个 Streamlit 网页（免费部署）")
st.text("身边人打开链接就能用，支持文件上传和预览～")

# 2. 交互组件：文件上传（支持 CSV/Excel）
uploaded_file = st.file_uploader("上传一个 CSV/Excel 文件", type=["csv", "xlsx"])

# 3. 逻辑处理：如果上传了文件，预览内容
if uploaded_file is not None:
    # 读取文件（pandas 处理表格数据）
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    # 显示表格预览
    st.subheader("文件内容预览")
    st.dataframe(df.head(10))  # 显示前10行
    # 可选：添加下载按钮（让用户下载处理后的文件）
    st.download_button(
        label="下载预览数据",
        data=df.head(10).to_csv(index=False),
        file_name="预览数据.csv",
        mime="text/csv"
    )