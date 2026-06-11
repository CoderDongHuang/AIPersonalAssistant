# Personal AI Assistant - Calendar & Email Automation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.x-orange.svg)
![Status](https://img.shields.io/badge/Status-Development-yellow.svg)

**基于自然语言的个人效率Agent，本地SQLite日历 + SMTP邮件，离线可用**

[技术文档](技术方案文档.md) · [问题反馈](../../issues) · [功能建议](../../discussions)

</div>

---

## 📖 项目简介

Personal AI Assistant 是一个智能个人效率助手，能够理解自然语言指令并自动完成日历查询、会议调整、邮件通知等复杂任务。

### ✨ 核心特性

- 🗣️ **自然语言交互**：支持"帮我把下周三下午的会议改到周五"等复杂指令
- 📅 **智能日历管理**：查询、创建、更新、删除日历事件
- ⚠️ **冲突检测**：自动检测时间冲突并提供备选方案
- 📧 **自动邮件通知**：会议变更后自动发送邮件通知参会人
- 🕐 **时间推理**：精准解析相对时间和模糊时间表达
- 🔄 **状态管理**：基于LangGraph构建有状态的工作流

### 🎯 典型场景
```bash
用户："帮我把下周三下午的团队周会改到周五下午"
Agent自动执行： 
✅ 解析时间：下周三下午 → 2026-06-10 14:00 
✅ 查询事件：找到"团队周会" 
✅ 冲突检测：检查周五下午是否有空闲 
✅ 更新日历：修改事件时间 
✅ 发送邮件：通知所有参会人 
✅ 返回结果："已成功将会议改到周五下午2点，并通知了3位参会人"
 ```
---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- DeepSeek API Key（可选，无Key时使用规则匹配降级）
- SMTP邮箱账号（可选，用于邮件通知功能）

### 安装步骤

1. **克隆仓库**
```bash
git clone 
https://github.com/your-username/AIPersonalAssistant.git 
cd AIPersonalAssistant
```
2. **创建虚拟环境**
```bash
python -m .venv .venv 
source .venv/bin/activate # Linux/Mac
```
或者
```bash
.venv\Scripts\activate # Windows
 ```
3. **安装依赖**
```bash
pip install -r requirements.txt
```
4. **配置环境变量**
```bash
cp .env.example .env
编辑 .env 文件，填入你的API密钥
```
5. **运行应用**
```bash
python main.py
 ```
---

## 📦 技术栈

| 类别 | 技术 |
|------|------|
| **核心框架** | LangChain + LangGraph |
| **LLM服务** | DeepSeek（兼容OpenAI SDK，支持规则降级） |
| **日历存储** | SQLite（本地数据库，离线可用） |
| **邮件服务** | SMTP（QQ/163/Gmail/Outlook） |
| **时间处理** | 自研TimeParser + pytz |
| **数据验证** | Pydantic v2 |

详细技术选型请参考 [技术方案文档](技术方案文档.md)。

---
## 🏗️ 项目结构
```plaintext
AIPersonalAssistant/
├── config/                 # 配置管理
├── models/                 # 数据模型
├── tools/                  # 工具层（Calendar/Gmail/TimeParser）
├── agents/                 # Agent核心（LangGraph状态图）
│   ├── nodes/              # 状态图节点
│   └── prompts/            # Prompt模板
├── services/               # 业务服务层
├── utils/                  # 工具函数
├── tests/                  # 测试套件
├── main.py                 # 应用入口
└── cli.py                  # CLI交互界面
```
---

## 📝 开发进度

### Phase 1: 基础架构搭建 ✅ 已完成
- [x] 项目初始化
- [x] 配置管理和日志系统
- [x] 数据模型和工具类

### Phase 2: 核心工具开发 ✅ 已完成
- [x] CalendarTool开发（SQLite本地存储）
- [x] GmailTool开发（SMTP邮件发送）
- [x] TimeParser优化（中文自然语言时间解析）

### Phase 3: Agent工作流开发 ✅ 基本完成
- [x] 意图识别模块（LLM + 规则降级）
- [x] 时间推理模块
- [x] 冲突检测模块
- [x] 执行引擎（日历 + 邮件）
- [x] LangGraph六节点工作流整合

详细任务分解见 [技术方案文档](技术方案文档.md#-开发任务分解)。

---

## 🔐 认证配置

### 环境变量配置

1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 填入配置：

```bash
# DeepSeek API（可选，无Key时自动使用规则匹配）
DEEPSEEK_API_KEY=sk-your-key-here

# SMTP邮件（可选，未配置时优雅降级）
EMAIL_SENDER=your-email@qq.com
EMAIL_PASSWORD=your-smtp-auth-code
```

### 邮箱授权码获取

- **QQ邮箱**：设置 → 账户 → POP3/SMTP服务 → 生成授权码
- **163邮箱**：设置 → POP3/SMTP/IMAP → 开启 → 新增授权码
- **Gmail**：需要开启"应用专用密码"

---

## 🧪 测试
```bash
运行所有测试
pytest
运行单元测试
pytest tests/unit/
运行集成测试
pytest tests/integration/
生成覆盖率报告
pytest --cov=. --cov-report=html
```
---

## 📊 性能指标

- **任务完成率**：≥ 92%（目标）
- **平均响应时间**：< 10秒
- **意图识别准确率**：≥ 95%
- **时间解析准确率**：≥ 98%

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 项目Issues：[提交问题](../../issues)
- 邮箱：[firstname.dh2005@outlook.com](mailto:firstname.dh2005@outlook.com)


---

## 🙏 致谢

感谢以下开源项目：
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Google APIs Client Library](https://github.com/googleapis/google-api-python-client)

---

<div align="center">

**如果这个项目对你有帮助，请考虑给它一个 ⭐️ Star！**

Made with ❤️ by CoderDongHuang

</div>

