"""
Microsoft Graph API 认证服务

负责Microsoft Graph的身份验证和授权管理
支持Calendar API和Mail API的认证
"""

import os
from typing import Optional
from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient
from loguru import logger
from config.settings import settings


class AuthService:
    """Microsoft Graph OAuth认证服务"""

    # Microsoft Graph API所需权限范围
    SCOPES = [
        'User.Read',                # 读取用户信息
        'Calendars.ReadWrite',      # 日历读写
        'Mail.Send',                # 发送邮件
        'Mail.Read'                 # 读取邮件（获取参会人）
    ]

    def __init__(self,
                 client_id: str = None,
                 tenant_id: str = 'common'):
        """
        初始化认证服务

        Args:
            client_id: Azure应用客户端ID
            tenant_id: 租户ID（默认common，支持多租户）
        """
        self.client_id = client_id or os.getenv('AZURE_CLIENT_ID')
        self.tenant_id = tenant_id
        self._credential: Optional[InteractiveBrowserCredential] = None
        self._graph_client: Optional[GraphClient] = None

        logger.info("AuthService 初始化 (Microsoft Graph)")
        logger.debug(f"Client ID: {self.client_id}")
        logger.debug(f"Tenant ID: {self.tenant_id}")
        logger.debug(f"Scopes: {self.SCOPES}")

    def authenticate(self) -> GraphClient:
        """
        执行认证流程

        Returns:
            GraphClient: Microsoft Graph客户端

        Raises:
            ValueError: 缺少必要的配置
            Exception: 认证失败
        """
        # 检查配置
        if not self.client_id:
            logger.error("❌ 缺少AZURE_CLIENT_ID配置")
            logger.error("请在.env文件中设置AZURE_CLIENT_ID")
            raise ValueError(
                "Azure Client ID is required.\n"
                "Please set AZURE_CLIENT_ID in .env file"
            )

        try:
            logger.info("🔐 启动Microsoft Graph认证流程...")

            # 创建交互式浏览器凭据
            self._credential = InteractiveBrowserCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id
            )

            logger.info("🌐 即将打开浏览器进行授权...")
            logger.info("请使用Microsoft账号登录并授权")

            # 创建Graph客户端
            self._graph_client = GraphClient(credential=self._credential)

            # 测试连接
            test_result = self._graph_client.get('/me')
            if test_result.status_code == 200:
                user_info = test_result.json()
                logger.info(f"✅认证成功: {user_info.get('displayName')}")
                logger.info(f"   邮箱: {user_info.get('mail')}")
            else:
                logger.warning(f"⚠️  认证测试返回状态码: {test_result.status_code}")

            logger.info("✅ Microsoft Graph认证成功")
            return self._graph_client

        except Exception as e:
            logger.error(f"❌ 认证失败: {e}")
            raise

    def get_graph_client(self) -> Optional[GraphClient]:
        """
        获取Graph客户端（如果已认证）

        Returns:
            GraphClient或None
        """
        if self._graph_client is None:
            logger.warning("⚠️  尚未进行认证，请先调用authenticate()")
        return self._graph_client

    def get_credential(self):
        """
        获取凭据对象

        Returns:
            InteractiveBrowserCredential或None
        """
        return self._credential

    def revoke_access(self):
        """撤销授权（清除缓存）"""
        self._credential = None
        self._graph_client = None
        logger.info("🗑️  已撤销授权")

    def get_user_email(self) -> Optional[str]:
        """
        获取当前授权用户的邮箱地址

        Returns:
            用户邮箱或None
        """
        if self._graph_client is None:
            logger.warning("⚠️  尚未认证")
            return None

        try:
            response = self._graph_client.get('/me')
            if response.status_code == 200:
                user_info = response.json()
                return user_info.get('mail') or user_info.get('userPrincipalName')
        except Exception as e:
            logger.warning(f"⚠️  获取用户邮箱失败: {e}")

        return None


# 全局认证服务实例
def create_auth_service():
    """创建认证服务实例"""
    from config.settings import settings
    return AuthService(
        client_id=settings.AZURE_CLIENT_ID,
        tenant_id=settings.AZURE_TENANT_ID
    )

auth_service = create_auth_service()
