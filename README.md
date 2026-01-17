# Local Knowledge Base Technical Documentation
## 1. Project Overview
This project is a knowledge base system built based on local Markdown documents, providing retrieval and Q&A functionality through a CLI interface. The main features include:

Efficient document retrieval based on vector storage
Support for multiple LLM APIs (Deepseek, Alibaba Cloud Bailian, etc.)
Intuitive CLI command-line interface
Option to return only answers (excluding source information)

## 2. Installation and Configuration
### 2.1 Environment Requirements

Python 3.8+
Valid API keys (Deepseek and Alibaba Cloud Bailian)

### 2.2 Installing Dependencies
Enter the project directory
```
cd local_knowledge_base

# Install dependencies
py -m pip install -r requirements.txt
```
### 2.3 Configuring API Keys
Create a .env file in the project root directory and add the following content:
DEEPSEEK_API_KEY=your_deepseek_api_key
DASHSCOPE_API_KEY=your_aliyun_dashscope_api_key
```
DEEPSEEK_API_KEY: Deepseek chat model API key
DASHSCOPE_API_KEY: Alibaba Cloud Bailian embedding model API key
```
## 3. Usage Guide
### 3.1 Building the Knowledge Base
Place Markdown documents into a directory, then execute the build command:
Replace "address of database" with the local knowledge base address
```
py -m src.main build --kb-dir "address of database" --persist-dir "./chroma_db"

--kb-dir: Directory containing Markdown documents
--persist-dir: Vector storage persistence directory (optional, default: ./chroma_db)
```
### 3.2 Single Question Query
```
# Return only answers (excluding sources)
py -m src.main ask "What's Coding Style？" --answer-only
# Or use shorthand
py -m src.main ask "What's Coding Style？" -a
```
### 3.3 Interactive Chat
```
py -m src.main chat
```
After entering interactive mode, you can ask questions continuously:

Press Enter after entering a question to get an answer
Type exit, quit, or q to exit the chat


# 本地知识库技术文档
## 1. 项目概述
本项目是一个基于本地Markdown文档构建的知识库系统，通过CLI界面提供检索问答功能。主要特点包括：

- 基于向量存储实现高效的文档检索
- 支持多种LLM API（Deepseek、阿里云百炼等）
- 提供直观的CLI命令行界面
- 可选择性仅返回答案（不包含来源信息）
## 2. 安装与配置
### 2.1 环境要求
- Python 3.8+
- 有效的API密钥（Deepseek和阿里云百炼）
### 2.2 安装依赖
```
# 进入项目目录
cd local_knowledge_base

# 安装依赖
py -m pip install -r requirements.txt
```
### 2.3 配置API密钥
在项目根目录创建 .env 文件，并添加以下内容：

```
DEEPSEEK_API_KEY=your_deepseek_api_key
DASHSCOPE_API_KEY=your_aliyun_dashscope_api_key
```
- DEEPSEEK_API_KEY : Deepseek聊天模型API密钥
- DASHSCOPE_API_KEY : 阿里云百炼embedding模型API密钥
## 3. 使用指南
### 3.1 构建知识库
将Markdown文档放入一个目录，然后执行build命令：
将address of database替换本地知识库地址
```
py -m src.main build --kb-dir "address of database" --persist-dir "./
chroma_db"
```
- --kb-dir : Markdown文档所在目录
- --persist-dir : 向量存储持久化目录（可选，默认：./chroma_db）
### 3.2 单个问题查询
```
# 仅返回答案（不包含来源）
py -m src.main ask "What's Coding Style？" --answer-only
# 或使用简写
py -m src.main ask "What's Coding Style？" -a
```
### 3.3 交互式聊天
```
py -m src.main chat
```
进入交互模式后，可以连续提问：

- 输入问题后按Enter获取答案
- 输入 exit 、 quit 或 q 退出聊天
