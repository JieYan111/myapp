import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 資金戰情室", page_icon="💰")

# --- 初始化 Session State (讓程式擁有記憶力) ---
# 如果是第一次打開，幫你預設這三個定期定額項目
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 3000},
        {"商品": "VOO", "金額": 6000}
    ]

# --- 標題 ---
st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 資產配置 | 定期定額管理")

# ==========================================
# 第一部分：收入分配 (你的核心基礎)
# ==========================================
st.header("1. 收入分配源頭")
income = st.number_input("本月收入 (TWD)", value=43000, step=1000)

col1, col2, col3, col4 = st.columns(4)
with col1:
    p_life = st.number_input("生活 40%", value=40)
with col2:
    p_invest = st.number_input("投資 35%", value=35)
with col3:
    p_random = st.number_input("隨機 20%", value=20) # 修正為 20% 湊 100%
with col4:
    p_kid = st.number_input("小孩 5%", value=5)

# 計算預算金額
budget_invest = int(income * (p_invest / 100))
budget_life = int(income * (p_life / 100))
budget_random = int(income * (p_random / 100))
budget_kid = int(income * (p_kid / 100))

# 顯示投資預算水位
st.info(f"💵 根據比例，本月可用於「定期定額」的總資金為： **${budget_invest:,}**")

st.divider()

# ==========================================
# 第二部分：定期定額管理 (動態增減)
# ==========================================
st.header("2. 定期定額配置")

# --- 新增商品區塊 ---
with st.expander("➕ 新增投資商品 (點擊展開)", expanded=False):
    c_add1, c_add2, c_add3 = st.columns([2, 2, 1])
    with c_add1:
        new_item = st.text_input("商品名稱 (例如: TSLA)")
    with c_add2:
        new_amount = st.number_input("扣款金額", value=3000, step=1000)
    with c_add3:
        st.write("") # 排版用
        st.write("") 
        if st.button("新增"):
            if new_item:
                st.session_state.portfolio.append({"商品": new_item, "金額": new_amount})
                st.rerun() # 重新整理畫面

# --- 刪除商品區塊 ---
# 只有當列表有東西時才顯示刪除選項
if len(st.session_state.portfolio) > 0:
    # 建立一個選單讓人選擇要刪除的項目
    item_names = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
    
    with st.expander("🗑️ 刪除商品 (點擊展開)"):
        selected_to_delete = st.selectbox("選擇要移除的項目", item_names)
        if st.button("確認刪除"):
            # 找出選到的那個項目並移除
            index_to_remove = item_names.index(selected_to_delete)
            st.session_state.portfolio.pop(index_to_remove)
            st.rerun()

# --- 顯示目前的投資清單 ---
st.subheader("📋 目前設定的扣款清單")

if len(st.session_state.portfolio) > 0:
    # 轉成表格顯示
    df = pd.DataFrame(st.session_state.portfolio)
    st.table(df)

    # 計算目前總扣款金額
    current_total = df["金額"].sum()
    
    # --- 關鍵數據比對 ---
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric("預計扣款總額", f"${current_total:,}")
    
    with col_res2:
        balance = budget_invest - current_total
        if balance > 0:
            st.metric("剩餘閒置資金", f"${balance:,}", delta_color="normal")
            st.success(f"還有 ${balance} 可以加碼或是存起來！")
        elif balance < 0:
            st.metric("透支金額", f"${balance:,}", delta_color="inverse")
            st.error(f"⚠️ 注意！你的定期定額超過預算了，超支 ${abs(balance)}")
        else:
            st.metric("資金狀態", "完美平衡", delta_color="off")
            st.success("資金分配剛剛好！")

    # --- 視覺化圓餅圖 ---
    fig, ax = plt.subplots()
    ax.pie(df["金額"], labels=df["商品"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

else:
    st.warning("目前沒有設定任何定期定額項目，請由上方新增。")

# ==========================================
# 頁尾
# ==========================================
st.divider()
st.caption("這是一個為未來專職 Trader 打造的資金管理系統")
