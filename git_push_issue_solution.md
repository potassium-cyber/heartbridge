 换了 GitHub 账号、或者 Token 过期了，但终端死活报错：
  remote: Permission to xxx denied to old-user.
  fatal: unable to access ... : The requested URL returned error: 403

  方法一：温和清理法（推荐先试这个）
  告诉 Mac：“忘掉我之前的密码吧！”

   1 # 1. 强制清理 GitHub 的凭据缓存
   2 printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain erase
   3 
   4 # 2. 再次 Push
   5 git push -u origin main
   6 # 此时终端会让你重新输账号密码。
   7 # 账号：新用户名
   8 # 密码：必须是 Token (ghp_...)，不能是登录密码！

  方法二：核弹级绕过法（百试百灵）
  如果不奏效，或者你懒得输密码，直接把 Token 镶嵌到 URL 里。这是最暴力的鉴权方式。

   1 # 1. 获取你的 Personal Access Token (ghp_xxxx...)
   2 
   3 # 2. 修改远程仓库地址 (注意格式！)
   4 # 语法：https://<Token>@github.com/<用户名>/<仓库名>.git
   5 git remote set-url origin https://ghp_YourTokenHere@github.com/potassium-cyber/heartbridge.git
   6 
   7 # 3. 直接 Push (无需再输密码)
   8 git push -u origin main

  方法三：SSH 彻底解脱法（一劳永逸）
  如果你不想每次都搞 Token，配置 SSH Key 是最优雅的长久之计。

   1. 生成 Key: ssh-keygen -t ed25519 -C "你的邮箱" (一路回车)
   2. 复制公钥: cat ~/.ssh/id_ed25519.pub -> 复制输出的内容。
   3. 上传 GitHub: 头像 -> Settings -> SSH and GPG keys -> New SSH key -> 粘贴。
   4. 修改仓库地址:
   1     git remote set-url origin git@github.com:potassium-cyber/heartbridge.git
   5. Push: git push -u origin main (从此告别密码)。