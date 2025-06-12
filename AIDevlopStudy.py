"""
MCP Server - AI需求分析和设计助手
协助AI初级开发者完善需求分析和架构设计

包含三个核心工具：
1. requirement_clarifier - 需求澄清助手
2. requirement_manager - 需求文档管理器  
3. architecture_designer - 架构设计生成器
"""

import logging
import os
import json
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("StudyAIDevelop", description="AI需求分析和设计助手")

# 配置存储目录
def get_storage_dir():
    """获取存储目录，优先使用环境变量配置"""
    env_dir = os.getenv("MCP_STORAGE_DIR", "./mcp_data")
    storage_dir = Path(env_dir)
    storage_dir.mkdir(exist_ok=True)
    return storage_dir

# 全局需求文档存储
current_requirements = {
    "project_overview": [],
    "functional_requirements": [],
    "technical_requirements": [],
    "design_requirements": [],
    "deployment_requirements": [],
    "ai_constraints": [],
    "clarification_history": [],
    "architecture_designs": [],
    "last_updated": None,
    "project_id": None
}

# 存储管理类
class RequirementStorage:
    def __init__(self):
        self.storage_dir = get_storage_dir()
        self.requirements_file = self.storage_dir / "requirements.json"
        self.history_file = self.storage_dir / "history.json"
        self.load_requirements()

    def load_requirements(self):
        """加载已保存的需求文档"""
        global current_requirements
        try:
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    current_requirements.update(saved_data)
                logger.info(f"✅ 已加载需求文档: {self.requirements_file}")
        except Exception as e:
            logger.warning(f"⚠️ 加载需求文档失败: {e}")

    def save_requirements(self):
        """保存需求文档到文件"""
        try:
            current_requirements["last_updated"] = datetime.now().isoformat()
            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                json.dump(current_requirements, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 需求文档已保存: {self.requirements_file}")
        except Exception as e:
            logger.error(f"❌ 保存需求文档失败: {e}")

    def save_history_entry(self, entry_type: str, content: str, metadata: dict = None):
        """保存历史记录条目"""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "content": content,
                "metadata": metadata or {}
            }

            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

            history.append(history_entry)

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 历史记录已保存: {entry_type}")
        except Exception as e:
            logger.error(f"❌ 保存历史记录失败: {e}")

    def export_final_document(self):
        """导出最终的完整需求和架构文档"""
        try:
            final_doc = {
                "project_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "project_id": current_requirements.get("project_id"),
                    "last_updated": current_requirements.get("last_updated")
                },
                "requirements": current_requirements,
                "export_format": "markdown"
            }

            export_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(final_doc, f, ensure_ascii=False, indent=2)

            # 同时生成Markdown格式
            md_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self.generate_markdown_report(md_file)

            logger.info(f"✅ 最终文档已导出: {export_file}")
            return str(export_file)
        except Exception as e:
            logger.error(f"❌ 导出最终文档失败: {e}")
            return None

    def generate_markdown_report(self, md_file: Path):
        """生成Markdown格式的报告"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("# 🚀 AI开发项目需求与架构文档\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 项目概述
                if current_requirements.get("project_overview"):
                    f.write("## 📋 项目概述\n\n")
                    for item in current_requirements["project_overview"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 功能需求
                if current_requirements.get("functional_requirements"):
                    f.write("## ⚙️ 功能需求\n\n")
                    for item in current_requirements["functional_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 技术需求
                if current_requirements.get("technical_requirements"):
                    f.write("## 🔧 技术需求\n\n")
                    for item in current_requirements["technical_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 架构设计
                if current_requirements.get("architecture_designs"):
                    f.write("## 🏗️ 架构设计\n\n")
                    for design in current_requirements["architecture_designs"]:
                        f.write(f"{design}\n\n")

                # 澄清历史
                if current_requirements.get("clarification_history"):
                    f.write("## 📝 需求澄清历史\n\n")
                    for item in current_requirements["clarification_history"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

            logger.info(f"✅ Markdown报告已生成: {md_file}")
        except Exception as e:
            logger.error(f"❌ 生成Markdown报告失败: {e}")

# 初始化存储管理器
storage = RequirementStorage()

# 需求澄清助手工具
@mcp.tool()
def requirement_clarifier(user_input: str, context: str = "") -> str:
    """需求澄清助手 - 分析用户需求完整性，主动发现不明确的地方"""

    # 保存澄清历史
    clarification_entry = f"用户输入: {user_input} | 上下文: {context}"
    current_requirements["clarification_history"].append({
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "context": context
    })
    storage.save_history_entry("requirement_clarification", user_input, {"context": context})
    storage.save_requirements()

    analysis_prompt = f"""# 🔍 AI需求分析任务 - 必须完成

