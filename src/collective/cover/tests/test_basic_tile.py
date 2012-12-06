# -*- coding: utf-8 -*-

import unittest2 as unittest

from DateTime import DateTime

from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from Products.ATContentTypes.utils import DT2dt
from collective.cover.testing import INTEGRATION_TESTING, loadImage
from collective.cover.tiles.basic import BasicTile
from collective.cover.tiles.base import IPersistentCoverTile
from zope.component import getMultiAdapter
from collective.cover.tiles.permissions import ITilesPermissions
from zope.annotation.interfaces import IAnnotations
from collective.cover.tiles.configuration import ITilesConfigurationScreen


class BasicTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.tile = self.portal.restrictedTraverse(
            '@@%s/%s' % ('collective.cover.basic', 'test-basic-tile'))

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(BasicTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, BasicTile))

        tile = BasicTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_editable)
        self.assertTrue(self.tile.is_droppable)

    def test_accepted_content_types(self):
        self.assertEqual(
            self.tile.accepted_ct(),
            ['Collection', 'Document', 'File', 'Image', 'Link', 'News Item'])

    def test_empty_date(self):
        self.assertEqual('', self.tile.get_date())

    def test_populated_empty_date(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        self.assertEqual('', self.tile.get_date())

    def test_populated_date(self):
        obj = self.portal['my-news-item']
        obj.effective_date = DateTime()
        self.tile.populate_with_object(obj)
        self.assertEqual(obj.effective_date.strftime('%y/%m/%d %H:%M'),
                         self.tile.get_date())

    def test_populated_faultydate(self):
        obj = self.portal['my-news-item']
        obj.effective_date = DateTime('1/1/1800')
        self.tile.populate_with_object(obj)
        self.assertEqual(DT2dt(obj.effective_date).ctime(),
                         self.tile.get_date())

    def test_populate_with_object(self):
        self.tile.populate_with_object(self.portal['my-news-item'])
        self.assertEqual('Test news item', self.tile.data['title'])
        self.assertEqual('This news item was created for testing purposes',
                         self.tile.data['description'])

    def test_render_empty(self):
        self.assertTrue(
            "Please drag&amp;drop some content here to populate the tile." in self.tile())

    def test_render_title(self):
        obj = self.portal['my-news-item']
        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue('Test news item' in rendered)

    def test_render(self):
        obj = self.portal['my-news-item']
        obj.setSubject('test-subject')
        obj.effective_date = DateTime()
        obj.setImage(loadImage('canoneye.jpg'))

        self.tile.populate_with_object(obj)
        rendered = self.tile()
        self.assertTrue(obj.UID() in rendered)
        self.assertTrue('Test news item' in rendered)
        self.assertTrue(
            "This news item was created for testing purposes" in rendered)
        self.assertTrue('test-subject' in rendered)
        self.assertTrue(
            obj.effective_date.strftime('%y/%m/%d %H:%M') in rendered)
        self.assertTrue('test-basic-tile/@@images' in rendered)

    def test_delete_tile_persistent_data(self):
        permissions = getMultiAdapter((self.tile.context,
                                       self.request,
                                       self.tile),
                                      ITilesPermissions)
        permissions.set_allowed_edit('masters_of_the_universe')
        annotations = IAnnotations(self.tile.context)
        self.assertIn('plone.tiles.permission.test-basic-tile',
                      annotations)

        configuration = getMultiAdapter((self.tile.context,
                                         self.request,
                                         self.tile),
                                        ITilesConfigurationScreen)
        configuration.set_configuration({'foo': 'bar'})
        self.assertIn('plone.tiles.configuration.test-basic-tile',
                      annotations)

        # Call the delete method
        self.tile.delete()

        # Now we should not see the stored data anymore
        self.assertNotIn('plone.tiles.permission.test-basic-tile',
                         annotations)
        self.assertNotIn('plone.tiles.configuration.test-basic-tile',
                         annotations)
