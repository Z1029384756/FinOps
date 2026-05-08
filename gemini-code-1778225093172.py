import json
import time

# ==========================================
# 1. 定义外部工具 (Tools / Function Calling)
# ==========================================

def get_cloud_metrics(instance_id: str) -> str:
    """模拟调用 AWS/阿里云 API 获取实例过去 7 天的 CPU 和网络指标"""
    print(f"🔧 [Tool Call] 正在拉取实例 {instance_id} 的监控指标...")
    time.sleep(1)
    # 模拟一个长期闲置的“僵尸实例”数据
    return json.dumps({
        "instance_id": instance_id,
        "status": "running",
        "avg_cpu_utilization_7d": "1.2%",
        "max_cpu_utilization_7d": "3.5%",
        "network_in_bytes_7d": "1024",
        "network_out_bytes_7d": "512"
    })

def generate_terraform_script(action: str, instance_id: str) -> str:
    """根据动作指令生成自动化 Terraform 脚本"""
    print(f"🔧 [Tool Call] 正在生成 Terraform 脚本，动作：{action}...")
    time.sleep(1)
    if action == "stop":
        script = f"""
resource "aws_ec2_instance_state" "auto_stop_{instance_id}" {{
  instance_id = "{instance_id}"
  state       = "stopped"
}}
"""
        return script
    return "Error: Unsupported action."

def send_slack_approval(instance_id: str, reason: str, tf_script: str) -> str:
    """向运维团队发送 Slack 审批卡片"""
    print(f"🔧 [Tool Call] 正在发送 Slack 审批请求...")
    message = f"🚨 【FinOps 优化建议】\n实例：{instance_id}\n原因：{reason}\n建议操作代码：\n```hcl\n{tf_script}\n```\n请回复 [Approve/Reject] 进行审批。"
    # 模拟发送成功
    return "Slack approval request sent successfully."

# ==========================================
# 2. 核心智能体类 (The Agent)
# ==========================================

class FinOpsAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        # 注册工具清单，供 LLM 知道自己可以使用哪些外部能力
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_cloud_metrics",
                    "description": "获取指定云服务器实例过去7天的监控指标，包括CPU和网络流量。",
                    "parameters": {"type": "object", "properties": {"instance_id": {"type": "string"}}, "required": ["instance_id"]}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_terraform_script",
                    "description": "生成用于关闭或修改实例配置的 Terraform 脚本。",
                    "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["stop", "terminate"]}, "instance_id": {"type": "string"}}, "required": ["action", "instance_id"]}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_slack_approval",
                    "description": "向人类管理员发送包含原因和代码的 Slack 审批请求。",
                    "parameters": {"type": "object", "properties": {"instance_id": {"type": "string"}, "reason": {"type": "string"}, "tf_script": {"type": "string"}}, "required": ["instance_id", "reason", "tf_script"]}
                }
            }
        ]
        
        # 设定系统 Prompt，赋予其专家人设和推理长链
        self.system_prompt = """
        你是公司的高级 FinOps 云成本优化专家 Agent。你的目标是扫描云资源，识别浪费并执行优化。
        
        你的执行逻辑链（长链推理）如下：
        1. 使用 get_cloud_metrics 获取实例数据。
        2. 分析数据：如果过去7天平均 CPU 使用率低于 5% 且网络流量极低，判定为“闲置僵尸实例”。
        3. 如果判定为闲置，调用 generate_terraform_script 生成关闭(stop)该实例的脚本。
        4. 调用 send_slack_approval，将你的分析原因和脚本发送给人类审批。
        
        请一步步执行，不要跳过必要的分析过程。
        """

    def run_diagnosis(self, instance_id: str):
        print(f"\n🚀 开始 FinOps 诊断流程，目标资源: {instance_id}\n" + "="*50)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请对实例 {instance_id} 进行成本优化诊断，并执行必要的操作。"}
        ]

        # ---------------------------------------------------------
        # 以下为模拟大模型对话循环 (Agent Loop)
        # 实际开发中会使用 client.chat.completions.create(...)
        # ---------------------------------------------------------
        
        # 步骤 1: LLM 决定调用 get_cloud_metrics
        metrics_result = get_cloud_metrics(instance_id)
        messages.append({"role": "function", "name": "get_cloud_metrics", "content": metrics_result})
        
        # 步骤 2: LLM 分析指标后，决定调用 generate_terraform_script
        print(f"🧠 [Agent Reasoning] 分析指标中：发现过去7天 CPU 平均使用率仅 1.2%，网络几乎停滞。判定为僵尸实例，准备生成降本脚本...")
        time.sleep(1.5)
        tf_result = generate_terraform_script("stop", instance_id)
        messages.append({"role": "function", "name": "generate_terraform_script", "content": tf_result})
        
        # 步骤 3: LLM 拿到脚本后，决定调用 send_slack_approval
        print(f"🧠 [Agent Reasoning] 脚本生成完毕，准备通知人类审批...")
        time.sleep(1)
        reason = f"实例 {instance_id} 过去 7 天平均 CPU 负载为 1.2%，流入流出流量极低，疑似被遗忘的测试机器，建议停机以节约成本。"
        slack_result = send_slack_approval(instance_id, reason, tf_result)
        
        print("\n✅ 诊断任务执行完毕。等待运维团队 Slack 审批确认后生效。")
        print("="*50)

# ==========================================
# 3. 运行测试
# ==========================================
if __name__ == "__main__":
    # 假设传入一个模拟的 llm 客户端
    agent = FinOpsAgent(llm_client="Mock_LLM_Client")
    
    # 传入一个疑似闲置的实例 ID
    agent.run_diagnosis(instance_id="i-0abcd1234efgh5678")