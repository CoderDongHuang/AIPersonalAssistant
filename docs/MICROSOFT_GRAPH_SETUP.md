# Microsoft Graph API 配置指南

## 📋 前置要求

- Microsoft账号（Outlook/Hotmail均可）
- 可访问 [Azure Portal](https://portal.azure.com/)

## 🚀 快速开始

### 步骤1: 注册Azure应用

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 登录你的Microsoft账号
3. 搜索 **"应用注册"** 或访问 [直接链接](https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps)
4. 点击 **"新注册"**
5. 填写信息:
   - **名称**: `Personal AI Assistant`
   - **支持的账户类型**: 选择 **"任何组织目录和个人Microsoft账户"**
   - **重定向URI**: 
     - 平台: `公共客户端(移动和桌面)`
     - URI: `http://localhost`
6. 点击 **"注册"**

### 步骤2: 获取客户端ID

1. 注册成功后，进入应用概览页面
2. 复制 **"应用程序(客户端) ID"**
3. 这就是你的 `AZURE_CLIENT_ID`

### 步骤3: 配置API权限

1. 在左侧菜单点击 **"API权限"**
2. 点击 **"添加权限"**
3. 选择 **"Microsoft Graph"**
4. 选择 **"委托的权限"**
5. 添加以下权限:
   - ✅ `User.Read` - 读取用户信息
   - ✅ `Calendars.ReadWrite` - 日历读写
   - ✅ `Mail.Send` - 发送邮件
   - ✅ `Mail.Read` - 读取邮件
6. 点击 **"添加权限"**
7. ⚠️ **重要**: 点击 **"授予管理员同意"**（如果是个人账号，此步骤自动完成）

### 步骤4: 配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 填入你的 `AZURE_CLIENT_ID`:
```env 
AZURE_CLIENT_ID=你的客户端ID 
AZURE_TENANT_ID=common
```
### 步骤5: 测试连接
```bash
激活虚拟环境
.\venv\Scripts\Activate.ps1
安装依赖
pip install -r requirements.txt
运行测试
python test_microsoft_graph.py
```
首次运行会:
1. 自动打开默认浏览器
2. 要求登录Microsoft账号
3. 请求授权访问日历和邮件
4. 授权成功后自动返回终端
5. 缓存Token供后续使用

## 🔒 安全注意事项

### 保护敏感信息

- ✅ `.env` 文件已添加到 `.gitignore`
- ✅ 不要分享客户端ID和密钥
- ✅ 定期轮换凭证

### Token缓存

- Token缓存在 `.msal_cache.bin`
- 该文件也已加入 `.gitignore`
- 如需重新认证，删除缓存文件即可

## ❓ 常见问题

### Q1: 认证时提示"需要管理员同意"

**A**: 
- 对于个人Microsoft账号，不需要管理员同意
- 确保选择了正确的账户类型："任何组织目录和个人Microsoft账户"

### Q2: 找不到日历事件

**A**: 
- 确保你的Microsoft账号有Outlook日历
- 检查是否添加了 `Calendars.ReadWrite` 权限

### Q3: 发送邮件失败

**A**: 
- 确保添加了 `Mail.Send` 权限
- 检查收件人邮箱格式是否正确

## 📚 参考资源

- [Microsoft Graph文档](https://docs.microsoft.com/zh-cn/graph/)
- [Calendar API参考](https://docs.microsoft.com/zh-cn/graph/api/resources/calendar)
- [Mail API参考](https://docs.microsoft.com/zh-cn/graph/api/resources/mail-api-overview)
- [Azure应用注册指南](https://docs.microsoft.com/zh-cn/azure/active-directory/develop/quickstart-register-app)

