# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from Products.Archetypes.Widget import LinesWidget
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile, PersistentCoverTile
from zope import schema
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from mpdg.govbr.biblioteca.content.arquivo_biblioteca import ArquivoBiblioteca
from mpdg.govbr.observatorio.content.boapratica import BoaPratica



FILE_CONTENT_TYPES = ArquivoBiblioteca.dict_file_content_types

portal_types = SimpleVocabulary(
    [
        SimpleTerm(value=u'ArquivoBiblioteca', title=_(u'Arquivos Biblioteca')),
        SimpleTerm(value=u'BoaPratica', title=_(u'Boas Práticas')),
    ]
    
)

class ISearchContentsTile(IPersistentCoverTile):
    """
    """

    search_on_context = schema.Bool(
        title=_(u'Buscar objetos no contexto'),
        description=_(u'Se marcado a busca de objetos será apenas no contexto do tile, caso contrário em todo portal'),
        default=True,
    )

    portal_type_selected = schema.Choice(
        title=_(u'Tipo de conteúdo'),
        vocabulary=portal_types,
        required=True,
        default='ArquivoBiblioteca'
    )

class SearchContentsTile(PersistentCoverTile):
    is_configurable = True

    @property
    def portal_catalog(self):
        return self.context.portal_catalog

    def get_dados(self):
        """ Obtem os dados que serão usados no template
        """

        portal_type_selected = self.data.get('portal_type_selected', None)
        search_on_context = self.data.get('search_on_context', None)
        all_subjects = self.portal_catalog.uniqueValuesFor('Subject')
        all_types = self.portal_catalog.uniqueValuesFor('tipo_arquivo')
        all_formats = FILE_CONTENT_TYPES.keys()
        all_formats.sort()
        all_formats.append('Outros')

        #Lista de VCGE
        terms = self.vocab_vcge()
        vcge_list = [{'value': term.token, 'title': term.title} for term in terms]
        vcge_list.sort()
        brains = []
        request = self.request
        form = request.form

        folder_context = self.context.aq_parent

        #Pega o contexto do portal
        portal_context = self.context.portal_url.getPortalObject()

        results = {}

        if portal_type_selected:
            if search_on_context:
                scontext = folder_context
            else:
                scontext = portal_context

            path = '/'.join(scontext.getPhysicalPath())
            query = {'path': {'query': path, 'depth': 99},
                     'portal_type': portal_type_selected,
                     'sort_on': 'effective',
                     'sort_order': 'descending'}


            if form.get('submitted', False):
                indexes =  self.portal_catalog.indexes()

                for field, value in form.items():
                    if (field in indexes or 'date-' in field) and value:

                        # if field == 'SearchableText':
                        #     SearchTerms().manageSearchTerms(**{'value': value,
                        #         'uid': folder_context.UID(),
                        #         'type_object': portal_type_selected})
                        #     value = '*%s*' % form[field]
                            # if portal_type_selected == u'ArquivoBiblioteca':
                            #     query['Title'] = value
                            #     continue
                        if 'date-' in field:
                            date, index, field = field.split('-')
                            if not query.get(index, False):
                                str_input = '%s-%s-' % (date, index)
                                end = form.get(str_input+'end', DateTime() + 0.1)
                                end = datetime.strptime(end, '%d/%m/%Y')

                                start = form.get(str_input+'start', DateTime() - 1)
                                start = datetime.strptime(start, '%d/%m/%Y')

                                if end: end = DateTime(end) + 1
                                if start: start = DateTime(start)

                                if start and end:
                                    query_range = { 'query':(start,end), 'range': 'min:max'}
                                elif not end and start:
                                    query_range = { 'query':start, 'range': 'min'}
                                elif not start and end:
                                    query_range = { 'query':end, 'range': 'max'}

                                query[index] = query_range

                            continue
                        else:
                            if field in ['Subject', 'skos']:
                                value= form[field]
                            else:
                                value = form[field].decode('utf-8')

                        query[field] = value

            brains = self.portal_catalog(query)

            #Filtro por formato de arquivo
            if brains and 'file-format' in form.keys():
                value_field = form.get('file-format')
                if value_field:
                    new_brains = []

                    all_mime_types = []
                    for types in FILE_CONTENT_TYPES.values():
                        all_mime_types += types

                    for brain in brains:
                        object = brain.getObject()
                        file_meta_type = object.getContentType()
                        if value_field == 'Outros':
                            if file_meta_type not in all_mime_types:
                                new_brains.append(brain)
                        else:
                            if file_meta_type in FILE_CONTENT_TYPES[value_field]:
                                new_brains.append(brain)

                    #Feito assim pois no result set de brains não da para remover conteudos
                    brains = new_brains

        results = {
            'portal_type_selected': portal_type_selected,
            'list': [self._brain_for_dict(brain) for brain in brains if brain],
            'all_subjects': all_subjects,
            'vcge_list': vcge_list,
            'all_formats': all_formats,
            'all_types': all_types,
        }
        
        return results

    def _brain_for_dict(self, brain):
        '''
            Converte uma pagina em dicionario
        '''
        data_object =  {
            'title': brain.Title,            
            'url': brain.getURL(),
            'created': brain.created.strftime('%d/%m/%Y'),
        }
        object = brain.getObject()

        if brain.portal_type == 'ArquivoBiblioteca':
            data_object['file_size'] = brain.getObjSize

            #Define e extensao do arquivo baseado no content_type do OBJ
            file_meta_type = object.getContentType()

            file_type = ''
            for type in FILE_CONTENT_TYPES:
                if file_meta_type in FILE_CONTENT_TYPES[type]:
                    file_type = type
            if not file_type:
                file_type = 'OUTRO'

            data_object['content_type'] = file_type
            data_object['download']     = object.absolute_url() + '/download'
            data_object['generic_type'] = object.getTipo_arquivo()

        # elif brain.portal_type == 'BoaPratica':
        #     data_object['generic_type'] = object.Title

        return data_object

    def js(self):
        js_template = """\
        (function($) {
            $().ready(function() {
                $('#archetypes-fieldname-%(id)s #%(id)s').each(function() {
                    $('#archetypes-fieldname-%(id)s').append('<input name="%(id)s-input" type="text" id="%(id)s-input" />');
                    %(js_populate)s
                    $(this).remove();
                    $('#archetypes-fieldname-%(id)s #%(id)s-input').autocomplete('%(url)s/@@autocompletevcge-search?f=%(id)s', {
                        autoFill: false,
                        minChars: %(minChars)d,
                        max: %(maxResults)d,
                        mustMatch: %(mustMatch)s,
                        matchContains: %(matchContains)s,
                        formatItem: %(formatItem)s,
                        formatResult: %(formatResult)s
                    }).result(%(js_callback)s);
                })
            });
        })(jQuery);
        """

        js_callback_template = """\
        function(event, data, formatted) {
            var field = $('#archetypes-fieldname-%(id)s input[type="checkbox"][value="' + data[0] + '"]');
            if(field.length == 0)
                $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='checkbox' name='%(id)s:list' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
            else
                field.each(function() { this.checked = true });
            if(data[0])
                $('#archetypes-fieldname-%(id)s #%(id)s-input').val('');
        }
        """

        js_populate_template = """\
        value = $(this).text().split("\\n");
        if(value)
            for(var i=0; i<value.length; i++)
                $.get('%(url)s/@@autocompletevcge-populate', {'f': '%(id)s', 'q': value[i]}, function(data) {
                    if(data) {
                        data = data.split('|');
                        $('#archetypes-fieldname-%(id)s #%(id)s-input').before("<" + "label class='plain'><" + "input type='checkbox' name='%(id)s:list' checked='checked' value='" + data[0] + "' /> " + data[1] + "</label><br />");
                    }
                });
        """

        context = self.context
        form_url = context.absolute_url()

        input_vcge_name = 'skos'

        properties = LinesWidget._properties.copy()
        properties.update({
            'blurrable' : False,
            'minChars' : 2,
            'maxResults' : 10,
            'mustMatch' : False,
            'matchContains' : True,
            'formatItem' : 'function(row, idx, count, value) { return row[1]; }',
            'formatResult': 'function(row, idx, count) { return ""; }',
            'macro' : "autocomplete",
            })

        js_callback = js_callback_template % dict(id=input_vcge_name)
        js_populate = js_populate_template % dict(id=input_vcge_name, url=form_url)

        return js_template % dict(id=input_vcge_name,
                                    url=form_url,
                                    minChars=properties.get('minChars'),
                                    maxResults=properties.get('maxResults'),
                                    mustMatch=str(properties.get('mustMatch')).lower(),
                                    matchContains=str(properties.get('matchContains')).lower(),
                                    formatItem=properties.get('formatItem'),
                                    formatResult=properties.get('formatResult'),
                                    js_callback=js_callback,
                                    js_populate=js_populate,)

    def vocab_vcge(self):
        name = 'brasil.gov.vcge'
        util = queryUtility(IVocabularyFactory, name)
        vcge = util(self.context)
        return vcge
