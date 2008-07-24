<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:param name="contextid">n1</xsl:param>
    <xsl:variable name="contextnode" select="id($contextid)"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>
                    <xsl:value-of select="$contextnode/title"/>
                </title>
            </head>
            <body>
                <h2>
                    <xsl:value-of select="$contextnode/title"/>
                </h2>
                <xsl:apply-templates select="$contextnode"/>
                <table border="1" cellpadding="6" cellspacing="0">
                    <tr>
                        <th>Type</th>
                        <th>@xml:id</th>
                        <th>@name</th>
                        <th>Parent Type</th>
                        <th>Parent @name</th>
                    </tr>
                    <tr>
                        <td>
                            <xsl:value-of select="name($contextnode)"/>
                        </td>
                        <td>
                            <xsl:value-of select="$contextnode/@xml:id"/>
                        </td>
                        <td>
                            <xsl:value-of select="$contextnode/@name"/>
                        </td>
                        <td>
                            <xsl:value-of select="name($contextnode/..)"/>
                        </td>
                        <td>
                            <xsl:value-of select="$contextnode/../@name"/>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="folder">
        <p>
            <em>Folders are special, they contain things.</em>
        </p>
        <xsl:if test="*[@xml:id]">
            <h2>Folder Contents</h2>
            <ul>
                <xsl:for-each select="*[@xml:id]">
                    <li>
                        <a href="{../@name}/{@name}">
                            <xsl:value-of select="title"/>
                        </a>
                    </li>
                </xsl:for-each>
            </ul>
        </xsl:if>
    </xsl:template>
    <xsl:template match="document">
        <p>
            <em>Documents contain text.</em>
        </p>
        <xsl:copy-of select="body/*"/>
    </xsl:template>
</xsl:stylesheet>
