from flask import Flask, render_template, request, send_file, redirect
from bs4 import BeautifulSoup as bs4
import requests
import re
import pandas as pd

app = Flask(__name__)
urls = []

@app.route('/')
def redirect_home():
    return redirect('/home')

@app.route('/linkscraper')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    if request.method == 'POST':
        return render_template('embedd.html')
    return render_template('embed.html')

def htmlDoc(url):
    page = requests.get(url)
    return page.text

def scrape_and_save_urls(url, type):
    try:
        urls.clear()  # Clear previous URLs before scraping
        html = htmlDoc(url)
        soup = bs4(html, 'html.parser')

        for link in soup.findAll('a', attrs={type: re.compile('^https://')}):
            urls.append(link.get('href'))

        return urls  # Return the list of URLs instead of just the filename
    except Exception as e:
        error = f"ERROR: Scraper ran into an issue: {e}. Please try again, make sure CSV is not open during the scraping process."
        return error

@app.route('/scrape', methods=['POST'])
def scrapeLinks():
    url = request.form['url']
    scraped_urls = scrape_and_save_urls(url, 'href')  # Get the list of scraped URLs
    if isinstance(scraped_urls, list):  # Check if scraping was successful
        return render_template('index.html', scraped_urls=scraped_urls, url=url)  # Pass scraped_urls to the template
    else:
        return render_template('index.html', error=scraped_urls)  # Pass error message to the template

@app.route('/download', methods=['POST'])
def download():
    df = pd.DataFrame(urls, columns=['URL'])
    df.to_csv('scrapedURLS.csv', index=False)
    return send_file('scrapedURLS.csv', as_attachment=True)

def extract_video_url(embed_url):
    response = requests.get(embed_url)
    soup = bs4(response.content, 'html.parser')
    iframe_src = soup.find('iframe')['src']
    return iframe_src

@app.route('/embedd', methods=['POST'])
def embeddownload():
    link = request.form['url']
    vidurl = extract_video_url(link)
    response = requests.get(vidurl)

    if response.status_code == 200:
        filename = 'downloaded_video.mp4'
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Video downloaded successfully as '{filename}'")
        return f"Video downloaded successfully as '{filename}'"
    else:
        return "Failed to download the video"

if __name__ == "__main__":
    app.run(debug=True)
