from flask import Flask, render_template, request, send_file, redirect
from bs4 import BeautifulSoup as bs4
import requests
import re
import pandas as pd
from pytube import YouTube

app = Flask(__name__)
urls = []


@app.route('/linkscraper')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/cookie')
def cookie():
    return render_template('cookie.html')


@app.route('/')
def reroutehome():
    return redirect('home')


@app.route('/embed')
def embedScrape():
    return render_template('embed.html')


def htmlDoc(url):
    page = requests.get(url)
    return page.text


def scrape_and_save_urls(url, type):
    try:
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





@app.route('/cookieScrape', methods=['POST'])
def cookieScrape():
    url = request.form['url']
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        cookies = response.cookies.get_dict()
        if cookies:
            return render_template('cookie.html', cookies=cookies, url=url)
        else:
            return render_template('cookie.html', error="No cookies found")
    except requests.exceptions.RequestException as e:
        return render_template('cookie.html', error=f"Error occurred: {e}")


@app.route('/youtube')
def yt():
    return render_template('youtube.html')

@app.route('/ytDownload', methods = ['POST'])
def ytDownload():
    try:
        url = request.form['url']
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        if video:
            video_path = video.download()
            return send_file(video_path, as_attachment=True)

        else:
            return render_template('youtube.html', error="No video found")
    except requests.exceptions.RequestException as e:
        return render_template('youtube.html', error=f"Error occurred: {e}")
    except requests.exceptions.RequestException as e:
        return render_template('youtube.html', error=f"Error occurred: {e}")



if __name__ == "__main__":
    app.run(debug=True)
