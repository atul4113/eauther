import io
import xml
from xml.parsers import expat
from xml.sax import saxutils
from xml.sax.saxutils import quoteattr, _gettextwriter


class EchoXMLGenerator(object):
    """
        XML parser with const memory usage.



        For parse XML override necessary methods to receive correct data.
        To generate XML, call original methods to generate correct XML elements.
    """

    """
        Args:
            out - File-like interface for EchoXML output or none if there should not be output
            encoding - encoding of input file
            process_instruction - if you want to parse special XML syntax from input XML, for example <% stylesheet %> then set this flag as True
            xml_header - put default xml header to output xml
    """
    def __init__(self, out=None, encoding="utf-8", process_instruction=True, xml_header=True, *args, **kwargs):
        self._in_cdata = 0

        self._xml_len = 0
        self._process_instruction = process_instruction
        self._put_xml_header = xml_header
        self._encoding = encoding

        self.bufsize = 1024
        self._has_internal_entities = False

        if out is None:
            self._write = lambda x: ''
        else:
            out = _gettextwriter(out, encoding=encoding)
            self._write = out.write

    def xml_declaration_handler(self, version, encoding, standalone):
        if standalone == -1:
            self._write('<?xml version="%s" encoding="%s"?>' % (version or "1.0", encoding or self._encoding))
        else:
            self._write('<?xml version="%s" encoding="%s" standalone="%s" ?>' % (version or "1.0", encoding or self._encoding, "yes" if standalone == 1 else "no"))

    """
        Content of cdata or element text content will be processed by this method. 
        WARNING:
            This method can be called more than once for one element or cdata section
        Args:
            content - values read by expat parser
    """
    def characters(self, content):
        if self._in_cdata:
            if not isinstance(content, str):
                content = str(content, self._encoding)
            self._write_protected(content)
        else:
            if not isinstance(content, str):
                content = str(content, self._encoding)
            self._write_protected(xml.sax.saxutils.escape(content))

    """
        Start cdata section
    """
    def start_cdata(self):
        self._write_protected('<![CDATA[')
        self._in_cdata = 1

    """
        End of cdata section
    """
    def end_cdata(self):
        self._write_protected(']]>')
        self._in_cdata = 0

    """
        Comment defined in XML. Only comment content will be passed to this function.
        Example: <!-- comment :) -->
        Args:
            content: comment content
    """
    def comment(self, content):
        self._write_protected('<!--%s-->' % content)

    """
        There will be information about document DOCTYPE
        Entities etc. will be passed to default_handler.
    """
    def start_dtd(self, name, system_id, public_id, has_internal_subset):
        self._write_protected('<!DOCTYPE %s' % name)
        if public_id:
            self._write_protected(' PUBLIC %s %s' % (
                saxutils.quoteattr(public_id),
                saxutils.quoteattr(system_id)))
        elif system_id:
            self._write_protected(' SYSTEM %s' % saxutils.quoteattr(system_id))

        if has_internal_subset == 1:
            self._has_internal_entities = True
            self._write_protected(' [')

    """
        End of DOCTYPE header
    """
    def end_dtd(self):
        if self._has_internal_entities:
            self._write_protected(']')

        self._write_protected('>')

    """
        Instructions defined in xml like <?PITarget PIContent?>
        Args:
            target: instruction name
            data: data passed to instruction
    """
    def processing_instruction(self, target, data):
        if self._process_instruction:
            self._write_protected('<?%s %s?>' % (target, data))

    """
        If expat parser will match start element then this callback will be called
        Args:
            name: name of element
            attrs: object as key:value
    """
    def start_element(self, name, attrs):
        self._write_protected('<' + name)
        for (name, value) in list(attrs.items()):
            self._write_protected(' %s=%s' % (name, quoteattr(value)))
        self._write_protected('>')

    def end_element(self, name):
        self._write_protected('</%s>' % name)

    """
        Text which expat parser doesen't match
        Args:
            data - text
    """
    def default_handler(self, data):
        self._write_protected(data)

    """
        Parse XML from source
        Args:
            source - xml source as file like interface
    """
    def parse(self, source):
        def start_element_wrapper (name, attr):
            new_attrs = {}
            for (key, value) in list(attr.items()):
                new_attrs[key] = value

            self.start_element(name, new_attrs)


        parser = xml.parsers.expat.ParserCreate()

        parser.XmlDeclHandler = self.xml_declaration_handler
        parser.StartDoctypeDeclHandler = self.start_dtd
        parser.EndDoctypeDeclHandler = self.end_dtd
        parser.StartElementHandler = start_element_wrapper
        parser.EndElementHandler = self.end_element
        parser.ProcessingInstructionHandler = self.processing_instruction
        parser.CharacterDataHandler = self.characters
        parser.CommentHandler = self.comment
        parser.StartCdataSectionHandler = self.start_cdata
        parser.EndCdataSectionHandler = self.end_cdata
        parser.DefaultHandler = self.default_handler

        parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        parser.UseForeignDTD(False)

        buff = source.read(self.bufsize)

        while buff != "":
            parser.Parse(buff)

            buff = source.read(self.bufsize)

    def _write_protected(self, content):
        self._xml_len += len(content)

        self._write(content)


class OutputEchoXMLGenerator(EchoXMLGenerator):
    def __init__(self, *args, **kwargs):
        handler_output = io.StringIO('')
        kwargs['out'] = handler_output

        super(OutputEchoXMLGenerator, self).__init__(*args, **kwargs)

        self.__handler_output = handler_output

    def get_output_value(self):
        return self.__handler_output.getvalue()