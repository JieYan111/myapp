import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="Trader 資金戰情室", page_icon="💰", layout="wide") 
# layout="wide" 讓畫面變寬，方便並排顯示三大資產

# ==========================================
# 0. 初始化 Session State (記憶體)
# ==========================================
# A. 定期定額清單
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"商品": "006208", "金額": 6000},
        {"商品": "Bitcoin", "金額": 6000},
        {"商品": "VOO", "金額": 3000}
    ]

# B. 銀行資產清單 (預設值)
if 'asset_bank' not in st.session_state:
    st.session_state.asset_bank = [
        {"項目": "緊急預備金(定存)", "金額": 400000},
        {"項目": "生活費活存", "金額": 200000},
        {"項目": "小孩帳戶", "金額": 0}
    ]

# C. 幣圈資產清單
if 'asset_crypto' not in st.session_state:
    st.session_state.asset_crypto = [
        {"項目": "冷錢包 (BTC)", "金額": 0},
        {"項目": "交易所 (USDT)", "金額": 0}
    ]

# D. 股票/期貨資產清單 (預設值)
if 'asset_stock' not in st.session_state:
    st.session_state.asset_stock = [
        {"項目": "台股證券戶", "金額": 0},
        {"項目": "美股證券戶", "金額": 0},
        {"項目": "期貨保證金", "金額": 90000}
    ]

st.title("💰 Trader 資金戰情室")
st.caption("目標：專職交易 | 嚴格風控 | 資產增值")

# ==========================================
# 1. 流量管理 (本月收入)
# ==========================================
with st.container():
    st.header("1. 流量管理 (Income Flow)")
    col_inc, col_ratio = st.columns([1, 3])
    
    with col_inc:
        income = st.number_input("本月收入", value=43000, step=1000)
    
    with col_ratio:
        c1, c2, c3, c4 = st.columns(4)
        with c1: p_life = st.number_input("生活 ", value=40)
        with c2: p_invest = st.number_input("投資 ", value=35)
        with c3: p_random = st.number_input("隨機 ", value=20)
        with c4: p_kid = st.number_input("小孩", value=5)

    # 計算與顯示
    b_life = int(income * (p_life / 100))
    b_invest = int(income * (p_invest / 100))
    b_random = int(income * (p_random / 100))
    b_kid = int(income * (p_kid / 100))
    
    st.info(f"📊 分配結果： 生活 **${b_life:,}** | 投資 **${b_invest:,}** | 隨機 **${b_random:,}** | 小孩 **${b_kid:,}**")

# ==========================================
# 2. 策略管理 (定期定額)
# ==========================================
st.divider()
st.header("2. 策略管理 (DCA Strategy)")

# 使用 Expander 收納新增/刪除功能，保持畫面整潔
with st.expander("⚙️ 調整定期定額項目 (新增/刪除)", expanded=False):
    c_dca1, c_dca2, c_dca3 = st.columns([2, 2, 1])
    with c_dca1: dca_item = st.text_input("DCA 商品名稱")
    with c_dca2: dca_val = st.number_input("DCA 金額", value=3000, step=1000)
    with c_dca3: 
        st.write(""); st.write("")
        if st.button("新增 DCA"):
            if dca_item:
                st.session_state.portfolio.append({"商品": dca_item, "金額": dca_val})
                st.rerun()
    
    if st.session_state.portfolio:
        dca_list = [f"{i['商品']} (${i['金額']})" for i in st.session_state.portfolio]
        del_dca = st.selectbox("刪除 DCA 項目", dca_list)
        if st.button("刪除 DCA"):
            st.session_state.portfolio.pop(dca_list.index(del_dca))
            st.rerun()

# 顯示表格與餘額
if st.session_state.portfolio:
    df_dca = pd.DataFrame(st.session_state.portfolio)
    # 轉置表格顯示比較省空間
    st.dataframe(df_dca.T, use_container_width=True)
    
    dca_total = df_dca["金額"].sum()
    dca_rem = b_invest - dca_total
    
    if dca_rem >= 0:
        st.success(f"✅ 投資預算 ${b_invest:,} - 設定扣款 ${dca_total:,} = 剩餘閒置 **${dca_rem:,}**")
    else:
        st.error(f"⚠️ 預算透支！超支金額：**${dca_rem:,}**")

# ==========================================
# 🔥 3. 存量管理 (總資產盤點)
# ==========================================
st.divider()
st.header("3. 存量管理 (Net Worth)")
st.caption("請在下方三大類別中，管理你的資產細項。")

# 建立三個大欄位
col_bank, col_crypto, col_stock = st.columns(3)

