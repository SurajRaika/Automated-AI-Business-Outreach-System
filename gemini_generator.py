import random
import logging
import os
import google.generativeai as genai

# ==========================================
#  USER CONFIGURATION
# ==========================================
MY_NAME = "Suraj Raika"
MY_PHONE = "+91 97991 05754"

def get_greeting_and_location_context(company_name, city_name):
    """
    Calls Gemini to create a simple, direct greeting for an email intro.
    """
    default_message = (
        f"And I've been thinking about applying to {company_name} as a developer. "
        f"I have seen your work and the services you provide, and I am excited to contribute."
    )
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return default_message
    
    prompt = f"""
    Write a 2-sentence email intro to {company_name}.
    Be direct and straightforward. No fluff or unnecessary words.
    Line 1: Start with "And I've been thinking about applying... as a developer".
    Line 2: Mention I have seen your  work and services you provide.
    Remove "Inc", "LLC", or special characters from the company name ,  Do not use the full legal company name in sentences. Use the short/common name only.
    Return only the text. No markdown, no subject line.
    """

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:

        logging.error(f"Gemini error: {e}")
        return default_message

def create_random_proposal_email(city_name, potential_client):
    # 1. Get AI Intro
    intro_context = get_greeting_and_location_context(potential_client, city_name)

    # 2. Tech Stack Variations
    # firstLine = [
    #     "I’m a full-stack developer working with PHP, React/Vue, Python, and Node.",
    #     "I’m a full-stack developer experienced with PHP, React/Vue, Python, and Node.",
    #     "I’m a full-stack developer specializing in PHP, React/Vue, Python, and Node.",
    #     "I work as a full-stack developer using PHP, React/Vue, Python, and Node.",
    #     "I’m a full-stack engineer working with PHP, React/Vue, Python, and Node.",
    #     "I’m a full-stack developer building applications with PHP, React/Vue, Python, and Node.",
    # ]
    firstLine = [
        "Just reaching out to introduce myself as a remote developer.",
        "Hi, I’m a remote developer and wanted to quickly say hello.",
        "I’m a remote developer, just dropping a quick introduction.",
        "Hello, I wanted to introduce myself as a remote developer.",
        "Hey, I’m a remote developer and thought I’d say hi.",
        "Quick note to introduce myself — I’m a remote developer.",
    ]


    # 3. Work Style Variations
    work_styles = [
        "I’m comfortable working across frontend and backend, building automation, managing databases, and even tackling cross-platform apps. I adapt quickly, enjoy collaborating, and focus on creating solutions that are both reliable and easy to maintain.",

        "I work confidently across frontend and backend, handle automation, manage databases, and build cross-platform apps when needed. I adapt quickly, enjoy collaboration, and focus on reliable, maintainable solutions.",

        "I’m comfortable across the full stack, from frontend to backend, including automation, database management, and cross-platform development. I adapt fast, collaborate well, and build solutions that are easy to maintain.",

        "I handle frontend and backend work, automation, databases, and cross-platform apps with ease. I adapt quickly, work well with teams, and focus on building stable, maintainable systems.",

        "I work across the entire stack, covering frontend, backend, automation, and databases, with experience in cross-platform apps. I adapt quickly and focus on clean, reliable, and maintainable solutions.",
    ]

    # 4. Construct the HTML
    # Note: Using f-string with triple quotes for the HTML wrapper
    html_template = f"""
<!DOCTYPE html>
<html>
<body style="font-family: monospace; font-size: 14px; line-height: 1.6; color: #000;">
    Hi,<br><br>
    <strong>TL;DR</strong><br><br>
    {random.choice(firstLine)}<br><br>
    {intro_context}<br><br>
    So, I’d like to join your team as a developer and contribute effectively to ongoing and upcoming projects.<br><br>
    
    Some of my work includes 
<a href="https://artifact.wuaze.com" target="_blank">Artisan's Direct Exchange</a> (a marketplace-style platform), 
<a href="https://www.rayca.in/projects" target="_blank">DuckSurvey</a> (a user-facing survey product), 
<a href="https://github.com/SurajRaika/OutreachPilot" target="_blank">OutreachPilot</a> (an LLM-based automation and outreach system), 
and <a href="https://taxi.rayca.in/" target="_blank">NRTours</a> (a real-world booking and customer-facing application)

    and a <a href="https://www.rayca.in/apps" target="_blank">collection of public online tools</a>.<br><br>
    
    You can explore more of my work on my <a href="https://www.rayca.in/" target="_blank">portfolio</a> 
    or view my freelance profile on <a href="https://www.upwork.com/freelancers/~01e307344c31edcc38" target="_blank">Upwork</a>.<br><br>

    <img src="https://www.rayca.in/MYPROOJECTS.webp" alt="My Projects" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; padding: 4px;"><br><br>
    
    <a href="https://www.rayca.in/resume" target="_blank">View My Resume</a><br><br>
    
    {random.choice(work_styles)}
    <br>
   I hope you might keep me in mind if any projects come up where I could help out. I’d be happy to pitch in on anything you have in mind. I’m based in Udaipur.<br><br>
    
    Best,<br>
    {MY_NAME}<br><br>
</body>
</html>
"""
    return html_template.strip()

def generate_personalized_html(city: str, company_name: str) -> str:
    try:
        logging.info(f"Generating professional HTML email for {company_name}")
        return create_random_proposal_email(city, company_name)
    except Exception as e:
        logging.error(f"Error generating email: {e}")
        return None