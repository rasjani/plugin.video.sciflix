from xbmcswift2 import Plugin
from BeautifulSoup import BeautifulSoup as BS
from urlparse import urlparse
from os.path import basename
from resources.lib import feedparser

FEED_URL="http://feeds.feedburner.com/Sciflix"
JSON_DATA_URL="http://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json"
THUMBNAIL_URL="http://img.youtube.com/vi/%s/hqdefault.jpg"
YOUTUBE_PLUGIN_URL="plugin://plugin.video.youtube/?action=play_video&videoid=%s"

plugin = Plugin()
feedparser._FeedParserMixin.can_contain_dangerous_markup.remove('content')


def _htmlify(url):
  return  feedparser.parse(url)


def videourl(pid):
  return YOUTUBE_PLUGIN_URL  % pid


def thumbnailurl(pid):
  return THUMBNAIL_URL % pid


@plugin.route('/')
def index():
  content = _htmlify(FEED_URL)
  items = []
  for cat in content.feed.categories:
    category_name = cat[1]
    if category_name not in ['sheepintheisland','fallout','half-life','series']:
      items.append( 
        {
          'label': category_name.title(),
          'path': plugin.url_for('category', name = category_name),
          'is_playable': False,
        }
      )

  return items

   
@plugin.route('/category/<name>/')
def category(name):
  content = _htmlify(FEED_URL)
  items = []
  for entry in content.entries:
    for cat in entry.categories:
      if cat[1] == name:
        label_name = entry.title
        foo = BS(entry.content[0].value)
        playid = basename(urlparse(foo.find('param')['value']).path)

        items.append ( 
          {
            'label': label_name,
            'path': videourl(playid),
            'thumbnail': thumbnailurl(playid),
            'is_playable' : True
          }
        )

  return items

if __name__ == '__main__':
    plugin.run()
