#!/usr/bin/env python3
"""
验证高德地图API请求格式
"""

import requests
import json

# 高德地图天气API配置
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
api_key = "fbeee2e481724aa266998babcc16dcd5"

def test_request_format():
    """测试请求格式"""
    print("测试高德地图天气API请求格式")
    print("=" * 50)
    
    # 按照官方文档格式构造请求
    city_code = "410100"  # 郑州
    
    # 方法1: 使用params参数
    print("方法1: 使用params参数")
    params = {
        "city": city_code,
        "key": api_key
    }
    
    full_url = f"{AMAP_WEATHER_URL}?city={city_code}&key={api_key}"
    print(f"完整URL: {full_url}")
    
    try:
        response = requests.get(AMAP_WEATHER_URL, params=params, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("status") == "1":
                print("✅ API调用成功!")
                if data.get("forecasts"):
                    forecast = data["forecasts"][0]
                    city = forecast.get("city", "未知城市")
                    print(f"📍 城市: {city}")
                    
                    if "casts" in forecast and forecast["casts"]:
                        today = forecast["casts"][0]
                        weather = today.get("weather", "未知")
                        temp_high = today.get("daytemp", "未知")
                        temp_low = today.get("nighttemp", "未知")
                        print(f"🌤️ 天气: {weather}")
                        print(f"🌡️ 温度: {temp_low}°C - {temp_high}°C")
            else:
                print(f"❌ API调用失败: {data.get('info', '未知错误')}")
                print(f"🔢 错误码: {data.get('infocode', '未知')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == "__main__":
    test_request_format()
