# 测试天气 API
import requests
response = requests.get("https://wttr.in/Beijing?format=j1")
print("天气API状态:", response.status_code)
print("天气API响应头 Content-Type:", response.headers.get("Content-Type"))
print("天气API原始文本前300字符:")
print(response.text[:300])
print("天气API data:")
payload = response.json()
current_condition = payload.get("data", {}).get("current_condition")
print(current_condition)

try:
    weather_json = response.json()
    print("天气API JSON 顶层字段:", list(weather_json.keys()))
    print("current_condition:", weather_json.get("current_condition"))
except ValueError as e:
    print("天气API返回不是合法JSON:", e)

# 测试 Tavily API
from tavily import TavilyClient
tavily = TavilyClient(api_key="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")
try:
    result = tavily.search("test", search_depth="basic")
    print("Tavily API 连接成功")
except Exception as e:
    print("Tavily API 错误:", e)