#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from string import Template
import urllib2
from BeautifulSoup import BeautifulSoup
from datetime import datetime
import codecs
import re
import  logging


class Hi2Wp:
    BASE_URL = 'http://hi.baidu.com'
    entry_id = 0
    prev_url = ''
    entries = []
    
    def __init__(self, blog_name):
        logging.debug('init...')
        Hi2Wp.prev_url = self.get_first_url(blog_name)
        logging.debug('get url of first entry: %s', Hi2Wp.prev_url)
        
    def download_page(self, page_url):
        logging.debug('downloading page: %s', page_url)
        request = urllib2.Request(page_url)
        request.add_header('User-agent', 'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0')
        page = urllib2.build_opener().open(request).read()
        
        return page.decode('gb2312', 'ignore')
        
    def get_first_url(self, blog_name):
        blog_url = Hi2Wp.BASE_URL + '/' + blog_name + '/blog'
        page = self.download_page(blog_url)
        soup = BeautifulSoup(page)
        return Hi2Wp.BASE_URL + soup.findAll(attrs={'class':'tit'})[1].a['href']
        
    #百度博客改版了，普通方法提取不到评论，该方法已失效
    def get_comments(self, m_blog):
        user_comment_list = m_blog.find(attrs={'id':'in_comment'})
        print user_comment_list
        
        comments = user_comment_list.findall(attrs={'class':'item'})
        for comment in comments:
            ucard = comment.find(attrs={'class':'ucard'})
            name = str(ucard)
            url = ucard('href')
            print name
            print url
    
    def get_entry(self, entry_url):
        entry = {'id':'', 'title':'', 'date':'', 'content':'', 'category':''}

        page = self.download_page(entry_url)
        soup = BeautifulSoup(page)
        
        m_blog = soup.find(attrs={'id':'m_blog'})
        
        #获得ID，标题，日期，博客正文
        Hi2Wp.entry_id = Hi2Wp.entry_id + 1
        entry['id'] = Hi2Wp.entry_id
        
        title = m_blog.find(attrs={'class':'tit'}).contents[0].strip()
        entry['title'] = unicode(title) 
        date = m_blog.find(attrs={'class':'date'}).contents[0].strip()
        entry['date'] = unicode(date)
        content = m_blog.find(attrs={'id':'blog_text'})
        entry['content'] = unicode(content)
        
        #获得分类
        blog_opt = m_blog.find(attrs={'id':'blogOpt'})
        entry['category'] = blog_opt.findAll('a')[0].string.strip().replace(u'类别：', '')
        
        logging.debug('title: %s', entry['title'])
        logging.debug('date: %s', entry['date'])
        logging.debug('category: %s', entry['category'])
        
        #获得上一篇日志的url
        p = re.compile(r"var pre = \[(.*?),.*?,.*?,'(.*?)'\]")
        m = p.search(str(blog_opt))
        
        if m and m.group(1) == 'true':
            Hi2Wp.prev_url = Hi2Wp.BASE_URL + m.group(2)
        else:
            Hi2Wp.prev_url = None
            
        return entry
    
    def get_entries(self):
        while Hi2Wp.prev_url:
            entry = self.get_entry(Hi2Wp.prev_url)
            Hi2Wp.entries.append(entry)
            
    def get_xml(self):
        header = u"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- This is a WordPress eXtended RSS file generated by WordPress as an export of your site. -->
<!-- It contains information about your site's posts, pages, comments, categories, and other content. -->
<!-- You may use this file to transfer that content from one site to another. -->
<!-- This file is not intended to serve as a complete backup of your site. -->

<!-- To import this information into a WordPress site follow these steps: -->
<!-- 1. Log in to that site as an administrator. -->
<!-- 2. Go to Tools: Import in the WordPress admin panel. -->
<!-- 3. Install the "WordPress" importer from the list. -->
<!-- 4. Activate & Run Importer. -->
<!-- 5. Upload this file using the form provided on that page. -->
<!-- 6. You will first be asked to map the authors in this export file to users -->
<!--    on the site. For each author, you may choose to map to an -->
<!--    existing user on the site or to create a new user. -->
<!-- 7. WordPress will then import each of the posts, pages, comments, categories, etc. -->
<!--    contained in this file into your site. -->

<!-- generator="WordPress/3.2.1" created="2011-08-13 07:21" -->
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.1/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.1/"
>

<channel>
        <wp:wxr_version>1.1</wp:wxr_version>
        <generator>http://wordpress.org/?v=3.2.1</generator>
        """
        
        footer = u"""</channel>
        </rss>
        """
        
        itemT = Template(u"""<item>
        <title>${title}</title>
        <description/>
        <content:encoded><![CDATA[${content}]]></content:encoded>
        <excerpt:encoded></excerpt:encoded>
        <wp:post_id>${id}</wp:post_id>
        <wp:post_date_gmt>${date}</wp:post_date_gmt>
        <wp:comment_status>open</wp:comment_status>
        <wp:ping_status>open</wp:ping_status>
        <wp:post_name>${title}</wp:post_name>
        <wp:status>publish</wp:status>
        <wp:post_parent>0</wp:post_parent>
        <wp:menu_order>0</wp:menu_order>
        <wp:post_type>post</wp:post_type>
        <wp:post_password/>
        <wp:is_sticky>0</wp:is_sticky>
        <category domain="category">${category}</category>
        </item>
        """)
        
        xml = header
        for entry in Hi2Wp.entries:
            xml = xml + itemT.substitute(entry)
        xml = xml + footer
        
        return xml


    def write_to_file(self):
        xml = self.get_xml()
        file_name = 'hi2wp-' + datetime.now().strftime('%Y%m%d-%H%M') + '.xml'
        logging.debug('writing to file %s, %d entries in total', file_name, len(Hi2Wp.entries))
        f = codecs.open(file_name, 'w', 'utf-8')
        f.write(xml)
        f.close()
                
    def run(self):
        self.get_entries()
        self.write_to_file()
         
def usage():
	print 'Usage: python Hi2wp.py blog_id'

if __name__ == '__main__':
	if len(sys.argv) != 2:
		usage()
	else:
	    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename='hi2wp.log', filemode='w')
        Hi2Wp('卧槽只用一次').run()
