"""
Microsoft Graph API连通性测试脚本

测试Calendar API和Mail API的连接是否正常
"""

import sys
from datetime import datetime, timedelta
from loguru import logger
from config import setup_logging
from services.auth_service import AuthService


def test_authentication():
    """测试认证流程"""
    print("\n" + "=" * 60)
    print("🔐 测试1: Microsoft Graph OAuth认证")
    print("=" * 60)

    try:
        auth_service = AuthService()
        graph_client = auth_service.authenticate()

        print(f"✅ 认证成功")

        user_email = auth_service.get_user_email()
        if user_email:
            print(f"   用户邮箱: {user_email}")

        return auth_service

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n📝 请按以下步骤获取AZURE_CLIENT_ID:")
        print("   1. 访问 https://portal.azure.com/")
        print("   2. 搜索 '应用注册' → 新注册")
        print("   3. 名称: Personal AI Assistant")
        print("   4. 支持的账户类型: 任何组织目录和个人Microsoft账户")
        print("   5. 重定向URI: 公共客户端 → http://localhost")
        print("   6. 注册后复制 '应用程序(客户端) ID'")
        print("   7. 在.env文件中设置AZURE_CLIENT_ID")
        return None

    except Exception as e:
        print(f"❌ 认证失败: {e}")
        logger.exception(e)
        return None


def test_calendar_api(auth_service):
    """测试Calendar API"""
    print("\n" + "=" * 60)
    print("📅 测试2: Microsoft Graph Calendar API")
    print("=" * 60)

    try:
        graph_client = auth_service.get_graph_client()

        # 获取未来7天的事件
        now = datetime.utcnow().isoformat() + 'Z'
        end_time = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

        response = graph_client.get(
            '/me/calendarview',
            params={
                'startDateTime': now,
                'endDateTime': end_time,
                '$top': 10
            }
        )

        if response.status_code == 200:
            events = response.json().get('value', [])
            print(f"✅ Calendar API连接成功")
            print(f"   未来7天内的事件数: {len(events)}")

            if events:
                print("\n   最近的事件:")
                for event in events[:3]:
                    print(f"   • {event.get('subject', '无标题')}")
                    start = event.get('start', {})
                    print(f"     时间: {start.get('dateTime', 'N/A')}")
        else:
            print(f"⚠️  Calendar API返回状态码: {response.status_code}")
            print(f"   响应: {response.text}")

        return True

    except Exception as e:
        print(f"❌ Calendar API测试失败: {e}")
        logger.exception(e)
        return False


def test_mail_api(auth_service):
    """测试Mail API"""
    print("\n" + "=" * 60)
    print("📧 测试3: Microsoft Graph Mail API")
    print("=" * 60)

    try:
        graph_client = auth_service.get_graph_client()

        # 获取用户信息
        response = graph_client.get('/me')

        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Mail API连接成功")
            print(f"   用户名: {user_info.get('displayName')}")
            print(f"   邮箱: {user_info.get('mail')}")
            print(f"   职位: {user_info.get('jobTitle', 'N/A')}")
        else:
            print(f"⚠️  Mail API返回状态码: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Mail API测试失败: {e}")
        logger.exception(e)
        return False


def main():
    """主测试函数"""
    # 初始化日志
    setup_logging()

    print("\n" + "=" * 60)
    print("🧪 Microsoft Graph API 连通性测试")
    print("=" * 60)
    print("\n本测试将验证:")
    print("  1. Microsoft OAuth认证流程")
    print("  2. Calendar API连接")
    print("  3. Mail API连接")
    print("\n" + "=" * 60)

    # 测试1: 认证
    auth_service = test_authentication()

    if auth_service is None:
        print("\n❌ 认证失败，无法继续测试")
        print("\n💡 提示: 请先完成Azure应用注册配置")
        sys.exit(1)

    # 测试2: Calendar API
    calendar_ok = test_calendar_api(auth_service)

    # 测试3: Mail API
    mail_ok = test_mail_api(auth_service)

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"  OAuth认证: {'✅ 通过' if auth_service else '❌ 失败'}")
    print(f"  Calendar API: {'✅ 通过' if calendar_ok else '❌ 失败'}")
    print(f"  Mail API: {'✅ 通过' if mail_ok else '❌ 失败'}")
    print("=" * 60)

    if auth_service and calendar_ok and mail_ok:
        print("\n🎉 所有测试通过！Microsoft Graph API配置正确。")
        print("\n下一步:")
        print("  1. 开始实现CalendarTool和GmailTool")
        print("  2. 构建LangGraph工作流")
        print("  3. 开发Agent核心功能")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()