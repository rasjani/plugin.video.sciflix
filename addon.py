from xbmcswift2 import Plugin
from xbmcswift2 import xbmcaddon
from BeautifulSoup import BeautifulSoup as BS
from urllib2 import HTTPError
from time import sleep
from urlparse import urlparse
from os.path import basename
import re
import json
import urllib2

GOOGLE_API_KEY="AIzaSyBIUneOnieL9jxdA1MiKuvaMrcibJc8Og0"
THUMBNAIL_QUALITY="standard"
YOUTUBE_JSON_DATA_URL="https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=contentDetails,snippet"
BLOGGER_POSTS_JSON_DATA_URL="https://www.googleapis.com/blogger/v3/blogs/8574416417432246234/posts?key=%s%s"
YOUTUBE_PLUGIN_URL="plugin://plugin.video.youtube/?action=play_video&videoid=%s"

plugin = Plugin()


def _download_page(url):
    conn = None
    if plugin.get_setting('use_proxy',bool):
      proxies = {
        'http': 'http://' + plugin.get_setting('proxy_host',unicode) + ":" + plugin.get_setting('proxy_port', unicode),
        'https': 'http://' + plugin.get_setting('proxy_host', unicode) + ":" + plugin.get_setting('proxy_port', unicode),
      }
      opener = urllib2.build_opener(urllib2.ProxyHandler(proxies))
      urllib2.install_opener(opener)
      conn = opener.open(url)
    else:
      conn = urllib2.urlopen(url)

    resp = conn.read()
    conn.close()
    return resp

def _convert_duration(val):
  ret = 60
  tmp = re.match("PT([0-9]+)H([0-9]+)M([0-9]+)S", val )
  if tmp != None:
    ret = (int(tmp.group(1)) * 60 * 60) +  (int(tmp.group(2))*60) + (int(tmp.group(3)))
  else:
    tmp = re.match("PT([0-9]+)M([0-9]+)S", val )
    if tmp != None:
      ret = (int(tmp.group(1))*60) + (int(tmp.group(2)))

  ret = (ret - ret % 60) / 60
  return ret;


def _jsonfy(url):
  try:
    return json.loads(_download_page(url))
  except:
    return None

def videourl(pid):
  return YOUTUBE_PLUGIN_URL  % pid

def thumbnailurl(data):
  if THUMBNAIL_QUALITY in data:
    return data[THUMBNAIL_QUALITY]['url']
  else:
    return data['default']['url']


@plugin.route('/playvid/<vid>')
def playvid(vid):
  url = videourl(vid)
  plugin.set_resolved_url(url)

@plugin.cached_route('/')
def index():
  items = []
  items.append(
    {
      'label': "All Videos",
      'path': plugin.url_for('category', name = 'all'),
      'is_playable': False,
    }
  )
  done = False
  jsondata = None
  token = "&maxResults=20&fetchBodies=false"
  categories = []
  while not done:
    if jsondata != None:
      if 'nextPageToken' in jsondata:
        token = "&maxResults=20&fetchBodies=false&pageToken=%s" % jsondata['nextPageToken']
      else:
        done = True
        token = ""

    if not done:
      url = BLOGGER_POSTS_JSON_DATA_URL % (GOOGLE_API_KEY, token)
      jsondata = _jsonfy(url)
      if jsondata != None and 'items' in jsondata:
        for item in jsondata['items']:
          for label in item['labels']:
            if label not in categories:
              categories.append(label)
              if label.find("series:") != 0 and label not in ['sheepintheisland','fallout','half-life']:
                items.append(
                    {
                      'label': label.title(),
                      'path': plugin.url_for('category', name = label),
                      'is_playable': False,
                    }
                )
      else:
        done = True
  return items

@plugin.cached_route('/category/<name>/')
def category(name):
  items = []
  done = False
  jsondata = None
  category = ''

  if name != 'all':
    category = '&labels=%s' % name

  token = "&maxResults=20&fetchBodies=true%s" % category

  while not done:
    if jsondata != None:
      if 'nextPageToken' in jsondata:
        token = "&maxResults=20&fetchBodies=true&pageToken=%s%s" % ( jsondata['nextPageToken'], category )
      else:
        done = True
        token = ""

    if not done:
      url = BLOGGER_POSTS_JSON_DATA_URL % (GOOGLE_API_KEY, token)
      jsondata = _jsonfy(url)
      if jsondata != None and 'items' in jsondata:
        if name == 'series':
          sidlist = []
          for item in jsondata['items']:
            for label in item['labels']:
              if label.find('series:')==0:
                if label not in sidlist:
                  sidlist.append(label)
                  name = ' '.join(re.findall('[A-Z][^A-Z]*',label.partition(':')[2]))
                  items.append(
                    {
                      'label': name,
                      'path': plugin.url_for('category', name = label),
                      'is_playable': False,
                    }
                  )

        else:

          for item in jsondata['items']:
            foo = BS(item['content'])
            playid = basename(urlparse(foo.find('param')['value']).path)
            youtube_url = YOUTUBE_JSON_DATA_URL % (playid, GOOGLE_API_KEY)
            try:
              videojsondata = _jsonfy( youtube_url )
            except:
              pass
            else:
              # if videojsondata['items'] != None and videojsondata['items'][0] != None:
              if videojsondata['pageInfo']['totalResults'] != 0:
                data = videojsondata['items'][0];
                items.append (
                  {
                    'label': item['title'],
                    'label2': data['snippet']['title'],
                    'path': plugin.url_for('playvid', vid = playid ),
                    'thumbnail': thumbnailurl(data['snippet']['thumbnails']),
                    'is_playable' : True,
                    'info': {
                        'plot': data['snippet']['description'],
                        'plotoutline': data['snippet']['title'],
                        'duration': _convert_duration(data['contentDetails']['duration'])
                        #'aired': data['snippet']['publishedAt']
                    },
                  }
                )
              else:
                print "Missing video: %s (%s)" % (item['title'], playid )
      else:
        done = True
  return items

if __name__ == '__main__':
    plugin.run()
