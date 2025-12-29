import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 戰情室", page_icon="💰", layout="centered")

# --- 初始化 Session State ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 6000},
        {"商品": "VOO", "金額": 3000}
    ]

st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 資產配置 | 總資產管理")

# ==========================================
# 1. 收入分配 (流量)
# ==========================================
st.header("1. 本月收入分配 (Flow)")
with st.expander("📝 設定收入與比例 (點擊展開/收合)", expanded=True):
    income = st.number_input("本月收入 (TWD)", value=43000, step=1000)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: p_life = st.number_input("生活 40%", value=40)
    with c2: p_invest = st.number_input("投資 35%", value=35)
    with c3: p_random = st.number_input("隨機 20%", value=20)
    with c4: p_kid = st.number_input("小孩 5%", value=5)

    # 計算
    b_life = int(income * (p_life / 100))
    b_invest = int(income * (p_invest / 100))
    b_random = int(income * (p_random / 100))
    b_kid = int(income * (p_kid / 100))
    
    # 顯示
    st.write("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏠 生活費", f"${b_life:,}")
    m2.metric("📈 投資額", f"${b_invest:,}")
    m3.metric("🎲 隨機", f"${b_random:,}")
    m4.metric("👶 小孩", f"${b_kid:,}")

# ==========================================
# 2. 定期定額 (策略)
# ==========================================
st.header("2. 定期定額管理 (Strategy)")
st.info(f"💵 本月投資預算： **${b_invest:,}**")

with st.expander("⚙️ 管理投資項目"):
    c_add1, c_add2, c_add3 = st.columns([2, 2, 1])
    with c_add1: new_item = st.text_input("商品")
    with c_add2: new_val = st.number_input("金額", value=3000, step=1000)
    with c_add3: 
        st.write(""); st.write("")
        if st.button("新增") and new_item:
            st.session_state.portfolio.append({"商品": new_item, "金額": new_val})
            st.rerun()
            
    if len(st.session_state.portfolio) > 0:
        item_names = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
        del_item = st.selectbox("刪除項目", item_names)
        if st.button("刪除"):
            st.session_state.portfolio.pop(item_names.index(del_item))
            st.rerun()

if len(st.session_state.portfolio) > 0:
    df_port = pd.DataFrame(st.session_state.portfolio)
    st.dataframe(df_port, use_container_width=True)
    curr_total = df_port["金額"].sum()
    rem_bal = b_invest - curr_total
    
    c_res1, c_res2 = st.columns(2)
    c_res1.metric("已設定", f"${curr_total:,}")
    c_res2.metric("閒置/透支", f"${rem_bal:,}", delta_color="normal" if rem_bal>=0 else "inverse")

# ==========================================
# 🔥 3. 總資產管理 (存量) - 新增功能
# ==========================================
st.divider()
st.header("3. 總資產盤點 (Net Worth)")
st.write("請輸入各帳戶「目前的市值」來檢視資產分佈。")

col_a1, col_a2 = st.columns(2)

with col_a1:
    st.subheader("🛡️ 防禦性資產 (現金)")
    # 預設值填入你之前提到的數字，方便你不用每次重打
    asset_bank_fixed = st.number_input("銀行定存 (緊急預備)", value=400000, step=10000)
    asset_bank_live = st.number_input("銀行活存 (生活/加碼)", value=200000, step=5000)
    asset_kid = st.number_input("小孩帳戶 (現金/其他)", value=0, step=1000)

with col_a2:
    st.subheader("⚔️ 攻擊性資產 (投資)")
    asset_stock = st.number_input("股票現值 (006208/VOO)", value=0, step=5000, help="請輸入證券戶目前的總市值")
    asset_crypto = st.number_input("加密貨幣 (BTC)", value=0, step=1000, help="請輸入錢包換算回台幣的價值")
    asset_futures = st.number_input("期貨保證金 (Trading)", value=90000, step=1000)

# --- 計算總資產 ---
total_cash = asset_bank_fixed + asset_bank_live + asset_kid
total_risk = asset_stock + asset_crypto + asset_futures
net_worth = total_cash + total_risk

# --- 顯示總資產卡片 ---
st.write("---")
c_net1, c_net2, c_net3 = st.columns(3)
c_net1.metric("💰 總資產 (Net Worth)", f"${net_worth:,}")
c_net2.metric("🛡️ 防禦部位 (Cash)", f"${total_cash:,}", f"{total_cash/net_worth*100:.1f}%")
c_net3.metric("⚔️ 攻擊部位 (Risk)", f"${total_risk:,}", f"{total_risk/net_worth*100:.1f}%")

# --- 總資產圓餅圖 ---
assets_data = {
    "類別": ["定存", "活存", "小孩", "股票", "加密貨幣", "期貨"],
    "金額": [asset_bank_fixed, asset_bank_live, asset_kid, asset_stock, asset_crypto, asset_futures]
}
df_assets = pd.DataFrame(assets_data)
# 過濾掉金額為 0 的項目不顯示在圖表
df_assets_chart = df_assets[df_assets["金額"] > 0]

fig_assets, ax_assets = plt.subplots()
# 使用不同色系區分：藍色系是現金，紅色系是投資
colors_list = ['#66b3ff', '#99ccff', '#cce6ff', '#ff9999', '#ffcc99', '#ff6666']
ax_assets.pie(df_assets_chart["金額"], labels=df_assets_chart["類別"], autopct='%1.1f%%', startangle=90, colors=colors_list)
ax_assets.axis('equal')
st.pyplot(fig_assets)


# ==========================================
# 4. 數據匯出 (Excel) - 升級版
# ==========================================
st.divider()
st.header("4. 報表存檔")

# 準備三個分頁的資料
# Sheet 1: 收入分配
df_flow = pd.DataFrame({
    "項目": ["總收入", "生活費", "投資", "隨機", "小孩"],
    "金額": [income, b_life, b_invest, b_random, b_kid],
    "比例": ["100%", f"{p_life}%", f"{p_invest}%", f"{p_random}%", f"{p_kid}%"]
})

# Sheet 2: 定期定額
if len(st.session_state.portfolio) > 0:
    df_strategy = pd.DataFrame(st.session_state.portfolio)
else:
    df_strategy = pd.DataFrame({"提示": ["無設定"]})

# Sheet 3: 總資產快照
df_snapshot = df_assets.copy()
df_snapshot.loc[len(df_snapshot)] = ["總計 (Net Worth)", net_worth] # 加一行總計

# Excel 產出邏輯
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_flow.to_excel(writer, sheet_name='1.本月流量分配', index=False)
    df_strategy.to_excel(writer, sheet_name='2.定期定額設定', index=False)
    df_snapshot.to_excel(writer, sheet_name='3.總資產快照', index=False)

buffer.seek(0)
curr_date = datetime.date.today().strftime("%Y%m%d")

st.download_button(
    label="📥 下載完整資產報表 (.xlsx)",
    data=buffer,
    file_name=f"Trader財務報表_{curr_date}.xlsx",
    mime="application/vnd.ms-excel"
)

st.caption("Powered by Python & Streamlit")
