# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from mpdg.govbr.biblioteca.testing import MPDG_GOVBR_BIBLIOTECA_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that mpdg.govbr.biblioteca is properly installed."""

    layer = MPDG_GOVBR_BIBLIOTECA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mpdg.govbr.biblioteca is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mpdg.govbr.biblioteca'))

    def test_browserlayer(self):
        """Test that IMpdgGovbrBibliotecaLayer is registered."""
        from mpdg.govbr.biblioteca.interfaces import (
            IMpdgGovbrBibliotecaLayer)
        from plone.browserlayer import utils
        self.assertIn(IMpdgGovbrBibliotecaLayer, utils.registered_layers())

   def test_tiles(self):
        self.registry = getUtility(IRegistry)
        registered_tiles = self.registry['plone.app.tiles']
        for tile in TILES:
            self.assertIn(tile, registered_tiles)

    def test_css_installed(self):
        installedStylesheetIds = self.ctool.getResourceIds()
        expected = ['++resource++mpdg.govbr.biblioteca/mpdg_govbr_biblioteca.css', ]
        for e in expected:
            self.assertTrue(e in installedStylesheetIds, e)

    def test_js_installed(self):
        installedScriptIds = self.jtool.getResourceIds()
        expected = ['++resource++mpdg.govbr.biblioteca/mpdg_govbr_biblioteca.js', ]
        for e in expected:
            self.assertTrue(e in installedScriptIds, e)


class TestUninstall(unittest.TestCase):

    layer = MPDG_GOVBR_BIBLIOTECA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mpdg.govbr.biblioteca'])

    def test_product_uninstalled(self):
        """Test if mpdg.govbr.biblioteca is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mpdg.govbr.biblioteca'))

    def test_browserlayer_removed(self):
        """Test that IMpdgGovbrBibliotecaLayer is removed."""
        from mpdg.govbr.biblioteca.interfaces import \
            IMpdgGovbrBibliotecaLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMpdgGovbrBibliotecaLayer, utils.registered_layers())

    def test_css_removed(self):
        installedStylesheetIds = self.ctool.getResourceIds()
        expected = ['++resource++mpdg.govbr.biblioteca/mpdg_govbr_biblioteca.css', ]
        for e in expected:
            self.assertTrue(e not in installedStylesheetIds, e)

    def test_js_removed(self):
        installedScriptIds = self.jtool.getResourceIds()
        expected = ['++resource++mpdg.govbr.biblioteca/mpdg_govbr_biblioteca.js', ]
        for e in expected:
            self.assertTrue(e not in installedScriptIds, e)
