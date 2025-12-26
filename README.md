# Automated AI Business Outreach System

An end-to-end, **AI-powered outreach system** that discovers businesses, ranks website links, extracts **high-value emails**, and sends **personalized emails via Gmail**.  
Supports **session tracking** and **smart resume**, so you can stop and continue anytime.

---

## 🚀 Features

- Discover businesses and websites via Google search  
- Extract, score, and rank links before scraping  
- Filter out generic emails (support, admin, marketing)  
- Extract only **high-value, decision-maker emails**  
- Generate **personalized emails** using Gemini  
- Send emails automatically via Gmail  
- Resume unfinished sessions seamlessly  

---

## 🧠 Session Tracking

Tracks progress and allows resuming:

![Session tracking](https://github.com/user-attachments/assets/36c82bc4-5355-468a-b824-3ed2e471f227)

Options when resuming:

![Resume options](https://github.com/user-attachments/assets/56755f36-fae7-455a-a699-3542290a8a73)

---

## 🔗 Link & Email Filtering

- Custom link scoring ensures only high-value pages are scraped  
- Blocks low-quality and tracking emails  

![Link & email filtering](https://github.com/user-attachments/assets/a172debd-b477-4aaa-9dd1-c84e250e576e)

---

## ✨ AI Email Generation

- Uses `template.html` + `gemini_generator.py`  
- Generates **personalized, contextual emails** for each business  

---
---
## 📁 Project Structure
```bash

main.py
config.py
company_search_cli.py
google_scraper.py
website_processor.py
email_extractor.py
EmailGuard.py
validateEmail.py
gemini_generator.py
send_email.py
outreach_manager.py
session_manager.py
excel_manager.py
driver_manager.py
validators.py
excel_files/
companies.txt
emails.txt
.scraping_session.json
app.log / scraping.log
requirements.txt
```

---

## ⚙️ Usage

```bash
python main.py
