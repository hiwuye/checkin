# -*- coding: utf-8 -*-
"""
cron: 0 9 * * *
new Env('绿联NAS社区签到-Notify版');
"""

import requests
import os
import re
import sys

# ==================== 1. 调用 notify.py 通知模块 ====================
def send_notification(title, content):
    """
    调用青龙脚本目录下现有的 notify.py 发送通知
    """
    print("\n📣 正在尝试调用 notify.py 发送通知...")
    
    # 强制定位路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # 尝试导入 notify.py 里的 send 函数
        from notify import send
        send(title, content)
        print("✅ 通知推送指令已发出")
    except ImportError:
        print("❌ 导入失败：未在同级目录找到 notify.py 文件")
    except Exception as e:
        print(f"⚠️ 推送过程出现错误: {str(e)}")

# ==================== 2. 签到核心逻辑 ====================
cookie = os.getenv("UGNAS_COOKIE") or ""

def ugnas_task():
    if not cookie:
        return "❌ 错误：请在环境变量中设置 UGNAS_COOKIE"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Cookie": cookie,
        "Referer": "https://club.ugnas.com/forum.php"
    }

    session = requests.Session()
    log_content = []

    try:
        print("🚀 正在同步社区数据...")
        # 访问积分中心（此页面数据最稳）
        res = session.get("https://club.ugnas.com/home.php?mod=spacecp&ac=credit&showall=1", headers=headers, timeout=15)
        res.encoding = 'utf-8'
        html = res.text

        if "退出" not in html:
            return "❌ 登录失效，请更新环境变量 UGNAS_COOKIE"

        # --- 提取用户名 ---
        user_name = "未知用户"
        name_match = re.search(r'href="home\.php\?mod=space&amp;uid=\d+"[^>]*>([^<]+)</a>', html)
        if name_match:
            user_name = name_match.group(1).strip()

        # --- 提取积分 ---
        points = "未知"
        points_match = re.search(r'积分: (?:</em>)?(\d+)', html)
        if points_match:
            points = points_match.group(1)

        status_msg = f"👤 用户名称：{user_name}\n💰 当前积分：{points}\n✅ 账号状态：在线"
        print("-" * 30)
        print(status_msg)
        print("-" * 30)
        log_content.append(status_msg)

        # 触发签到
        session.get("https://club.ugnas.com/plugin.php?id=k_misign:sign", headers=headers, timeout=10)
        log_content.append("📢 签到结果：已完成自动签到触发")

        return "\n"。join(log_content)

    except Exception as e:
        return f"💥 运行异常: {str(e)}"

# ==================== 3. 执行入口 ====================
if __name__ == "__main__":
    # 执行任务
    final_msg = ugnas_task()
    
    # 组织通知信息
    from datetime import datetime
    today_str = datetime.当前().strftime('%Y-%m-%d %H:%M')
    
    # 发送通知
    send_notification("绿联社区签到报告"， f"{final_msg}\n⏰ 时间：{today_str}")
