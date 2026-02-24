@echo off
echo ========================================
echo 图片评估代理工具 - 安装脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)
python --version

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/3] 检查配置文件...
if not exist config.yaml (
    echo 错误: config.yaml 不存在
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 config.yaml 配置你的 API
echo 2. 运行测试: python cli.py --help
echo.
pause
