# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import mpdg.govbr.biblioteca


class MpdgGovbrBibliotecaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=mpdg.govbr.biblioteca)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'mpdg.govbr.biblioteca:default')


MPDG_GOVBR_BIBLIOTECA_FIXTURE = MpdgGovbrBibliotecaLayer()


MPDG_GOVBR_BIBLIOTECA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MPDG_GOVBR_BIBLIOTECA_FIXTURE,),
    name='MpdgGovbrBibliotecaLayer:IntegrationTesting'
)


MPDG_GOVBR_BIBLIOTECA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MPDG_GOVBR_BIBLIOTECA_FIXTURE,),
    name='MpdgGovbrBibliotecaLayer:FunctionalTesting'
)


MPDG_GOVBR_BIBLIOTECA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MPDG_GOVBR_BIBLIOTECA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MpdgGovbrBibliotecaLayer:AcceptanceTesting'
)
