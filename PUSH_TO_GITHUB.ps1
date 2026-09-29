# ============================================================
# native-ai-lifeforms — 一键推送到 GitHub
# 在你自己的 PowerShell 窗口里运行（不是在豆包沙箱里）
# ============================================================

# 1. 进入仓库目录
cd "C:\Users\Lenovo\Doubao\chats\2026-09-29\new-chat-3\native-ai-lifeforms"

# 2. 让 git 走本机 Clash 代理（你机器上 Clash Mi 在 7890）
git config http.proxy  http://127.0.0.1:7890
git config https.proxy http://127.0.0.1:7890

# 3. 登录 GitHub（首次需要；已登录会跳过）
#    选 GitHub.com -> HTTPS -> Yes -> Login with a web browser
gh auth login

# 4. 创建公开仓库并把 main 分支推上去
gh repo create native-ai-lifeforms --public --source=. --push `
  --description "Native AI Lifeforms: autonomous NPC architecture with negotiation, goal graphs, and event-driven replanning. Based on the Monta NPC Camp (Unity) and QY third-person (UE5) prototypes."

# 5. 完成后会输出仓库 URL，类似：
#    https://github.com/<你的用户名>/native-ai-lifeforms
