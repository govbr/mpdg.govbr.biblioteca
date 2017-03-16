# -*- coding: utf-8 -*-
from five import grok

from mpdg.govbr.biblioteca.content.interfaces import IArquivoBiblioteca
from mpdg.govbr.observatorio.browser.utils import ContadorManager


grok.templatedir('templates')


class ArquivoBibliotecaView(grok.View):
    grok.context(IArquivoBiblioteca)
    grok.require('zope2.View')
    grok.name('arquivobiblioteca-view')

    def getAccessObject(self):
        uid = self.context.UID()
        content_type = self.context.meta_type
        contador = ContadorManager(uid=uid, content_type=content_type)
        return contador.setAcesso()