import os
import requests
import asyncio
from fastapi import APIRouter
from typing import Optional

router = APIRouter()

# 高德地图天气API配置
AMAP_API_KEY = "fbeee2e481724aa266998babcc16dcd5"
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

async def get_weather_by_city(city_code: str = "410100") -> dict:
    """根据城市编码获取天气信息"""
    if not AMAP_API_KEY:
        return {
            "weather": "晴天",
            "temperature": 25,
            "description": "今天是晴天，温度25°C",
            "city": "郑州"
        }
    
    try:
        params = {
            "city": city_code,
            "key": AMAP_API_KEY
        }
        
        response = requests.get(AMAP_WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data["status"] == "1":
            # 检查是否有实时天气数据
            if "lives" in data and data["lives"]:
                # 实时天气数据
                live_weather = data["lives"][0]
                weather = live_weather["weather"]
                temperature = live_weather["temperature"]
                wind_dir = live_weather["winddirection"]
                wind_power = live_weather["windpower"]
                humidity = live_weather["humidity"]
                
                # 构建描述
                description = f"今天是{weather}，温度{temperature}°C，{wind_dir}风{wind_power}级，湿度{humidity}%"
                
                return {
                    "weather": weather,
                    "temperature": int(temperature),
                    "wind_direction": wind_dir,
                    "wind_power": wind_power,
                    "humidity": int(humidity),
                    "description": description,
                    "city": live_weather["city"]
                }
            elif "forecasts" in data and data["forecasts"]:
                # 预报天气数据
                forecast = data["forecasts"][0]
                casts = forecast["casts"]
                
                # 获取今天的天气
                today_weather = casts[0]
                
                # 提取天气信息
                weather = today_weather["weather"]
                temp_high = today_weather["daytemp"]
                temp_low = today_weather["nighttemp"]
                wind_dir = today_weather["daywind"]
                wind_power = today_weather["daypower"]
                
                # 构建描述
                description = f"今天是{weather}，温度{temp_low}-{temp_high}°C，{wind_dir}风{wind_power}级"
                
                return {
                    "weather": weather,
                    "temperature_high": int(temp_high),
                    "temperature_low": int(temp_low),
                    "wind_direction": wind_dir,
                    "wind_power": wind_power,
                    "description": description,
                    "city": forecast["city"]
                }
            else:
                return {
                    "error": "API返回数据格式异常"
                }
        else:
            # API调用失败，返回错误信息
            error_msg = data.get("info", "未知错误")
            return {
                "error": f"API调用失败: {error_msg}"
            }
        
    except Exception as e:
        print(f"获取天气失败: {e}")
        return {
            "error": f"网络请求失败: {str(e)}"
        }

@router.get("/api/weather")
async def get_weather(city: Optional[str] = "410100"):
    """获取天气信息
    
    Args:
        city: 城市编码，默认410100（郑州）
    """
    weather_data = await get_weather_by_city(city)
    return weather_data