## 📝 用户输入
{user_input}

## 📋 当前上下文
{context}

## 🎯 你的分析任务（AI助手必须执行）

### 1. 项目类型识别
根据用户描述，判断项目类型：
- **Web应用**：网站、Web系统、在线平台
- **移动应用**：手机APP、移动端应用
- **桌面应用**：PC软件、桌面工具
- **小程序**：微信小程序、支付宝小程序
- **通用项目**：其他类型或混合项目

### 2. 需求完整性深度分析
检查以下关键维度是否明确：

**🎯 项目目标维度**
- 解决什么具体问题？
- 目标用户群体是谁？
- 预期达到什么效果？

**⚙️ 功能需求维度**
- 核心功能有哪些？（最重要的3-5个）
- 次要功能有哪些？
- 功能的优先级如何？

**🔧 技术需求维度**
- 有技术栈偏好吗？
- 性能要求如何？
- 兼容性要求？

**🎨 用户体验维度**
- 界面风格偏好？
- 交互方式要求？

**📊 规模和性能维度**
- 预期用户规模？
- 并发量要求？

**🚀 部署和维护维度**
- 部署环境偏好？
- 维护方式？

### 3. 智能澄清策略
生成2-3个最重要的澄清问题：
- 优先澄清对项目影响最大的方面
- 提供具体选项帮助用户理解
- 使用友好语言，避免过于技术化

## 📤 输出格式要求

**🔍 需求分析结果：**
- **项目类型**：[明确识别的类型]
- **已明确信息**：[用户已经清楚表达的需求点]
- **需要澄清**：[不明确、有歧义或缺失的关键信息]

**❓ 关键澄清问题：**
1. [最重要的澄清问题，包含选项]
2. [第二重要的问题，提供示例]
3. [第三个问题，如果需要的话]

**💡 专业建议：**
[基于分析给出的建议和提示]

**🎯 下一步指导：**
[告诉用户接下来应该如何回答或思考]

---
*重要提醒：每次澄清后，请使用 requirement_manager 工具保存明确的需求信息！*
"""

    return analysis_prompt

# 需求文档管理器工具
@mcp.tool()
def requirement_manager(clarified_info: str, category: str) -> str:
    """需求文档管理器 - 实时更新和维护结构化的需求文档"""

    # 根据类别保存到对应的需求分类中
    category_mapping = {
        "项目概述": "project_overview",
        "核心功能需求": "functional_requirements",
        "功能和UI需求": "functional_requirements",
        "功能需求": "functional_requirements",
        "技术需求": "technical_requirements",
        "技术和设计约束": "technical_requirements",
        "设计需求": "design_requirements",
        "部署需求": "deployment_requirements",
        "AI约束": "ai_constraints"
    }

    # 确定存储类别
    storage_category = category_mapping.get(category, "functional_requirements")

    # 添加到对应类别
    requirement_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "content": clarified_info
    }

    current_requirements[storage_category].append(requirement_entry)

    # 保存到文件
    storage.save_history_entry("requirement_update", clarified_info, {"category": category})
    storage.save_requirements()

    # 统计当前需求数量
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])

    result = f"""# ✅ 需求文档已更新

## 📝 更新信息
- **类别**：{category}
- **内容**：{clarified_info}
- **时间**：{datetime.now().isoformat()}
- **存储位置**：{storage.requirements_file}

## 📋 当前需求文档状态
- **总需求条目**：{total_requirements}
- **项目概述**：{len(current_requirements['project_overview'])} 条
- **功能需求**：{len(current_requirements['functional_requirements'])} 条
- **技术需求**：{len(current_requirements['technical_requirements'])} 条
- **设计需求**：{len(current_requirements['design_requirements'])} 条

## 💾 持久化存储
- ✅ 需求已保存到: `{storage.requirements_file}`
- ✅ 历史记录已保存到: `{storage.history_file}`

## 🎯 下一步建议
继续使用 requirement_clarifier 完善其他需求信息，或在需求完整后使用 architecture_designer 生成架构设计。
"""

    return result

# 架构设计生成器工具
@mcp.tool()
def architecture_designer(design_focus: str = "full_architecture") -> str:
    """架构设计生成器 - 基于完整需求生成最优技术架构方案"""

    # 生成架构设计
    architecture_design = f"""# 🏗️ 项目架构设计方案

