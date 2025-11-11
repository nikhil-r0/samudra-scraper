<<<<<<< HEAD
**Samudra Social Media Scraper**
This project contains a set of Python scripts for scraping post data from X.com (formerly Twitter) and Instagram. The scrapers use Playwright to control a browser, enabling them to bypass simple bot detection and scrape content as a logged-in user.

**Features**

* **X.com Scraper:** Search X.com for a query and scrape tweet text, URLs, authors, and images.
* **Instagram Scraper:** Scrape posts from an Instagram profile or by hashtag, saving captions, authors, and media.
* **Authentication Manager:** A script to log in to platforms manually once and save the session cookies for all future scraping.
* **Media & Debugging:** Scrapers save screenshots, downloaded media, and debug files to local folders.

---

### Setup & Installation

Follow these steps to get the project running on your local machine.

**1. Prerequisites**

* Python 3.8+
* A "bot" or "fake" account for X.com and Instagram. It is strongly recommended not to use your personal accounts, as scraping can lead to rate limits or account suspension.

**2. Install Dependencies**
First, install all the required Python libraries using `requirements.txt`:

```bash
pip install -r requirements.txt
```

**3. Install Browsers**
The scrapers use Playwright, which needs to download browser binaries. Run the following command to install them:

```bash
playwright install
```

---

### How to Use

#### Step 1: Authentication (Required)

You must generate authentication files before you can scrape. This script will open a browser, allow you to log in manually, and then save your session state.

Run the `authenticate.py` script from the `scraper/` directory:

```bash
python scraper/authenticate.py
```

You will be prompted to choose which platform to authenticate:

```
Which platform do you want to authenticate?
1. Instagram
2. X.com (Twitter)
Enter (1 or 2):
```

* **For Instagram:** Choose 1. A browser will open to the Instagram login page. Log in with your bot account. Once you see your feed, close the browser window. This will create an `ig_auth_state.json` file.
* **For X.com:** Choose 2. A browser will open to the X.com login page. Log in with your bot account. Once you see your feed, close the browser window. This will create an `x_auth_state.json` file.

You must do this for both platforms to use both scrapers.

---

#### Step 2: Running the Scrapers

The scrapers are designed to be run as standalone scripts for testing, which you can see in their `if __name__ == "__main__":` blocks.

**Instagram Scraper**

* **Script:** `scraper/instagram_scrapper.py`
* **Function:** `search_and_scrape_instagram(query, max_results)`
* **Test:** To test the script, you can modify the query in the `main()` block of the file and run it:

  ```bash
  python scraper/instagram_scrapper.py
  ```
* **Output:**

  * Returns a JSON string of the scraped data.
  * Saves post screenshots to the `screenshots/` folder.
  * Saves post images/videos to the `pictures/` folder.
  * Saves a debug HTML file to the `debug/` folder.

**X.com Scraper**

* **Script:** `scraper/x_scraper.py`
* **Function:** `search_and_scrape_x(query, max_results)`
* **Test:** To test the script, you can modify the query in the `main()` block of the file and run it:

  ```bash
  python scraper/x_scraper.py
  ```
* **Output:**

  * Returns a JSON string of the scraped data.
  * Saves search page screenshots to the `screenshots/` folder.
  * Saves all scraped images to the `screenshots/` folder.

---

### API (Optional)

This project also includes a FastAPI backend in `api/main.py`. This API is designed to serve the scraped data (presumably after it's been processed and stored in a database like Supabase, based on the config).

To run the API server for development:

```bash
uvicorn api.main:app --reload --port 8000
```

---

### Disclaimer

Web scraping can be against the Terms of Service of these platforms. Use these scripts responsibly and at your own risk.

* **Account Safety:** Using a bot/fake account is critical. Scraping activity can lead to your account being flagged or banned.
* **Rate Limits:** The platforms have rate limits. If you scrape too frequently or too quickly, you may be temporarily or permanently blocked.

---
=======
# samudra-scraper
>>>>>>> 2ccbdef3d10890cc9221e166b0922894d02d6496
