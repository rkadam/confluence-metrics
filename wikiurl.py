#!/usr/bin/env python

"""
wikiurl.py

Class that interprets a Confluence wiki URL

"""

import urllib

class WikiUrl:

    def __init__(self, url, userid, timestamp, ipaddress):

        self.actionType             = ""                # one of display, download, or pages
        self.userAction             = ""                # will be create, view (for action Types - display, pages with viewpage.action), edit (pages with editpage.action) and so on
        self.userSubAction          = ""                # for user Action -> "Create", subaction will be "page" or "space" or "blogpost" or so.
        self.actionName             = ""                # <something>.action, e.g. "editpage.action", empty if actionType != "pages"
        self.pageId                 = ""                # some URLs have a pageId property, including attachments and doeditpage, among others
                                                        # We will need to get custom filter class to get this value all .action urls. Current ConfluenceAccessFilter does not provide this values.
        self.queryString            = ""                # part of URL occurring after optional '?' character, empty if URL has no query component
        self.queryProperties        = ""                # list of properties in query string, in form "<propertyName>=<propertyValue>"
        #self.queryDictionary        = []               # Dictionary of key values from querystring.

        self.spacekey               = ""
        self.title                  = ""                # page title or attachment file name
        self.unknownActionUrl       = ""                # this contains value only for unknown action types.

        self.datetimestamp          = timestamp         # time at which user did this activity
        self.userid                 = userid            # User can be '-' when accessing pages as anonymous user.
        self.ipaddress              = ipaddress         # User ip address

        urlHalves = url.split('?')
        url = urlHalves[0]
        if len(urlHalves) > 1:
            self.queryString = urlHalves[1]

        #self.queryDictionary = dict(u.split("=") for u in self.queryString.split("&"))

        self.queryProperties = self.queryString.split('&')

        # trim any leading slashes from URL (sometimes there are two or more)
        while url[0] == '/':
            url = url[1:]

        urlParts = url.split('/')  # e.g. ['display', 'competitive', 'Juniper+Blog']

        self.actionType = urlParts[0]

        if self.actionType == "display":

            self.userAction = "view"

            # url "/display" is valid, and redirects to dashboard page
            if len(urlParts) == 0:
                self.userSubAction = "dashboard"
            else:
                self.userSubAction = "page"

            # url "/display/<spacekey>" is valid, and redirects to home page of space
            if len(urlParts) > 1:
                self.spacekey = urlParts[1].lower()

            # url "/display/<spacekey>/<pagetitle>" is most common
            if len(urlParts) > 2:
                self.title = urlParts[2]

        elif self.actionType == "download":

            self.userAction = "download"

            # url "/download/<downloadtype>/..." is general form
            if len(urlParts) > 1:
                self.userSubAction = urlParts[1]

            # url "/download/attachments/..." is only interesting form so far
            if self.userSubAction == "attachments":
                if len(urlParts) > 2:
                    self.pageId = urlParts[2]
                if len(urlParts) > 3:
                    self.title = urlParts[3]

        # url "dashboard/configurerssfeed.action"

        # url "labels/<action>"
        elif self.actionType == "labels":

            if len(urlParts) > 1:
                self.userAction = urlParts[1]

                if self.userAction == "listlabels-heatmap.action":
                    self.userAction = "list"
                    self.userSubAction = "labels heatmap"
                elif self.userAction == "viewlabel.action":
                    self.userAction = "view"
                    self.userSubAction = "label"

        # url "spaces/<action>" is general form
        # dochoosetheme.action
        # doeditspace.action
        # doeditspacepermissions.action
        # doeditstylesheet.action
        # doemptytrash.action
        # doexportspace.action
        # doimportpages.action
        # dopurgetrashitem.action
        elif self.actionType == "spaces":
            if len(urlParts) > 1:
                self.actionName = urlParts[1]

                if self.actionName == "dochoosetheme.action":
                    self.userAction = "choose"
                    self.userSubAction = "theme"
                elif self.actionName == "doeditspace.action":
                    self.userAction = "edit"
                    self.userSubAction = "space"
                elif self.actionName == "doeditspacepermissions":
                    self.userAction = "edit"
                    self.userSubAction = "spacepermissions"
                elif self.actionName == "doeditstylesheet.action":
                    self.userAction = "edit"
                    self.userSubAction = "stylesheet"
                elif self.actionName == "doemptytrash.action":
                    self.userAction = "empty"
                    self.userSubAction = "trash"
                elif self.actionName == "doexportspace.action":
                    self.userAction = "export"
                    self.userSubAction = "space"
                elif self.actionName == "doimportpages.action":
                    self.userAction = "import"
                    self.userSubAction = "pages"
                elif self.actionName == "dopurgetrashitem.action":
                    self.userAction = "purge"
                    self.userSubAction = "trashitem"
                elif self.actionName == "listattachmentsforspace.action":
                    self.userAction = "list"
                    self.userSubAction = "attachments"
                elif self.actionName == "space-bookmarks.action":
                    self.userAction = "view"
                    self.userSubAction = "bookmarks"
                elif self.actionName == "viewspacesummary.action":
                    self.userAction = "view"
                    self.userSubAction = "spacesummary"
                elif self.actionName == "listorphanedpages.action":
                    self.userAction = "list"
                    self.userSubAction = "orphanedpages"
                elif self.actionName == "listundefinedpages.action":
                    self.userAction = "list"
                    self.userSubAction = "undefinedpages"
                elif self.actionName == "listrssfeeds.action":
                    self.userAction = "list"
                    self.userSubAction = "rssfeeds"
                elif self.actionName == "addspacetofavourites.action":
                    self.userAction = "add"
                    self.userSubAction = "space to favourites"

        # url "/pages/<action>" is general form
        # There are all the possible actions I know of. Interesting ones are marked with an asterisk:
        #   doattachfile.action
        #   docopypage.action
        #   docreatepagetemplate.action
        #   children.action                   Shows child page without page context, perhaps {children} macro
        # * docreateblogpost.action             Add Content > Add News
        # * docreatepage.action                 Add Content > Add Page
        #   diffpages.action                  Page Operations > Info > view changes (between page versions in page history)
        # * docreatepage.action               Add Content > Add Page > Save
        # * doeditpage.action                 Page Operations > Edit > Save
        # * doexportpage.action               Page Operations > Info > Export As: > PDF | Word
        #   dopurgetrashitem.action           Browse Space > Space Admin > Trash > Purge > OK
        #   doremovepage.action               Page Operations > Edit > Remove Page > Ok
        # * editpage.action                   Page Operations > Edit
        #   listpages-alphaview.action        Browse Space > Pages > Alphabetical
        #   listpages-dirview.action          Browse Space > Pages > Tree
        #   listpages.action                  Browse Space > Pages
        #   pageinfo.action                   Page Operations > Info
        #   purgetrashitem.action             Browse Space > Space Admin > Trash > Purge
        #   recentlyupdated.action            Browse Space > Pages > Recently Updated
        #   removepage.action                 Page Operations > Edit > Remove Page
        # * viewpage.action                   Same as /display/<pagetitle>, used when page title contains certain special characters
        #   viewpageattachments.action        Page Operations > Attachments
        #   viewpreviouspageversions.action   Page Operations > Info > View page history
        #   viewrecentblogposts.action        Browse Space > News
        #   viewtrash.action                  Browse Space > Space Admin > Trash
        elif self.actionType == "pages":

            if len(urlParts) > 1:

                self.actionName = urlParts[1]

                if(self.actionName == "doattachfile.action"):
                    self.userAction = "attach"
                    self.userSubAction = "file"
                elif (self.actionName == "docreatepagetemplate.action"):
                    self.userAction = "create"
                    self.userSubAction = "pagetemplate"
                elif (self.actionName == "docopypage.action"):
                    self.userAction = "copy"
                    self.userSubAction = "page"
                elif (self.actionName == "docreateblogpost.action"):
                    self.userAction = "create"
                    self.userSubAction = "blogpost"
                elif (self.actionName == "docreatepage.action"):
                    self.userAction = "create"
                    self.userSubAction = "page"
                elif (self.actionName == "doeditblogpost.action"):
                    self.userAction = "edit"
                    self.userSubAction = "blogpost"
                elif (self.actionName == "doeditattachment.action"):
                    self.userAction = "edit"
                    self.userSubAction = "attachment"
                elif (self.actionName == "doeditcomment.action"):
                    self.userAction = "edit"
                    self.userSubAction = "comment"
                elif (self.actionName == "doeditpage.action"):
                    self.userAction = "edit"
                    self.userSubAction = "page"
                elif (self.actionName == "doeditpagetemplate.action"):
                    self.userAction = "edit"
                    self.userSubAction = "pagetemplate"
                elif (self.actionName == "doexportpage.action"):
                    self.userAction = "export"
                    self.userSubAction = "page"
                elif (self.actionName == "doremoveblogpost.action"):
                    self.userAction = "remove"
                    self.userSubAction = "blogpost"
                elif (self.actionName == "doremovepage.action"):
                    self.userAction = "remove"
                    self.userSubAction = "page"
                elif (self.actionName == "doremovepagetemplate.action"):
                    self.userAction = "remove"
                    self.userSubAction = "pagetemplate"
                elif (self.actionName == "dashboard.action"):
                    self.userAction = "view"
                    self.userSubAction = "dashboard"
                elif (self.actionName == "diffpages.action"):
                    self.userAction = "diff"
                    self.userSubAction = "page"
                elif (self.actionName == "viewpage.action"):
                    self.userAction = "view"
                    self.userSubAction = "page"
                elif (self.actionName == "viewpageattachments.action"):
                    self.userAction = "view"
                    self.userSubAction = "pageattachments"
                elif (self.actionName == "viewrecentblogposts.action"):
                    self.userAction = "view"
                    self.userSubAction = "recentblogposts"
                elif (self.actionName == "viewtrash.action"):
                    self.userAction = "view"
                    self.userSubAction = "trash"
                elif (self.actionName == "doemptytrash.action"):
                    self.userAction = "empty"
                    self.userSubAction = "trash"
                elif (self.actionName == "listpages.action"):
                    self.userAction = "list"
                    self.userSubAction = "pages"
                elif (self.actionName == "listpages-dirview.action"):
                    self.userAction = "list"
                    self.userSubAction = "pages in tree view"
                elif (self.actionName == "listpages-alphaview.action"):
                    self.userAction = "list"
                    self.userSubAction = "pages in alpha view"
                elif (self.actionName == "dopurgetrashitem.action"):
                    self.userAction = "delete"
                    self.userSubAction = "pages"
                elif (self.actionName == "recentlyupdated.action"):
                    self.userAction = "recentlyupdated"
                    self.userSubAction = "pages"

            # Interpret query string-----------------------

            # harvest relevant properties from the query string
            for propertyString in self.queryProperties:

                sides = propertyString.split('=')

                property = sides[0]

                if len(sides) > 1:
                    value = sides[1]
                else:
                    value = ""

                if   property == "pageId"   : self.pageId   = value
                elif property == "title"    : self.title    = value
                elif property == "spaceKey" : self.spacekey = value

        elif (self.actionType == "homepage.action"):
            # This url needs to be skipped as it is redirected to HOME url as set by Confluence Administrator
            self.actionType = "display"
            self.actionName = "homepage.action"
        else:
            #We haven't figured out what this relative url is about. So let's store it as it is.
            #Also handle any special case relative URLs such as homepage.action

            self.actionType = "unknown"
            self.unknownActionUrl = url

        # remove URL encoding on title
        if len(self.title) > 0:
            self.title = urllib.unquote_plus(self.title)


    def __repr__(self):
        return "<Wiki Entry: userid=%s, ipaddress=%s, actionType=%s, userAction=%s, userSubAction=%s, unknownActionUrl=%s, space=%s, title=%s, actionName=%s, pageId=%s, queryString=%s, queryProperties=%s, datetimestamp=%s" % (self.userid, self.ipaddress, self.actionType, self.userAction, self.userSubAction, self.unknownActionUrl, self.spacekey, self.title, self.actionName, self.pageId, self.queryString, self.queryProperties, self.datetimestamp)

