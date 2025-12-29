import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 資金戰情室", page_icon="💰", layout="centered")

# --- 初始化 Session State (記憶功能) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 6000}, # 照你原本設定的
        {"商品": "VOO", "金額": 3000}
    ]

# --- 標題 ---
st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 資產配置 | 定期定額管理")

# ==========================================
# 第一部分：收入分配 (含金額顯示)
# ==========================================
st.header("1. 收入分配源頭")
income = st.number_input("本月收入 (TWD)", value=43000, step=1000)

st.subheader("設定分配比例 (%)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    p_life = st.number_input("生活費", value=40, help="食衣住行")
with col2:
    p_invest = st.number_input("投資", value=35, help="退休/資產累積")
with col3:
    p_random = st.number_input("隨機", value=20, help="課程/玩樂/期貨") 
with col4:
    p_kid = st.number_input("小孩", value=5, help="尿布/現金")

# --- 計算邏輯 ---
budget_life = int(income * (p_life / 100))
budget_invest = int(income * (p_invest / 100))
budget_random = int(income * (p_random / 100))
budget_kid = int(income * (p_kid / 100))
total_percent = p_life + p_invest + p_random + p_kid

# --- 🔥 新增功能：直接顯示計算後的金額 ---
st.write("---") # 分隔線
st.subheader(f"📊 分配結果 (總比例: {total_percent}%)")

# 檢查比例是否為 100%
if total_percent != 100:
    st.error(f"⚠️ 目前比例總和為 {total_percent}%，請調整至 100%！")
else:
    # 顯示四個大數字
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏠 生活費", f"${budget_life:,}")
    m2.metric("📈 投資總額", f"${budget_invest:,}", delta="投入下方資產")
    m3.metric("🎲 隨機運用", f"${budget_random:,}")
    m4.metric("👶 小孩資金", f"${budget_kid:,}")

st.divider()

# ==========================================
# 第二部分：定期定額管理 (動態增減)
# ==========================================
st.header("2. 定期定額配置 (投資帳戶)")
st.info(f"💵 根據上方計算，本月可用於「投資」的總資金為： **${budget_invest:,}**")

# --- 新增商品區塊 ---
with st.expander("➕ 新增投資商品 (點擊展開)", expanded=False):
    c_add1, c_add2, c_add3 = st.columns([2, 2, 1])
    with c_add1:
        new_item = st.text_input("商品名稱 (例如: TSLA)")
    with c_add2:
        new_amount = st.number_input("扣款金額", value=3000, step=1000)
    with c_add3:
        st.write("") 
        st.write("") 
        if st.button("新增"):
            if new_item:
                st.session_state.portfolio.append({"商品": new_item, "金額": new_amount})
                st.rerun()

# --- 刪除商品區塊 ---
if len(st.session_state.portfolio) > 0:
    item_names = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
    with st.expander("🗑️ 刪除商品 (點擊展開)"):
        selected_to_delete = st.selectbox("選擇要移除的項目", item_names)
        if st.button("確認刪除"):
            index_to_remove = item_names.index(selected_to_delete)
            st.session_state.portfolio.pop(index_to_remove)
            st.rerun()

# --- 顯示清單與檢查預算 ---
st.subheader("📋 目前扣款清單")

if len(st.session_state.portfolio) > 0:
    df = pd.DataFrame(st.session_state.portfolio)
    
    # 顯示表格 (使用 st.dataframe 可以調整寬度)
    st.dataframe(df, use_container_width=True)

    current_total = df["金額"].sum()
    balance = budget_invest - current_total
    
    # 預算檢查顯示
    c_chk1, c_chk2 = st.columns(2)
    with c_chk1:
        st.metric("已設定扣款", f"${current_total:,}")
    with c_chk2:
        if balance > 0:
            st.metric("剩餘閒置資金", f"${balance:,}", delta="可加碼")
        elif balance < 0:
            st.metric("透支金額", f"${balance:,}", delta="-超支", delta_color="inverse")
        else:
            st.metric("資金狀態", "完美平衡", delta="OK")

    # 圓餅圖
    fig, ax = plt.subplots()
    # 設定顏色讓它好看一點
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0']
    ax.pie(df["金額"], labels=df["商品"], autopct='%1.1f%%', startangle=90, colors=colors[:len(df)])
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.warning("目前沒有設定任何定期定額項目")

st.divider()
st.caption("Powered by Python & Streamlit")
