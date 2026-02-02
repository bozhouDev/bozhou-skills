#!/usr/bin/env python3
"""Fetch RSS feeds and filter posts from last 24 hours."""

import feedparser
import json
from datetime import datetime, timezone, timedelta
from time import mktime
import sys
import concurrent.futures

RSS_FEEDS = [
    "https://simonwillison.net/atom/everything/",
    "https://www.jeffgeerling.com/blog.xml",
    "https://www.seangoedecke.com/rss.xml",
    "https://krebsonsecurity.com/feed/",
    "https://daringfireball.net/feeds/main",
    "https://ericmigi.com/rss.xml",
    "http://antirez.com/rss",
    "https://idiallo.com/feed.rss",
    "https://maurycyz.com/index.xml",
    "https://pluralistic.net/feed/",
    "https://shkspr.mobi/blog/feed/",
    "https://lcamtuf.substack.com/feed",
    "https://mitchellh.com/feed.xml",
    "https://dynomight.net/feed.xml",
    "https://utcc.utoronto.ca/~cks/space/blog/?atom",
    "https://xeiaso.net/blog.rss",
    "https://devblogs.microsoft.com/oldnewthing/feed",
    "https://www.righto.com/feeds/posts/default",
    "https://lucumr.pocoo.org/feed.atom",
    "https://skyfall.dev/rss.xml",
    "https://garymarcus.substack.com/feed",
    "https://rachelbythebay.com/w/atom.xml",
    "https://overreacted.io/rss.xml",
    "https://timsh.org/rss/",
    "https://www.johndcook.com/blog/feed/",
    "https://gilesthomas.com/feed/rss.xml",
    "https://matklad.github.io/feed.xml",
    "https://www.theatlantic.com/feed/author/derek-thompson/",
    "https://evanhahn.com/feed.xml",
    "https://terriblesoftware.org/feed/",
    "https://rakhim.exotext.com/rss.xml",
    "https://joanwestenberg.com/rss",
    "https://xania.org/feed",
    "https://micahflee.com/feed/",
    "https://nesbitt.io/feed.xml",
    "https://www.construction-physics.com/feed",
    "https://feed.tedium.co/",
    "https://susam.net/feed.xml",
    "https://entropicthoughts.com/feed.xml",
    "https://buttondown.com/hillelwayne/rss",
    "https://www.dwarkeshpatel.com/feed",
    "https://borretti.me/feed.xml",
    "https://www.wheresyoured.at/rss/",
    "https://jayd.ml/feed.xml",
    "https://minimaxir.com/index.xml",
    "https://geohot.github.io/blog/feed.xml",
    "http://www.aaronsw.com/2002/feeds/pgessays.rss",
    "https://www.filfre.net/feed/",
    "https://blog.jim-nielsen.com/feed.xml",
    "https://dfarq.homeip.net/feed/",
    "https://jyn.dev/atom.xml",
    "https://www.geoffreylitt.com/feed.xml",
    "https://www.downtowndougbrown.com/feed/",
    "https://brutecat.com/rss.xml",
    "https://eli.thegreenplace.net/feeds/all.atom.xml",
    "https://www.abortretry.fail/feed",
    "https://fabiensanglard.net/rss.xml",
    "https://oldvcr.blogspot.com/feeds/posts/default",
    "https://bogdanthegeek.github.io/blog/index.xml",
    "https://hugotunius.se/feed.xml",
    "https://gwern.substack.com/feed",
    "https://berthub.eu/articles/index.xml",
    "https://chadnauseam.com/rss.xml",
    "https://simone.org/feed/",
    "https://it-notes.dragas.net/feed/",
    "https://beej.us/blog/rss.xml",
    "https://hey.paris/index.xml",
    "https://danielwirtz.com/rss.xml",
    "https://matduggan.com/rss/",
    "https://refactoringenglish.com/index.xml",
    "https://worksonmymachine.substack.com/feed",
    "https://philiplaine.com/index.xml",
    "https://steveblank.com/feed/",
    "https://bernsteinbear.com/feed.xml",
    "https://danieldelaney.net/feed",
    "https://www.troyhunt.com/rss/",
    "https://herman.bearblog.dev/feed/",
    "https://tomrenner.com/index.xml",
    "https://blog.pixelmelt.dev/rss/",
    "https://martinalderson.com/feed.xml",
    "https://danielchasehooper.com/feed.xml",
    "https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/feed.xml",
    "https://grantslatton.com/rss.xml",
    "https://www.experimental-history.com/feed",
    "https://anildash.com/feed.xml",
    "https://aresluna.org/main.rss",
    "https://michael.stapelberg.ch/feed.xml",
    "https://blog.miguelgrinberg.com/feed",
    "https://keygen.sh/blog/feed.xml",
    "https://mjg59.dreamwidth.org/data/rss",
    "https://computer.rip/rss.xml",
    "https://www.tedunangst.com/flak/rss",
]


def parse_date(entry):
    """Extract datetime from entry, return None if not available."""
    for attr in ['published_parsed', 'updated_parsed']:
        if hasattr(entry, attr) and getattr(entry, attr):
            try:
                return datetime.fromtimestamp(mktime(getattr(entry, attr)), tz=timezone.utc)
            except:
                pass
    return None


def fetch_feed(url, cutoff):
    """Fetch single feed and return recent entries."""
    results = []
    try:
        feed = feedparser.parse(url)
        feed_title = feed.feed.get('title', url)
        for entry in feed.entries:
            pub_date = parse_date(entry)
            if pub_date and pub_date > cutoff:
                results.append({
                    'source': feed_title,
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', ''),
                    'published': pub_date.isoformat(),
                    'summary': entry.get('summary', '')[:500] if entry.get('summary') else ''
                })
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
    return results


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_entries = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_feed, url, cutoff): url for url in RSS_FEEDS}
        for future in concurrent.futures.as_completed(futures):
            all_entries.extend(future.result())

    # Sort by date descending
    all_entries.sort(key=lambda x: x['published'], reverse=True)

    print(json.dumps(all_entries, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
