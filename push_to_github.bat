@echo off
echo 正在推送 NPC 聊天功能到 GitHub...
echo.

echo 检查 Git 状态...
git status
echo.

echo 检查网络连接...
ping github.com -n 2
echo.

echo 尝试推送到远程仓库...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 推送成功！
    echo 🎉 NPC 聊天功能已成功推送到 GitHub
) else (
    echo.
    echo ❌ 推送失败，可能的原因：
    echo 1. 网络连接问题
    echo 2. 防火墙或代理设置
    echo 3. GitHub 访问限制
    echo.
    echo 💡 建议解决方案：
    echo 1. 检查网络连接
    echo 2. 尝试使用 VPN 或其他网络环境
    echo 3. 稍后重试：git push origin main
)

echo.
echo 按任意键退出...
pause >nul