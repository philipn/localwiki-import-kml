from urlparse import urljoin
import json

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GeometryCollection

import slumber

SITE_URL = raw_input("Enter URL of LocalWiki instance: ").strip()
API_KEY = raw_input("Enter API key: ").strip()
USERNAME = raw_input("Enter API username: ").strip()
KML_PATH = raw_input("Enter path to KML file: ").strip()

api = slumber.API(urljoin(SITE_URL, '/api/'))

ds = DataSource(KML_PATH)


def get_or_create_tag():
    tag_name = raw_input(
"""What tag name would you like to associate with this layer?
(or just press Enter for no tag):\n""").strip()
    if tag_name:
        # Find or create the tag
        if not api.tag.get(name__iexact=tag_name)['objects']:
            api.tag.post({'name': tag_name},
                api_key=API_KEY, username=USERNAME)
        # get tag uri
        return api.tag.get(name__iexact=tag_name)['objects'][0]['resource_uri']
    return None


def get_or_create_page():
    # If the page doesn't exist, create it
    if not api.page.get(name__iexact=pagename)['objects']:
        try:
            result = api.page.post({'name': pagename, 'content': content},
                api_key=API_KEY, username=USERNAME)
        except:
            pass
        print ('..created page %s with description %s' %
            (pagename, content))
        return result['resource_uri']
    else:
        # Get page URI
        return api.page.get(
            name__iexact=pagename)['objects'][0]['resource_uri']


def add_tag_to_page(tag, pagename):
    # Add page tag
    page_tags = api.page_tags.get(page__name__iexact=pagename)['objects']
    if page_tags:
        page_tags = page_tags[0]
        if tag not in page_tags['tags']:
            # Update existing page_tags
            page_tags['tags'].append(tag)
            api.page_tags(pagename).put(page_tags,
                api_key=API_KEY, username=USERNAME)
    else:
        # Add a new page_tags
        page_tags = {'page': page_uri, 'tags': [tag]}
        api.page_tags.post(page_tags, api_key=API_KEY, username=USERNAME)


def update_map(pagename):
    map = {
        'page': page_uri,
        'geom': json.loads(GeometryCollection(feature.geom.geos).geojson),
    }
    # Update the map with the new geometry
    api.map(pagename).put(map, api_key=API_KEY, username=USERNAME)


for layer in ds:
    print 'Importing layer: %s' % layer.name

    tag = get_or_create_tag()

    for feature in layer:
        pagename = feature.get('Name')
        content = feature.get('Description') or 'Describe %s here.' % pagename

        page_uri = get_or_create_page()
        add_tag_to_page(tag, pagename)
        update_map(pagename)

        print '..imported geometry for %s' % pagename
