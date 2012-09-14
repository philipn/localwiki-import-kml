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


def clean_pagename(name):
    # Pagename's can't contain a slash with spaces surrounding it.
    # LocalWiki will clean this up on save, but we want to stay
    # consistent here.
    name = '/'.join([part.strip() for part in name.split('/')])
    return name


for layer in ds:
    print 'Importing layer: %s' % layer.name
    tag = None
    tag_name = raw_input(
"""What tag name would you like to associate with this layer?
(or just press Enter for no tag):\n""").strip()
    if tag_name:
        # Find or create the tag
        if not api.tag.get(name__iexact=tag_name)['objects']:
            api.tag.post({'name': tag_name},
                api_key=API_KEY, username=USERNAME)
        # get tag uri
        tag = api.tag.get(name__iexact=tag_name)['objects'][0]['resource_uri']

    for feature in layer:
        pagename = clean_pagename(feature.get('Name'))
        content = feature.get('Description') or 'Describe %s here.' % pagename

        # If the page doesn't exist, create it
        if not api.page.get(name__iexact=pagename)['objects']:
            try:
                result = api.page.post({'name': pagename, 'content': content},
                    api_key=API_KEY, username=USERNAME)
            except:
                pass
            page_uri = result['resource_uri']
            print ('..created page %s with description %s' %
                (pagename, content))
        else:
            # Get page URI
            page_uri = api.page.get(
                name__iexact=pagename)['objects'][0]['resource_uri']

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

        map = {
            'page': page_uri,
            'geom': json.loads(GeometryCollection(feature.geom.geos).geojson),
        }

        # Does the page already have a map?
        map_data = api.map.get(page__name__iexact=pagename)['objects']
        if map_data:
            map = map_data[0]
            map['geom'] = json.loads(
                GeometryCollection(feature.geom.geos).geojson)
            # Update the map with the new geometry
            api.map(pagename).put(map, api_key=API_KEY, username=USERNAME)
        else:
            # Create new map from the feature's geometry.
            api.map.post(map, api_key=API_KEY, username=USERNAME)

        print '..imported geometry for %s' % pagename
