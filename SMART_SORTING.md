# 智能新闻排序系统

## 概述

OneMinNews 现在支持智能排序功能，通过多维度评分算法为用户提供最相关、最优质的新闻内容。

## 评分算法

### 综合评分公式

```
score = time_decay_weight(published_at) * 0.4 +
        ai_structure_score * 0.2 +
        source_weight(source) * 0.15 +
        keyword_novelty_score(keywords) * 0.15 +
        headline_count_score(headline_count) * 0.1
```

### 各项评分详解

#### 1. 时间衰减权重 (40%)
- **函数**: `time_decay_weight(published_at)`
- **算法**: 指数衰减，半衰期12小时
- **公式**: `Math.exp(-hoursSince / 12)`
- **效果**: 最新新闻获得更高权重

#### 2. AI摘要结构评分 (20%)
- **函数**: `ai_structure_score(summary_ai)`
- **范围**: 1-5分
- **来源**: AI生成的摘要质量评估
- **默认值**: 3.0（中等质量）

#### 3. 新闻源权重 (15%)
- **函数**: `source_weight(source)`
- **权重配置**:
  - Financial Times, WSJ: 5.0
  - Reuters, AP, Bloomberg: 4.0
  - BBC, CNN, The Guardian: 3.0
  - 其他来源: 2.0

#### 4. 关键词新颖度 (15%)
- **函数**: `keyword_novelty_score(keywords, existing_keyword_map)`
- **算法**: 统计页面已有关键词频率，新关键词获得更高分数
- **效果**: 避免重复内容，提高内容多样性

#### 5. 点赞数评分 (10%)
- **函数**: `headline_count_score(headline_count)`
- **算法**: 归一化处理，超过20个点赞按满分计算
- **公式**: `Math.min(count / 20, 1)`

## 数据结构

### 新闻对象结构

```json
{
  "id": "news_001",
  "title": "新闻标题",
  "content": "新闻内容",
  "link": "原文链接",
  "date": "2024-06-24T08:00:00Z",
  "source": "Financial Times",
  "published_at": "2024-06-24T08:00:00Z",
  "summary_ai": {
    "brief": "简短摘要",
    "detailed": "详细摘要",
    "structure_score": 4.5
  },
  "headline_count": 12,
  "keywords": ["AI", "regulation", "Europe"],
  "score": 0.85,
  "vote_count": 12
}
```

## 前端功能

### 排序选项

1. **Smart Sort (推荐)**: 使用智能排序算法
2. **Latest First**: 按发布时间排序
3. **Most Popular**: 按点赞数排序

### 显示功能

- **评分显示**: 智能排序时显示综合评分（⭐ 85%）
- **关键词标签**: 显示新闻关键词（🏷️ AI, regulation, Europe）
- **来源过滤**: 支持按新闻来源筛选
- **实时更新**: 点赞后自动重新计算评分

## 后端实现

### 核心文件

- `backend/app/scoring.py`: 评分算法实现
- `backend/app/models.py`: 数据模型定义
- `backend/app/news/postgres_service.py`: 数据库服务
- `backend/routes/news.py`: API路由

### 关键词提取

使用简单的词频统计算法：
- 过滤停用词
- 统计词频
- 返回最常见的5个词作为关键词

### 摘要生成

支持两种摘要类型：
- **Brief**: 2-3句话，150-200字符
- **Detailed**: 420+字符，65+单词

## 部署说明

### 数据库迁移

运行迁移脚本添加新字段：

```bash
cd backend
python migrate_db.py
```

### 环境变量

确保以下环境变量已配置：
- `DATABASE_URL`: 数据库连接字符串
- `OPENAI_API_KEY`: OpenAI API密钥

## 测试

运行测试脚本验证功能：

```bash
cd backend
python test_scoring.py
```

## 性能优化

1. **缓存机制**: 摘要生成结果缓存到本地文件
2. **批量处理**: 新闻保存时批量计算评分
3. **索引优化**: 数据库字段添加适当索引

## 未来改进

1. **机器学习**: 使用用户行为数据训练排序模型
2. **个性化**: 基于用户兴趣调整权重
3. **实时更新**: 支持实时评分更新
4. **A/B测试**: 测试不同排序算法的效果 