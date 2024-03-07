# quartzyItemSearch


# Quartzy CSV Analyzer

## 项目概述

Quartzy CSV Analyzer 是一个基于 Python 和 tkinter 的 GUI 应用程序，专为处理和分析从 Quartzy 网站下载的统计 CSV 文件设计。它提供了一个简单的界面，用于加载 CSV 文件、查询数据、并可视化统计结果，如每个项目每月的购买数量和金额。

## 功能

- **数据加载**：用户可以加载从 Quartzy 网站下载的 CSV 文件。
- **查询功能**：
  - **按数量查询** (`SearchForQty`)：用户可以查询每个项目每月的购买数量。
  - **按金额查询** (`SearchForMoney`)：用户可以查询每个项目每月的总花费。
  - **详细查询** (`SearchForDetail`)：用户可以查询具体项目的购买详情，包括购买日期和次数。
- **数据可视化**：为选定的查询结果提供图表展示。

## 安装

确保您的系统已安装 Python 3。此外，您需要安装以下依赖：

```bash
pip install pandas matplotlib
```

## 使用说明

1. 启动应用程序：

```bash
python quartzyItemSearch.py
```

2. 使用**加载 CSV** 功能选择并加载您的 CSV 文件。
3. 通过选项卡切换到 **按数量查询**、**按金额查询** 或 **详细查询** 进行数据查询和查看。
4. 在查询结果中，点击具体项目或日期获取更多详情。

## CSV 文件格式

您的 CSV 文件应包含以下列（示例）：

```
Item Name, Requested By, Lab Name, Vendor, Catalog #, Type, Spend Tracking Code, Other Details, Qty, Unit Size, URL, Unit Price, Total Price, Date Ordered, ...
```

确保您的 CSV 文件遵循此格式以确保应用程序可以正确处理数据。

## 开发

- **语言**：Python 3
- **GUI 框架**：tkinter
- **数据处理**：pandas

