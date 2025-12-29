import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io # 用來處理檔案下載的記憶體緩衝

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 資金戰情室", page_icon="💰", layout="centered")

# --- 初始化 Session State ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 6000},
        {"商品": "VOO", "金額": 3000}
    ]

st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 資產配置 | 數據匯出")

# ==========================================
# 1. 收入分配
# ==========================================
st.header("1. 收入分配源頭")
income = st.number_input("本月收入 (TWD)", value=43000, step=1000)

st.subheader("設定分配比例 (%)")
col1, col2, col3, col4 = st.columns(4)
with col1: p_life = st.number_input("生活費", value=40)
with col2: p_invest = st.number_input("投資", value=35)
with col3: p_random = st.number_input("隨機", value=20)
with col4: p_kid = st.number_input("小孩", value=5)

# 計算金額
budget_life = int(income * (p_life / 100))
budget_invest = int(income * (p_invest / 100))
budget_random = int(income * (p_random / 100))
budget_kid = int(income * (p_kid / 100))
total_percent = p_life + p_invest + p_random + p_kid

# 顯示金額
st.write("---")
if total_percent != 100:
    st.error(f"⚠️ 比例總和為 {total_percent}%，請調整至 100%！")
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏠 生活費", f"${budget_life:,}")
    m2.metric("📈 投資總額", f"${budget_invest:,}")
    m3.metric("🎲 隨機運用", f"${budget_random:,}")
    m4.metric("👶 小孩資金", f"${budget_kid:,}")

# ==========================================
# 2. 定期定額配置
# ==========================================
st.header("2. 定期定額配置")
st.info(f"💵 投資預算： **${budget_invest:,}**")

# 新增/刪除功能 (保持原本邏輯，簡化顯示)
with st.expander("⚙️ 管理投資商品 (新增/刪除)"):
    c_add1, c_add2, c_add3 = st.columns([2, 2, 1])
    with c_add1: new_item = st.text_input("商品名稱")
    with c_add2: new_amount = st.number_input("金額", value=3000, step=1000)
    with c_add3: 
        st.write("")
        st.write("")
        if st.button("新增") and new_item:
            st.session_state.portfolio.append({"商品": new_item, "金額": new_amount})
            st.rerun()
            
    if len(st.session_state.portfolio) > 0:
        item_names = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
        del_item = st.selectbox("選擇刪除", item_names)
        if st.button("刪除"):
            st.session_state.portfolio.pop(item_names.index(del_item))
            st.rerun()

# 顯示清單與圖表
if len(st.session_state.portfolio) > 0:
    df_portfolio = pd.DataFrame(st.session_state.portfolio)
    st.dataframe(df_portfolio, use_container_width=True)
    
    current_total = df_portfolio["金額"].sum()
    balance = budget_invest - current_total
    
    c_res1, c_res2 = st.columns(2)
    c_res1.metric("已設定扣款", f"${current_total:,}")
    if balance >= 0:
        c_res2.metric("剩餘閒置資金", f"${balance:,}")
    else:
        c_res2.metric("透支金額", f"${balance:,}", delta_color="inverse")

    # 圓餅圖
    fig, ax = plt.subplots()
    ax.pie(df_portfolio["金額"], labels=df_portfolio["商品"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# ==========================================
# 3. 資料匯出區 (Excel 下載)
# ==========================================
st.divider()
st.header("3. 數據存檔與匯出")
st.write("將本月的規劃匯出成 Excel，方便未來進行總資產管理。")

# 準備要匯出的資料
# A. 收入分配表
data_income = {
    "項目": ["本月收入", "生活費", "投資", "隨機運用", "小孩資金"],
    "比例": ["100%", f"{p_life}%", f"{p_invest}%", f"{p_random}%", f"{p_kid}%"],
    "金額": [income, budget_life, budget_invest, budget_random, budget_kid]
}
df_income = pd.DataFrame(data_income)

# B. 投資組合表 (如果有的話)
if len(st.session_state.portfolio) > 0:
    df_export_portfolio = pd.DataFrame(st.session_state.portfolio)
else:
    df_export_portfolio = pd.DataFrame({"訊息": ["目前無設定投資項目"]})

# C. 製作 Excel 的魔法 (使用 BytesIO 在記憶體中寫入)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # 寫入第一頁：收入分配
    df_income.to_excel(writer, sheet_name='收入分配', index=False)
    # 寫入第二頁：投資組合
    df_export_portfolio.to_excel(writer, sheet_name='投資組合', index=False)

    # (進階) 可以在這裡用 xlsxwriter 調整欄寬，但先保持簡單

# 讓 buffer 回到起點
buffer.seek(0)

# 下載按鈕
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        label="📥 下載 Excel 報表",
        data=buffer,
        file_name=f"Trader財務規劃_{income}.xlsx",
        mime="application/vnd.ms-excel"
    )

with col_dl2:
    st.info("💡 提示：若要存成 PDF (含圖表)，請直接使用瀏覽器的「列印 -> 另存為 PDF」功能，效果最好！")

st.divider()
