import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent #找到main
DATA_FILE = BASE_DIR / "data" / "resources.json"

load_dotenv(BASE_DIR / ".env") #导入.env

# 1. 资源库搜索
def resource_search(query: str) -> str:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: #识别中问
            resources = json.load(f)
    except Exception as e:
        return f"读取失败：{e}"

    query = query.strip().lower() #空格大小写
    if not query:
        return "没有提供关键词。"

    results = []
    for item in resources:
        text = json.dumps(item, ensure_ascii=False).lower()
        if query in text:
            results.append(item) #找关键词

    if not results:
        return f"没有找到“{query}”相关内容。"

    lines = ["找到以下学习资源："]
    for i, item in enumerate(results[:5], 1):
        lines.append(
            f"{i}. {item['name']}：{item['description']}（适合：{item['level']}）"
        )
    return "\n".join(lines)

# 2. 计划工具
def study_plan(topic: str, days: int) -> str:
    if days <= 0:
        return "学习天数必须大于 0。"

    if days <= 7: #天数分布任务
        stages = [
            ("基础认识", 0.30),
            ("重点学习", 0.40),
            ("练习巩固", 0.30),
        ]
    else:
        stages = [
            ("基础认识", 0.20),
            ("核心知识", 0.40),
            ("专项练习", 0.25),
            ("复习总结", 0.15),
        ]

    lines = [f"学习主题：{topic}", f"计划周期：{days} 天", "", "学习安排："]
    start = 1
    for name, ratio in stages:
        count = max(1, round(days * ratio))
        end = min(days, start + count - 1)
        lines.append(f"- 第 {start}-{end} 天：{name}")
        start = end + 1
        if start > days:
            break

    return "\n".join(lines)



# 3. 练习题工具
def quiz_generator(topic: str, count: int) -> str:
    count = max(1, min(count, 10)) #按数量创造题目
    return (
        f"练习任务已创建：主题={topic}，题目数量={count}。\n"
        "请根据这个任务生成适合初学者的练习题，并在题目后提供参考答案。"
    )

# 4. StudyAgent主体
class StudyAgent:
    def __init__(self):
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL_ID") #读取api配置

        if not api_key or not base_url or not model:
            raise RuntimeError(
                "请先配置 .env 文件中的 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL_ID。"
            ) #防止没配置

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        self.system_prompt = """
你是 StudyAgent，面向初学者的智能学习助手。
你的主要任务是帮助用户完成学习任务，不用聊天：
1. 理解目标；
2. 制定计划；
3. 推荐资源；
4. 生成题目；
5. 解释并帮助用户复习。
如果问题与学习没有明显关系，可以简短回答
注意要面向初学者，回答时尽量清楚、简洁，适合初学者理解。
"""

    def choose_tool(self, user_input: str): #判断用户要干嘛 找关键词
        text = user_input.lower()

        if any(k in text for k in ["学习计划", "学习安排", "计划", "多少天学"]):
            return "study_plan"

        if any(k in text for k in ["学习资源", "资料", "教材", "课程", "推荐资源"]):
            return "resource_search"

        if any(k in text for k in ["练习题", "测试题", "题目", "测验", "习题"]):
            return "quiz_generator"

        return None

    def run_tool(self, tool_name: str, user_input: str) -> str:
        if tool_name == "study_plan":   # 尝试读取“主题 天数”
            days = 30
            for token in user_input.replace("；", " ").replace("，", " ").split():
                if token.isdigit():
                    days = int(token)
                    break

            topic = user_input
            for word in ["学习计划", "学习安排", "帮我", "请", "制定", "制定一个"]:
                topic = topic.replace(word, "")
            topic = topic.strip(" ：:，,。")

            return study_plan(topic or "目标学习内容", days)

        if tool_name == "resource_search":
            query = user_input
            for word in ["学习资源", "推荐资源", "资料", "教材", "课程", "帮我", "请", "搜索"]:
                query = query.replace(word, "")
            query = query.strip(" ：:，,。")
            return resource_search(query or user_input)

        if tool_name == "quiz_generator":
            count = 5
            for token in user_input.replace("；", " ").replace("，", " ").split():
                if token.isdigit():
                    count = int(token)
                    break

            topic = user_input
            for word in ["练习题", "测试题", "题目", "测验", "习题", "帮我", "请", "生成", "出"]:
                topic = topic.replace(word, "")
            topic = topic.strip(" ：:，,。")

            return quiz_generator(topic or "当前学习内容", count)

        return "没有找到对应工具。"

    def ask_llm(self, user_input: str, tool_result: str = "") -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if tool_result:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"用户需求：{user_input}\n\n"
                        f"StudyMateAgent 工具执行结果：\n{tool_result}\n\n"
                        "请结合工具，整理学习建议。"
                    ),
                }
            )
        else:
            messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create( #调用api
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content

    def run(self, user_input: str) -> str:  #串联
        tool_name = self.choose_tool(user_input)

        if tool_name:
            print(f"\n[Agent] 判断需要使用工具：{tool_name}")
            tool_result = self.run_tool(tool_name, user_input)
            print("[Agent] 工具执行完成，正在整理结果...\n")
            return self.ask_llm(user_input, tool_result)

        print("\n[Agent] 当前问题不需要调用学习工具，直接进行知识讲解...\n")
        return self.ask_llm(user_input)


def main():
    print("=" * 55)
    print("StudyAgent - 初学者智能学习助手")
    print("=" * 55)
    print("功能包含：")
    print("1. 询问学习计划")
    print("2. 推荐学习资源")
    print("3. 生成练习题")
    print("4. 相关领域知识")
    print("可调用工具关键词有计划、资源、练习题等")
    print("输入 exit / quit 退出程序。")
    print("-" * 55)

    try:
        agent = StudyAgent()
    except Exception as e:
        print(f"\n启动失败：{e}")
        return

    while True:
        user_input = input("\n请输入：").strip()

        if user_input.lower() in {"exit", "quit", "退出"}:
            print("StudyMateAgent：下次学习见！")
            break

        if not user_input:
            continue

        try:
            answer = agent.run(user_input) #开始
            print("StudyAgent：")
            print(answer)
        except Exception as e:
            print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
