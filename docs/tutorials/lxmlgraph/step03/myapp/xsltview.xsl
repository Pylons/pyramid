<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match="/document">
        <html>
            <head/>
            <body>
                <h1>My template is viewing item: <xsl:value-of select="@name"/></h1>
                <p>The node has a name of: <xsl:value-of select="name()"/>.</p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
