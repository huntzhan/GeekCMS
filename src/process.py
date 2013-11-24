import os
import markdown

from settings import TEMPLATE_DIR


class BasicPage(object):

    def __init__(self, env, *args, **kwargs):
        self.env = env
        self.url = self._generate_url(*args, **kwargs)
        self.html = self._generate_html(*args, **kwargs)

    def _generate_url(self, *args, **kwargs):
        pass

    def _generate_html(self, *args, **kwargs):
        pass


class ArticlePage(BasicPage):

    def __init__(self, env, article):
        super(ArticlePage, self).__init__(env, article)
        self.article = article

    def _generate_url(self, article):
        return article.url

    def _generate_html(self, article):
        template = self.env.get_template('article.html')
        # render markdown to html
        article_html = markdown.markdown(article.content)
        # insert html to template
        return template.render(article_html=article_html)
    
        
class HomePage(BasicPage):

    def _generate_url(self, *args, **kwargs):
        return '/home/page.html'

    def _generate_html(self, article_set):
        template = self.env.get_template('home.html')
        return template.render(article_html='nothing')


class ArticleSetPreprocessor(object):

    def __call__(self, article_set):
        return sorted(
            article_set,
            key=lambda x: x.post_time,
        )


class ArchivePage(BasicPage):

    def _generate_url(self, *args, **kwargs):
        return '/archives/archives.html'

    def _generate_html(self, article_set):
        
        def construct_article_tree(article_tree, dirs):
            cur_node = article_tree
            for dir in dirs:
                if dir in cur_node:
                    cur_node = cur_node[dir]
                else:
                    cur_node[dir] = {}
                    cur_node = cur_node[dir]
            
            return cur_node

        # generate structure
        article_tree = {}
        for article in article_set:
            head, tail = os.path.split(article.relative_path)
            dirs = head.split('/')[1:]

            cur_node = construct_article_tree(article_tree, dirs)
            if None not in cur_node:
                cur_node[None] = []

            cur_node[None].append({
                'url': article.url,
                'title': article.title,
            })

        # render to html
        template = self.env.get_template('archives.html')
        return template.render(article_tree=article_tree)


class AboutPage(BasicPage):

    def _generate_url(self, *args, **kwargs):
        return '/about/me.html'

    def _generate_html(self, loader):
        template = self.env.get_template('article.html')
        article = loader('about/me.md')
        # render markdown to html
        article_html = markdown.markdown(article.content)
        # insert html to template
        return template.render(article_html=article_html)


class PageSetGenerator(object):

    def __init__(self, article_set, env, loader):
        self._page_set = []
        self._generate_article_page(env, article_set)
        self._generate_home_page(env, article_set)
        self._generate_archive_page(env, article_set)
        self._generate_about_page(env, loader)

    def _generate_article_page(self, env, article_set):
        for article in article_set:
            self._page_set.append(ArticlePage(env, article))

    def _generate_home_page(self, env, article_set):
        self._page_set.append(HomePage(env, article_set))

    def _generate_archive_page(self, env, article_set):
        self._page_set.append(ArchivePage(env, article_set))

    def _generate_about_page(self, env, loader):
        self._page_set.append(AboutPage(env, loader))

    def _get_page_set(self):
        return self._page_set
    page_set = property(_get_page_set)
