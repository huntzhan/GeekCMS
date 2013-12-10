from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as ET
import re

script_mapping = {
    'applescript': 'shBrushAppleScript.js',
    'actionscript3': 'shBrushAS3.js',
    'as3': 'shBrushAS3.js',
    'bash': 'shBrushBash.js',
    'shell': 'shBrushBash.js',
    'coldfusion': 'shBrushColdFusion.js',
    'cf': 'shBrushColdFusion.js',
    'cpp': 'shBrushCpp.js',
    'c': 'shBrushCpp.js',
    'c#': 'shBrushCSharp.js',
    'c-sharp': 'shBrushCSharp.js',
    'csharp': 'shBrushCSharp.js',
    'css': 'shBrushCss.js',
    'delphi': 'shBrushDelphi.js',
    'pascal': 'shBrushDelphi.js',
    'diff': 'shBrushDiff.js',
    'patch': 'shBrushDiff.js',
    'pas': 'shBrushDiff.js',
    'erl': 'shBrushErlang.js',
    'erlang': 'shBrushErlang.js',
    'groovy': 'shBrushGroovy.js',
    'java': 'shBrushJava.js',
    'jfx': 'shBrushJavaFX.js',
    'javafx': 'shBrushJavaFX.js',
    'js': 'shBrushJScript.js',
    'jscript': 'shBrushJScript.js',
    'javascript': 'shBrushJScript.js',
    'perl': 'shBrushPerl.js',
    'pl': 'shBrushPerl.js',
    'php': 'shBrushPhp.js',
    'text': 'shBrushPlain.js',
    'plain': 'shBrushPlain.js',
    'py': 'shBrushPython.js',
    'python': 'shBrushPython.js',
    'ruby': 'shBrushRuby.js',
    'rails': 'shBrushRuby.js',
    'ror': 'shBrushRuby.js',
    'rb': 'shBrushRuby.js',
    'sass': 'shBrushSass.js',
    'scss': 'shBrushSass.js',
    'scala': 'shBrushScala.js',
    'sql': 'shBrushSql.js',
    'vb': 'shBrushVb.js',
    'vbnet': 'shBrushVb.js',
    'xml': 'shBrushXml.js',
    'xhtml': 'shBrushXml.js',
    'xslt': 'shBrushXml.js',
    'html': 'shBrushXml.js',
}

class SyntaxHighlighter(Treeprocessor):

    def iterparent(self, root):
        for parent in root.iter():
            for child in parent:
                yield parent, child

    def run(self, root):
        pattern = re.compile('\[lang=(\w+?)\]')
        scripts = []
        for parent, child in self.iterparent(root):
            # check
            if parent.tag != 'pre':
                continue
            # ok
            m = pattern.match(child.text.lstrip())
            if m is not None:
                # find it!
                lang = m.group(1).lower()
                script = script_mapping.get(lang, None)
                if script:
                    scripts.append(script)
                    parent.attrib['class'] = 'brush: ' + lang
                # remove pattern
                text = re.sub('\[lang=(\w+?)\]', '', child.text)
                parent.remove(child)
                parent.text = text


        if len(scripts) > 0:
            url = 'http://alexgorbatchev.com/pub/sh/current/'
            # necessary js and css
            core_js_dom = ET.Element('script')
            core_js_dom.attrib['src'] = url + 'scripts/shCore.js'
            core_js_dom.attrib['type'] = 'text/javascript'

            autoload_dom = ET.Element('script')
            autoload_dom.attrib['src'] = url + 'scripts/shAutoloader.js'
            autoload_dom.attrib['type'] = 'text/javascript'

            core_css_dom = ET.Element('link')
            core_css_dom.attrib['href'] = url + 'styles/shCore.css'
            core_css_dom.attrib['rel'] = 'stylesheet'
            core_css_dom.attrib['type'] = 'text/css'

            default_theme_dom = ET.Element('link')
            default_theme_dom.attrib['href'] = url + 'styles/shThemeDefault.css'
            default_theme_dom.attrib['rel'] = 'stylesheet'
            default_theme_dom.attrib['type'] = 'text/css'

            fix_style_dom = ET.Element('style')
            fix_style_dom.text = """
            .syntaxhighlighter .container:before, .container:after {
	        content: none;
	        display: table;
	    }
            """
            # append
            root.insert(0, fix_style_dom)
            root.insert(0, default_theme_dom)
            root.insert(0, core_css_dom)
            root.insert(0, autoload_dom)
            root.insert(0, core_js_dom)

            # create autoload
            script_dom = ET.Element('script')
            script_dom.attrib['type'] = "text/javascript"
            script_dom.text = """
            function path()
            {
              var args = arguments,
                  result = []
                  ;

              for(var i = 0; i < args.length; i++)
            """ + """
                  result.push(args[i].replace('@', '{}'));
            """.format(url + 'scripts/') +  """

              return result
            };

            SyntaxHighlighter.autoloader.apply(null, path(
              'applescript            @shBrushAppleScript.js',
              'actionscript3 as3      @shBrushAS3.js',
              'bash shell             @shBrushBash.js',
              'coldfusion cf          @shBrushColdFusion.js',
              'cpp c                  @shBrushCpp.js',
              'c# c-sharp csharp      @shBrushCSharp.js',
              'css                    @shBrushCss.js',
              'delphi pascal          @shBrushDelphi.js',
              'diff patch pas         @shBrushDiff.js',
              'erl erlang             @shBrushErlang.js',
              'groovy                 @shBrushGroovy.js',
              'java                   @shBrushJava.js',
              'jfx javafx             @shBrushJavaFX.js',
              'js jscript javascript  @shBrushJScript.js',
              'perl pl                @shBrushPerl.js',
              'php                    @shBrushPhp.js',
              'text plain             @shBrushPlain.js',
              'py python              @shBrushPython.js',
              'ruby rails ror rb      @shBrushRuby.js',
              'sass scss              @shBrushSass.js',
              'scala                  @shBrushScala.js',
              'sql                    @shBrushSql.js',
              'vb vbnet               @shBrushVb.js',
              'xml xhtml xslt html    @shBrushXml.js'
            ));
            SyntaxHighlighter.all();
            """

            root.append(script_dom)
        return root


class SyntaxHighlighterExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        # Insert instance of 'mypattern' before 'references' pattern
        md.treeprocessors.add(
            "syntax_highlighter",
            SyntaxHighlighter(md),
            "_end"
        )
