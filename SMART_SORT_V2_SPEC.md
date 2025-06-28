# Smart Sort V2 - 新闻智能排序系统重构说明

## 🧠 任务目标

为 `smart sort` 新闻排序逻辑重新设计评分机制，加入更多维度，并输出总分 `smart_score` 字段用于前端排序。

## 📊 新评分机制

```python
SmartScore = w1 * Significance + w2 * Freshness + w3 * SourceWeight + w4 * Popularity + w5 * Novelty + w6 * SummaryQuality
```

## 🔧 维度定义

### 1. Significance（事件影响力）- 权重 0.3
- **定义**：事件影响力（国际政治、科技突破、经济风向等优先）
- **范围**：1-10
- **实现**：基于关键词规则和分类映射
- **优先级**：
  - 10: 重大国际政治事件、战争、重大科技突破
  - 8-9: 经济政策、重要选举、重大自然灾害
  - 6-7: 商业并购、体育重大赛事、娱乐重大事件
  - 4-5: 一般商业新闻、地方政治
  - 1-3: 娱乐八卦、生活新闻

### 2. Freshness（新闻时效性）- 权重 0.2
- **定义**：根据发布时间递减的时效性评分
- **范围**：0-10
- **实现**：滑动评分机制
  - 3小时内：10分
  - 6小时内：7分
  - 12小时内：5分
  - 24小时内：3分
  - 48小时内：1分
  - 48小时以上：0分

### 3. SourceWeight（新闻来源信誉）- 权重 0.15
- **定义**：新闻来源的可信度和权威性
- **范围**：1-10
- **实现**：预定义来源权重映射
  - 10: Financial Times, The New York Times, Reuters, Associated Press
  - 9: BBC News, The Washington Post, The Guardian
  - 8: Bloomberg, CNBC, Los Angeles Times
  - 7: NBC News, CBS News, ABC News
  - 6: Fox News, Sky News, The Telegraph
  - 5: The Independent, Euronews, Deutsche Welle
  - 4: Al Jazeera, Axios
  - 3: 其他一般媒体
  - 1-2: 小媒体、博客等

### 4. Popularity（流行度）- 权重 0.1
- **定义**：被多个源转载的频率和用户互动
- **范围**：0-10
- **实现**：基于 headline_count 和重复度
  - 0: 无点赞
  - 1-5: 少量点赞
  - 6-10: 大量点赞
  - 额外加分：被多个RSS源报道的新闻

### 5. Novelty（新颖性）- 权重 0.15
- **定义**：新闻是否是新事件，与已知新闻的相似度
- **范围**：0-10
- **实现**：与已存新闻标题的相似度比较
  - 完全新事件：10分
  - 轻微相似：7-9分
  - 中等相似：4-6分
  - 高度相似：1-3分
  - 重复新闻：0分

### 6. SummaryQuality（摘要质量）- 权重 0.1
- **定义**：AI生成摘要的结构得分
- **范围**：0-10
- **实现**：基于 structure_score
  - 10: 结构完整，逻辑清晰
  - 7-9: 结构良好
  - 4-6: 结构一般
  - 1-3: 结构较差
  - 0: 无摘要

## ⚖️ 推荐权重设置

```python
w1 = 0.3  # Significance - 事件影响力最重要
w2 = 0.2  # Freshness - 时效性次重要
w3 = 0.15 # SourceWeight - 来源可信度
w4 = 0.1  # Popularity - 流行度
w5 = 0.15 # Novelty - 新颖性
w6 = 0.1  # SummaryQuality - 摘要质量
```

## 🔨 待处理模块

### 1. 核心评分函数
- `compute_significance_score(title, content)`：基于关键词或分类映射
- `compute_freshness_score(published_at)`：滑动评分
- `compute_source_weight_score(source)`：来源权重映射
- `compute_popularity_score(headline_count, duplicate_count)`：流行度计算
- `compute_novelty_score(title, existing_titles)`：与已存新闻比较
- `compute_summary_quality_score(summary_ai)`：摘要质量评估
- `compute_smart_score(article, existing_news)`：整合所有评分

### 2. 辅助函数
- `get_significance_keywords()`：获取重要性关键词映射
- `get_source_weights()`：获取来源权重映射
- `calculate_title_similarity(title1, title2)`：计算标题相似度
- `normalize_score(score, min_val, max_val)`：分数标准化

## 📁 文件修改位置

### 1. 新增文件
- `backend/app/smart_scoring.py`：新的智能评分模块
- `backend/app/scoring_config.py`：评分配置和权重设置

### 2. 修改文件
- `backend/app/models.py`：在 News 模型中加入 `smart_score: float` 字段
- `backend/app/news/postgres_service.py`：在保存新闻时调用智能评分
- `backend/routes/news.py`：增加 `sort_by=smart_score` 查询能力
- `backend/news/fetch_news.py`：拉取后统一调用 smart score 计算

### 3. 数据库迁移
- 需要为 `news` 表添加 `smart_score` 字段
- 为现有新闻重新计算 smart_score

## 🚀 实施步骤

1. **创建评分模块**：实现所有评分函数
2. **更新数据模型**：添加 smart_score 字段
3. **修改保存逻辑**：在保存新闻时计算并存储 smart_score
4. **更新查询接口**：支持按 smart_score 排序
5. **数据库迁移**：为现有数据重新计算分数
6. **测试验证**：确保评分逻辑正确工作

## 📊 预期效果

- 更智能的新闻排序，重要新闻优先显示
- 时效性更好的新闻获得更高权重
- 减少重复新闻的影响
- 提供更个性化的新闻体验 