# 按钮颜色指导文档

## 概述

本文档定义了OneMinNews应用中各种按钮在浅色和深色模式下的颜色规范。

## 按钮颜色规范

### 1. Sort按钮（选中状态）
- **浅色模式**: 背景 `#111111`，文字 `#ffffff`
- **深色模式**: 背景 `#f0f0f0`，文字 `#111111`

### 2. Show Summary按钮
- **浅色模式**: 背景 `#f5f5f5`，文字 `#111111`
- **深色模式**: 背景 `#222222`，文字 `#ffffff`

### 3. View Original按钮
- **浅色模式**: 边框 `#666666`，文字 `#111111`，透明背景
- **深色模式**: 边框 `#aaaaaa`，文字 `#ffffff`，透明背景

### 4. Save按钮
- **浅色模式**: 背景 `#ededed`，文字 `#111111`，悬停 `#cccccc`
- **深色模式**: 背景 `#333333`，文字 `#ffffff`，悬停 `#444444`

### 5. Like按钮
- **浅色模式**: 背景透明，文字 `#888888`，悬停 `#111111`
- **深色模式**: 背景透明，文字 `#888888`，悬停 `#ffffff`

## CSS变量映射

### 深色模式变量
```css
--sort-selected-bg: #f0f0f0;
--sort-selected-text: #111111;
--show-summary-bg: #222222;
--show-summary-text: #ffffff;
--view-original-border: #aaaaaa;
--view-original-text: #ffffff;
--save-bg: #333333;
--save-text: #ffffff;
--save-hover-bg: #444444;
--like-text: #888888;
--like-hover-text: #ffffff;
```

### 浅色模式变量
```css
--sort-selected-bg: #111111;
--sort-selected-text: #ffffff;
--show-summary-bg: #f5f5f5;
--show-summary-text: #111111;
--view-original-border: #666666;
--view-original-text: #111111;
--save-bg: #ededed;
--save-text: #111111;
--save-hover-bg: #cccccc;
--like-text: #888888;
--like-hover-text: #111111;
```

## 实现说明

1. **CSS变量**: 所有按钮颜色都通过CSS变量定义，支持主题切换
2. **悬停效果**: 按钮悬停时使用统一的蓝色主题 (`--button-hover-bg`, `--button-hover-text`, `--button-hover-border`)
3. **状态管理**: Save和Like按钮根据状态（已保存/已点赞）显示不同的颜色
4. **一致性**: 所有按钮都遵循相同的设计语言和交互模式

## 应用范围

- **Home.jsx**: 排序按钮
- **NewsCard.jsx**: View Original, Save, Like, Read Summary按钮
- **Article.jsx**: Back to Home, Summary Type Toggle, Original Article, Save, Share按钮
- **Saved.jsx**: Export, Read Summary, View Original, Remove, Undo按钮

## 维护指南

1. 修改颜色时，请同时更新深色和浅色模式的CSS变量
2. 确保所有按钮的悬停效果保持一致
3. 测试按钮在不同主题下的视觉效果
4. 保持按钮的可访问性和对比度 