## 🎯 设计目标
- **设计重点**：{design_focus}
- **优化目标**：AI友好、低耦合、可维护

## 🏛️ 架构设计原则（针对AI开发优化）

### 1. 低耦合设计原则
- **模块独立性**：每个模块功能单一，边界清晰
- **接口标准化**：统一的API接口规范
- **依赖最小化**：减少模块间的强依赖关系
- **错误隔离**：单个模块问题不影响整体系统

### 2. AI友好架构原则
- **代码可理解性**：清晰的命名和注释规范
- **模块化开发**：避免大文件，便于AI理解和修改
- **标准化结构**：统一的项目结构和代码组织
- **渐进式开发**：支持分阶段实现和测试

## 🔧 技术架构建议

### 前端架构
**推荐技术栈：**
- 框架：React 18 / Vue 3 / Next.js 15
- 状态管理：Redux Toolkit / Zustand / Pinia
- UI组件：Ant Design / Material-UI / Tailwind CSS

### 后端架构
**推荐技术栈：**
- 框架：FastAPI / Express.js / Spring Boot
- 数据库：PostgreSQL / MySQL / MongoDB
- 缓存：Redis / Memcached

## 📦 功能模块划分

### 核心业务模块
1. **用户管理模块**
   - 功能：用户注册、登录、权限管理
   - 接口：用户CRUD、认证API
   - AI开发提示：先实现基础认证，再添加高级功能

2. **业务核心模块**
   - 功能：[根据具体需求定制]
   - 接口：业务逻辑API、数据处理接口
   - AI开发提示：按功能优先级逐步实现

## 📅 开发阶段规划

### 第一阶段：基础框架搭建（1-2周）
- 项目初始化和环境配置
- 基础框架代码搭建
- 数据库设计和初始化

### 第二阶段：核心功能开发（2-4周）
- 用户管理功能实现
- 核心业务逻辑开发
- 前端主要页面实现

### 第三阶段：功能完善和优化（1-3周）
- 次要功能实现
- 性能优化和调试
- 用户体验优化

## 🤖 AI开发最佳实践

### 模块开发指导
1. **先实现核心逻辑**：专注主要功能
2. **再添加错误处理**：完善异常处理
3. **最后进行优化**：性能优化和代码重构

### 接口设计规范
- GET /api/users - 获取用户列表
- POST /api/users - 创建用户
- PUT /api/users/:id - 更新用户
- DELETE /api/users/:id - 删除用户

## 🎯 总结和建议

### 架构优势
1. **低耦合设计**：模块独立，便于维护和扩展
2. **AI友好**：清晰的结构，便于AI理解和开发
3. **可扩展性**：支持业务增长和功能扩展

### 实施建议
1. **分阶段实施**：按计划逐步实现
2. **持续测试**：每个阶段都要进行充分测试
3. **文档同步**：及时更新文档

---

**🎉 架构设计完成！**

这个架构设计方案专门针对AI开发进行了优化，确保低耦合、AI友好的开发体验！

## 💾 文档存储信息
- **架构设计已保存到**: `{storage.requirements_file}`
- **完整文档导出**: 使用 `export_final_document` 工具导出完整项目文档
"""

    # 保存架构设计到需求文档
    architecture_entry = {
        "timestamp": datetime.now().isoformat(),
        "design_focus": design_focus,
        "content": architecture_design
    }

    current_requirements["architecture_designs"].append(architecture_entry)

    # 保存到文件
    storage.save_history_entry("architecture_design", architecture_design, {"design_focus": design_focus})
    storage.save_requirements()

    return architecture_design

# 新增：导出最终文档工具
@mcp.tool()
def export_final_document() -> str:
    """导出完整的项目需求和架构文档"""

    export_path = storage.export_final_document()

    if export_path:
        # 统计信息
        total_clarifications = len(current_requirements.get("clarification_history", []))
        total_requirements = sum(len(current_requirements[key]) for key in [
            "project_overview", "functional_requirements", "technical_requirements",
            "design_requirements", "deployment_requirements", "ai_constraints"
        ])
        total_architectures = len(current_requirements.get("architecture_designs", []))

        result = f"""# 📄 项目文档导出完成

