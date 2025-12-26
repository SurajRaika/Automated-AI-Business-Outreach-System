# Google Business Scraper - Multi-City Email Extractor

A refactored, modular web scraping tool that extracts business information from Google search results and retrieves email addresses from company websites across multiple cities.

## 🎯 Key Features

### ✨ New Features
- **Multi-city scraping**: Process multiple cities in a single run (no need to run the script multiple times)
- **Smart resume**: Automatically detects incomplete work and resumes from where you left off
- **Auto-delete option**: Removes companies without emails from the Excel file
- **Better session management**: Easily resume previous scraping sessions
- **Improved error handling**: Better error messages and logging

### 📊 Core Features
- Google Maps business search scraping
- Email extraction from company websites
- Excel file management with automatic formatting
- Headless browser support
- Comprehensive logging

## 📁 Project Structure

```
project/
├── config.py              # Configuration settings
├── driver_manager.py      # WebDriver initialization and management
├── excel_manager.py       # Excel file operations
├── validators.py          # URL and email validation utilities
├── email_extractor.py     # Email extraction from websites
├── google_scraper.py      # Google search results scraper
├── website_processor.py   # Website processing coordinator
├── session_manager.py     # Session and resume functionality
├── main.py               # Main application entry point
├── scraping.log          # Log file (auto-generated)
└── scraped_data/         # Excel files directory (auto-generated)
```

## 🚀 Installation

### Prerequisites
- Python 3.7+
- Microsoft Edge browser
- Edge WebDriver (msedgedriver)

### Install Dependencies
```bash
pip install selenium openpyxl
```

### Configure Paths
Edit `config.py` to set your Edge driver and binary paths:
```python
EDGE_DRIVER_PATH = "/path/to/msedgedriver"
EDGE_BINARY_PATH = "/path/to/microsoft-edge"
```

## 💻 Usage

### Run the Application
```bash
python main.py
```

### Step-by-Step Guide

1. **Select or Create Session**
   - If previous sessions exist, you can resume them
   - Or create a new session by entering business type and cities

2. **Enter Business Information**
   ```
   Enter Business type (e.g., 'dental clinic'): dental clinic
   Enter cities separated by comma (e.g., 'new york, los angeles'): new york, chicago, miami
   ```

3. **Choose Processing Option**
   - Option 1: Google search only
   - Option 2: Email extraction only
   - Option 3: Full process (search + extraction)
   - Option 4: Smart resume (continues incomplete work)

4. **Delete Without Email (Optional)**
   - When running email extraction, choose whether to delete companies without emails

### Multi-City Processing

**Before (Old Version):**
```bash
# Had to run 3 separate times
python script.py  # Run for New York
python script.py  # Run for Chicago  
python script.py  # Run for Miami
```

**After (New Version):**
```bash
# Run once for all cities
python main.py
> Enter cities: new york, chicago, miami
```

## 📋 Example Workflow

### New Scraping Session
```
1. Run: python main.py
2. Select: 'n' for new session
3. Enter: 'dental clinic'
4. Enter: 'new york, los angeles, chicago'
5. Choose: Option 3 (Full process)
6. Wait for completion
```

### Resume Previous Session
```
1. Run: python main.py
2. Select: Session number (e.g., '1')
3. Choose: Option 4 (Smart resume)
4. Script detects pending work automatically
```

## 🗂️ Output

### Excel File Structure
The generated Excel file contains:
- **Name**: Company name
- **Website**: Company website URL
- **Emails**: Extracted email addresses
- **Number**: Phone number
- **Rating Ratio**: Google rating
- **Number of Ratings**: Number of reviews
- **Social Media Accounts**: (Reserved for future use)
- **City**: City where the business was found

### File Naming Convention
```
BusinessType_City1_City2_City3.xlsx
```
Example: `dental_clinic_new_york_chicago_miami.xlsx`

### Storage Location
All Excel files are stored in the `scraped_data/` directory.

## 🔧 Configuration

Edit `config.py` to customize:

- **Timeouts**: Page load, element wait times
- **Email validation**: Invalid domains, prefixes
- **Scraping behavior**: Number of contact pages to check
- **Logging**: Log file location and format

## 📝 Logging

All activities are logged to `scraping.log` with timestamps:
```
2025-11-02 10:30:15 - INFO - WebDriver initialized successfully
2025-11-02 10:30:20 - INFO - Inserted new data: ABC Dental - New York
2025-11-02 10:30:25 - WARNING - No website found for XYZ Clinic
```

## ⚙️ Advanced Features

### Smart Resume
The smart resume feature automatically:
- Detects which cities haven't been fully processed
- Identifies companies without emails
- Suggests appropriate actions
- Continues from where you left off

### Email Validation
Filters out invalid emails:
- Test/example domains
- No-reply addresses
- Malformed addresses
- File extensions
- Suspicious patterns

### Multi-Strategy Email Extraction
1. Visible page text
2. HTML source code
3. Mailto links
4. Contact/About pages

## 🐛 Troubleshooting

### Driver Not Found
```
✗ Error initializing the web driver
```
**Solution**: Update `EDGE_DRIVER_PATH` in `config.py`

### No Businesses Found
```
✗ No businesses found on this page
```
**Solution**: Try different search terms or check internet connection

### Email Extraction Failed
```
⊙ No email found
```
**Solution**: Website may not have visible emails, or may be blocking scrapers

## 🚦 Best Practices

1. **Start Small**: Test with 1-2 cities first
2. **Use Option 4**: Resume incomplete sessions with smart resume
3. **Enable Delete**: Remove companies without emails to keep data clean
4. **Check Logs**: Review `scraping.log` for detailed information
5. **Backup Data**: Keep copies of Excel files before re-running

## ⚠️ Legal Notice

This tool is for educational purposes. Ensure you:
- Comply with websites' Terms of Service
- Respect robots.txt files
- Follow data protection regulations (GDPR, CCPA, etc.)
- Use responsibly and ethically

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Social media extraction
- More email validation patterns
- Support for other browsers (Chrome, Firefox)
- API integration
- GUI interface

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- Selenium WebDriver
- OpenPyXL for Excel operations
- Google Search for business data