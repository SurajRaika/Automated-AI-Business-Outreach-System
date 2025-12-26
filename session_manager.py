# session_manager.py
"""Manages scraping sessions and resume functionality"""

import os
import glob
import json
import re
from pathlib import Path
from config import EXCEL_DIRECTORY
import base64



def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return re.sub(r'^-|-$', '', text)
class SessionManager:
    """Manages scraping sessions, progress tracking, and resume functionality"""
    
    def __init__(self):
        self.session_file = ".scraping_session.json"
        self.excel_dir = EXCEL_DIRECTORY
        self._ensure_excel_directory()
    
    def _ensure_excel_directory(self):
        """Create Excel directory if it doesn't exist"""
        if not os.path.exists(self.excel_dir):
            os.makedirs(self.excel_dir)
            print(f"✓ Created directory: {self.excel_dir}")
    
    def get_existing_sessions(self):
        """Get list of existing Excel files with session info"""
        excel_files = glob.glob(os.path.join(self.excel_dir, "*.xlsx"))
        
        sessions = []
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            # Parse filename: BusinessName_City1_City2_City3.xlsx
            file_parts = filename.replace('.xlsx', '').split('_')
            
            if len(file_parts) >= 2:
                business_name = file_parts[0].replace('_', ' ')
                cities = [city.replace('_', ' ') for city in file_parts[1:]]
                
                sessions.append({
                    'filename': filename,
                    'filepath': file_path,
                    'business_name': business_name,
                    'cities': cities
                })
        
        return sessions
    
    def display_existing_sessions(self):
        """Display existing sessions to user"""
        sessions = self.get_existing_sessions()
        
        if not sessions:
            return None
        
        print("\n" + "="*60)
        print("Found existing scraping sessions:")
        print("="*60)
        
        for idx, session in enumerate(sessions, 1):
            cities_str = ", ".join(session['cities'])
            print(f"  {idx}. {session['business_name']}")
            print(f"     Cities: {cities_str}")
            print(f"     File: {session['filename']}")
            print()
        
        return sessions
    
    def select_session(self):
        """Let user select an existing session"""
        sessions = self.display_existing_sessions()
        
        if not sessions:
            return None
        
        while True:
            choice = input(f"Enter session number (1-{len(sessions)}) or 'n' for new: ").strip().lower()
            
            if choice == 'n':
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(sessions):
                    return sessions[idx]
                else:
                    print(f"✗ Please enter a number between 1 and {len(sessions)}")
            except ValueError:
                print("✗ Invalid input. Enter a number or 'n'")
    
    def save_session(self, business_name, cities, filename):
        """Save current session information"""
        session_data = {
            'business_name': business_name,
            'cities': cities,
            'filename': filename
        }
        
        # Only add last_updated if file exists
        if os.path.exists(filename):
            session_data['last_updated'] = str(Path(filename).stat().st_mtime)
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"✓ Session saved")
        except Exception as e:
            print(f"⚠ Warning: Could not save session: {e}")
    
    def load_last_session(self):
        """Load the last session if available"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Warning: Could not load last session: {e}")
        
        return None
    
    def create_filename(self, business_name, cities):
        """Create filename using slug + encoded metadata"""
        
        # Create a readable slug
        slug = slugify(business_name)
        
        # Encode metadata
        meta = {"business": business_name, "cities": cities}
        meta_json = json.dumps(meta)
        meta_b64 = base64.urlsafe_b64encode(meta_json.encode()).decode()
        
        filename = f"{slug}__meta={meta_b64}.xlsx"
        return os.path.join(self.excel_dir, filename)
    
    def parse_cities_input(self, cities_input):
        """Parse cities from comma-separated input"""
        from config import CITY_DELIMITER
        
        # Split by delimiter and clean
        cities = [city.strip() for city in cities_input.split(CITY_DELIMITER)]
        
        # Remove empty strings
        cities = [city for city in cities if city]
        
        return cities
    
    def get_existing_sessions(self):
        """Parse files and reconstruct business + city metadata"""
        
        sessions = []
        excel_files = glob.glob(os.path.join(self.excel_dir, "*.xlsx"))
        
        for file_path in excel_files:
            filename = os.path.basename(file_path)
            
            if "__meta=" not in filename:
                continue
            
            meta_b64 = filename.split("__meta=")[-1].replace(".xlsx", "")
            
            try:
                meta_json = base64.urlsafe_b64decode(meta_b64).decode()
                meta = json.loads(meta_json)
            except Exception:
                continue
            
            sessions.append({
                "filename": filename,
                "filepath": file_path,
                "business_name": meta.get("business"),
                "cities": meta.get("cities"),
            })
        
        return sessions
    
    def confirm_resume(self, session):
        """Ask user to confirm resuming a session"""
        print("\n" + "="*60)
        print(f"Resume session: {session['business_name']}")
        print(f"Cities: {', '.join(session['cities'])}")
        print("="*60)
        
        choice = input("\nResume this session? (y/n): ").strip().lower()
        return choice == 'y'