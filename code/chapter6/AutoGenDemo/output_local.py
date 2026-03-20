import streamlit as st
import requests
import time

# ==========================================
# 配置与常量
# ==========================================
PAGE_TITLE = "BTC 实时行情"
PAGE_ICON = "₿"
API_URL = "https://api.coingecko.com/api/v3/simple/price"
TIMEOUT_SECONDS = 5
CACHE_TTL = 30  # 缓存30秒，避免频繁请求导致被API封禁

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="centered"
)

# ==========================================
# 核心功能函数
# ==========================================

@st.cache_data(ttl=CACHE_TTL)
def fetch_btc_data():
    """
    从 CoinGecko API 获取比特币价格数据
    注意：使用了 @st.cache_data 装饰器来缓存结果，避免超过 API 速率限制        
    """
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }

    try:
        # 发送请求
        response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # 检查 HTTP 错误

        data = response.json()
        btc_info = data.get('bitcoin', {})

        current_price = btc_info.get('usd')
        change_percentage = btc_info.get('usd_24h_change')

        # 数据校验
        if current_price is None or change_percentage is None:
            st.error("❌ 数据解析失败：API 返回的数据格式不正确")
            return None

        # 计算涨跌额
        change_value = current_price * (change_percentage / 100.0)

        return {
            "price": current_price,
            "change_value": change_value,
            "change_percentage": change_percentage
        }

    except requests.exceptions.Timeout:
        st.error("⚠️ 请求超时，网络连接可能较慢。")
        return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ 网络连接错误，请检查您的网络。")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            st.error("⚠️ 请求过于频繁，请稍后再试 (API 限流)。")
        else:
            st.error(f"⚠️ API 请求失败 (状态码: {e.response.status_code})")    
        return None
    except Exception as e:
        st.error(f"⚠️ 发生未知错误: {str(e)}")
        return None

def format_currency(value):
    return f"${value:,.2f}"

def format_percentage(value):
    return f"{value:+.2f}%"

# ==========================================
# UI 界面构建
# ==========================================

def main():
    st.title(PAGE_TITLE)

    # 顶部操作栏
    col_header_1, col_header_2 = st.columns([6, 1])
    with col_header_2:
        # 使用 key 确保按钮点击能正确触发
        if st.button("🔄 刷新", key="refresh_btn", use_container_width=True):  
            st.rerun()

    st.markdown("---")

    # 数据加载
    # 移除了 time.sleep，让加载状态完全取决于网络速度
    with st.spinner('正在获取最新比特币行情...'):
        btc_data = fetch_btc_data()

    if btc_data:
        col_price, col_trend = st.columns([1, 1])

        with col_price:
            st.metric(
                label="Bitcoin (USD)",
                value=format_currency(btc_data['price']),
                delta=f"{format_currency(btc_data['change_value'])} (24h)"     
            )

        with col_trend:
            # 优化：直接将涨跌幅作为主值显示，视觉上更直观
            st.metric(
                label="24小时涨跌幅",
                value=format_percentage(btc_data['change_percentage']),        
                delta=None # 不需要辅助数据
            )

        # 获取缓存数据的最后更新时间（近似）
        last_updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    
        st.caption(f"数据来源: CoinGecko API (每30秒自动缓存更新) | 最后更新: {last_updated}")

    else:
        st.info("暂无数据，请检查网络后点击刷新按钮。")

if __name__ == "__main__":
    main()