## ✅ 导出信息
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文件路径**: `{export_path}`
- **Markdown版本**: `{export_path.replace('.json', '.md')}`

## 📊 文档统计
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}

## 📁 存储目录结构
```
{storage.storage_dir}/
├── requirements.json      # 实时需求文档
├── history.json          # 操作历史记录
├── final_document_*.json # 导出的完整文档
└── final_document_*.md   # Markdown格式报告
```

## 🎯 文档用途
- **requirements.json**: 实时更新的结构化需求数据
- **history.json**: 完整的操作历史，便于追溯
- **final_document_*.json**: 完整项目文档，包含所有信息
- **final_document_*.md**: 人类可读的Markdown报告

## 💡 使用建议
1. 将导出的文档保存到项目仓库中
2. 使用Markdown文件作为项目README的基础
3. JSON文件可用于后续的自动化处理

**🎉 项目文档已完整保存，可以开始开发了！**
"""
    else:
        result = """# ❌ 文档导出失败

请检查存储目录权限和磁盘空间。

**存储目录**: `{storage.storage_dir}`
"""

    return result

# 新增：查看当前需求状态工具
@mcp.tool()
def view_requirements_status() -> str:
    """查看当前需求文档的详细状态和内容"""

    # 统计信息
    total_clarifications = len(current_requirements.get("clarification_history", []))
    total_requirements = sum(len(current_requirements[key]) for key in [
        "project_overview", "functional_requirements", "technical_requirements",
        "design_requirements", "deployment_requirements", "ai_constraints"
    ])
    total_architectures = len(current_requirements.get("architecture_designs", []))

    # 构建状态报告
    status_report = f"""# 📋 当前需求文档状态

## 📊 总体统计
- **最后更新**: {current_requirements.get('last_updated', '未更新')}
- **需求澄清次数**: {total_clarifications}
- **需求条目总数**: {total_requirements}
- **架构设计方案**: {total_architectures}
- **存储位置**: `{storage.storage_dir}`

## 📝 需求分类详情

### 🎯 项目概述 ({len(current_requirements['project_overview'])} 条)
"""

    # 添加项目概述
    for i, item in enumerate(current_requirements['project_overview'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### ⚙️ 功能需求 ({len(current_requirements['functional_requirements'])} 条)
"""

    # 添加功能需求
    for i, item in enumerate(current_requirements['functional_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🔧 技术需求 ({len(current_requirements['technical_requirements'])} 条)
"""

    # 添加技术需求
    for i, item in enumerate(current_requirements['technical_requirements'], 1):
        content = item['content'] if isinstance(item, dict) else str(item)
        status_report += f"{i}. {content[:100]}{'...' if len(content) > 100 else ''}\n"

    status_report += f"""
### 🏗️ 架构设计 ({len(current_requirements['architecture_designs'])} 个)
"""

    # 添加架构设计
    for i, design in enumerate(current_requirements['architecture_designs'], 1):
        focus = design.get('design_focus', '未指定') if isinstance(design, dict) else '未指定'
        timestamp = design.get('timestamp', '未知时间') if isinstance(design, dict) else '未知时间'
        status_report += f"{i}. 设计重点: {focus} (生成时间: {timestamp[:19]})\n"

    status_report += f"""
## 📁 文件信息
- **需求文档**: `{storage.requirements_file}`
- **历史记录**: `{storage.history_file}`
- **文件大小**: 需求文档 {storage.requirements_file.stat().st_size if storage.requirements_file.exists() else 0} 字节

## 🎯 下一步建议
"""

    if total_requirements < 3:
        status_report += "- 📝 需求信息较少，建议继续使用 requirement_clarifier 澄清更多需求\n"

    if total_architectures == 0:
        status_report += "- 🏗️ 尚未生成架构设计，建议使用 architecture_designer 生成技术方案\n"

    if total_requirements >= 3 and total_architectures >= 1:
        status_report += "- 📄 需求和架构已基本完善，可以使用 export_final_document 导出完整文档\n"
        status_report += "- 🚀 可以开始项目开发了！\n"

    status_report += """
## 🛠️ 可用工具
- `requirement_clarifier`: 澄清和分析需求
- `requirement_manager`: 管理和保存需求
- `architecture_designer`: 生成架构设计
- `export_final_document`: 导出完整文档
- `view_requirements_status`: 查看当前状态（当前工具）
"""

    return status_report

if __name__ == "__main__":
    logger.info("🚀 启动AI需求分析和设计助手")
    mcp.run()