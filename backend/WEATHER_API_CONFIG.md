# 高德地图天气API配置

## 环境变量配置

在 `backend/.env` 文件中添加：

```
# 高德地图API Key
AMAP_API_KEY=fbeee2e481724aa266998babcc16dcd5
```

## 获取API Key步骤

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册/登录账号
3. 创建应用，选择"Web服务"类型
4. 获取API Key

## API接口说明

### 请求地址
```
https://restapi.amap.com/v3/weather/weatherInfo
```

### 请求参数
- `key`: 用户在高德地图官网申请的Web服务API类型KEY（必填）
- `city`: 城市编码，如410100（郑州）
- `extensions`: 返回结果控制，可选值：base/all（base:返回实况天气，all:返回预报天气）

### 当前配置
- 默认城市：410100（郑州）
- 返回格式：详细预报天气
- 包含信息：天气状况、温度范围、风向风力、城市名称

## 测试接口

```bash
# 测试天气接口
curl "http://localhost:8000/api/weather?city=410100"
```

## 城市编码参考

- 410100: 郑州
- 110100: 北京
- 310100: 上海
- 440100: 广州
- 440300: 深圳

## 注意事项

1. 如果没有配置API Key，系统会返回模拟天气数据
2. API有调用频率限制，请合理使用
3. 建议缓存天气数据，避免频繁调用




