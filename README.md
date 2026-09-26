# StudyAgent

按照Hello-Agents 教程学习思路，结合自己的代码与ai提供的部分代码，整合制作的面向初学者的智能学习助手。

## 一、StudyAgent解释

StudyAgent 围绕学习任务设计了三个简单工具，不是简单问答工具：

- `study_plan`：根据学习目标和时间制定学习计划
- `resource_search`：搜索示例学习资源
- `quiz_generator`：创建练习题任务

程序会根据用户输入的关键词决定是否使用工具：

```text
用户输入
   ↓
Agent 判断任务
   ↓
是否需要学习工具？
   ├── 是 → 调用工具 → 把结果交给大模型整理
   └── 否 → 直接让大模型解释知识
```
## 二、和 Hello-Agents 教程的关系

本成果主要参考了教程的第四、五、六章以及第十六章，借鉴了教程中的运行模式与思路以及部分代码。

教程中许多高级或复杂功能还未能进一步学习了解，只应用了较为基础的部分。

## 三、安装

建议 Python 3.10+。

```bash
pip install -r requirements.txt
```

## 四、配置 API

将.env.example改名为.env 然后填写：

```env
LLM_API_KEY=你的API_KEY
LLM_BASE_URL=你的OpenAI兼容接口地址
LLM_MODEL_ID=你的模型ID
```

## 五、运行

点击python main.py即可

## 六、使用例子
### 示例 1：学习计划

```text
输入：帮我制定一个30天的Python学习计划
```

Agent 会识别出这是学习计划任务，并使用计划模块输出

### 示例 2：学习资源

```text
输入：推荐一些日语学习资源
```

Agent 会寻找 `data/resources.json` 中写入的小部分示例资源。

### 示例 3：练习题

```text
输入：帮我生成5道Java练习题
```

Agent 会调用使用题目模块，让大模型根据工具结果生成适合初学者的练习。

### 示例 4：普通知识学习

```text
输入：什么是C++头文件？
```

Agent 会直接使用大模型输出结果。

## 七、项目结构

```text
StudyMateAgent/
|— main.py
|— README.md
|— requirements.txt
|— .env.example
|— example.png
|── data/
    |── resources.json
```
其中 `main.py` 为主程序，`example.png` 为运行实例

## 八、Agent 思路

本作品参照helloagents教程，使用教程中最基本的思路：

```text
感知 → 判断 → 行动 → 观察 → 回答
```

例如：

```text
输入：“帮我制定30天Python学习计划”
          ↓
Agent 判断：这是学习计划任务
          ↓
调用 study_plan
          ↓
得到计划
          ↓
大模型整理
          ↓
输出给用户
```

## 九、说明

本人没有太多python基础，成果思路的代码参考了教程，最终呈现也使用了部分ai的帮助，对教程的理解也并不是十分清楚，后续会精进python技术继续研究，多多谅解。
感谢datawhale的教程让我有了接触到研究智能体的机会。
```text
原教程仓库地址：https://github.com/datawhalechina/Hello-Agents
```
