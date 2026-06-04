"""
项目设置验证脚本

检查所有必需的组件是否正确配置
"""

import sys
from pathlib import Path


def check_directory_structure():
    """检查目录结构"""
    required_dirs = [
        "config",
        "models",
        "tools",
        "agents",
        "agents/nodes",
        "agents/prompts",
        "services",
        "utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        print("❌ 缺少的目录:")
        for d in missing_dirs:
            print(f"   - {d}")
        return False

    print("✅ 目录结构完整")
    return True


def check_required_files():
    """检查必需文件"""
    required_files = [
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "main.py",
        "cli.py",
        "LICENSE",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ 缺少的文件:")
        for f in missing_files:
            print(f"   - {f}")
        return False

    print("✅ 必需文件完整")
    return True


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 10):
        print(f"❌ Python版本过低: {sys.version}")
        print("   需要 Python 3.10 或更高版本")
        return False

    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("loguru", "loguru"),
        ("python-dotenv", "dotenv"),
    ]

    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"⚠️  缺少的包: {', '.join(missing_packages)}")
        print("   运行: pip install -r requirements.txt")
        return False

    print("✅ 核心依赖已安装")
    return True



def main():
    """主验证函数"""
    print("\n" + "=" * 60)
    print("🔍 Personal AI Assistant - 项目设置验证")
    print("=" * 60 + "\n")

    checks = [
        ("Python版本", check_python_version),
        ("目录结构", check_directory_structure),
        ("必需文件", check_required_files),
        ("依赖包", check_dependencies),
    ]

    results = []
    for name, check_func in checks:
        print(f"检查 {name}...")
        result = check_func()
        results.append(result)
        print()

    print("=" * 60)
    if all(results):
        print("🎉 所有检查通过！项目已正确初始化。")
        print("\n下一步:")
        print("  1. cp .env.example .env")
        print("  2. 编辑 .env 填入API密钥")
        print("  3. pip install -r requirements.txt")
        print("  4. python main.py")
    else:
        print("⚠️  部分检查未通过，请根据上述提示修复。")
    print("=" * 60 + "\n")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())