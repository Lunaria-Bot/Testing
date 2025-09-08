# Discord Bot for Railway

## 🚀 Features
- Slash commands (`/embed`, `/autorole`, `/setup`)
- Persistent auto-roles and setup messages (stored in `storage.json`)
- Only administrators can use the commands

## 📦 Installation (local)
1. Clone the repo and enter the project folder
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Linux/Mac
   .venv\Scripts\activate    # on Windows
   pip install -r requirements.txt
   ```
3. Create a `.env` file locally (not in GitHub):
   ```env
   TOKEN=your_discord_token_here
   GUILD_ID=your_guild_id_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## 🚀 Deployment on Railway
1. Push this project to GitHub
2. Create a new project on [Railway](https://railway.app/)
3. Connect your GitHub repo
4. Add the following **Environment Variables** in Railway:
   - `TOKEN` → your Discord Bot token
   - `GUILD_ID` → your Discord server ID
5. Deploy 🚀

Railway will automatically install dependencies and run the bot using the `Procfile`.
