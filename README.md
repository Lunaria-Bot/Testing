# Discord Bot for Railway (Bash Start)

## 🚀 Features
- Slash commands (`/embed`, `/autorole`, `/setup`)
- Persistent auto-roles and setup messages
- Only administrators can use the commands

## 📦 Installation (local)
1. Clone repo & enter folder
2. Create virtual env & install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
3. Create `.env` file (for local only):
   ```env
   TOKEN=your_token_here
   GUILD_ID=your_guild_id_here
   ```
4. Run bot:
   ```bash
   python bot.py
   ```

## 🚀 Deployment on Railway
1. Push repo to GitHub
2. Create new Railway project, link GitHub
3. Add environment variables in Railway:
   - `TOKEN` → your Discord bot token
   - `GUILD_ID` → your server ID
4. Deploy 🚀

The bot runs with `bash start.sh` via Procfile, so Railway won't need exec permissions.