# --- 函數：處理新增刪除邏輯 (讓程式碼不重複) ---
def manage_asset_section(title, session_key, icon):
    st.subheader(f"{icon} {title}")
    
    # 1. 顯示目前的清單與總和
    current_list = st.session_state[session_key]
    df = pd.DataFrame(current_list)
    if not df.empty:
        total = df["金額"].sum()
        st.metric(f"{title} 總值", f"${total:,}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        total = 0
        st.metric(f"{title} 總值", "$0")
        st.warning("無項目")

    # 2. 管理區塊 (Expander)
    with st.expander(f"✏️ 編輯 {title}"):
        # 新增
        with st.form(key=f"add_{session_key}"):
            new_item = st.text_input("項目名稱")
            new_val = st.number_input("目前市值", value=0, step=1000)
            if st.form_submit_button("新增"):
                st.session_state[session_key].append({"項目": new_item, "金額": new_val})
                st.rerun()
        
        # 刪除
        if current_list:
            del_list = [f"{i['項目']} (${i['金額']})" for i in current_list]
            to_del = st.selectbox(f"刪除 {title} 項目", del_list, key=f"del_sel_{session_key}")
            if st.button("刪除", key=f"del_btn_{session_key}"):
                idx = del_list.index(to_del)
                st.session_state[session_key].pop(idx)
                st.rerun()
    return total

# --- 呼叫函數建立三個區塊 ---
with col_bank:
    sum_bank = manage_asset_section("銀行 (Bank)", "asset_bank", "🏦")

with col_crypto:
    sum_crypto = manage_asset_section("幣圈 (Crypto)", "asset_crypto", "₿")

with col_stock:
    sum_stock = manage_asset_section("股票 (Stock)", "asset_stock", "📈")

# ==========================================
# 4. 總資產統計與圖表
# ==========================================
net_worth = sum_bank + sum_crypto + sum_stock

st.write("---")
st.header(f"💰 總資產 (Net Worth): ${net_worth:,}")

# 圖表區
c_chart1, c_chart2 = st.columns(2)

with c_chart1:
    st.subheader("資產類別佔比")
    if net_worth > 0:
        labels = ['銀行 (Cash)', '幣圈 (Crypto)', '股票 (Stock)']
        sizes = [sum_bank, sum_crypto, sum_stock]
        colors = ['#66b3ff', '#ffcc99', '#ff9999']
        
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        st.pyplot(fig1)
    else:
        st.write("尚無資產數據")

with c_chart2:
    st.subheader("風險屬性分析")
    if net_worth > 0:
        # 定義：銀行是守，幣圈+股票是攻
        risk_assets = sum_crypto + sum_stock
        safe_assets = sum_bank
        
        st.progress(risk_assets / net_worth, text=f"⚔️ 攻擊型資產 (Crypto+Stock): {risk_assets/net_worth*100:.1f}%")
        st.progress(safe_assets / net_worth, text=f"🛡️ 防禦型資產 (Bank): {safe_assets/net_worth*100:.1f}%")
        
        st.caption("對於專職 Trader，建議隨時保留至少 6-12 個月生活費在防禦型資產中。")

# ==========================================
# 5. Excel 匯出 (包含三大類別細項)
# ==========================================
st.divider()

# 準備資料
# Sheet 1: 流量
df_flow = pd.DataFrame({
    "項目": ["總收入", "生活費", "投資", "隨機", "小孩"],
    "金額": [income, b_life, b_invest, b_random, b_kid]
})

# Sheet 2: 存量細項 (將三個清單合併並標註類別)
list_all_assets = []
for i in st.session_state.asset_bank:
    list_all_assets.append({"類別": "銀行", "項目": i["項目"], "金額": i["金額"]})
for i in st.session_state.asset_crypto:
    list_all_assets.append({"類別": "幣圈", "項目": i["項目"], "金額": i["金額"]})
for i in st.session_state.asset_stock:
    list_all_assets.append({"類別": "股票", "項目": i["項目"], "金額": i["金額"]})
    
df_assets_detail = pd.DataFrame(list_all_assets)
# 加一行總計
df_assets_detail.loc[len(df_assets_detail)] = ["總計", "Net Worth", net_worth]

# 匯出邏輯
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_flow.to_excel(writer, sheet_name='1.本月流量', index=False)
    if st.session_state.portfolio:
        pd.DataFrame(st.session_state.portfolio).to_excel(writer, sheet_name='2.定期定額設定', index=False)
    df_assets_detail.to_excel(writer, sheet_name='3.總資產細項', index=False)

buffer.seek(0)
curr_date = datetime.date.today().strftime("%Y%m%d")

st.download_button(
    label="📥 下載完整資產報表 (Excel)",
    data=buffer,
    file_name=f"Trader_Report_{curr_date}.xlsx",
    mime="application/vnd.ms-excel"
)
