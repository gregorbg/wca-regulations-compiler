''' Backend for JSON.  '''
import json
from wrc.sema.ast import WCADocument, Guideline
from wrc.codegen.cg import CGDocument
from wrc.codegen.cghtml import simple_md2html

REGULATIONS_ROOT = "https://www.worldcubeassociation.org/regulations/"


class WCADocumentJSON(CGDocument):
    ''' Implement a simple JSON generator from Regulations and Guidelines ASTs. '''

    name = "JSON"
    def __init__(self, versionhash, language, pdf):
        # We don't need it
        del language
        super(WCADocumentJSON, self).__init__(list)
        self.versionhash = versionhash
        self.urls = {'regulations': REGULATIONS_ROOT,
                     'guidelines': REGULATIONS_ROOT + "guidelines.html",
                     'pdf': pdf}

    def visitWCAStates(self, document):
        self.state_lists = []
        retval = super(WCADocumentJSON, self).visitWCAStates(document)
        self.codegen = {'title': document.title, 'version': document.version,
                        'version_hash': self.versionhash,
                        'text': document.text, 'states_lists': self.state_lists}
        return retval

    def visitStatesList(self, states_list):
        self.current_states = []
        retval = super(WCADocumentJSON, self).visitStatesList(states_list)
        self.state_lists.append({'title': states_list.title,
                                 'states': self.current_states})
        return retval

    def emit(self, regulations, guidelines):
        reg_list, guide_list = super(WCADocumentJSON, self).emit(regulations, guidelines)
        if len(guide_list) > 0:
            reg_list.extend(guide_list)
        return json.dumps(reg_list), ""


    def visitRule(self, reg):
        url = "/regulations/"
        if isinstance(reg, Guideline):
            url += "guidelines.html"
        url += "#" + reg.number
        self.codegen.append({'class': 'regulation', 'id': reg.number,
                             'content_html': simple_md2html(reg.text, self.urls),
                             'url': url})
        retval = super(WCADocumentJSON, self).visitRule(reg)
        return retval

    def visitState(self, state):
        self.current_states.append({'class': 'state', 'iso2': state.state_id,
                                    'continent_id': state.continent_id,
                                    'name': state.name, 'info': state.info,
                                    'id': state.friendly_id})
        return True

